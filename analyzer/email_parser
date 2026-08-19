"""
Email parsing: turns raw .eml bytes or pasted email text into a structured
ParsedEmail object that every other analyzer module consumes.

Uses Python's stdlib `email` package (RFC 5322 / MIME aware) rather than
regex, so multipart messages, encoded headers, and HTML+plaintext
alternatives are handled correctly.

This module is read-only: it never opens, executes, or writes attachment
contents to disk. Attachments are represented only by their metadata
(filename, declared content-type, size).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from email import message_from_bytes, message_from_string, policy
from email.header import decode_header
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr

from bs4 import BeautifulSoup

from utils.logger import get_logger
from utils.validators import MAX_QUICK_SCAN_CHARS, clamp_text

logger = get_logger(__name__)

MAX_EML_BYTES = 5_000_000  # 5 MB cap; this is a text/metadata parser, not a file loader


@dataclass(frozen=True)
class AttachmentInfo:
    """Metadata only — the attachment's bytes are never read into memory here."""

    filename: str
    content_type: str
    size_bytes: int


@dataclass(frozen=True)
class ParsedEmail:
    """Structured representation of an email, ready for downstream analysis."""

    subject: str
    from_display_name: str
    from_address: str
    reply_to_address: str
    to_addresses: list[str]
    date: str
    raw_headers: dict[str, str]
    body_text: str          # plain-text body (extracted from HTML if needed)
    body_html: str          # raw HTML body, if present, else ""
    links: list[str]        # every href/src URL found in the HTML body
    attachments: list[AttachmentInfo]
    parse_warnings: list[str] = field(default_factory=list)


class EmailParseError(Exception):
    """Raised when the input cannot be parsed as an email at all."""


def parse_eml_bytes(raw_bytes: bytes) -> ParsedEmail:
    """Parse a raw .eml file's bytes into a ParsedEmail."""
    if not raw_bytes:
        raise EmailParseError("No content to parse.")
    if len(raw_bytes) > MAX_EML_BYTES:
        logger.warning("Truncating oversized .eml input (%d bytes)", len(raw_bytes))
        raw_bytes = raw_bytes[:MAX_EML_BYTES]

    try:
        msg = message_from_bytes(raw_bytes, policy=policy.default)
    except Exception as exc:  # noqa: BLE001
        raise EmailParseError(f"Could not parse .eml content: {exc}") from exc

    return _build_parsed_email(msg)


def parse_raw_text(text: str) -> ParsedEmail:
    """
    Parse pasted email text (headers + body, as a user might copy from a
    mail client) into a ParsedEmail. Falls back gracefully if headers are
    missing entirely — the whole input is then treated as body text.
    """
    if not text or not text.strip():
        raise EmailParseError("No content to parse.")

    text = clamp_text(text, max_chars=MAX_QUICK_SCAN_CHARS * 5)

    try:
        msg = message_from_string(text, policy=policy.default)
    except Exception as exc:  # noqa: BLE001
        raise EmailParseError(f"Could not parse email text: {exc}") from exc

    parsed = _build_parsed_email(msg)

    # If parsing found essentially nothing (no subject/from and no body),
    # the pasted text likely wasn't in header+body format at all — treat
    # it as a bare body so Quick-Scan-style pastes still work upstream.
    if not parsed.subject and not parsed.from_address and not parsed.body_text.strip():
        return ParsedEmail(
            subject="",
            from_display_name="",
            from_address="",
            reply_to_address="",
            to_addresses=[],
            date="",
            raw_headers={},
            body_text=text,
            body_html="",
            links=_extract_links_from_html(""),
            attachments=[],
            parse_warnings=["No headers detected; treated entire input as body text."],
        )
    return parsed


def _build_parsed_email(msg: EmailMessage) -> ParsedEmail:
    warnings: list[str] = []

    subject = _decode_header_value(msg.get("Subject", ""))
    from_display_name, from_address = parseaddr(msg.get("From", ""))
    from_display_name = _decode_header_value(from_display_name)

    reply_to_raw = msg.get("Reply-To", "")
    _, reply_to_address = parseaddr(reply_to_raw) if reply_to_raw else ("", "")

    to_addresses = [addr for _, addr in getaddresses(msg.get_all("To", []))]

    date = msg.get("Date", "")

    raw_headers = {k: _decode_header_value(v) for k, v in msg.items()}

    body_text, body_html, links, attachments = _walk_parts(msg, warnings)

    return ParsedEmail(
        subject=subject,
        from_display_name=from_display_name,
        from_address=from_address.lower(),
        reply_to_address=reply_to_address.lower(),
        to_addresses=to_addresses,
        date=date,
        raw_headers=raw_headers,
        body_text=body_text,
        body_html=body_html,
        links=links,
        attachments=attachments,
        parse_warnings=warnings,
    )


def _walk_parts(
    msg: EmailMessage, warnings: list[str]
) -> tuple[str, str, list[str], list[AttachmentInfo]]:
    body_text = ""
    body_html = ""
    attachments: list[AttachmentInfo] = []

    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = part.get_content_disposition()
            content_type = part.get_content_type()

            if content_disposition == "attachment":
                attachments.append(_attachment_info(part))
                continue

            if content_type == "text/plain" and not body_text:
                body_text = _safe_get_content(part, warnings)
            elif content_type == "text/html" and not body_html:
                body_html = _safe_get_content(part, warnings)
    else:
        content_type = msg.get_content_type()
        if content_type == "text/html":
            body_html = _safe_get_content(msg, warnings)
        else:
            body_text = _safe_get_content(msg, warnings)

    links = _extract_links_from_html(body_html)

    if not body_text and body_html:
        body_text = _html_to_text(body_html)

    return body_text, body_html, links, attachments


def _safe_get_content(part: EmailMessage, warnings: list[str]) -> str:
    try:
        content = part.get_content()
        return content if isinstance(content, str) else str(content)
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"Could not decode a message part: {exc}")
        return ""


def _attachment_info(part: EmailMessage) -> AttachmentInfo:
    filename = part.get_filename() or "(unnamed)"
    filename = _decode_header_value(filename)
    content_type = part.get_content_type()
    try:
        payload = part.get_payload(decode=True)
        size_bytes = len(payload) if payload else 0
    except Exception:  # noqa: BLE001
        size_bytes = 0
    return AttachmentInfo(filename=filename, content_type=content_type, size_bytes=size_bytes)


def _extract_links_from_html(html: str) -> list[str]:
    if not html:
        return []
    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as exc:  # noqa: BLE001
        logger.debug("HTML link extraction failed: %s", exc)
        return []

    links: list[str] = []
    for tag in soup.find_all(["a", "img", "iframe", "script"]):
        url = tag.get("href") or tag.get("src")
        if url:
            links.append(url.strip())
    # de-duplicate while preserving order
    seen: set[str] = set()
    unique_links = []
    for link in links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)
    return unique_links


def _html_to_text(html: str) -> str:
    try:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception:  # noqa: BLE001
        return ""


def _decode_header_value(value: str) -> str:
    if not value:
        return ""
    try:
        parts = decode_header(value)
        decoded = []
        for chunk, encoding in parts:
            if isinstance(chunk, bytes):
                decoded.append(chunk.decode(encoding or "utf-8", errors="replace"))
            else:
                decoded.append(chunk)
        return "".join(decoded)
    except Exception:  # noqa: BLE001
        return value
