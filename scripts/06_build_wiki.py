"""Generate GitHub wiki pages for each transcript with rich navigation and crosslinks."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from utils.timecode import to_hms

SAFE_RE = re.compile(r"[^A-Za-z0-9_-]+")


def safe_name(title: str) -> str:
    return SAFE_RE.sub("_", title).strip("_")


def link_entity(name: str, kind: str) -> str:
    return f"[{name}](entities/{kind}/{safe_name(name)})"


def link_topic(keyword: str) -> str:
    return f"[{keyword}](topics/{safe_name(keyword)})"


def info_box(entry: Dict, url: str) -> List[str]:
    """Return a small summary box similar to a wiki infobox."""
    return [
        "## Info",
        "| Key | Value |",
        "|---|---|",
        f"| Date | {entry.get('date', 'N/A')} |",
        f"| Duration | {to_hms(float(entry.get('duration_covered', 0)))} |",
        f"| Top keywords | {', '.join(link_topic(k) for k in entry.get('keywords_top', []))} |",
        f"| YouTube | [{url}]({url}) |",
        "",
    ]


def build_backlinks(entry: Dict, entity_map: Dict[str, Dict[str, List[Dict]]], topic_map: Dict[str, List[Dict]],
                    name_map: Dict[str, str], title_map: Dict[str, str]) -> List[str]:
    vid = entry["video_id"]
    referenced = set()
    for kind in ("people", "orgs", "places"):
        for name in entry.get(kind, []):
            for other in entity_map[kind][name]:
                if other["video_id"] != vid:
                    referenced.add(other["video_id"])
    for kw in entry.get("keywords_top", []):
        for other in topic_map[kw]:
            if other["video_id"] != vid:
                referenced.add(other["video_id"])
    if not referenced:
        return []
    lines = ["## Referenced by", ""]
    for ref in sorted(referenced):
        lines.append(f"- [{title_map.get(ref, ref)}]({name_map.get(ref, safe_name(ref))})")
    lines.append("")
    return lines


def page_content(entry: Dict, entity_map: Dict[str, Dict[str, List[Dict]]], topic_map: Dict[str, List[Dict]],
                 name_map: Dict[str, str], title_map: Dict[str, str]) -> str:
    vid = entry["video_id"]
    html_embed = entry.get("html_embed", "")
    url = entry.get("url", f"https://www.youtube.com/watch?v={vid}")
    transcript_clean = Path(f"transcripts/{vid}/{vid}.clean.md")
    transcript_section: list[str]
    if transcript_clean.exists():
        transcript_text = transcript_clean.read_text()
        transcript_section = [
            "## Transcript",
            "<details><summary>Show transcript</summary>",
            "",
            transcript_text,
            "",
            "</details>",
            "",
        ]
    else:
        transcript_section = [
            "## Transcript",
            "> **Warning:** Transcript not available.",
            "",
        ]

    people_links = ", ".join(link_entity(p, "people") for p in entry.get("people", [])) or "None"
    org_links = ", ".join(link_entity(o, "orgs") for o in entry.get("orgs", [])) or "None"
    place_links = ", ".join(link_entity(p, "places") for p in entry.get("places", [])) or "None"

    lines = [
        f"# {entry.get('title', vid)}",
        "",
        "[[_TOC_]]",
        "",
        *info_box(entry, url),
        html_embed,
        "",
        f"[![Watch on YouTube](https://img.youtube.com/vi/{vid}/0.jpg)]({url})",
        "",
        "## TL;DR",
        "> **Note:** Summary coming soon.",
        "",
        "## Statistics",
        f"- Duration covered: {to_hms(float(entry.get('duration_covered',0)))}",
        f"- Words: {entry.get('words','0')} · WPM: {entry.get('wpm','0')} · FK Grade: {entry.get('fk_grade','0')}",
        f"- Sentences: {entry.get('sentences','0')} · Questions: {entry.get('questions_count','0')}",
        f"- Hedges: {entry.get('hedge_terms_count','0')} · Uncertainty: {entry.get('uncertainty_markers_count','0')}",
        "",
        "## Entities",
        f"- **People:** {people_links}",
        f"- **Organizations:** {org_links}",
        f"- **Places:** {place_links}",
        "",
        "## Timeline (Referenced)",
        f"- {', '.join(str(y) for y in entry.get('years', []))}" +
        (f" (earliest: {entry.get('earliest')})" if entry.get('earliest') else "") +
        (f" (latest: {entry.get('latest')})" if entry.get('latest') else ""),
        "",
        "## Top Keywords",
        ", ".join(link_topic(k) for k in entry.get("keywords_top", [])),
        "",
        "## Files",
        f"- Clean transcript: `transcripts/{vid}/{vid}.clean.md`",
        f"- Timecoded transcript: `transcripts/{vid}/{vid}.timecoded.md`",
        f"- Segments (CSV): `transcripts/{vid}/{vid}.segments.csv`",
        "",
        *transcript_section,
        *build_backlinks(entry, entity_map, topic_map, name_map, title_map),
    ]
    return "\n".join(lines)


def build_entity_pages(entity_map: Dict[str, Dict[str, List[Dict]]], topic_map: Dict[str, List[Dict]], out_dir: Path,
                       name_map: Dict[str, str], title_map: Dict[str, str]) -> None:
    base = out_dir / "entities"
    for kind, mapping in entity_map.items():
        kind_dir = base / kind
        if not mapping:
            continue
        kind_dir.mkdir(parents=True, exist_ok=True)
        for name, entries in mapping.items():
            lines = [f"# {name}", "", "Referenced in:", ""]
            for e in sorted(entries, key=lambda x: x.get("title", x["video_id"])):
                vid = e["video_id"]
                lines.append(f"- [{title_map.get(vid, vid)}]({name_map[vid]})")
            (kind_dir / f"{safe_name(name)}.md").write_text("\n".join(lines) + "\n")

    topics_dir = out_dir / "topics"
    if topic_map:
        topics_dir.mkdir(parents=True, exist_ok=True)
    for kw, entries in topic_map.items():
        lines = [f"# {kw}", "", "Referenced in:", ""]
        for e in sorted(entries, key=lambda x: x.get("title", x["video_id"])):
            vid = e["video_id"]
            lines.append(f"- [{title_map.get(vid, vid)}]({name_map[vid]})")
        (topics_dir / f"{safe_name(kw)}.md").write_text("\n".join(lines) + "\n")


def build_pages(index: Path, out_dir: Path, only: str | None = None) -> None:
    entries = json.loads(index.read_text())
    out_dir.mkdir(exist_ok=True)
    entity_map: Dict[str, Dict[str, List[Dict]]] = {k: defaultdict(list) for k in ("people", "orgs", "places")}
    topic_map: Dict[str, List[Dict]] = defaultdict(list)
    name_map: Dict[str, str] = {}
    title_map: Dict[str, str] = {}
    filtered: List[Dict] = []
    for entry in entries:
        vid = entry["video_id"]
        if only and vid != only:
            continue
        name_map[vid] = safe_name(entry.get('title', vid))
        title_map[vid] = entry.get('title', vid)
        for kind in entity_map:
            for name in entry.get(kind, []):
                entity_map[kind][name].append(entry)
        for kw in entry.get("keywords_top", []):
            topic_map[kw].append(entry)
        filtered.append(entry)

    rows = []
    for entry in filtered:
        vid = entry["video_id"]
        content = page_content(entry, entity_map, topic_map, name_map, title_map)
        page_file = out_dir / f"{name_map[vid]}.md"
        page_file.write_text(content)
        rows.append(entry)

    build_entity_pages(entity_map, topic_map, out_dir, name_map, title_map)

    rows.sort(key=lambda x: x.get("title", ""))
    home_lines = [
        "# Index",
        "",
        "| Title | Duration | Words | WPM | FK | Top keywords | First year–Last year |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        title = r.get("title", r["video_id"])
        filename = name_map[r["video_id"]]
        duration = to_hms(float(r.get("duration_covered", 0)))
        keywords = ", ".join(r.get("keywords_top", [])[:5])
        years = f"{r.get('earliest','')}–{r.get('latest','')}" if r.get("earliest") else ""
        home_lines.append(
            f"| [{title}]({filename}) | {duration} | {r.get('words','')} | {r.get('wpm','')} | {r.get('fk_grade','')} | {keywords} | {years} |"
        )
    (out_dir / "Home.md").write_text("\n".join(home_lines) + "\n")

    sidebar_lines = ["## Videos", "- [Home](Home)", ""]
    for r in rows:
        title = r.get("title", r["video_id"])
        filename = name_map[r["video_id"]]
        sidebar_lines.append(f"- [{title}]({filename})")
    sidebar_lines.append("")
    (out_dir / "_Sidebar.md").write_text("\n".join(sidebar_lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only")
    args = parser.parse_args()
    build_pages(Path("data/transcripts_index.json"), Path("wiki_out"), args.only)


if __name__ == "__main__":
    main()
