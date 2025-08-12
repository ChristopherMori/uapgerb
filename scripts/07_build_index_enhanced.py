import json
import html
from datetime import datetime, timedelta
from pathlib import Path

def to_hms(seconds: float) -> str:
    seconds = int(float(seconds))
    h, m = divmod(seconds, 3600)
    m, s = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"

def build_index_page(index_path: Path, out_dir: Path) -> None:
    entries = json.loads(index_path.read_text())
    rows = sorted(entries, key=lambda x: x.get('title', ''))
    years = sorted({(e.get('date') or '')[:4] for e in rows if e.get('date')})
    lines = [
        '# Index',
        '',
        'Status icons: 🆕 recent · ⚠️ missing summary · ❗ missing transcript',
        '',
        '<input id="search" type="text" placeholder="Search by title or keyword"/>'
    ]
    if years:
        opts = ''.join(f"<option value='{y}'>{y}</option>" for y in years)
        lines.extend([
            '<label for="year-filter">Year:</label> ',
            f'<select id="year-filter"><option value="">All</option>{opts}</select>',
            ''
        ])
    lines.extend([
        '<table id="index-table" class="sortable">',
        '<thead><tr><th>Title</th><th>Year</th><th>Duration</th><th>Words</th><th>WPM</th><th>FK</th><th>Top keywords</th><th>First year–Last year</th><th>Status</th></tr></thead>',
        '<tbody>'
    ])
    search_data = []
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
            "<tr data-id='{id}' data-year='{year}'><td><a href='{file}'>{title}</a></td>"
            "<td>{year}</td><td>{dur}</td><td>{words}</td><td>{wpm}</td><td>{fk}</td>"
            "<td>{kw}</td><td>{yrs}</td><td>{st}</td></tr>".format(
                id=html.escape(vid),
                year=html.escape(year),
                file=html.escape(e.get('title', vid).replace(' ', '_')),
                title=html.escape(title),
                dur=html.escape(duration),
                words=html.escape(e.get('words', '')),
                wpm=html.escape(e.get('wpm', '')),
                fk=html.escape(e.get('fk_grade', '')),
                kw=html.escape(kw),
                yrs=html.escape(yrs),
                st=html.escape(' '.join(status))
            )
        )
        search_data.append({'id': vid, 'title': title, 'keywords': ' '.join(kw_list)})
    lines.extend([
        '</tbody></table>',
        '<script src="https://cdn.jsdelivr.net/npm/lunr@2.3.9/lunr.min.js"></script>',
        '<script src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>',
        '<script>',
        f"const searchData = {json.dumps(search_data)};",
        "const idx = lunr(function(){this.ref('id');this.field('title');this.field('keywords');searchData.forEach(d=>this.add(d));});",
        "const tbody = document.querySelector('#index-table tbody');",
        "const searchInput = document.getElementById('search');",
        "const yearFilter = document.getElementById('year-filter');",
        "function apply(){",
        "  const q = searchInput.value;",
        "  const y = yearFilter ? yearFilter.value : '';",
        "  let ids = null;",
        "  if(q){const res = idx.search(q);ids = new Set(res.map(r=>r.ref));}",
        "  tbody.querySelectorAll('tr').forEach(tr=>{",
        "    const m1 = !ids || ids.has(tr.dataset.id);",
        "    const m2 = !y || tr.dataset.year == y;",
        "    tr.style.display = m1 && m2 ? '' : 'none';",
        "  });",
        "}",
        "searchInput.addEventListener('input', apply);",
        "if(yearFilter){yearFilter.addEventListener('change', apply);}",
        '</script>'
    ])
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'Home.md').write_text('\n'.join(lines) + '\n')

if __name__ == '__main__':
    build_index_page(Path('data/transcripts_index.json'), Path('wiki_out'))
