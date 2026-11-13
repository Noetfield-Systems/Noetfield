"""Recipient-side read-only Gmail proof for Runway delivery verification.

Runs inside existing platform-api with its own Google Workspace credentials.
This is not a delivery claim unless the exact unpredictable token is found in
a recent message addressed to the expected recipient.
"""
from __future__ import annotations

import email
import imaplib
import re
from datetime import datetime, timedelta, timezone
from email.header import decode_header, make_header
from email.utils import getaddresses, parsedate_to_datetime
from typing import Any

PROVIDER_ID = re.compile(r"provider_message_id[:\s]+([a-f0-9-]{8,})", re.IGNORECASE)


def _subject(msg: email.message.Message) -> str:
    raw = str(msg.get("Subject", ""))
    try:
        return str(make_header(decode_header(raw)))
    except (ValueError, TypeError, email.errors.HeaderParseError):
        return raw


def observe_mailbox_token(
    *, mailbox: str, password: str, token: str,
    expected_recipient: str, max_age_minutes: int = 30,
    max_messages: int = 100,
) -> dict[str, Any] | None:
    """Return evidence only for an exact token, recent date and real recipient."""
    if not mailbox or not password or not token or not expected_recipient:
        raise ValueError("MAILBOX_OBSERVER_CONFIGURATION_MISSING")
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=max_age_minutes)
    client = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=15)
    try:
        client.login(mailbox, password)
        typ, _ = client.select("INBOX", readonly=True)
        if typ != "OK":
            raise RuntimeError("IMAP_INBOX_UNAVAILABLE")
        typ, data = client.uid("SEARCH", None, "ALL")
        if typ != "OK":
            raise RuntimeError("IMAP_SEARCH_UNAVAILABLE")
        uids = (data[0] or b"").split()[-max_messages:]
        for raw_uid in reversed(uids):
            uid = raw_uid.decode("ascii", "ignore")
            typ, fetched = client.uid("FETCH", uid, "(BODY.PEEK[])")
            if typ != "OK":
                continue
            raw = next((row[1] for row in fetched if isinstance(row, tuple) and
                        isinstance(row[1], bytes)), b"")
            if not raw:
                continue
            msg = email.message_from_bytes(raw)
            try:
                received = parsedate_to_datetime(str(msg.get("Date", "")))
                if received.tzinfo is None:
                    received = received.replace(tzinfo=timezone.utc)
                received = received.astimezone(timezone.utc)
            except (TypeError, ValueError, IndexError):
                continue
            if received < cutoff or received > now + timedelta(minutes=5):
                continue
            recipients = {address.casefold() for _, address in
                          getaddresses(msg.get_all("To", []) + msg.get_all("Cc", []))}
            if expected_recipient.casefold() not in recipients:
                continue
            subj = _subject(msg)
            # Raw MIME includes text/plain and text/html, preserving exact token.
            content = raw.decode("utf-8", errors="replace")
            if token not in subj and token not in content:
                continue
            provider_id = PROVIDER_ID.search(content)
            return {
                "observed_verification_token": token,
                "observed_recipient": expected_recipient,
                "provider_message_id": provider_id.group(1) if provider_id else "",
                "mailbox_observation_id": "imap_" + uid,
                "subject": subj[:160],
                "last_event": "delivered",
                "observation_source": "RECIPIENT_MAILBOX_READ",
                "not_observed_reason": "",
            }
        return None
    finally:
        try:
            client.logout()
        except Exception:
            pass
