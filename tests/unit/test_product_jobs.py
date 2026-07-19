"""Product job gateway wiring tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from noetfield_governance.product_entitlement_store import get_product_entitlement_store
from noetfield_governance.product_jobs import submit_product_job
from noetfield_governance.research_product_catalog import resolve_research_product
from noetfield_governance.stripe_webhook import create_research_entitlement_outbox


def setup_function() -> None:
    store = get_product_entitlement_store()
    store.entitlements.clear()
    store.outbox.clear()
    store.outbox_by_entitlement.clear()


def test_resolve_research_product_vendor_brief() -> None:
    product = resolve_research_product("Vendor_Decision_Brief")
    assert product is not None
    assert product["recipe_id"] == "vendor-decision-brief"
    assert product["runway_id"] == "research"


def test_create_research_entitlement_outbox() -> None:
    fulfillment = create_research_entitlement_outbox(
        {
            "session_id": "cs_test_research_1",
            "customer_email": "buyer@example.com",
            "sku": "spreadsheet-kpi-pack",
            "amount_total": "59900",
            "currency": "USD",
        }
    )
    assert fulfillment is not None
    assert fulfillment["runway_id"] == "research"
    assert fulfillment["recipe_id"] == "spreadsheet-kpi-pack"
    assert fulfillment["job_submit_ready"] is True


def test_submit_product_job_requires_gateway_or_marks_failed() -> None:
    create_research_entitlement_outbox(
        {
            "session_id": "cs_test_research_2",
            "customer_email": "buyer2@example.com",
            "sku": "rfp-response-pack",
            "amount_total": "149900",
            "currency": "USD",
        }
    )
    entitlement_id = next(iter(get_product_entitlement_store().entitlements))
    settings = MagicMock()
    settings.runway_job_gateway_base_url = None
    settings.runway_job_gateway_key_id = None
    settings.runway_job_gateway_hmac_secret = None
    status, payload = submit_product_job(
        settings,
        {
            "entitlement_id": entitlement_id,
            "idempotency_key": "test-idempotency-key-001",
            "goal": {"summary": "test goal"},
        },
    )
    assert status == 503
    assert payload["error"] == "RUNWAY_JOB_GATEWAY_NOT_CONFIGURED"
    outbox = get_product_entitlement_store().get_outbox_for_entitlement(entitlement_id)
    assert outbox is not None
    assert outbox.status == "failed"


def test_submit_product_job_success_marks_outbox_submitted() -> None:
    fulfillment = create_research_entitlement_outbox(
        {
            "session_id": "cs_test_research_3",
            "customer_email": "buyer3@example.com",
            "sku": "vendor-decision-brief",
            "amount_total": "69900",
            "currency": "USD",
        }
    )
    settings = MagicMock()
    settings.runway_job_gateway_base_url = "https://gateway.example"
    settings.runway_job_gateway_key_id = "nf-www"
    settings.runway_job_gateway_hmac_secret = "secret"
    with patch(
        "noetfield_governance.product_jobs.gateway_request",
        return_value=(202, {"job_id": "rj_" + "a" * 32, "status": "QUEUED", "created": True}),
    ):
        status, payload = submit_product_job(
            settings,
            {
                "entitlement_id": fulfillment["entitlement_id"],
                "idempotency_key": "test-idempotency-key-002",
                "goal": {"summary": "vendor comparison"},
            },
        )
    assert status == 202
    assert payload["recipe_id"] == "vendor-decision-brief"
    outbox = get_product_entitlement_store().get_outbox_for_entitlement(fulfillment["entitlement_id"])
    assert outbox is not None
    assert outbox.status == "submitted"
    assert outbox.job_id == payload["job_id"]
