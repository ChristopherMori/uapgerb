"""Generate GitHub wiki pages for each transcript."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict

from utils.timecode import to_hms

SAFE_RE = re.compile(r"[^A-Za-z0-9_-]+")


def safe_name(title: str) -> str:
    return SAFE_RE.sub("_", title).strip("_")


def page_content(entry: Dict) -> str:
    vid = entry["video_id"]
    html_embed = entry.get("html_embed", "")
    url = entry.get("url", f"https://www.youtube.com/watch?v={vid}")
    lines = [f"# {entry.get('title', vid)}", "", html_embed, "",
             f"[![Watch on YouTube](https://img.youtube.com/vi/{vid}/0.jpg)]({url})", "",
             f"**YouTube:** {url}", "",
             "## TL;DR", "- Summary coming soon.", "",
             "## Statistics",
             f"- Duration covered: {to_hms(float(entry.get('duration_covered',0)))}",
             f"- Words: {entry.get('words','0')} · WPM: {entry.get('wpm','0')} · FK Grade: {entry.get('fk_grade','0')}",
             f"- Sentences: {entry.get('sentences','0')} · Questions: {entry.get('questions_count','0')}",
             f"- Hedges: {entry.get('hedge_terms_count','0')} · Uncertainty: {entry.get('uncertainty_markers_count','0')}",
             "",
             "## Entities",
             f"- **People:** {', '.join(entry.get('people', []))}",
             f"- **Organizations:** {', '.join(entry.get('orgs', []))}",
             f"- **Places:** {', '.join(entry.get('places', []))}",
             "",
             "## Timeline (Referenced)",
             f"- {', '.join(str(y) for y in entry.get('years', []))}"
             + (f" (earliest: {entry.get('earliest')})" if entry.get('earliest') else "")
             + (f" (latest: {entry.get('latest')})" if entry.get('latest') else ""),
             "",
             "## Top Keywords",
             ', '.join(entry.get('keywords_top', [])),
             "",
             "## Files",
             f"- Clean transcript: `transcripts/{vid}/{vid}.clean.md`",
             f"- Timecoded transcript: `transcripts/{vid}/{vid}.timecoded.md`",
             f"- Segments (CSV): `transcripts/{vid}/{vid}.segments.csv`",
             ""]
    return "\n".join(lines)


def build_pages(index: Path, out_dir: Path, only: str | None = None) -> None:
    entries = json.loads(index.read_text())
    out_dir.mkdir(exist_ok=True)
    rows = []
    for entry in entries:
        vid = entry["video_id"]
        if only and vid != only:
            continue
        content = page_content(entry)
        page_file = out_dir / f"{safe_name(entry.get('title', vid))}.md"
        page_file.write_text(content)
        rows.append(entry)
    # Build index page
    rows.sort(key=lambda x: x.get('title',''))
    home_lines = ["# Index", "", "| Title | Duration | Words | WPM | FK | Top keywords | First year–Last year |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        title = r.get('title', r['video_id'])
        filename = f"{safe_name(title)}.md"
        duration = to_hms(float(r.get('duration_covered',0)))
        keywords = ', '.join(r.get('keywords_top', [])[:5])
        years = f"{r.get('earliest','')}–{r.get('latest','')}" if r.get('earliest') else ""
        home_lines.append(f"| [{title}]({filename}) | {duration} | {r.get('words','')} | {r.get('wpm','')} | {r.get('fk_grade','')} | {keywords} | {years} |")
    (out_dir / "_Home.md").write_text("\n".join(home_lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only")
    args = parser.parse_args()
    build_pages(Path("data/transcripts_index.json"), Path("wiki_out"), args.only)


if __name__ == "__main__":
    main()
