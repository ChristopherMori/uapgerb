"""Normalize raw transcripts into clean and timecoded markdown and CSV segments."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import List, Dict

import webvtt
import pysrt

from utils.timecode import to_hms
from utils.text_helpers import clean_caption

MAX_GAP = 4.0


def load_segments(raw_file: Path) -> List[Dict[str, float | str]]:
    ext = raw_file.suffix.lower()
    segments: List[Dict[str, float | str]] = []
    if ext == ".vtt":
        for cue in webvtt.read(raw_file):
            segments.append({
                "start": cue.start_in_seconds,
                "end": cue.end_in_seconds,
                "text": cue.text,
            })
    elif ext == ".srt":
        subs = pysrt.open(str(raw_file))
        for sub in subs:
            start = sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds + sub.start.milliseconds / 1000
            end = sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds + sub.end.milliseconds / 1000
            segments.append({"start": start, "end": end, "text": sub.text})
    elif ext == ".json":
        data = json.loads(raw_file.read_text())
        for item in data:
            # Some transcripts may contain stray strings or other non-dict
            # entries. Skip any item that does not provide the expected
            # mapping interface to avoid AttributeError when calling `.get`.
            if not isinstance(item, dict):
                continue
            start = float(item.get("start", 0))
            dur = float(item.get("duration", 0))
            segments.append({"start": start, "end": start + dur, "text": item.get("text", "")})
    else:
        raise ValueError(f"Unsupported extension: {raw_file}")
    return segments


def merge_segments(segments: List[Dict[str, float | str]]) -> List[Dict[str, float | str]]:
    merged: List[Dict[str, float | str]] = []
    current: Dict[str, float | str] | None = None
    for seg in segments:
        text = clean_caption(str(seg["text"]))
        if not text:
            continue
        start = float(seg["start"])
        end = float(seg["end"])
        if current and start - float(current["end"]) <= MAX_GAP:
            current["text"] += " " + text
            current["end"] = end
        else:
            if current:
                merged.append(current)
            current = {"start": start, "end": end, "text": text}
    if current:
        merged.append(current)
    return merged


def write_outputs(video_id: str, segs: List[Dict[str, float | str]], out_dir: Path) -> None:
    clean_path = out_dir / f"{video_id}.clean.md"
    time_path = out_dir / f"{video_id}.timecoded.md"
    csv_path = out_dir / f"{video_id}.segments.csv"
    paragraphs = [s["text"] for s in segs]
    clean_path.write_text("\n\n".join(paragraphs))
    with time_path.open("w") as f:
        for s in segs:
            f.write(f"[{to_hms(float(s['start']))}] {s['text']}\n\n")
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["start", "end", "duration_ms", "text"])
        for s in segs:
            start = float(s["start"])
            end = float(s["end"])
            writer.writerow([start, end, int((end - start) * 1000), s["text"]])


def process(video_id: str, folder: Path) -> None:
    raw_files = sorted(folder.glob(f"{video_id}.raw.*"))
    if not raw_files:
        return
    latest = max(f.stat().st_mtime for f in raw_files)
    clean_file = folder / f"{video_id}.clean.md"
    if clean_file.exists() and clean_file.stat().st_mtime >= latest:
        return
    segs: List[Dict[str, float | str]] = []
    for f in raw_files:
        segs.extend(load_segments(f))
    segs.sort(key=lambda x: x["start"])
    merged = merge_segments(segs)
    write_outputs(video_id, merged, folder)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only")
    args = parser.parse_args()
    base = Path("transcripts")
    if not base.exists():
        return
    for folder in base.iterdir():
        if not folder.is_dir():
            continue
        vid = folder.name
        if args.only and vid != args.only:
            continue
        process(vid, folder)


if __name__ == "__main__":
    main()
