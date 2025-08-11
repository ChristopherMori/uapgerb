"""Derive claim types and referenced years for each transcript."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

from nltk.tokenize import sent_tokenize

SPEC_WORDS = {"maybe", "might", "perhaps", "possibly", "i think", "i guess"}
YEAR_RE = re.compile(r"(19|20)\d{2}")


def analyze(video_id: str, folder: Path) -> Dict:
    clean = folder / f"{video_id}.clean.md"
    if not clean.exists():
        return {}
    text = clean.read_text()
    sentences = sent_tokenize(text)
    years = sorted({int(m.group()) for m in YEAR_RE.finditer(text)})
    counts = {"assertion": 0, "question": 0, "speculation": 0}
    for s in sentences:
        low = s.lower()
        if s.strip().endswith("?"):
            counts["question"] += 1
        elif any(w in low for w in SPEC_WORDS):
            counts["speculation"] += 1
        else:
            counts["assertion"] += 1
    result = {
        "video_id": video_id,
        "years": years,
        "earliest": years[0] if years else None,
        "latest": years[-1] if years else None,
        "claims": counts,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only")
    args = parser.parse_args()
    base = Path("transcripts")
    out = {}
    if base.exists():
        for folder in base.iterdir():
            if not folder.is_dir():
                continue
            vid = folder.name
            if args.only and vid != args.only:
                continue
            res = analyze(vid, folder)
            if res:
                out[vid] = res
    Path("data/claims_timeline.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
