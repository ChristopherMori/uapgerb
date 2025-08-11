#!/usr/bin/env python3
import argparse
import datetime, time, random, re
from pathlib import Path
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import frontmatter, slugify

DEFAULT_CHANNEL = "https://www.youtube.com/@UAPGerb"
DEFAULT_OUT_DIR = Path("docs/transcripts")

def get_channel_id(handle_or_url: str) -> str:
    with YoutubeDL({'quiet': True, 'extract_flat': True, 'dump_single_json': True}) as ydl:
        info = ydl.extract_info(handle_or_url, download=False)
    for k in ("channel_id", "uploader_id", "id"):
        cid = info.get(k)
        if cid and cid.startswith("UC"):
            return cid
    raise RuntimeError("Could not resolve channel_id")

def list_uploads_entries(channel_id: str):
    uploads = "UU" + channel_id[2:]
    url = f"https://www.youtube.com/playlist?list={uploads}"
    with YoutubeDL({'quiet': True, 'extract_flat': True, 'dump_single_json': True}) as ydl:
        pl = ydl.extract_info(url, download=False)
    return pl.get("entries", [])

def safe_date(entry):
    ts = entry.get("timestamp") or entry.get("release_timestamp")
    if ts:
        return datetime.datetime.utcfromtimestamp(ts).date()
    up = entry.get("upload_date")
    if up and re.fullmatch(r"\d{8}", up):
        return datetime.datetime.strptime(up, "%Y%m%d").date()
    return datetime.date.today()

def best_effort_transcript(video_id: str, prefer_langs=("en",)):
    try:
        lst = YouTubeTranscriptApi.list_transcripts(video_id)
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
    except (TranscriptsDisabled, NoTranscriptFound):
        return "*No transcript available yet*"
    except Exception:
        for i in range(3):
            try:
                time.sleep((2 ** i) + random.random())
                segs = YouTubeTranscriptApi.get_transcript(video_id, languages=list(prefer_langs))
                return "\n\n".join(seg["text"] for seg in segs)
            except Exception:
                continue
        return "*Transcript fetch error – will retry later*"

def write_page(entry, out_dir: Path) -> bool:
    vid   = entry["id"]
    title = entry.get("title") or vid
    date  = safe_date(entry)
    slug  = f"{date}--{slugify.slugify(title, lowercase=True)[:60]}--{vid}.md"
    path  = out_dir / slug

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
            "tags": ["uap", "gerb"]
        }
    )
    new_text = frontmatter.dumps(post)
    if path.exists() and path.read_text(encoding="utf-8") == new_text:
        return False
    path.write_text(new_text, encoding="utf-8")
    print("Saved", path.name)
    return True

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
    entries = list_uploads_entries(cid)
    if args.max_videos is not None:
        entries = entries[:args.max_videos]
    changed = False
    for e in entries:
        if not e.get("id") or e.get("_type") == "url":
            continue
        changed |= write_page(e, out_dir)
    print("Done. Changed =", changed)

if __name__ == "__main__":
    main()
