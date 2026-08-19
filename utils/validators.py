"""
Small, dependency-free input validation/sanitization helpers shared
across the GUI and analyzer modules.
"""
from __future__ import annotations

MAX_QUICK_SCAN_CHARS = 20_000


def clamp_text(text: str, max_chars: int = MAX_QUICK_SCAN_CHARS) -> str:
    """Trim text to a safe upper bound before running any analysis on it."""
    if text is None:
        return ""
    return text[:max_chars]


def is_blank(text: str) -> bool:
    """Return True if text is empty or whitespace-only."""
    return not text or not text.strip()
