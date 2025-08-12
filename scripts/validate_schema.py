#!/usr/bin/env python3
import json, sys, pathlib, re
from jsonschema import validate, Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "transcripts_index.json"
SCHEMA = ROOT / "data" / "schema" / "transcripts.schema.json"

def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)

def main():
    if not INDEX.exists():
        die(f"missing {INDEX}")
    if not SCHEMA.exists():
        die(f"missing {SCHEMA}")

    data = json.loads(INDEX.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    validator = Draft202012Validator(schema)
    errs = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errs:
        for e in errs:
            print(f"Schema error at {list(e.path)}: {e.message}", file=sys.stderr)
        sys.exit(1)

    # Custom validations
    ids = set()
    slugs = set()
    tag_ns_re = re.compile(r"^(person|place|topic):[a-z0-9-]+$")

    for i, item in enumerate(data):
        vid = item["id"]
        slug = item["slug"]
        if vid in ids:
            die(f"duplicate id: {vid}")
        if slug in slugs:
            die(f"duplicate slug: {slug}")
        ids.add(vid)
        slugs.add(slug)

        # Ensure transcript file exists
        txt_path = ROOT / item["sources"]["transcript_txt"]
        if not txt_path.exists():
            die(f"[{vid}] transcript_txt not found: {txt_path}")

        # Namespaced tags (optional but enforced if present)
        for t in item.get("tags", []):
            if not tag_ns_re.match(t):
                die(f"[{vid}] tag not namespaced or invalid: {t}")

        # Entities slugs are hyphen-kebab
        ents = item.get("entities", {})
        for group in ("people", "places", "topics"):
            for eslug in ents.get(group, []):
                if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", eslug):
                    die(f"[{vid}] invalid {group} slug: {eslug}")

    print("OK: transcripts_index.json is valid")

if __name__ == "__main__":
    main()
