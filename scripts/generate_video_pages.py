#!/usr/bin/env python3
import json, pathlib, sys, html

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "transcripts_index.json"
DOCS = ROOT / "docs" / "videos"
DOCS.mkdir(parents=True, exist_ok=True)

def humanize_slug(s: str) -> str:
    return " ".join([w.capitalize() for w in s.replace("-", " ").split()])

def mdx_escape_triple_backticks(text: str) -> str:
    # Avoid breaking fenced blocks if transcript contains ```
    return text.replace("```", "``\u200b`")

def ent_links(ents: dict) -> dict:
    out = {}
    for k, base in (("people", "/docs/entities/people/"),
                    ("places", "/docs/entities/places/"),
                    ("topics", "/docs/entities/topics/")):
        slugs = ents.get(k, []) if ents else []
        out[k] = [f"[{humanize_slug(s)}]({base}{s})" for s in slugs]
    return out

TEMPLATE = """---
id: {id}
title: {title_front}
slug: /videos/{slug}
published_at: {published_at}
duration: {duration}
tags:
{tags_yaml}---

# {title_heading}

**Published:** {published_at} · **Duration:** {duration}

## Files & Links
{links}

## Entities
{entities_block}

## Transcript
<details open>
  <summary>Hide transcript</summary>

```text
{transcript}
```

</details>
"""

def build_video_page(item: dict, transcript_text: str) -> str:
    title_raw = item["title"].replace("\n", " ").strip()
    title_front = json.dumps(title_raw)
    tags = item.get("tags", [])
    tags_yaml = "".join([f"  - {t}\n" for t in tags]) if tags else "  - topic:untagged\n"
    links = []
    yt = item.get("sources", {}).get("youtube")
    if yt:
        links.append(f"- [YouTube]({yt})")
    served_txt = item.get("sources", {}).get("transcript_txt_served", item["sources"]["transcript_txt"])
    links.append(f"- Transcript: [download .txt](/{served_txt})")
    vtt = item.get("sources", {}).get("transcript_vtt_served") or item.get("sources", {}).get("transcript_vtt")
    if vtt:
        links.append(f"- Captions: [.vtt](/{vtt})")
    links_block = "\n".join(links) if links else "- (no external links)"

    ent = ent_links(item.get("entities", {}))
    ents_lines = []
    if ent["people"]:
        ents_lines.append(f"People: {', '.join(ent['people'])}")
    if ent["places"]:
        ents_lines.append(f"Places: {', '.join(ent['places'])}")
    if ent["topics"]:
        ents_lines.append(f"Topics: {', '.join(ent['topics'])}")
    entities_block = "\n".join(ents_lines) if ents_lines else "_No entities tagged yet_"

    # Full embed (your choice): no truncation
    transcript = mdx_escape_triple_backticks(transcript_text.rstrip("\n"))

    return TEMPLATE.format(
        id=item["id"],
        title_front=title_front,
        slug=item["slug"],
        published_at=item.get("published_at", "unknown"),
        duration=item.get("duration", "unknown"),
        tags_yaml=tags_yaml,
        links=links_block,
        entities_block=entities_block,
        transcript=transcript,
        title_heading=title_raw,
    )

def main():
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    for item in data:
        txt_path = ROOT / item["sources"]["transcript_txt"]
        t = txt_path.read_text(encoding="utf-8", errors="ignore")
        out = build_video_page(item, t)
        out_file = DOCS / f"{item['slug']}.mdx"
        # Only rewrite if changed
        prev = out_file.read_text(encoding="utf-8") if out_file.exists() else None
        if prev != out:
            out_file.write_text(out, encoding="utf-8")
            print(f"Wrote {out_file.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
