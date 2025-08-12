#!/usr/bin/env python3
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "transcripts_index.json"

ENT_ROOT = ROOT / "docs" / "entities"
PEOPLE = ENT_ROOT / "people"
PLACES = ENT_ROOT / "places"
TOPICS = ENT_ROOT / "topics"
for p in (PEOPLE, PLACES, TOPICS):
    p.mkdir(parents=True, exist_ok=True)

def humanize(slug: str) -> str:
    return " ".join([w.capitalize() for w in slug.split("-")])

ENTITY_TEMPLATE = """---
title: {title}
slug: /entities/{etype}/{slug}
---

# {title}

> Placeholder summary. Add a 1–2 sentence description.

## Appears in
{links}
"""

def write_entity(etype: str, slug: str, items: list):
    # items: list of (video_title, video_slug)
    links = "\n".join([f"- [{vt}](/docs/videos/{vs})" for vt, vs in items]) if items else "_No linked videos yet_"
    content = ENTITY_TEMPLATE.format(title=humanize(slug), etype=etype, slug=slug, links=links)
    outdir = {"people": PEOPLE, "places": PLACES, "topics": TOPICS}[etype]
    outf = outdir / f"{slug}.md"
    prev = outf.read_text(encoding="utf-8") if outf.exists() else None
    if prev != content:
        outf.write_text(content, encoding="utf-8")
        print(f"Wrote {outf.relative_to(ROOT)}")

def main():
    data = json.loads(INDEX.read_text(encoding="utf-8"))

    buckets = {"people": {}, "places": {}, "topics": {}}
    for item in data:
        title = item["title"].replace("\n", " ").strip()
        vslug = item["slug"]
        ents = item.get("entities", {})
        for etype in buckets.keys():
            for eslug in ents.get(etype, []):
                buckets[etype].setdefault(eslug, []).append((title, vslug))

    for etype, m in buckets.items():
        for eslug, vids in sorted(m.items()):
            write_entity(etype, eslug, vids)

    return 0

if __name__ == "__main__":
    sys.exit(main())
