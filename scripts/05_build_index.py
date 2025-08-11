"""Merge analysis outputs with video metadata."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def load_metrics() -> dict:
    path = Path("data/metrics.csv")
    if not path.exists():
        return {}
    with path.open() as f:
        reader = csv.DictReader(f)
        return {r['video_id']: r for r in reader}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only")
    args = parser.parse_args()
    videos = json.loads(Path("data/videos.json").read_text())
    metrics = load_metrics()
    entities = json.loads(Path("data/entities_topics.json").read_text())
    claims = json.loads(Path("data/claims_timeline.json").read_text())
    index = []
    for vid_meta in videos:
        vid = vid_meta["video_id"]
        if args.only and vid != args.only:
            continue
        entry = {"video_id": vid, **vid_meta}
        if vid in metrics:
            entry.update(metrics[vid])
        if vid in entities:
            entry.update(entities[vid])
        if vid in claims:
            entry.update({"years": claims[vid]["years"], "earliest": claims[vid]["earliest"], "latest": claims[vid]["latest"]})
            entry["claims"] = claims[vid]["claims"]
        index.append(entry)
    Path("data/transcripts_index.json").write_text(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
