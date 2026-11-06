"""Stripe commercial billing webhook tests."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

from noetfield_governance.stripe_webhook import (
    InMemoryStripeWebhookEventStore,
    notify_stripe_checkout,
    parse_checkout_completed,
    parse_invoice_event,
)


def test_parse_checkout_completed() -> None:
    event = {
        "id": "evt_test_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "customer": "cus_test_123",
                "customer_details": {"email": "buyer@corp.com"},
                "amount_total": 1000000,
                "currency": "usd",
                "payment_status": "paid",
                "metadata": {"gtm_sku": "Trust_Brief"},
            }
        },
    }
    out = parse_checkout_completed(event)
    assert out is not None
    assert out["session_id"] == "cs_test_123"
    assert out["customer_id"] == "cus_test_123"
    assert out["customer_email"] == "buyer@corp.com"
    assert out["sku"] == "Trust_Brief"
    assert out["payment_status"] == "paid"


def test_parse_checkout_ignores_unpaid_completion() -> None:
    event = {
        "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_test_unpaid", "payment_status": "unpaid"}},
    }
    assert parse_checkout_completed(event) is None


def test_parse_checkout_ignores_other_events() -> None:
    assert parse_checkout_completed({"type": "invoice.paid", "data": {}}) is None


def test_parse_invoice_paid() -> None:
    event = {
        "id": "evt_invoice_paid",
        "type": "invoice.paid",
        "data": {
            "object": {
                "id": "in_test_123",
                "number": "NOE-0001",
                "customer": "cus_test_123",
                "customer_email": "buyer@corp.com",
                "amount_due": 200000,
                "amount_paid": 200000,
                "currency": "usd",
                "status": "paid",
                "hosted_invoice_url": "https://invoice.stripe.test/i/test",
                "metadata": {"gtm_sku": "Copilot_Readiness_Pack"},
            }
        },
    }
    out = parse_invoice_event(event)
    assert out is not None
    assert out["invoice_id"] == "in_test_123"
    assert out["invoice_number"] == "NOE-0001"
    assert out["amount_paid"] == "200000"
    assert out["status"] == "paid"
    assert out["sku"] == "Copilot_Readiness_Pack"


def test_in_memory_event_store_deduplicates_and_allows_retry_after_failure() -> None:
    async def run() -> None:
        store = InMemoryStripeWebhookEventStore()
        assert await store.reserve("evt_1", "invoice.paid", "in_1") is True
        assert await store.reserve("evt_1", "invoice.paid", "in_1") is False
        await store.mark_failed("evt_1", "temporary")
        assert await store.reserve("evt_1", "invoice.paid", "in_1") is True
        await store.mark_processed("evt_1")
        assert await store.reserve("evt_1", "invoice.paid", "in_1") is False

    asyncio.run(run())


def test_notify_stripe_checkout_uses_intake_email() -> None:
    settings = MagicMock()
    settings.intake_email_to = "operations@noetfield.com"
    settings.intake_email_notify_enabled = True
    settings.intake_email_from = "Noetfield <notifications@noetfield.com>"
    settings.resend_api_key = "re_test"
    settings.intake_smtp_host = None
    with patch("noetfield_governance.intake_notify._send_via_resend", return_value=True) as send:
        ok = notify_stripe_checkout(
            settings,
            {
                "session_id": "cs_x",
                "customer_id": "cus_x",
                "customer_email": "buyer@corp.com",
                "sku": "Copilot_Readiness_Pack",
                "amount_total": "200000",
                "currency": "USD",
                "payment_status": "paid",
            },
        )
    assert ok is True
    send.assert_called_once()
