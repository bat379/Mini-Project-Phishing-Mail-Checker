"""
Rotating cybersecurity trivia used by the Hacker Zone's "Fact of the Day"
widget. Original, general-knowledge facts — not quoted from any source.
"""
from __future__ import annotations

CYBER_FACTS: list[str] = [
    "The term 'phishing' is a deliberate misspelling of 'fishing' — attackers "
    "cast bait and wait for someone to bite.",
    "SPF, DKIM, and DMARC are three separate email authentication standards "
    "that work together to make sender spoofing harder.",
    "Business Email Compromise (BEC) scams often skip malicious links entirely "
    "and rely purely on convincing text to trigger a wire transfer.",
    "Domain look-alikes often swap a single character (e.g. 'rn' for 'm') — "
    "always worth a second glance at the actual domain, not just the display name.",
    "Multi-factor authentication (MFA) stops the vast majority of account "
    "takeover attempts even when a password has been stolen.",
    "Spear phishing targets a specific person using personal details gathered "
    "in advance, making it far more convincing than generic mass phishing.",
    "'Vishing' is phishing over voice calls, and 'smishing' is phishing via "
    "SMS text messages — the psychological tricks are the same.",
    "Legitimate organizations almost never ask you to email your password — "
    "if a message asks for credentials directly, that's a major red flag.",
    "Attackers frequently register lookalike domains years before using them, "
    "so a domain's age alone isn't proof it's safe.",
    "Reporting a phishing email — even a convincing one — helps your "
    "organization block it before it reaches your colleagues.",
]
