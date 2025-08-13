#!/usr/bin/env python3
"""
Generate GitHub Pages-ready Markdown into docs/ from data/transcripts_index.json
and data/videos.json.

Outputs:
- docs/index.md
- docs/videos/<id>--<slug>.md
- docs/entities/people/<slug>.md
- docs/entities/places/<slug>.md
- docs/entities/topics/<slug>.md
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, DefaultDict
from collections import defaultdict
import sys

# Allow running as a script without setting PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.common import (
    DATA_DIR,
    DOCS_DIR,
    read_json,
    write_text,
    slugify,
    safe_filename,
    hhmmss,
    read_segments_csv,
    rel,
)

INDEX_JSON = DATA_DIR / "transcripts_index.json"
FALLBACK_VIDEOS_JSON = DATA_DIR / "videos.json"


def _nice_label(slug: str) -> str:
    label = slug.replace("-", " ")
    return label.upper() if len(label) <= 4 and label.isalpha() else label.title()


@dataclass
class Video:
    id: str
    title: str
    published_at: str | None
    duration: int | None
    links: Dict[str, str]
    people: List[str]
    locations: List[str]
    tags: List[str]
    paths: Dict[str, str]

    @property
    def page_filename(self) -> str:
        return safe_filename(self.id, self.title or self.id)

    def entity_triplets(self) -> List[Tuple[str, str, str]]:
        """
        Returns list of (type, slug, display) for entities attached to this video.
        """
        out: List[Tuple[str, str, str]] = []
        for pid in self.people or []:
            slug = pid.split(":", 1)[-1]
            out.append(("people", slug, _nice_label(slug)))
        for loc in self.locations or []:
            slug = loc.split(":", 1)[-1]
            out.append(("places", slug, _nice_label(slug)))
        # topics come from free-form tags without a namespace
        for t in self.tags or []:
            if ":" in t:
                continue
            slug = slugify(t)
            out.append(("topics", slug, t))
        return out


def load_index() -> List[Video]:
    idx = read_json(INDEX_JSON, default=None)
    if not idx:
        # Fallback path if index not built yet
        idx = read_json(FALLBACK_VIDEOS_JSON, default={"videos": []})
    videos_raw = idx if isinstance(idx, list) else idx.get("videos", [])
    videos: List[Video] = []
    for v in videos_raw:
        videos.append(
            Video(
                id=v.get("id") or v.get("video_id") or v.get("youtube_id"),
                title=v.get("title") or v.get("id"),
                published_at=v.get("published_at"),
                duration=v.get("duration"),
                links=v.get("links", {}),
                people=v.get("people", []),
                locations=v.get("locations", []),
                tags=v.get("tags", []),
                paths=v.get("paths", {}),
            )
        )
    # Ensure ids are strings like "yt-<id>" when possible
    for v in videos:
        if v and v.id and not str(v.id).startswith("yt-") and len(str(v.id)) in (11, 12):
            v.id = f"yt-{v.id}"
    return videos


def build_index_page(videos: List[Video]) -> None:
    rows = []
    rows.append("| Title | Date | Duration | People | Places |")
    rows.append("|---|---|---:|---|---|")
    for v in videos:
        pf = v.page_filename
        date = v.published_at or ""
        dur = hhmmss(v.duration or 0) if v.duration else ""
        people_cells = []
        for p in v.people:
            slug = p.split(":",1)[-1]
            people_cells.append(f"[{_nice_label(slug)}](./entities/people/{slug}.md)")
        people = ", ".join(people_cells) or ""
        place_cells = []
        for p in v.locations:
            slug = p.split(":",1)[-1]
            place_cells.append(f"[{_nice_label(slug)}](./entities/places/{slug}.md)")
        places = ", ".join(place_cells) or ""
        rows.append(f"| [{v.title}](./videos/{pf}) | {date} | {dur} | {people} | {places} |")

    body = "\n".join([
        "---",
        "title: \"UAPGerbs Catalog\"",
        "---",
        "",
        "# UAPGerbs Video Catalog",
        "",
        "Below is an index of all cataloged videos. Click a title to view details, transcript links, and related entities.",
        "",
        *rows,
        "",
    ])
    write_text(DOCS_DIR / "index.md", body)


def build_video_pages(videos: List[Video]) -> Dict[str, List[Tuple[str, str]]]:
    """
    Returns an entity->list of (video_filename, video_title) for building entity pages later.
    Keys use namespace "people:<slug>", "places:<slug>", "topics:<slug>".
    """
    index_for_entities: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    for v in videos:
        pf = v.page_filename
        # Segment table, if any
        seg_table = ""
        seg_path = v.paths.get("segments_csv")
        if seg_path:
            from scripts.common import REPO_ROOT
            segs = read_segments_csv(REPO_ROOT / seg_path)
            if segs:
                lines = []
                lines.append("| Start | End | Excerpt |")
                lines.append("|---:|---:|---|")
                # Cap to 200 rows to keep pages snappy
                for s in segs[:200]:
                    lines.append(f"| {hhmmss(s.t_start)} | {hhmmss(s.t_end)} | {s.excerpt()} |")
                seg_table = "\n".join(lines)

        # Transcript file links
        links = []
        if v.paths.get("clean_md"):
            links.append(f"- Clean transcript: `{v.paths['clean_md']}`")
        if v.paths.get("timecoded_md"):
            links.append(f"- Timecoded transcript: `{v.paths['timecoded_md']}`")
        if v.paths.get("segments_csv"):
            links.append(f"- Segments CSV: `{v.paths['segments_csv']}`")
        if v.links.get("youtube"):
            links.append(f"- YouTube: {v.links['youtube']}")

        # Entities
        people_links = []
        for p in v.people:
            slug = p.split(":",1)[-1]
            people_links.append(f"[{_nice_label(slug)}](../entities/people/{slug}.md)")
        place_links = []
        for p in v.locations:
            slug = p.split(":",1)[-1]
            place_links.append(f"[{_nice_label(slug)}](../entities/places/{slug}.md)")
        topic_links  = [f"[{t}](../entities/topics/{slugify(t)}.md)" for t in v.tags if ":" not in t]

        # Aggregate for entity pages
        for ns, slug, disp in v.entity_triplets():
            key = f"{ns}:{slug}"
            index_for_entities[key].append((pf, v.title))

        # Front matter and body
        fm = [
            "---",
            f"id: {v.id}",
            f'title: "{v.title.replace("\"", "\\\"")}",'
            f"published_at: {v.published_at or ''}",
            f"duration: {v.duration or ''}",
            f"tags: {v.tags!r}",
            "---",
            "",
        ]
        body = []
        body.append(f"# {v.title}")
        body.append("")
        if v.links.get("youtube"):
            body.append(f"[Open on YouTube]({v.links['youtube']})")
            body.append("")
        if people_links or place_links or topic_links:
            body.append("**Entities**:")
            if people_links:
                body.append(f"- People: {', '.join(people_links)}")
            if place_links:
                body.append(f"- Places: {', '.join(place_links)}")
            if topic_links:
                body.append(f"- Topics: {', '.join(topic_links)}")
            body.append("")
        if links:
            body.append("**Files and Links**:")
            body.extend(links)
            body.append("")
        if seg_table:
            body.append("## Segments")
            body.append("")
            body.append(seg_table)
            body.append("")

        write_text(DOCS_DIR / "videos" / pf, "\n".join(fm + body))

    return index_for_entities


def build_entity_pages(entity_index: Dict[str, List[Tuple[str, str]]]) -> None:
    """
    entity_index maps "people:slug" or "places:slug" or "topics:slug" -> list[(video_file, video_title)]
    """
    for key, refs in sorted(entity_index.items()):
        ns, slug = key.split(":", 1)
        title = _nice_label(slug) if ns != "topics" else slug.replace("-", " ")
        folder = DOCS_DIR / "entities" / ns
        folder.mkdir(parents=True, exist_ok=True)

        rows = []
        rows.append("| Video | Link |")
        rows.append("|---|---|")
        for vf, vt in sorted(refs, key=lambda x: x[1].lower()):
            rows.append(f"| {vt} | [Open](../../videos/{vf}) |")

        fm = [
            "---",
            f"id: {ns}:{slug}",
            f"title: \"{title}\"",
            f"type: \"{ns[:-1] if ns.endswith('s') else ns}\"",
            "---",
            "",
        ]

        body = [f"# {title}", "", "## Related Videos", "", *rows, ""]
        write_text(folder / f"{slug}.md", "\n".join(fm + body))


def main() -> None:
    videos = load_index()
    if not videos:
        print("No videos found. Did you run scripts/scan_transcripts.py?")
        return
    build_index_page(videos)
    entity_index = build_video_pages(videos)
    build_entity_pages(entity_index)
    print(f"Pages built under {rel(DOCS_DIR)}")


if __name__ == "__main__":
    main()
