"""Contract tests for corporate lead recovery and the evidence-aware revenue cockpit."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app
from noetfield_governance.corporate_revenue_ops import (
    build_revenue_plan, outreach_draft, recover_intakes,
)


def test_empty_plan_is_truthful_and_does_not_claim_revenue_or_agent_execution():
    board = {"deals": [], "total_deals": 0, "metrics": {
        "paid_verified_by_currency_minor": {}, "due": 0}}
    result = build_revenue_plan(board, as_of="2026-11-16")
    assert result["sample_is_complete"]
    assert result["forecast_estimated_minor_sample"] == {"USD": 0, "CAD": 0}
    assert result["matched_paid_checkouts_minor_all"] == {"USD": 0, "CAD": 0}
    assert result["actions"] == []
    assert not result["external_outreach_sent"]
    assert not result["customer_billing_initiated"]
    assert not result["delivery_dispatched"]
    assert result["provider_acknowledgements"] == 0


def test_plan_prioritizes_reversals_over_late_followups_and_keeps_cash_separate():
    deal = {
        "id": str(uuid4()), "account_name": "Example Asset Operator",
        "contact_name": "", "offer": "rwa_technical_sprint", "stage": "SIGNED",
        "currency": "usd", "estimated_minor": 95000,
        "source_intake_id": "INT-ABCDEF123456", "next_date": "2026-11-15",
        "next_action": "Check deposit", "owner": "Revenue",
        "payment": {"status": "REVERSED"},
    }
    board = {
        "deals": [deal], "total_deals": 2,
        "metrics": {"paid_verified_by_currency_minor": {"USD": 47500},
                    "due": 1, "without_owner": 0},
    }
    result = build_revenue_plan(board, as_of="2026-11-16")
    assert result["sample_is_complete"] is False
    assert result["forecast_estimated_minor_sample"]["USD"] == 95000
    assert result["matched_paid_checkouts_minor_all"]["USD"] == 47500
    assert result["actions"][0]["priority"] == "CRITICAL"
    assert result["actions"][0]["execution_state"] == "SUGGESTED_NOT_EXECUTED"
    assert "reversal" in result["actions"][0]["reasons"][0].lower()
    assert "draft" in result["actions"][0]
    assert result["actions"][0]["draft"]["delivery_provider_ack"] is False


def test_draft_does_not_impersonate_buyer_or_claim_a_meeting():
    draft = outreach_draft({"offer": "ai_sales_os_pilot", "account_name": "Acme Ltd"})
    assert draft["status"] == "DRAFT_ONLY_NOT_SENT"
    assert "Acme Ltd" in draft["body"]
    assert "Would a brief" in draft["body"]
    assert "we spoke" not in draft["body"].lower()


def test_recovery_previews_and_imports_only_real_noetfield_sources():
    rows = [
        {"intake_id": "INT-ABCDEF123456", "request_id": "RID-CUSTOMER-001",
         "contact_email": "buyer@realasset.org", "vector": "onchain-project",
         "metadata": {"form_id": "nfCapitalIntake", "initiative": "noetfield"}},
        {"intake_id": "INT-ABCDEF123457", "request_id": "RID-CUSTOMER-002",
         "contact_email": "buyer@realcorp.org", "vector": "external-opportunities",
         "metadata": {"form_id": "nfConnectWizard", "initiative": "noetfield",
                      "category": "business"}},
        {"intake_id": "INT-ABCDEF123458", "request_id": "RID-E2E-TEST",
         "contact_email": "e2e@noetfield.com", "vector": "onchain-project",
         "metadata": {"form_id": "nfCapitalIntake", "initiative": "noetfield"}},
    ]
    async def run():
        db = AsyncMock()
        db.fetch.return_value = rows
        with patch("noetfield_governance.corporate_revenue_ops.asyncpg.connect",
                   new_callable=AsyncMock, return_value=db), \
             patch("noetfield_governance.corporate_revenue_ops.schema",
                   new_callable=AsyncMock), \
             patch("noetfield_governance.corporate_revenue_ops.import_intake",
                   new_callable=AsyncMock,
                   return_value={"deal": {"id": str(uuid4())}}) as imported:
            preview = await recover_intakes(object(), limit=20)
            assert preview["eligible"] == 2 and preview["imported"] == 0
            assert preview["excluded_or_invalid"] == 1
            assert imported.await_count == 0
            executed = await recover_intakes(object(), execute=True, limit=20)
            assert executed["mode"] == "EXECUTE"
            assert executed["imported"] == 2 and executed["failed"] == 0
            assert imported.await_count == 2
            assert {c.kwargs["intake_id"] for c in imported.await_args_list} == {
                "INT-ABCDEF123456", "INT-ABCDEF123457"
            }
            assert imported.await_args_list[0].kwargs["offer"] == "rwa_technical_sprint"
            assert imported.await_args_list[1].kwargs["offer"] == "business_automation"
            assert not executed["outreach_sent"] and not executed["payment_claimed"]
    # database URL extraction should be pure; mock the canonical URL only in this test.
    with patch("noetfield_governance.corporate_revenue_ops._database_url",
               return_value="postgresql://unused"):
        asyncio.run(run())


def test_recovery_rejects_unbounded_scans():
    async def run():
        with pytest.raises(Exception, match="INVALID_BACKFILL_LIMIT"):
            await recover_intakes(object(), limit=0)
    asyncio.run(run())


def test_ops_endpoints_require_private_operator_auth():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),
                               base_url="http://test") as client:
            plan = await client.get("/api/corporate-crm/operations/plan")
            recover = await client.post("/api/corporate-crm/operations/recover-intakes",
                                        json={"execute": True, "limit": 20})
            assert plan.status_code in (403, 503)
            assert recover.status_code in (403, 503)
        planned = {"schema": "noetfield.corporate-revenue-ops.v1",
                   "actions": [], "external_outreach_sent": False}
        preview = {"mode": "PREVIEW", "eligible": 0, "imported": 0}
        with patch("noetfield_governance.api._require_connect_desk_operator",
                   return_value=None), \
             patch("noetfield_governance.corporate_revenue_ops.revenue_plan",
                   new_callable=AsyncMock, return_value=planned) as plan_call, \
             patch("noetfield_governance.corporate_revenue_ops.recover_intakes",
                   new_callable=AsyncMock, return_value=preview) as recover_call:
            async with AsyncClient(transport=ASGITransport(app=app),
                                   base_url="http://test") as client:
                okay = await client.get("/api/corporate-crm/operations/plan")
                also = await client.post("/api/corporate-crm/operations/recover-intakes",
                                         json={"limit": 20})
                assert okay.status_code == 200
                assert also.status_code == 200
                assert plan_call.await_count == 1
                assert recover_call.await_args.kwargs["execute"] is False
    asyncio.run(run())


def test_ui_has_real_source_controls_and_no_fake_execution_claims():
    from pathlib import Path
    html = (Path(__file__).resolve().parents[2] /
            "services/governance/noetfield_governance/private_corporate_crm.html").read_text()
    assert 'id="ops-recover-preview"' in html
    assert 'id="ops-recover-apply"' in html
    assert 'id="ops-queue"' in html
    assert "/api/corporate-crm/operations/plan" in html
    assert "Draft copied. It has not been sent" in html
    assert "Verified Checkout is not the same as bank settlement" in html
