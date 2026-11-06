"""Stripe commercial webhook parsing, signature and notification tests."""

from __future__ import annotations

import hashlib
import hmac
import json

from unittest.mock import MagicMock, patch

from noetfield_governance.stripe_webhook import (
    notify_stripe_checkout,
    notify_stripe_event,
    parse_checkout_completed,
    parse_stripe_event,
    verify_stripe_signature,
)


def _event(event_type: str, obj: dict, *, event_id: str = "evt_live_123") -> dict:
    return {
        "id": event_id,
        "type": event_type,
        "livemode": True,
        "data": {"object": obj},
    }


def test_verify_stripe_v1_signature_and_timestamp_tolerance() -> None:
    secret = "whsec_test_secret"
    payload = b'{"id":"evt_123","type":"checkout.session.completed"}'
    timestamp = 1_800_000_000
    signed = str(timestamp).encode("ascii") + b"." + payload
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    header = f"t={timestamp},v1={digest}"

    assert verify_stripe_signature(payload, header, secret, now=timestamp)
    assert not verify_stripe_signature(payload, header, secret, now=timestamp + 301)
    assert not verify_stripe_signature(payload, f"t={timestamp},v1=bad", secret, now=timestamp)
    assert not verify_stripe_signature(payload, header, "", now=timestamp)


def test_parse_paid_checkout_completed() -> None:
    event = _event(
        "checkout.session.completed",
        {
            "id": "cs_live_123",
            "payment_status": "paid",
            "customer_details": {"email": "buyer@corp.com"},
            "amount_total": 1_000_000,
            "currency": "usd",
            "payment_link": "plink_live",
            "metadata": {"gtm_sku": "Trust_Brief"},
        },
    )
    out = parse_stripe_event(event)
    assert out is not None
    assert out["kind"] == "payment"
    assert out["object_id"] == "cs_live_123"
    assert out["customer_email"] == "buyer@corp.com"
    assert out["sku"] == "Trust_Brief"
    assert out["amount"] == "10,000.00 USD"
    assert out["livemode"] == "true"


def test_unpaid_checkout_completed_is_not_a_sale() -> None:
    event = _event(
        "checkout.session.completed",
        {
            "id": "cs_live_pending",
            "payment_status": "unpaid",
            "amount_total": 200_000,
            "currency": "usd",
        },
    )
    assert parse_stripe_event(event) is None
    assert parse_checkout_completed(event) is None


def test_async_payment_failure_is_routed_to_operations() -> None:
    event = _event(
        "checkout.session.async_payment_failed",
        {
            "id": "cs_live_failed",
            "payment_status": "unpaid",
            "customer_email": "buyer@corp.com",
            "amount_total": 200_000,
            "currency": "usd",
            "metadata": {"gtm_sku": "Copilot_Readiness_Pack"},
            "last_payment_error": {"message": "payment failed"},
        },
    )
    out = parse_stripe_event(event)
    assert out is not None
    assert out["kind"] == "payment_failure"
    assert out["payment_status"] == "failed"
    assert out["failure_reason"] == "payment failed"
    assert out["sku"] == "Copilot_Readiness_Pack"


def test_parse_refund_event() -> None:
    out = parse_stripe_event(
        _event(
            "charge.refunded",
            {
                "id": "ch_live_1",
                "amount": 1_000_000,
                "amount_refunded": 500_000,
                "currency": "usd",
                "payment_intent": "pi_live_1",
            },
        )
    )
    assert out is not None
    assert out["kind"] == "refund"
    assert out["amount"] == "5,000.00 USD"
    assert out["payment_intent"] == "pi_live_1"


def test_parse_dispute_includes_evidence_deadline() -> None:
    out = parse_stripe_event(
        _event(
            "charge.dispute.created",
            {
                "id": "dp_live_1",
                "amount": 1_000_000,
                "currency": "usd",
                "charge": "ch_live_1",
                "payment_intent": "pi_live_1",
                "status": "needs_response",
                "reason": "fraudulent",
                "evidence_details": {"due_by": 1_800_000_000},
            },
        )
    )
    assert out is not None
    assert out["kind"] == "dispute"
    assert out["risk_status"] == "needs_response"
    assert out["reason"] == "fraudulent"
    assert out["evidence_due_by"].startswith("2027-")


def test_parse_ignores_unsubscribed_event_types() -> None:
    assert parse_stripe_event(_event("invoice.paid", {"id": "in_1"})) is None


def test_notify_stripe_event_uses_operations_inbox_and_reply_to() -> None:
    settings = MagicMock()
    settings.intake_email_to = "operations@noetfield.com"
    settings.intake_email_notify_enabled = True
    settings.intake_email_from = "Noetfield <notifications@noetfield.com>"
    settings.resend_api_key = "re_test"
    settings.intake_smtp_host = None
    with patch(
        "noetfield_governance.intake_notify._send_via_resend",
        return_value=True,
    ) as send:
        ok = notify_stripe_event(
            settings,
            {
                "event_id": "evt_live_123",
                "event_type": "checkout.session.completed",
                "livemode": "true",
                "object_id": "cs_live_123",
                "sku": "Trust_Brief",
                "customer_email": "buyer@corp.com",
                "kind": "payment",
                "payment_status": "paid",
                "amount": "10,000.00 USD",
            },
        )
    assert ok is True
    send.assert_called_once()
    assert send.call_args.kwargs["to_addrs"] == ["operations@noetfield.com"]
    assert send.call_args.kwargs["reply_to"] == "buyer@corp.com"
    assert "evt_live_123" in send.call_args.kwargs["text"]


def test_notify_stripe_checkout_compatibility_wrapper() -> None:
    settings = MagicMock()
    settings.intake_email_to = "operations@noetfield.com"
    settings.intake_email_notify_enabled = True
    settings.intake_email_from = "Noetfield <notifications@noetfield.com>"
    settings.resend_api_key = "re_test"
    settings.intake_smtp_host = None
    with patch(
        "noetfield_governance.intake_notify._send_via_resend",
        return_value=True,
    ) as send:
        ok = notify_stripe_checkout(
            settings,
            {
                "session_id": "cs_live_x",
                "customer_email": "buyer@corp.com",
                "sku": "Copilot_Readiness_Pack",
                "amount_total": "200000",
                "currency": "USD",
            },
        )
    assert ok is True
    send.assert_called_once()
