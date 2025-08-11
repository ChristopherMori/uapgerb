"""Extract named entities and top keywords for each transcript."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer


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


def extract_keywords(texts: Dict[str, str], top_n: int = 5) -> Dict[str, List[str]]:
    if not texts:
        return {}
    vectorizer = TfidfVectorizer(stop_words='english')
    ids = list(texts.keys())
    corpus = [texts[i] for i in ids]
    tfidf = vectorizer.fit_transform(corpus)
    keywords = {}
    for idx, vid in enumerate(ids):
        row = tfidf[idx].toarray().ravel()
        top_idx = row.argsort()[-top_n:][::-1]
        terms = [vectorizer.get_feature_names_out()[i] for i in top_idx]
        keywords[vid] = terms
    return keywords


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only")
    args = parser.parse_args()
    base = Path("transcripts")
    texts = gather_texts(base, args.only)
    nlp = spacy.load("en_core_web_sm")
    keywords = extract_keywords(texts)
    result = {}
    for vid, text in texts.items():
        result[vid] = extract_entities(nlp, text)
        result[vid]["keywords_top"] = keywords.get(vid, [])
    out_file = Path("data/entities_topics.json")
    out_file.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
