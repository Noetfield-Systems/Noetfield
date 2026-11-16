"""Commercial revenue chain: strict source, scope and real-payment invariants."""
from __future__ import annotations

import pytest

from noetfield_governance.commercial_pipeline import (
    CommercialError, OFFER_TERMS, check_payment_match, email_hash,
    evidence_url, paid_checkout_evidence,
)

def checkout(*, paid=True, live=True, amount=47500, currency="usd", session="cs_live_12345678",
             email="buyer@company.com", event_type="checkout.session.completed"):
    return {
        "id":"evt_live_123456",
        "type":event_type,
        "livemode":live,
        "data":{"object":{
            "id":session,"payment_status":"paid" if paid else "unpaid",
            "amount_total":amount,"currency":currency,
            "customer_details":{"email":email},
            "payment_intent":"pi_live_12345678",
            "payment_link":OFFER_TERMS["rwa_technical_sprint"]["payment_link_id"],
        }},
    }

def accepted_rwa():
    return {
        "offer":"rwa_technical_sprint",
        "stage":"SCOPE_ACCEPTED",
        "acceptance_evidence":"https://evidence.noetfield.com/scopes/SOW-001",
        "payment_link_id":OFFER_TERMS["rwa_technical_sprint"]["payment_link_id"],
    }

def test_accepts_real_paid_checkout_with_exact_amount():
    evidence=paid_checkout_evidence(checkout())
    assert evidence is not None
    assert evidence["amount_minor"]==47500
    assert evidence["currency"]=="usd"
    assert evidence["customer_email_hash"]==email_hash("BUYER@COMPANY.COM")
    check_payment_match(accepted_rwa(),evidence,intake_email="buyer@company.com")
    assert OFFER_TERMS["rwa_technical_sprint"]["amount_minor"]==95000
    assert OFFER_TERMS["ai_sales_os_pilot"]["currency"]=="cad"

@pytest.mark.parametrize("event",[
    checkout(paid=False),checkout(live=False),checkout(amount=0),
    checkout(session="cs_test_12345678"),
    checkout(currency="eur"),
    checkout(event_type="invoice.paid"),
    checkout(event_type="checkout.session.async_payment_failed"),
])
def test_non_paid_non_live_or_unsupported_events_never_count_as_cash(event):
    assert paid_checkout_evidence(event) is None

def test_async_paid_event_supported_without_double_counting_a_case():
    evidence=paid_checkout_evidence(checkout(event_type="checkout.session.async_payment_succeeded"))
    assert evidence is not None and evidence["livemode"] is True

@pytest.mark.parametrize("case,receipt,error",[
    ({"offer":"rwa_technical_sprint","stage":"QUALIFY","acceptance_evidence":"https://evidence.noetfield.com/a"},
     paid_checkout_evidence(checkout()),"ACCEPTED_SCOPE_REQUIRED"),
    (accepted_rwa(),paid_checkout_evidence(checkout(amount=95000)),"PAYMENT_AMOUNT_OR_CURRENCY_MISMATCH"),
    (accepted_rwa(),paid_checkout_evidence(checkout(currency="cad")),"PAYMENT_AMOUNT_OR_CURRENCY_MISMATCH"),
    (accepted_rwa(),{**paid_checkout_evidence(checkout()),"livemode":False},"LIVE_STRIPE_PAYMENT_REQUIRED"),
    (accepted_rwa(),{**paid_checkout_evidence(checkout()),"payment_link_id":"plink_another_offer"},"WRONG_APPROVED_PAYMENT_LINK"),
])
def test_rejects_wrong_scope_terms_or_link(case,receipt,error):
    with pytest.raises(CommercialError,match=error):
        check_payment_match(case,receipt,intake_email="buyer@company.com")

def test_different_payer_requires_external_authorization_evidence():
    evidence=paid_checkout_evidence(checkout(email="finance@somewhere-else.com"))
    with pytest.raises(CommercialError,match="PAYER_DIFFERENT_FROM_INTAKE"):
        check_payment_match(accepted_rwa(),evidence,intake_email="buyer@company.com")
    check_payment_match(accepted_rwa(),evidence,intake_email="buyer@company.com",
                        payer_authorization_url="https://documents.noetfield.com/payer/authorization")

@pytest.mark.parametrize("url",[
    "", "http://example.org/paper","https://example.com/stub",
    "https://attacker:pass@somewhere.org/paper","https://somewhere.org/#fragment",
    "https://localhost/paper",
])
def test_acceptance_evidence_cannot_be_local_or_placeholder(url):
    with pytest.raises(CommercialError):
        evidence_url(url)

def test_scope_links_are_required_for_recording_real_acceptance():
    assert evidence_url("https://docs.noetfield.com/sow/signed/123") == "https://docs.noetfield.com/sow/signed/123"


def test_stripe_api_accepts_both_account_signatures_without_old_key_regression(monkeypatch):
    """A separate Noetfield Stripe account must not replace Primary's active webhook."""
    import asyncio
    import hmac
    import hashlib
    import json
    import time
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, patch
    from noetfield_governance.stripe_webhook import handle_stripe_webhook

    monkeypatch.setenv("STRIPE_NOETFIELD_WEBHOOK_SECRET", "whsec_secondary_account")
    settings = SimpleNamespace(stripe_webhook_secret="whsec_primary_account",
                               database_url="postgresql://unused.example/db")
    event = checkout()
    payload = json.dumps(event).encode()
    timestamp = int(time.time())
    for secret in ("whsec_primary_account", "whsec_secondary_account"):
        signature = hmac.new(secret.encode(),f"{timestamp}.".encode()+payload,
                             hashlib.sha256).hexdigest()
        with (patch("noetfield_governance.stripe_webhook._claim_event",
                    new_callable=AsyncMock,return_value=(True,event["id"])),
              patch("noetfield_governance.stripe_webhook._finish_event",
                    new_callable=AsyncMock),
              patch("noetfield_governance.commercial_pipeline.capture_stripe_payment",
                    new_callable=AsyncMock,return_value={"captured":True}),
              patch("noetfield_governance.stripe_webhook.notify_stripe_event",
                    return_value=True)):
            result = asyncio.run(handle_stripe_webhook(settings,payload,
                                      f"t={timestamp},v1={signature}"))
            assert result["ok"] is True and result["handled"] is True
    assert asyncio.run(handle_stripe_webhook(settings,payload,
                    f"t={timestamp},v1=bad"))["error"] == "invalid_signature"
