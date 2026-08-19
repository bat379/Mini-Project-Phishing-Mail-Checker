"""
Social-engineering language detection.

Scans email text for phrase patterns commonly associated with the five
manipulation categories covered in the Education Center: Urgency, Fear,
Authority Impersonation, Reward/Curiosity, and Trust Exploitation.

This module is pure text analysis: no network calls, no execution of
anything found in the input. It is intentionally pattern-level (keyword /
phrase matching) rather than a machine-learning classifier, so its
reasoning is fully transparent and explainable to students.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Category(str, Enum):
    URGENCY = "Urgency"
    FEAR = "Fear"
    AUTHORITY = "Authority Impersonation"
    REWARD = "Reward / Curiosity"
    TRUST = "Trust Exploitation"


@dataclass(frozen=True)
class ContentFinding:
    category: Category
    matched_phrase: str
    risk_points: int
    explanation: str


# Each category maps to (weight, [regex patterns], explanation).
# Patterns are intentionally generic/descriptive of *techniques*, not
# copies of any real attack campaign.
_PATTERNS: dict[Category, tuple[int, list[str], str]] = {
    Category.URGENCY: (
        15,
        [
            r"\bimmediately\b",
            r"\bact now\b",
            r"\burgent\b",
            r"\bwithin \d+\s*(hours?|minutes?)\b",
            r"\baccount will be (closed|suspended|locked|terminated)\b",
            r"\blast (chance|warning)\b",
            r"\bexpires? (today|soon)\b",
        ],
        "Attackers create time pressure so the reader reacts before thinking carefully.",
    ),
    Category.FEAR: (
        15,
        [
            r"\bsuspicious activity\b",
            r"\bunauthorized (access|login|attempt)\b",
            r"\byour account (has been|was) compromised\b",
            r"\bsecurity (alert|breach|warning)\b",
            r"\bunusual (sign[- ]in|login)\b",
        ],
        "Fear-based messages provoke a rushed, anxious response instead of careful verification.",
    ),
    Category.AUTHORITY: (
        20,
        [
            r"\bit department\b",
            r"\bhelp ?desk\b",
            r"\bhuman resources\b",
            r"\bfrom the (ceo|cfo|director|manager)\b",
            r"\bpayroll (team|department)\b",
            r"\bfailure to comply\b",
            r"\blegal (action|notice)\b",
        ],
        "Impersonating a trusted authority (IT, HR, leadership) discourages the reader from questioning the request.",
    ),
    Category.REWARD: (
        10,
        [
            r"\byou('?ve| have) won\b",
            r"\bclaim your (prize|reward|gift)\b",
            r"\bexclusive offer\b",
            r"\bfree (gift|reward)\b",
            r"\bcongratulations\b",
        ],
        "Reward and curiosity hooks lower the reader's guard by appealing to excitement rather than caution.",
    ),
    Category.TRUST: (
        15,
        [
            r"\bas (we )?discussed\b",
            r"\bplease see attached invoice\b",
            r"\bupdate your (payment|billing) (info|information|details)\b",
            r"\bconfirm your (password|credentials|account details)\b",
            r"\bkindly\b",
        ],
        "These phrases mimic legitimate business or personal correspondence to lower suspicion.",
    ),
}

MAX_INPUT_CHARS = 50_000  # defensive cap; this is a text-analysis tool, not a file executor


def analyze_content(text: str) -> list[ContentFinding]:
    """
    Scan `text` for social-engineering language patterns.

    Returns a list of ContentFinding, one per unique pattern match found.
    Input longer than MAX_INPUT_CHARS is truncated for analysis.
    """
    if not text:
        return []

    sample = text[:MAX_INPUT_CHARS].lower()
    findings: list[ContentFinding] = []

    for category, (weight, patterns, explanation) in _PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, sample, flags=re.IGNORECASE)
            if match:
                findings.append(
                    ContentFinding(
                        category=category,
                        matched_phrase=match.group(0),
                        risk_points=weight,
                        explanation=explanation,
                    )
                )

    return findings


def total_content_score(findings: list[ContentFinding]) -> int:
    """Sum risk points across findings, capped at 100 for display purposes."""
    return min(100, sum(f.risk_points for f in findings))
