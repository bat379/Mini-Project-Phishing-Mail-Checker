"""
Header analysis: examines the structured header data already extracted by
email_parser.py for authentication and sender-consistency red flags.

This module does not perform live DNS lookups (an .eml/paste doesn't carry
enough context to query the sending server's DNS retroactively). Instead
it reads the Authentication-Results header, if present, which is how real
mail servers record their own SPF/DKIM/DMARC verdicts — this is what makes
the check "awareness" rather than live re-verification.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from analyzer.email_parser import ParsedEmail
from utils.logger import get_logger

logger = get_logger(__name__)


class AuthResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    SOFTFAIL = "softfail"
    NEUTRAL = "neutral"
    NONE = "none"
    NOT_PRESENT = "not present"


@dataclass(frozen=True)
class HeaderFinding:
    title: str
    risk_points: int
    explanation: str
    detail: str = ""


# Weights align with the risk-scoring table from the project spec.
WEIGHT_REPLY_TO_MISMATCH = 20
WEIGHT_DISPLAY_NAME_MISMATCH = 15
WEIGHT_SPF_FAIL = 20
WEIGHT_DKIM_FAIL = 20
WEIGHT_DMARC_FAIL = 20
WEIGHT_NO_AUTH_HEADER = 5  # mild — common in forwarded/pasted mail, not proof of anything


def analyze_headers(parsed: ParsedEmail) -> list[HeaderFinding]:
    """Run all header-level checks against a ParsedEmail and return findings."""
    findings: list[HeaderFinding] = []

    findings.extend(_check_reply_to_mismatch(parsed))
    findings.extend(_check_display_name_mismatch(parsed))
    findings.extend(_check_authentication_results(parsed))

    return findings


def _check_reply_to_mismatch(parsed: ParsedEmail) -> list[HeaderFinding]:
    if not parsed.reply_to_address or not parsed.from_address:
        return []

    from_domain = _domain_of(parsed.from_address)
    reply_domain = _domain_of(parsed.reply_to_address)

    if from_domain and reply_domain and from_domain != reply_domain:
        return [
            HeaderFinding(
                title="Sender domain does not match Reply-To address",
                risk_points=WEIGHT_REPLY_TO_MISMATCH,
                explanation=(
                    "Attackers often set Reply-To to an address they control while "
                    "spoofing a trusted From address, so replies go to them instead "
                    "of the real organization."
                ),
                detail=f"From: {from_domain}  |  Reply-To: {reply_domain}",
            )
        ]
    return []


def _check_display_name_mismatch(parsed: ParsedEmail) -> list[HeaderFinding]:
    """Flag when the display name suggests a well-known-style identity that the
    actual address domain has no relationship to (heuristic, not a domain list)."""
    if not parsed.from_display_name or not parsed.from_address:
        return []

    name = parsed.from_display_name.lower()
    domain = _domain_of(parsed.from_address)
    if not domain:
        return []

    # Heuristic: if the display name contains a word that looks like a brand/
    # department term ("support", "security", "billing", "admin", "team",
    # "service") but that word does not appear anywhere in the domain, flag
    # it for the student to verify manually. This is intentionally a nudge,
    # not a verdict.
    trigger_words = ["support", "security", "billing", "admin", "service", "team", "official", "helpdesk"]
    domain_root = domain.split(".")[0]

    for word in trigger_words:
        if word in name and word not in domain_root and domain_root not in name:
            return [
                HeaderFinding(
                    title="Display name suggests an official identity the domain doesn't match",
                    risk_points=WEIGHT_DISPLAY_NAME_MISMATCH,
                    explanation=(
                        "Display names are freely chosen by the sender and are not "
                        "verified by mail servers. A name like this paired with an "
                        "unrelated domain is a common impersonation pattern — always "
                        "check the actual address, not just the name shown."
                    ),
                    detail=f'Display name: "{parsed.from_display_name}"  |  Domain: {domain}',
                )
            ]
    return []


def _check_authentication_results(parsed: ParsedEmail) -> list[HeaderFinding]:
    auth_header = parsed.raw_headers.get("Authentication-Results", "")

    if not auth_header:
        return [
            HeaderFinding(
                title="No Authentication-Results header present",
                risk_points=WEIGHT_NO_AUTH_HEADER,
                explanation=(
                    "This header is normally added by the receiving mail server and is "
                    "often stripped when an email is forwarded or pasted as plain text, "
                    "so its absence here is a mild signal at most — not proof of spoofing."
                ),
            )
        ]

    findings: list[HeaderFinding] = []
    spf = _extract_auth_verdict(auth_header, "spf")
    dkim = _extract_auth_verdict(auth_header, "dkim")
    dmarc = _extract_auth_verdict(auth_header, "dmarc")

    if spf == AuthResult.FAIL:
        findings.append(HeaderFinding(
            title="SPF check failed",
            risk_points=WEIGHT_SPF_FAIL,
            explanation=(
                "SPF (Sender Policy Framework) verifies the sending server is authorized "
                "for the claimed domain. A failure means the server that sent this email "
                "was not on that domain's approved list."
            ),
        ))
    if dkim == AuthResult.FAIL:
        findings.append(HeaderFinding(
            title="DKIM check failed",
            risk_points=WEIGHT_DKIM_FAIL,
            explanation=(
                "DKIM (DomainKeys Identified Mail) verifies the message body and headers "
                "weren't altered in transit using a cryptographic signature. A failure "
                "suggests the message was tampered with or the signature is invalid."
            ),
        ))
    if dmarc == AuthResult.FAIL:
        findings.append(HeaderFinding(
            title="DMARC check failed",
            risk_points=WEIGHT_DMARC_FAIL,
            explanation=(
                "DMARC ties SPF and DKIM together and tells receiving servers what to do "
                "on failure. A DMARC failure means the domain owner's own policy was violated."
            ),
        ))

    return findings


def _extract_auth_verdict(auth_header: str, mechanism: str) -> AuthResult:
    match = re.search(rf"{mechanism}=([a-z]+)", auth_header, flags=re.IGNORECASE)
    if not match:
        return AuthResult.NOT_PRESENT
    value = match.group(1).lower()
    try:
        return AuthResult(value)
    except ValueError:
        return AuthResult.NOT_PRESENT


def _domain_of(address: str) -> str:
    if "@" not in address:
        return ""
    return address.rsplit("@", 1)[-1].strip().lower()
