"""Extract named entities and top keywords for each transcript."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import spacy
from rake_nltk import Rake


def gather_texts(base: Path, only: str | None = None) -> Dict[str, str]:
    texts = {}
    if not base.exists():
        return texts
    for folder in base.iterdir():
        if not folder.is_dir():
            continue
        vid = folder.name
        if only and vid != only:
            continue
        clean = folder / f"{vid}.clean.md"
        if clean.exists():
            texts[vid] = clean.read_text()
    return texts


def extract_entities(nlp, text: str) -> Dict[str, List[str]]:
    doc = nlp(text)
    people = sorted({e.text for e in doc.ents if e.label_ == "PERSON"})
    orgs = sorted({e.text for e in doc.ents if e.label_ == "ORG"})
    places = sorted({e.text for e in doc.ents if e.label_ in {"GPE", "LOC"}})
    return {"people": people, "orgs": orgs, "places": places}


def extract_keywords(texts: Dict[str, str], top_n: int = 5,
                     synonyms: Dict[str, str] | None = None,
                     manual: Dict[str, Dict[str, List[str]]] | None = None) -> Dict[str, List[str]]:
    """Return top keywords per video using RAKE and optional overrides."""
    if not texts:
        return {}
    rake = Rake()
    synonyms = {k.lower(): v.lower() for k, v in (synonyms or {}).items()}
    manual = manual or {}
    keywords: Dict[str, List[str]] = {}
    for vid, text in texts.items():
        rake.extract_keywords_from_text(text)
        phrases = rake.get_ranked_phrases()[:top_n]
        mapped = [synonyms.get(p.lower(), p.lower()) for p in phrases]
        overrides = manual.get(vid, {})
        remove = {synonyms.get(r.lower(), r.lower()) for r in overrides.get("remove", [])}
        add = [synonyms.get(a.lower(), a.lower()) for a in overrides.get("add", [])]
        unique: List[str] = []
        for kw in mapped:
            if kw not in unique and kw not in remove:
                unique.append(kw)
        for kw in add:
            if kw not in unique:
                unique.append(kw)
        keywords[vid] = unique
    return keywords


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only")
    args = parser.parse_args()
    base = Path("transcripts")
    texts = gather_texts(base, args.only)
    nlp = spacy.load("en_core_web_sm")
    synonyms = {}
    syn_file = Path("data/keyword_synonyms.json")
    if syn_file.exists():
        synonyms = json.loads(syn_file.read_text())
    manual = {}
    man_file = Path("data/manual_keywords.json")
    if man_file.exists():
        manual = json.loads(man_file.read_text())
    keywords = extract_keywords(texts, synonyms=synonyms, manual=manual)
    result = {}
    for vid, text in texts.items():
        result[vid] = extract_entities(nlp, text)
        result[vid]["keywords_top"] = keywords.get(vid, [])
    out_file = Path("data/entities_topics.json")
    out_file.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
