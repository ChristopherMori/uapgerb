"""Compute transcript statistics and output ``data/metrics.csv``."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from statistics import mean, pstdev

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
import textstat

from utils.text_helpers import HEDGE_TERMS, UNCERTAINTY_TERMS, count_terms

# Allow very long CSV fields such as transcript segments
csv.field_size_limit(sys.maxsize)


def analyze(video_id: str, folder: Path) -> dict:
    clean_file = folder / f"{video_id}.clean.md"
    seg_csv = folder / f"{video_id}.segments.csv"
    if not clean_file.exists() or not seg_csv.exists():
        return {}
    text = clean_file.read_text()
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    unique_words = len({w.lower() for w in words})
    ttr = unique_words / len(words) if words else 0
    questions = text.count('?')
    hedges = count_terms(text, HEDGE_TERMS)
    uncertainty = count_terms(text, UNCERTAINTY_TERMS)
    fk = textstat.flesch_kincaid_grade(text) if text else 0
    with seg_csv.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    duration = 0.0
    if rows:
        start0 = float(rows[0]['start'])
        end_last = float(rows[-1]['end'])
        duration = end_last - start0
    wpm = len(words) / (duration / 60) if duration else 0
    sent_lens = [len(word_tokenize(s)) for s in sentences]
    mean_sent_len = mean(sent_lens) if sent_lens else 0
    sia = SentimentIntensityAnalyzer()
    sentiments = [sia.polarity_scores(s)['compound'] for s in sentences] if sentences else [0]
    sentiment_mean = mean(sentiments)
    sentiment_std = pstdev(sentiments) if len(sentiments) > 1 else 0
    return {
        'video_id': video_id,
        'words': len(words),
        'sentences': len(sentences),
        'unique_words': unique_words,
        'ttr': round(ttr, 3),
        'duration_covered': round(duration, 2),
        'wpm': round(wpm, 2),
        'mean_sentence_length': round(mean_sent_len, 2),
        'fk_grade': round(fk, 2),
        'sentiment_mean': round(sentiment_mean, 3),
        'sentiment_std': round(sentiment_std, 3),
        'questions_count': questions,
        'hedge_terms_count': hedges,
        'uncertainty_markers_count': uncertainty,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only")
    args = parser.parse_args()
    base = Path("transcripts")
    rows = []
    if base.exists():
        for folder in base.iterdir():
            if not folder.is_dir():
                continue
            vid = folder.name
            if args.only and vid != args.only:
                continue
            result = analyze(vid, folder)
            if result:
                rows.append(result)
    out_file = Path("data/metrics.csv")
    with out_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            'video_id','words','sentences','unique_words','ttr','duration_covered',
            'wpm','mean_sentence_length','fk_grade','sentiment_mean','sentiment_std',
            'questions_count','hedge_terms_count','uncertainty_markers_count'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


if __name__ == "__main__":
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    main()
