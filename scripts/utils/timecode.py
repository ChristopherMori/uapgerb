"""Utilities for working with timecodes."""
from __future__ import annotations

import re

TIME_RE = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})(?:\.(\d+))?")


def to_seconds(tc: str) -> float:
    """Convert a timecode string to seconds.

    Accepts formats like ``HH:MM:SS`` or ``MM:SS`` optionally with ``.ms``
    components.
    """
    match = TIME_RE.match(tc.strip())
    if not match:
        raise ValueError(f"Invalid timecode: {tc}")
    hours, minutes, seconds, millis = match.groups(default="0")
    total = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    if millis:
        total += int(millis) / (10 ** len(millis))
    return total


def to_hms(seconds: float) -> str:
    """Return ``HH:MM:SS`` string from seconds."""
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
