"""Stripe commercial webhook — checkout notification."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from noetfield_governance.stripe_webhook import (
    create_research_entitlement_outbox,
    notify_stripe_checkout,
    parse_checkout_completed,
)


def test_parse_checkout_completed() -> None:
    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "customer_details": {"email": "buyer@corp.com"},
                "amount_total": 1000000,
                "currency": "usd",
                "metadata": {"gtm_sku": "Trust_Brief"},
            }
        },
    }
    out = parse_checkout_completed(event)
    assert out is not None
    assert out["session_id"] == "cs_test_123"
    assert out["customer_email"] == "buyer@corp.com"
    assert out["sku"] == "Trust_Brief"


def test_parse_checkout_ignores_other_events() -> None:
    assert parse_checkout_completed({"type": "invoice.paid", "data": {}}) is None


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
                "customer_email": "buyer@corp.com",
                "sku": "Copilot_Readiness_Pack",
                "amount_total": "200000",
                "currency": "USD",
            },
        )
    assert ok is True
    send.assert_called_once()


def test_create_research_entitlement_outbox_for_rfp_pack() -> None:
    fulfillment = create_research_entitlement_outbox(
        {
            "session_id": "cs_research",
            "customer_email": "buyer@corp.com",
            "sku": "RFP_Response_Pack",
            "amount_total": "149900",
            "currency": "USD",
        }
    )
    assert fulfillment is not None
    assert fulfillment["recipe_id"] == "rfp-response-pack"
    assert fulfillment["runway_id"] == "research"
    assert fulfillment["outbox_status"] == "pending_submit"
