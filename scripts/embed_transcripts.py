#!/usr/bin/env python3
"""Embed transcript text into each video page under docs/videos.

For each Markdown/MDX file in docs/videos, this script looks for a matching
transcript text file and inserts a "## Transcript" section if one is not
already present. Transcript files are searched using the video's ID and title
and are copied into ``transcripts/<video_id>/`` so they can be served by the
site. Links to the transcript (and caption file, if available) are also added
under the existing "Files and Links" section.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "videos"
TRANSCRIPTS = ROOT / "transcripts"

def mdx_escape(text: str) -> str:
    """Escape triple backticks so they don't terminate fenced blocks."""
    return text.replace("```", "``\u200b`")

def parse_frontmatter(text: str) -> tuple[dict, list[str], list[str]]:
    """Return (metadata, body_lines, front_lines) from a Markdown/MDX file."""
    if not text.startswith("---"):
        lines = text.splitlines()
        return {}, lines, []
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        lines = text.splitlines()
        return {}, lines, []
    front, body = parts
    meta: dict[str, str] = {}
    for line in front.splitlines()[1:]:
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"')
    front_lines = front.splitlines() + ["---"]
    return meta, body.splitlines(), front_lines

def find_source_files(title: str, vid_short: str) -> tuple[Path | None, Path | None]:
    """Locate transcript (.txt) and caption (.vtt) files for a video."""
    base = ROOT / title
    txt = base / f"{title} [{vid_short}].txt"
    vtt = base / f"{title} [{vid_short}].vtt"
    if txt.exists():
        return txt, vtt if vtt.exists() else None
    pattern = f"*{vid_short}*.txt"
    matches = list(ROOT.rglob(pattern))
    txt = matches[0] if matches else None
    vtt = None
    if txt:
        v_pattern = txt.with_suffix(".vtt").name
        v_matches = list(ROOT.rglob(v_pattern))
        if v_matches:
            vtt = v_matches[0]
    return txt, vtt

def insert_links(lines: list[str], vid: str, have_txt: bool, have_vtt: bool) -> None:
    marker = "**Files and Links**:"
    try:
        idx = lines.index(marker)
    except ValueError:
        return
    insert_at = idx + 1
    while insert_at < len(lines) and lines[insert_at].startswith("-"):
        insert_at += 1
    if have_txt:
        lines.insert(insert_at, f"- Transcript: [download .txt](/transcripts/{vid}/clean.txt)")
        insert_at += 1
    if have_vtt:
        lines.insert(insert_at, f"- Captions: [.vtt](/transcripts/{vid}/original.vtt)")

def append_transcript(lines: list[str], transcript: str) -> None:
    lines.extend([
        "",
        "## Transcript",
        "<details open>",
        "  <summary>Hide transcript</summary>",
        "",
        "```text",
        mdx_escape(transcript.rstrip("\n")),
        "```",
        "",
        "</details>",
        "",
    ])

def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    meta, lines, front = parse_frontmatter(text)
    vid = meta.get("id")
    title = meta.get("title")
    if not vid or not title:
        return False
    if any("## Transcript" in line for line in lines):
        return False
    vid_short = vid.split("-", 1)[-1]
    src_txt, src_vtt = find_source_files(title, vid_short)
    if not src_txt:
        return False
    dest_dir = TRANSCRIPTS / vid
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_txt = dest_dir / "clean.txt"
    shutil.copyfile(src_txt, dest_txt)
    have_vtt = False
    if src_vtt and src_vtt.exists():
        dest_vtt = dest_dir / "original.vtt"
        shutil.copyfile(src_vtt, dest_vtt)
        have_vtt = True
    transcript_text = src_txt.read_text(encoding="utf-8")
    insert_links(lines, vid, have_txt=True, have_vtt=have_vtt)
    append_transcript(lines, transcript_text)
    new_lines = front + lines if front else lines
    path.write_text("\n".join(new_lines), encoding="utf-8")
    return True

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="Process only this video id")
    args = parser.parse_args()
    processed = 0
    for md in sorted(DOCS.glob("*.md*")):
        meta, _, _ = parse_frontmatter(md.read_text(encoding="utf-8"))
        vid = meta.get("id")
        if args.only and vid != args.only:
            continue
        if process_file(md):
            print(f"Updated {md.relative_to(ROOT)}")
            processed += 1
    if processed == 0:
        print("No pages updated.")

if __name__ == "__main__":
    main()
