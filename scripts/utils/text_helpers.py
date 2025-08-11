"""Helpers for cleaning and processing transcript text."""
from __future__ import annotations

import re
from typing import Iterable

BRACKET_RE = re.compile(r"\[(?:music|applause|laughter|silence|\s*)\]", re.I)
HEDGE_TERMS = {
    "maybe", "perhaps", "seems", "appears", "approx", "likely",
}
UNCERTAINTY_TERMS = {
    "i think", "i believe", "i guess", "possibly", "could", "might",
}


def clean_caption(text: str) -> str:
    """Remove bracketed stage directions and trim whitespace."""
    text = BRACKET_RE.sub("", text)
    return text.strip()


def count_terms(text: str, terms: Iterable[str]) -> int:
    """Count occurrences of any of ``terms`` in ``text`` (case-insensitive)."""
    lower = text.lower()
    return sum(lower.count(t) for t in terms)
