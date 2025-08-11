"""Reorganize transcript files into ``transcripts/<video_id>`` directories."""
from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path

ID_RE = re.compile(r"\[([A-Za-z0-9_-]{6,})\]")


def reorg(base: Path, only: str | None = None) -> None:
    transcripts = base / "transcripts"
    transcripts.mkdir(exist_ok=True)
    for item in base.iterdir():
        if item.name in {"data", "scripts", "transcripts", ".git"}:
            continue
        if not item.is_dir():
            continue
        files = list(item.iterdir())
        video_id = None
        for f in files:
            m = ID_RE.search(f.name)
            if m:
                video_id = m.group(1)
                break
        if not video_id:
            continue
        if only and video_id != only:
            continue
        dest = transcripts / video_id
        dest.mkdir(exist_ok=True)
        for f in files:
            ext = ''.join(f.suffixes)
            new_name = f"{video_id}.raw{ext}"
            target = dest / new_name
            idx = 2
            while target.exists():
                target = dest / f"{video_id}.raw_{idx}{ext}"
                idx += 1
            shutil.copy2(f, target)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="Process only this video id")
    args = parser.parse_args()
    reorg(Path.cwd(), args.only)


if __name__ == "__main__":
    main()
