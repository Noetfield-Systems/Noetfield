"""Noetfield delegated mailbox receipt: only observed exact delivery counts."""
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import format_datetime
from unittest.mock import patch

from noetfield_governance.mailbox_receipt import observe_mailbox_token, probe_mailbox_read_access


class FakeImap:
    def __init__(self, raw: bytes):
        self.raw = raw
        self.closed = False

    def login(self, *args):
        return "OK", [b""]

    def select(self, *args, **kwargs):
        return "OK", [b""]

    def uid(self, cmd, *args):
        if cmd == "SEARCH":
            return "OK", [b"47"]
        if cmd == "FETCH":
            return "OK", [(b"47 (BODY[])", self.raw)]
        raise AssertionError(cmd)

    def logout(self):
        self.closed = True


def make_message(token: str = "runtoken_1234567890", recipient: str = "operations@noetfield.com"):
    msg = EmailMessage()
    msg["Subject"] = "Runway delivery " + token
    msg["To"] = recipient
    msg["From"] = "sender@example.net"
    msg["Date"] = format_datetime(datetime.now(timezone.utc))
    msg.set_content("provider_message_id: e39dffab-1111-4444-8888-abcdef123456")
    return msg.as_bytes()


def observe(token: str, recipient: str, raw: bytes):
    fake = FakeImap(raw)
    with patch("noetfield_governance.mailbox_receipt.imaplib.IMAP4_SSL", return_value=fake):
        outcome = observe_mailbox_token(mailbox="operations@noetfield.com",
            password="configured-only-in-platform", token=token,
            expected_recipient=recipient)
    assert fake.closed
    return outcome


def test_exact_mailbox_observation():
    outcome = observe("runtoken_1234567890", "operations@noetfield.com", make_message())
    assert outcome is not None
    assert outcome["observation_source"] == "RECIPIENT_MAILBOX_READ"
    assert outcome["provider_message_id"] == "e39dffab-1111-4444-8888-abcdef123456"


def test_foreign_recipient_does_not_verify():
    assert observe("runtoken_1234567890", "other@noetfield.com", make_message()) is None


def test_wrong_token_does_not_verify():
    assert observe("incorrect_1234567890", "operations@noetfield.com", make_message()) is None


def test_imap_probe_is_read_only():
    fake = FakeImap(make_message())
    with patch("noetfield_governance.mailbox_receipt.imaplib.IMAP4_SSL", return_value=fake):
        assert probe_mailbox_read_access(
            mailbox="operations@noetfield.com", password="test-token"
        )
    assert fake.closed


def test_imap_probe_missing_password_is_disabled():
    assert probe_mailbox_read_access(mailbox="operations@noetfield.com", password="") is False
