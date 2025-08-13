#!/usr/bin/env python3
import json, pathlib, sys, re, shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "transcripts_index.json"
STATIC_DIR = ROOT / "static" / "transcripts"  # served by Docusaurus
STATIC_DIR.mkdir(parents=True, exist_ok=True)

def normalize_text(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = s.strip() + "\n"
    return s

def ensure_served_copy(src: pathlib.Path, video_id: str) -> pathlib.Path:
    # Ensure the transcript is available under static/transcripts/<id>/clean.txt
    dest_dir = STATIC_DIR / video_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "clean.txt"
    if src.resolve() != dest.resolve():
        shutil.copyfile(src, dest)
    return dest

def main():
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    videos = data.get("videos", data)
    changed = False

    for item in videos:
        vid = item["id"]
        src_txt = ROOT / item["sources"]["transcript_txt"]
        text = src_txt.read_text(encoding="utf-8", errors="ignore")
        norm = normalize_text(text)
        if text != norm:
            src_txt.write_text(norm, encoding="utf-8")
            changed = True

        served_txt = ensure_served_copy(src_txt, vid)
        # Add a convenience served path if desired
        item.setdefault("sources", {})["transcript_txt_served"] = str(served_txt.relative_to(ROOT / 'static'))

        # Optional: clean VTT/SRT similarly (not strictly needed for embed)
        for k in ("transcript_vtt",):
            v = item["sources"].get(k)
            if v:
                p = ROOT / v
                if p.exists():
                    # ensure served copy too
                    dest_dir = STATIC_DIR / vid
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest = dest_dir / p.name
                    if p.resolve() != dest.resolve():
                        shutil.copyfile(p, dest)
                    item["sources"][k + "_served"] = str(dest.relative_to(ROOT / 'static'))

    if changed:
        print("Normalized transcript files.")
    INDEX.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Updated served paths.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
