#!/usr/bin/env python3
"""Utilities for synchronising YouTube transcripts.

This module provides a small command line interface that downloads the
transcripts of the latest videos from a YouTube channel and stores them as
Markdown files inside ``docs/transcripts``.  The implementation is deliberately
light‑weight so that it can easily be tested.

Only a tiny subset of the original project is required for the unit tests in
this kata.  The focus therefore lies on the transcript fetching logic which is
exercised by ``tests/test_sync.py``.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import logging
import random
import re
import time
from functools import partial
from pathlib import Path
from typing import Any, Callable, Iterable

import frontmatter
import slugify
from yt_dlp import YoutubeDL
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Default values for the small CLI -------------------------------------------------------
DEFAULT_CHANNEL = "https://www.youtube.com/@UAPGerb"
DEFAULT_OUT_DIR = Path("docs/transcripts")


# Helper functions ----------------------------------------------------------------------

def get_channel_id(handle_or_url: str) -> str:
    """Resolve a YouTube handle or channel URL to a channel id.

    ``yt_dlp`` returns a number of different keys depending on the type of URL.
    We try a couple of options and raise an error if none yield a valid id.
    """

    with YoutubeDL({"quiet": True, "extract_flat": True, "dump_single_json": True}) as ydl:
        info = ydl.extract_info(handle_or_url, download=False)

    for key in ("channel_id", "uploader_id", "id"):
        cid = info.get(key)
        if isinstance(cid, str) and cid.startswith("UC"):
            return cid
    raise RuntimeError("Could not resolve channel_id")


def list_upload_entries(channel_id: str) -> list[dict[str, Any]]:
    """Return entries for the uploads playlist of ``channel_id``."""

    uploads = "UU" + channel_id[2:]
    url = f"https://www.youtube.com/playlist?list={uploads}"
    with YoutubeDL({"quiet": True, "extract_flat": True, "dump_single_json": True}) as ydl:
        pl = ydl.extract_info(url, download=False)
    entries = pl.get("entries", [])
    return entries if isinstance(entries, list) else []


def safe_date(entry: dict[str, Any]) -> _dt.date:
    """Extract the best available upload date from a playlist entry."""

    ts = entry.get("timestamp") or entry.get("release_timestamp")
    if isinstance(ts, int):
        return _dt.datetime.utcfromtimestamp(ts).date()
    up = entry.get("upload_date")
    if isinstance(up, str) and re.fullmatch(r"\d{8}", up):
        return _dt.datetime.strptime(up, "%Y%m%d").date()
    return _dt.date.today()


# Transcript fetching -------------------------------------------------------------------

def _join_segments(segs: Iterable[dict[str, str]]) -> str:
    return "\n\n".join(seg["text"] for seg in segs)


def _fetch_manual(lst, langs: Iterable[str]) -> str:
    t = lst.find_manually_created_transcript(langs)
    return _join_segments(t.fetch())


def _fetch_generated(lst, langs: Iterable[str]) -> str:
    t = lst.find_generated_transcript(langs)
    return _join_segments(t.fetch())


def _fetch_translation(lst, _langs: Iterable[str]) -> str:
    for t in lst:
        try:
            en = t.translate("en")
            return _join_segments(en.fetch())
        except Exception:
            continue
    raise NoTranscriptFound()


def _fetch_api_transcript(video_id: str, langs: Iterable[str]) -> str:
    return _join_segments(
        YouTubeTranscriptApi.get_transcript(video_id, languages=list(langs))
    )


def _fetch_with_retry(fn: Callable[[], str], retries: int = 3) -> str:
    """Run ``fn`` with exponential backoff on unexpected errors."""

    last_exc: Exception | None = None
    for i in range(retries):
        try:
            return fn()
        except (TranscriptsDisabled, NoTranscriptFound):
            raise
        except Exception as exc:  # pragma: no cover - logging
            last_exc = exc
            logger.warning("Transcript fetch attempt %d failed: %s", i + 1, exc)
            time.sleep((2**i) + random.random())
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("unreachable")  # pragma: no cover


def best_effort_transcript(video_id: str, prefer_langs: Iterable[str] = ("en",)) -> str:
    """Return the best available transcript for ``video_id``.

    The function mirrors the behaviour of the original project but in a concise
    and testable form.  It first tries to list available transcripts via the
    API.  Depending on the outcome different strategies are attempted and
    failures are retried a couple of times.
    """

    try:
        lst = YouTubeTranscriptApi.list_transcripts(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        logger.info("No transcripts for %s", video_id)
        return "*No transcript available yet*"
    except Exception as exc:  # pragma: no cover - logging
        logger.warning("Listing transcripts failed for %s: %s", video_id, exc)
        try:
            return _fetch_with_retry(partial(_fetch_api_transcript, video_id, prefer_langs))
        except (TranscriptsDisabled, NoTranscriptFound):
            logger.info("No transcripts for %s", video_id)
            return "*No transcript available yet*"
        except Exception as exc2:  # pragma: no cover - logging
            logger.error("Retries failed for %s: %s", video_id, exc2)
            return "*Transcript fetch error – will retry later*"

    strategies = [
        ("manual", partial(_fetch_manual, lst, prefer_langs)),
        ("generated", partial(_fetch_generated, lst, prefer_langs)),
        ("translation", partial(_fetch_translation, lst, prefer_langs)),
    ]

    for name, strat in strategies:
        try:
            return _fetch_with_retry(strat)
        except (NoTranscriptFound, TranscriptsDisabled):
            continue
        except Exception as exc:  # pragma: no cover - logging
            logger.info("Strategy %s failed for %s: %s", name, video_id, exc)

    try:
        return _fetch_with_retry(partial(_fetch_api_transcript, video_id, prefer_langs))
    except (TranscriptsDisabled, NoTranscriptFound):
        logger.info("No transcripts for %s", video_id)
        return "*No transcript available yet*"
    except Exception as exc:  # pragma: no cover - logging
        logger.error("Retries failed for %s: %s", video_id, exc)
        return "*Transcript fetch error – will retry later*"


# Writing pages ------------------------------------------------------------------------

def write_page(entry: dict[str, Any], out_dir: Path) -> bool:
    """Create or update a transcript page for a single video entry."""

    vid = entry["id"]
    title = entry.get("title") or vid
    date = safe_date(entry)
    slug = f"{date}--{slugify.slugify(title, lowercase=True)[:60]}--{vid}.md"
    path = out_dir / slug

    body = best_effort_transcript(vid)

    post = frontmatter.Post(
        f"""<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{vid}\" allowfullscreen></iframe>

---

## Transcript
{body}
""",
        **{
            "title": title,
            "date": str(date),
            "video_id": vid,
            "tags": ["uap", "gerb"],
        },
    )
    new_text = frontmatter.dumps(post)
    if path.exists() and path.read_text(encoding="utf-8") == new_text:
        return False
    path.write_text(new_text, encoding="utf-8")
    logger.info("Saved %s", path.name)
    return True


# CLI ----------------------------------------------------------------------------------

def sync(channel: str, out_dir: Path, max_videos: int | None = None) -> int:
    """Synchronise transcripts for ``channel`` into ``out_dir``.

    Returns the number of files that were created or updated.
    """

    out_dir.mkdir(parents=True, exist_ok=True)
    cid = get_channel_id(channel)
    entries = list_upload_entries(cid)
    if max_videos is not None:
        entries = entries[:max_videos]

    changed = 0
    for entry in entries:
        try:
            if write_page(entry, out_dir):
                changed += 1
        except Exception as exc:  # pragma: no cover - logging
            logger.error("Failed to write page for %s: %s", entry.get("id"), exc)
    return changed


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--channel", default=DEFAULT_CHANNEL, help="YouTube channel handle or URL"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Directory where transcripts should be stored",
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        help="Limit the number of videos processed",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> None:  # pragma: no cover - CLI wrapper
    args = _parse_args(argv)
    changed = sync(args.channel, args.output_dir, args.max_videos)
    logger.info("Processed %d videos", changed)


if __name__ == "__main__":  # pragma: no cover - script entry point
    main()

