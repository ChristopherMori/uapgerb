import json
import html
import re
from datetime import datetime, timedelta
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
    entries = json.loads(index_path.read_text())
    rows = sorted(entries, key=lambda x: x.get('title', ''))
    lines = [
        '# Index',
        '',
        'Status icons: 🆕 recent · ⚠️ missing summary · ❗ missing transcript',
        '',
        '<table id="index-table">',
        '<thead><tr><th>Title</th><th>Year</th><th>Duration</th><th>Words</th><th>WPM</th><th>FK</th><th>Top keywords</th><th>First year–Last year</th><th>Status</th></tr></thead>',
        '<tbody>'
    ]
    for e in rows:
        vid = e['video_id']
        title = e.get('title', vid)
        duration = to_hms(e.get('duration_covered', 0))
        kw_list = e.get('keywords_top', [])
        kw = ', '.join(kw_list[:5])
        yrs = f"{e.get('earliest','')}–{e.get('latest','')}" if e.get('earliest') else ''
        upload = e.get('date') or ''
        year = upload[:4] if upload else ''
        status = []
        if not Path(f'transcripts/{vid}/{vid}.clean.md').exists():
            status.append('❗')
        if not e.get('summary'):
            status.append('⚠️')
        if upload:
            try:
                if datetime.now() - datetime.fromisoformat(upload) < timedelta(days=30):
                    status.append('🆕')
            except ValueError:
                pass
        lines.append(
            "<tr><td><a href='{file}'>{title}</a></td>"
            "<td>{year}</td><td>{dur}</td><td>{words}</td><td>{wpm}</td><td>{fk}</td>"
            "<td>{kw}</td><td>{yrs}</td><td>{st}</td></tr>".format(
                file=html.escape(safe_name(e.get('title', vid))),
                title=html.escape(title),
                year=html.escape(year),
                dur=html.escape(duration),
                words=html.escape(e.get('words', '')),
                wpm=html.escape(e.get('wpm', '')),
                fk=html.escape(e.get('fk_grade', '')),
                kw=html.escape(kw),
                yrs=html.escape(yrs),
                st=html.escape(' '.join(status))
            )
        )
    lines.append('</tbody></table>')
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'Home.md').write_text('\n'.join(lines) + '\n')

if __name__ == '__main__':
    build_index_page(Path('data/transcripts_index.json'), Path('wiki_out'))
