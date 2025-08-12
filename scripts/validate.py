#!/usr/bin/env python3
"""Validate repo health for GitHub Pages."""
from __future__ import annotations
import re, sys
from pathlib import Path
from typing import Dict, Any, List, Set

sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts.common import DATA_DIR, DOCS_DIR, read_json, rel, safe_filename

INDEX_JSON = DATA_DIR / "transcripts_index.json"
INDEX_MD = DOCS_DIR / "index.md"
LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")

def fail(msg: str) -> None:
    print(f"VALIDATION ERROR: {msg}")
    sys.exit(1)

def warn(msg: str) -> None:
    print(f"VALIDATION WARNING: {msg}")

def load_index() -> List[Dict[str, Any]]:
    if not INDEX_JSON.exists():
        fail(f"Missing {rel(INDEX_JSON)}. Run scripts/scan_transcripts.py first.")
    idx = read_json(INDEX_JSON)
    if not isinstance(idx, dict) or "videos" not in idx or not isinstance(idx["videos"], list):
        fail(f"Bad schema in {rel(INDEX_JSON)}; expected {{'videos': [...]}}.")
    return idx["videos"]

def expect_video_pages(videos: List[Dict[str, Any]]) -> Set[Path]:
    missing = []
    expected: Set[Path] = set()
    for v in videos:
        vid = v.get("id")
        title = v.get("title") or vid
        pf = DOCS_DIR / "videos" / safe_filename(vid, title)
        expected.add(pf)
        if not pf.exists():
            missing.append(rel(pf))
    if missing:
        fail("Missing video pages:\n" + "\n".join(f"- {m}" for m in missing))
    return expected

def validate_index_links(videos: List[Dict[str, Any]]) -> None:
    if not INDEX_MD.exists():
        fail(f"Missing {rel(INDEX_MD)}")
    text = INDEX_MD.read_text(encoding="utf-8")
    missing = []
    for v in videos:
        vid = v.get("id")
        title = v.get("title") or vid
        pf = safe_filename(vid, title)
        if f"](./videos/{pf})" not in text:
            missing.append(pf)
    if missing:
        fail("Index missing links for:\n" + "\n".join(f"- {m}" for m in missing))

def check_links() -> None:
    errors = []
    for md in DOCS_DIR.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            target = (md.parent / m.group(1)).resolve()
            try:
                target.relative_to(DOCS_DIR.resolve())
            except Exception:
                errors.append(f"{rel(md)} → {m.group(1)} (escapes docs/)")
                continue
            if not target.exists():
                errors.append(f"{rel(md)} → {rel(target)}")
    if errors:
        fail("Broken links found:\n" + "\n".join(f"- {e}" for e in errors))

def warn_orphans(expected: Set[Path]) -> None:
    actual = set((DOCS_DIR / "videos").glob("*.md"))
    orphans = sorted({rel(p) for p in actual - expected})
    if orphans:
        warn("Orphaned docs/videos pages (not in index):\n" + "\n".join(f"- {o}" for o in orphans))

def main() -> None:
    videos = load_index()
    expected = expect_video_pages(videos)
    validate_index_links(videos)
    check_links()
    warn_orphans(expected)
    print("Validation passed.")

if __name__ == "__main__":
    main()
