#!/usr/bin/env python3
"""
Scan transcripts/ and data/videos.json to produce data/transcripts_index.json.

Schema of transcripts_index.json:
{
  "videos": [
    {
      "id": "yt-abc123",
      "youtube_id": "abc123",
      "title": "Video Title",
      "published_at": "2024-11-07",
      "duration": 822,
      "links": {"youtube": "https://www.youtube.com/watch?v=abc123"},
      "people": ["person:richard-l"],
      "locations": ["loc:oak-ridge-tn"],
      "tags": ["thermal","night"],
      "paths": {
        "clean_md": "transcripts/yt-abc123/yt-abc123.clean.md",
        "timecoded_md": "transcripts/yt-abc123/yt-abc123.timecoded.md",
        "segments_csv": "transcripts/yt-abc123/yt-abc123.segments.csv"
      }
    },
    ...
  ]
}
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import sys

# Allow running as a script by adding repo root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.common import (
    DATA_DIR,
    TRANSCRIPTS_DIR,
    read_json,
    write_json,
    rel,
)

VIDEOS_JSON = DATA_DIR / "videos.json"
OUT_JSON = DATA_DIR / "transcripts_index.json"


def main() -> None:
    videos_meta = read_json(VIDEOS_JSON, default={"videos": []})
    if isinstance(videos_meta, list):
        # Backward compat: allow a top-level list
        videos_list = videos_meta
    else:
        videos_list = videos_meta.get("videos", [])

    # Index by id for easy merge
    by_id: Dict[str, Dict[str, Any]] = {}
    for v in videos_list:
        vid = v.get("id") or v.get("video_id") or v.get("youtube_id")
        if not vid:
            continue
        # Normalize to "yt-<id>" if it looks like a bare YouTube id
        if not str(vid).startswith("yt-") and len(str(vid)) in (11, 12):
            vid_norm = f"yt-{vid}"
        else:
            vid_norm = str(vid)
        v["id"] = vid_norm
        # Map url to links.youtube if present
        url = v.pop("url", None)
        if url:
            links = v.get("links", {})
            links.setdefault("youtube", url)
            v["links"] = links
        by_id[vid_norm] = v

    # Scan transcripts/<video_id>/ for artifacts
    if not TRANSCRIPTS_DIR.exists():
        TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    for vf in TRANSCRIPTS_DIR.iterdir():
        if not vf.is_dir():
            continue
        video_id = vf.name

        # Ensure record exists
        rec = by_id.get(video_id)
        if not rec:
            rec = {"id": video_id, "title": video_id, "links": {}, "people": [], "locations": [], "tags": []}
            by_id[video_id] = rec

        clean_md = vf / f"{video_id}.clean.md"
        timecoded_md = vf / f"{video_id}.timecoded.md"
        segments_csv = vf / f"{video_id}.segments.csv"

        paths = rec.get("paths", {})
        if clean_md.exists():
            paths["clean_md"] = rel(clean_md)
        if timecoded_md.exists():
            paths["timecoded_md"] = rel(timecoded_md)
        if segments_csv.exists():
            paths["segments_csv"] = rel(segments_csv)
        if paths:
            rec["paths"] = paths

    # If there is no source catalog and no transcript directories, preserve existing index
    has_source_catalog = bool(by_id)
    has_transcript_dirs = any(p.is_dir() for p in TRANSCRIPTS_DIR.iterdir())
    if not has_source_catalog and not has_transcript_dirs:
        prev = read_json(OUT_JSON, default=None)
        if isinstance(prev, dict) and prev.get("videos"):
            write_json(OUT_JSON, prev)
            print(
                f"No data/videos.json and no transcripts found. Preserved existing {rel(OUT_JSON)} with {len(prev['videos'])} videos."
            )
            return

    # Emit unified index (sorted for determinism)
    out = {
        "videos": sorted(
            by_id.values(), key=lambda x: ((x.get("published_at") or ""), (x.get("title") or ""))
        )
    }
    write_json(OUT_JSON, out)
    print(f"Wrote {rel(OUT_JSON)} with {len(out['videos'])} videos")


if __name__ == "__main__":
    main()
