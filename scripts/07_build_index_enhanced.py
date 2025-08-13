import json
import html
import re
from pathlib import Path

def to_hms(seconds: float) -> str:
    seconds = int(float(seconds))
    h, m = divmod(seconds, 3600)
    m, s = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"

SAFE_RE = re.compile(r"[^A-Za-z0-9_-]+")


def safe_name(title: str) -> str:
    return SAFE_RE.sub("_", title).strip("_")


def build_index_page(index_path: Path, out_dir: Path) -> None:
    data = json.loads(index_path.read_text())
    entries = data.get("videos", data)
    rows = sorted(entries, key=lambda x: x.get('title', ''))
    lines = [
        '# Index',
        '',
        '<table id="index-table">',
        '<thead><tr><th>Title</th><th>Date</th><th>Duration</th><th>Description</th></tr></thead>',
        '<tbody>'
    ]
    for e in rows:
        vid = e['video_id']
        title = e.get('title', vid)
        duration = e.get('duration_covered')
        duration = to_hms(duration) if duration else ''
        upload = e.get('date', '')
        desc = e.get('summary', '') or e.get('description', '')
        lines.append(
            "<tr><td><a href='{file}'>{title}</a></td><td>{date}</td><td>{dur}</td><td>{desc}</td></tr>".format(
                file=html.escape(safe_name(e.get('title', vid))),
                title=html.escape(title),
                date=html.escape(upload),
                dur=html.escape(duration),
                desc=html.escape(desc)
            )
        )
    lines.append('</tbody></table>')
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'Home.md').write_text('\n'.join(lines) + '\n')

if __name__ == '__main__':
    build_index_page(Path('data/transcripts_index.json'), Path('wiki_out'))
