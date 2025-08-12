#!/usr/bin/env python3
"""
Shared helpers for path handling, slugs, JSON I/O, and formatting.
"""

from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

# Root directories
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = REPO_ROOT / "docs"
TRANSCRIPTS_DIR = REPO_ROOT / "transcripts"

# Ensure base dirs exist
for _p in (DATA_DIR, DOCS_DIR, DOCS_DIR / "videos", DOCS_DIR / "entities",
           DOCS_DIR / "entities" / "people", DOCS_DIR / "entities" / "places",
           DOCS_DIR / "entities" / "topics"):
    _p.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)


_slug_re = re.compile(r"[^a-z0-9]+")
def slugify(s: str, min_len: int = 1) -> str:
    """
    Lowercase, replace non-alnum with hyphens, collapse runs, trim hyphens.
    """
    s = s.lower().strip()
    s = _slug_re.sub("-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    if len(s) < min_len:
        s = s.ljust(min_len, "x")
    return s


def hhmmss(seconds: int | float) -> str:
    try:
        seconds = int(round(float(seconds)))
    except Exception:
        return "00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def safe_filename(video_id: str, title: str) -> str:
    """
    Deterministic page filename: <id>--<slug>.md to avoid collisions.
    """
    slug = slugify(title)
    return f"{video_id}--{slug}.md"


@dataclass
class Segment:
    t_start: float
    t_end: float
    text: str

    def excerpt(self, max_chars: int = 140) -> str:
        t = re.sub(r"\s+", " ", self.text).strip()
        if len(t) <= max_chars:
            return t
        return t[: max_chars - 1].rstrip() + "…"


def read_segments_csv(path: Path) -> List[Segment]:
    """
    Reads a CSV with headers: t_start,t_end,text
    """
    import csv

    segments: List[Segment] = []
    if not path.exists():
        return segments
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ts = float(row.get("t_start", "0") or 0)
                te = float(row.get("t_end", "0") or 0)
                tx = row.get("text", "") or ""
                segments.append(Segment(ts, te, tx))
            except Exception:
                continue
    return segments


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT).as_posix())
