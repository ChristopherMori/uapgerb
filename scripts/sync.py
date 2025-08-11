#!/usr/bin/env python3
import argparse
import datetime, time, random, re
from pathlib import Path
from typing import Any, Sequence

import frontmatter  # type: ignore[import-untyped]
import slugify  # type: ignore[import-untyped]
from yt_dlp import YoutubeDL  # type: ignore[import-untyped]
from youtube_transcript_api import (  # type: ignore[import-untyped]
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

DEFAULT_CHANNEL = "https://www.youtube.com/@UAPGerb"
DEFAULT_OUT_DIR = Path("docs/transcripts")

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

def best_effort_transcript(video_id: str, prefer_langs: Sequence[str] = ("en",)) -> str:
    """Retrieve the transcript for a video, trying several strategies.

    The function first attempts to fetch a manually created transcript,
    then a generated one. If neither are available, it attempts to
    translate any transcript to English. As a final fallback it retries
    direct fetching a few times with exponential backoff.

    Parameters
    ----------
    video_id:
        The ID of the YouTube video.
    prefer_langs:
        Preferred languages ordered by priority.

    Returns
    -------
    str
        The concatenated transcript text or an informative placeholder
        on failure.
    """

    try:
        lst = YouTubeTranscriptApi.list_transcripts(video_id)  # type: ignore[attr-defined]
        try:
            t = lst.find_manually_created_transcript(prefer_langs)
            return "\n\n".join(seg["text"] for seg in t.fetch())
        except Exception:
            pass
        try:
            t = lst.find_generated_transcript(prefer_langs)
            return "\n\n".join(seg["text"] for seg in t.fetch())
        except Exception:
            pass
        for t in lst:
            try:
                en = t.translate("en")
                return "\n\n".join(seg["text"] for seg in en.fetch())
            except Exception:
                continue
        return "*No transcript available yet*"
    except (TranscriptsDisabled, NoTranscriptFound):
        return "*No transcript available yet*"
    except Exception:
        for i in range(3):
            try:
                time.sleep((2 ** i) + random.random())
                segs = YouTubeTranscriptApi.get_transcript(video_id, languages=list(prefer_langs))  # type: ignore[attr-defined]
                return "\n\n".join(seg["text"] for seg in segs)
            except Exception:
                continue
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
=======
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
