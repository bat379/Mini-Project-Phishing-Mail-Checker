"""
Sample sender/subject pairs used by the "Spot the Phish" quiz.

All examples are deliberately generic and non-branded (no real company
names, no working URLs, no ready-to-send content) — they exist purely to
teach recognizable *patterns*, not to serve as attack templates.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuizItem:
    sender: str
    subject: str
    is_phishing: bool
    explanation: str


QUIZ_ITEMS: list[QuizItem] = [
    QuizItem(
        sender="it-support@company-secure-verify.com",
        subject="URGENT: Your mailbox will be deleted in 24 hours",
        is_phishing=True,
        explanation=(
            "Look-alike domain plus urgency + fear language. Real IT teams "
            "rarely threaten deletion with a hard countdown."
        ),
    ),
    QuizItem(
        sender="hr@yourcompany.com",
        subject="Reminder: benefits enrollment closes Friday",
        is_phishing=False,
        explanation=(
            "Matches the organization's real domain, gives a normal (not "
            "artificially urgent) deadline, and references a routine HR process."
        ),
    ),
    QuizItem(
        sender="rewards@prize-notify-center.net",
        subject="Congratulations! You've won a gift card - claim now",
        is_phishing=True,
        explanation=(
            "Unsolicited reward notification from an unrelated domain — "
            "classic reward/curiosity bait."
        ),
    ),
    QuizItem(
        sender="billing@your-streaming-service.com",
        subject="Your monthly receipt is attached",
        is_phishing=False,
        explanation=(
            "Routine, low-pressure transactional email matching an expected "
            "billing pattern with no urgent call to action."
        ),
    ),
    QuizItem(
        sender="ceo.office@corp-alerts-secure.com",
        subject="Confidential request - reply ASAP, can't talk right now",
        is_phishing=True,
        explanation=(
            "Authority impersonation (claims to be an executive) combined "
            "with urgency and an excuse for why normal verification (a call) "
            "isn't possible — a hallmark of Business Email Compromise."
        ),
    ),
    QuizItem(
        sender="no-reply@calendar-app.com",
        subject="Meeting reminder: Team sync at 2:00 PM",
        is_phishing=False,
        explanation="Neutral, expected notification with no request for action or data.",
    ),
]
