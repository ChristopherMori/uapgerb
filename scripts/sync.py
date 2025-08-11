#!/usr/bin/env python3
import datetime, logging, random, re, time
from functools import partial
from pathlib import Path
from typing import Callable

from yt_dlp import YoutubeDL
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)
import frontmatter, slugify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HANDLE_OR_URL = "https://www.youtube.com/@UAPGerb"
OUT_DIR = Path("docs/transcripts")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def get_channel_id(handle_or_url: str) -> str:
    """Resolve a channel handle or URL to a channel ID.

    Parameters
    ----------
    handle_or_url:
        The YouTube handle (e.g., ``"@user"``) or full channel URL.

    Returns
    -------
    str
        The channel ID starting with ``"UC"``.

    Raises
    ------
    RuntimeError
        If no channel ID could be found in the response.
    """

    with YoutubeDL({"quiet": True, "extract_flat": True, "dump_single_json": True}) as ydl:
        info = ydl.extract_info(handle_or_url, download=False)
    for k in ("channel_id", "uploader_id", "id"):
        cid = info.get(k)
        if isinstance(cid, str) and cid.startswith("UC"):
            return cid
    raise RuntimeError("Could not resolve channel_id")

def list_uploads_entries(channel_id: str) -> list[dict[str, Any]]:
    """Return entries for the uploads playlist of a channel.

    Parameters
    ----------
    channel_id:
        The ID of the channel whose uploads playlist should be queried.

    Returns
    -------
    list[dict[str, Any]]
        A list of entry dictionaries as returned by ``yt_dlp``.
    """

    uploads = "UU" + channel_id[2:]
    url = f"https://www.youtube.com/playlist?list={uploads}"
    with YoutubeDL({"quiet": True, "extract_flat": True, "dump_single_json": True}) as ydl:
        pl = ydl.extract_info(url, download=False)
    entries = pl.get("entries", [])
    return entries if isinstance(entries, list) else []

def safe_date(entry: dict[str, Any]) -> datetime.date:
    """Extract the best available upload date from a playlist entry.

    Parameters
    ----------
    entry:
        The entry dictionary returned by ``yt_dlp``.

    Returns
    -------
    datetime.date
        The parsed date, falling back to today when unavailable.
    """

    ts = entry.get("timestamp") or entry.get("release_timestamp")
    if isinstance(ts, int):
        return datetime.datetime.utcfromtimestamp(ts).date()
    up = entry.get("upload_date")
    if isinstance(up, str) and re.fullmatch(r"\d{8}", up):
        return datetime.datetime.strptime(up, "%Y%m%d").date()
    return datetime.date.today()


def _join_segments(segs):
    return "\n\n".join(seg["text"] for seg in segs)


def _fetch_manual(lst, langs):
    t = lst.find_manually_created_transcript(langs)
    return _join_segments(t.fetch())


def _fetch_generated(lst, langs):
    t = lst.find_generated_transcript(langs)
    return _join_segments(t.fetch())


def _fetch_translation(lst, _):
    for t in lst:
        try:
            en = t.translate("en")
            return _join_segments(en.fetch())
        except Exception:
            continue
    raise NoTranscriptFound()


def _fetch_api_transcript(video_id: str, langs):
    return _join_segments(
        YouTubeTranscriptApi.get_transcript(video_id, languages=list(langs))
    )


def _fetch_with_retry(fn: Callable[[], str], retries: int = 3):
    last_exc = None
    for i in range(retries):
        try:
            return fn()
        except (TranscriptsDisabled, NoTranscriptFound):
            raise
        except Exception as e:
            last_exc = e
            logger.warning("Transcript fetch attempt %d failed: %s", i + 1, e)
            time.sleep((2 ** i) + random.random())
    raise last_exc


def best_effort_transcript(video_id: str, prefer_langs=("en",)):
    try:
        lst = YouTubeTranscriptApi.list_transcripts(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        logger.info("No transcripts for %s", video_id)
        return "*No transcript available yet*"
    except Exception as e:
        logger.warning("Listing transcripts failed for %s: %s", video_id, e)

        try:
            return _fetch_with_retry(partial(_fetch_api_transcript, video_id, prefer_langs))
        except (TranscriptsDisabled, NoTranscriptFound):
            logger.info("No transcripts for %s", video_id)
            return "*No transcript available yet*"
        except Exception as e2:
            logger.error("Retries failed for %s: %s", video_id, e2)
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
        except Exception as e:
            logger.info("Strategy %s failed for %s: %s", name, video_id, e)

    try:
        return _fetch_with_retry(partial(_fetch_api_transcript, video_id, prefer_langs))

    except (TranscriptsDisabled, NoTranscriptFound):
        logger.info("No transcripts for %s", video_id)
        return "*No transcript available yet*"
    except Exception as e:
        logger.error("Retries failed for %s: %s", video_id, e)

        return "*Transcript fetch error – will retry later*"

def write_page(entry: dict[str, Any]) -> bool:
    """Create or update a transcript page for a single video entry.

    Parameters
    ----------
    entry:
        The playlist entry containing video metadata.

    Returns
    -------
    bool
        ``True`` if a new file was written or an existing one updated,
        ``False`` if the existing file was unchanged.
    """

    vid = entry["id"]
    title = entry.get("title") or vid
    date = safe_date(entry)
    slug = f"{date}--{slugify.slugify(title, lowercase=True)[:60]}--{vid}.md"
    path = OUT_DIR / slug


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
    print("Saved", path.name)
    return True

def main() -> None:
    """Synchronise transcripts for the configured YouTube channel."""

    cid = get_channel_id(HANDLE_OR_URL)
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", default=DEFAULT_CHANNEL, help="YouTube channel handle or URL")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR, help="Directory to store transcripts")
    parser.add_argument("--max-videos", type=int, default=None, help="Maximum number of videos to sync")
    return parser.parse_args()

def main():
    args = parse_args()
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    cid = get_channel_id(args.channel)
