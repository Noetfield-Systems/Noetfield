"""Native BIJAN preparations are CRM-specific, private and evidence honest."""
from __future__ import annotations
import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from noetfield_governance.api import app
from noetfield_governance.corporate_bijan import compile_bijan_corporate_brief

DEAL_ID=str(uuid4())
ACCOUNT_ID=str(uuid4())

def sample(stage="DISCOVERY"):
    return {
      "source":"NOETFIELD_CORPORATE_CRM_ONLY",
      "deal":{"id":DEAL_ID,"account_id":ACCOUNT_ID,"account_name":"Original Corporate Buyer",
        "contact_name":"Client Delegate","contact_email":"private@example.org",
        "stage":stage,"offer":"business_automation","owner":"Corporate Team",
        "next_action":"Prepare relevant proof","summary":"Operator noted a process problem",
        "source_intake_id":"INT-ABCDEF123456","accepted_scope_url":""},
      "activity":[{"kind":"REPLY_REPORTED","created_at":"2026-11-21T20:00:00Z",
                   "source_status":"OPERATOR_REPORTED","evidence_url":"https://example.org/activity"}],
      "commercial_case":{"stage":"NOT_OPEN","acceptance_evidence":None}
    }

def test_native_corporate_brief_uses_exact_original_crm_and_no_fieldwork():
    x=compile_bijan_corporate_brief(sample(),as_of="2026-11-22T00:00:00Z")
    assert x["scope"]["crm"]=="NOETFIELD_CORPORATE_ONLY"
    assert x["scope"]["account_id"]==ACCOUNT_ID
    assert x["next_best_action"]=="PREPARE_ACCOUNT_SPECIFIC_DISCOVERY_BRIEF"
    assert x["no_fieldwork_identity_inherited"] is True
    assert x["verified_customer_preferences"]==[]
    assert x["recent_operator_activities"][0]["provider_attested"] is False
    assert x["verified_settled_cash_minor"] is None
    assert "private@example.org" not in str(x)
    assert x["checkout_or_payment_performed"] is False

def test_lost_deal_is_suppressed_and_no_outreach():
    x=compile_bijan_corporate_brief(sample("LOST"))
    assert x["next_best_action"]=="NO_FURTHER_OUTREACH_WITHOUT_NEW_AUTHORIZED_CONTEXT"
    assert x["communication_authorized_by_this_output"] is False

def test_scope_stage_changes_preparation_without_claiming_payment():
    x=compile_bijan_corporate_brief(sample("IN_DELIVERY"))
    assert x["next_best_action"]=="PREPARE_DELIVERY_ACCEPTANCE_AND_NEXT_CLIENT_SERVICE"
    assert x["verified_settled_cash_minor"] is None

def test_foreign_crm_data_rejected():
    bad=sample()
    bad["source"]="FIELDWORK_SOURCE_NETWORK"
    with pytest.raises(ValueError,match="NATIVE_CRM_SOURCE_REQUIRED"):
        compile_bijan_corporate_brief(bad)

def test_missing_native_deal_rejected():
    with pytest.raises(ValueError,match="ORIGINAL_DEAL_REQUIRED"):
        compile_bijan_corporate_brief({"source":"NOETFIELD_CORPORATE_CRM_ONLY"})

def test_private_route_denies_anonymous_requests():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
            r=await c.get("/api/corporate-crm/bijan/brief/"+DEAL_ID)
            assert r.status_code in (403,503)
    asyncio.run(run())

def test_authorized_route_uses_original_native_reader_only():
    async def run():
        result=compile_bijan_corporate_brief(sample())
        with patch("noetfield_governance.api._require_connect_desk_operator",return_value=None),patch(
            "noetfield_governance.corporate_bijan.native_corporate_bijan_brief",
            new_callable=AsyncMock,return_value=result
        ) as original_reader:
            async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
                r=await c.get("/api/corporate-crm/bijan/brief/"+DEAL_ID)
        assert r.status_code==200
        assert r.json()["scope"]["crm"]=="NOETFIELD_CORPORATE_ONLY"
        assert original_reader.await_args.kwargs["deal_id"]==DEAL_ID
    asyncio.run(run())
