"""Noetfield-only corporate CRM: privacy, dedupe, evidence and real API contracts."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app
from noetfield_governance.corporate_crm import (
    CorporateCRMError, KIND, OFFER, STAGE, normalize_account,
    validate_intake, source_url, date_only, uuid_text,
)


def test_corporate_segments_do_not_contain_web3_fieldwork_projects():
    assert "asset_originator" in KIND and "buyer" in KIND
    assert "rwa_technical_sprint" in OFFER and "ai_sales_os_pilot" in OFFER
    assert "SIGNED" in STAGE and "RETAINED" in STAGE
    assert "ARQANT" not in OFFER and "BuildRelay" not in OFFER


def test_deduplicate_organization_case_and_whitespace():
    assert normalize_account("  Acme   Capital  ") == "acme capital"
    assert normalize_account("ACME Capital") == "acme capital"
    with pytest.raises(CorporateCRMError,match="INVALID_ACCOUNT_NAME"):
        normalize_account("  ")


def test_validates_https_source_and_next_action_dates():
    assert source_url("https://acme.example.org/about")=="https://acme.example.org/about"
    assert date_only("2026-12-01").isoformat()=="2026-12-01"
    assert uuid_text(str(uuid4()),"ACCOUNT_ID")
    for bad in ("http://acme.example.org","javascript:alert(1)","https://admin:pass@acme.example.org"):
        with pytest.raises(CorporateCRMError):
            source_url(bad)
    with pytest.raises(CorporateCRMError,match="INVALID_NEXT_DATE"):
        date_only("tomorrow")


def fake_intake(*,initiative="",kind="lead",vector="onchain-project",
                email="buyer@company.org",rid="RID-BUYER-12345"):
    return {"request_id":rid,"contact_email":email,"vector":vector,
            "metadata":{"initiative":initiative,"intake_kind":kind}}


def test_rejects_foreign_venture_and_synthetic_customer_imports():
    for initiative in ("signalforge","buildrelay","trustfield","portfolio"):
        with pytest.raises(CorporateCRMError,match="CROSS_VENTURE_IMPORT"):
            validate_intake(fake_intake(initiative=initiative))
    for record in (fake_intake(kind="test"), fake_intake(email="e2e@noetfield.com"),
                   fake_intake(rid="RID-E2E-123456")):
        with pytest.raises(CorporateCRMError,match="SYNTHETIC"):
            validate_intake(record)
    with pytest.raises(CorporateCRMError,match="NON_CORPORATE_SOURCE"):
        validate_intake(fake_intake(vector="fieldwork-outreach"))
    with pytest.raises(CorporateCRMError,match="SOURCE_INTAKE_NOT_FOUND"):
        validate_intake(None)
    validate_intake(fake_intake())
    validate_intake(fake_intake(initiative="noetfield",vector="external-opportunities"))


def test_api_does_not_expose_private_account_people_or_deals_unauthenticated():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            board=await client.get("/api/corporate-crm/board")
            assert board.status_code in (403,503)
            account=await client.post("/api/corporate-crm/accounts",json={
                "name":"Sensitive Commercial Buyer","owner":"Sales owner",
                "kind":"buyer","sector":"financial_services",
            })
            assert account.status_code in (403,503)
            new=await client.post("/api/corporate-crm/import-intake",json={
                "intake_id":"INT-ABCDEF123456","offer":"rwa_technical_sprint",
                "owner":"Revenue owner","next_action":"Qualify mandate",
            })
            assert new.status_code in (403,503)
    asyncio.run(run())


def test_authenticated_board_and_source_import_are_real_operations_not_fixtures():
    async def run():
        fixture={"schema":"noetfield.corporate-crm.v1",
                 "scope":"NOETFIELD_CORPORATE_ONLY",
                 "accounts":[],"people":[],"deals":[],"total_deals":0,
                 "metrics":{"open":0,"due":0,"paid_verified_by_currency_minor":{}},
                 "fieldwork_contact_data_included":False}
        imported={"imported_from":"INT-ABCDEF123456",
                  "account":{"id":str(uuid4()),"name":"Acme Capital"},
                  "deal":{"id":str(uuid4()),"stage":"NEW"},"outreach_sent":False}
        with patch("noetfield_governance.api._require_connect_desk_operator",return_value=None),patch(
            "noetfield_governance.corporate_crm.dashboard",new_callable=AsyncMock,return_value=fixture
        ) as board_call,patch(
            "noetfield_governance.corporate_crm.import_intake",
            new_callable=AsyncMock,return_value=imported
        ) as import_call:
            async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
                board=await client.get("/api/corporate-crm/board")
                lead=await client.post("/api/corporate-crm/import-intake",json={
                    "intake_id":"INT-ABCDEF123456","offer":"rwa_technical_sprint",
                    "owner":"Revenue owner","next_action":"Review asset mandate",
                    "currency":"usd",
                })
        assert board.status_code==200 and board.json()["fieldwork_contact_data_included"] is False
        assert lead.status_code==200 and lead.json()["outreach_sent"] is False
        assert board_call.await_count==1
        assert import_call.await_args.kwargs["intake_id"]=="INT-ABCDEF123456"
    asyncio.run(run())


def test_corporate_workspace_is_private_noindex_shell_only():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            response=await client.get("/api/corporate-crm/app")
        assert response.status_code==200
        assert "noindex" in response.headers["x-robots-tag"]
        assert "no-store" in response.headers["cache-control"]
        body=response.text
        assert "Corporate CRM" in body
        assert "api/opportunities/desk/session" in body
        assert "api/corporate-crm/board" in body
        assert "Fieldwork's Web3 network" in body
        assert "SYNTHETIC LEAD" not in body
        assert "PRIVATE_CONTACTS" not in body
    asyncio.run(run())


def test_auto_import_only_noetfield_inbound_not_portfolio_web3():
    from noetfield_governance.corporate_crm import inbound_offer
    def record(vector,meta,**kwargs):
        return SimpleNamespace(vector=vector,metadata=meta,
                    request_id=kwargs.get("rid","RID-CUSTOMER-123456"),
                    contact_email=kwargs.get("email","real@buyer.example.org"))
    rwa=record("onchain-project",{"form_id":"nfCapitalIntake"})
    assert inbound_offer(rwa)==("rwa_technical_sprint","usd",95000)
    crm=record("external-opportunities",{"form_id":"nfConnectWizard",
                          "initiative":"noetfield","category":"business"})
    assert inbound_offer(crm)==("business_automation","cad",0)
    partner=record("external-opportunities",{"form_id":"nfConnectWizard",
                          "initiative":"noetfield","category":"partnership"})
    assert inbound_offer(partner)==("strategic_partnership","cad",0)
    for invalid in (
        record("external-opportunities",{"form_id":"nfConnectWizard",
                       "initiative":"buildrelay","category":"business"}),
        record("external-opportunities",{"form_id":"nfConnectWizard",
                       "initiative":"portfolio","category":"business"}),
        record("onchain-project",{"form_id":"nfCapitalIntake","intake_kind":"test"}),
        record("web-intake",{"form_id":"nfCapitalIntake"}),
        record("external-opportunities",{"form_id":"nfConnectWizard",
                       "initiative":"noetfield","category":"people"}),
        record("onchain-project",{"form_id":"nfCapitalIntake"},email="e2e@noetfield.com"),
    ):
        assert inbound_offer(invalid) is None


def test_auto_import_uses_canonical_intake_and_produces_no_outreach():
    from noetfield_governance.corporate_crm import auto_import_inbound
    record=SimpleNamespace(intake_id="INT-ABCDEF123456",vector="onchain-project",
            metadata={"form_id":"nfCapitalIntake"},request_id="RID-REAL-123456",
            contact_email="buyer@realcompany.org")
    imported={"imported_from":"INT-ABCDEF123456","deal":{"id":str(uuid4())}}
    async def run():
        with patch("noetfield_governance.corporate_crm.import_intake",
                   new_callable=AsyncMock,return_value=imported) as worker:
            result=await auto_import_inbound(object(),record)
            assert result["imported"] and result["outreach_sent"] is False
            assert result["payment_verified"] is False
            assert worker.await_args.kwargs["intake_id"]=="INT-ABCDEF123456"
            assert worker.await_args.kwargs["offer"]=="rwa_technical_sprint"
    asyncio.run(run())


def test_commercial_step_private_and_cookie_session_guarded():
    async def run():
        deal_id=str(uuid4())
        payload={"action":"scope","expected_revision":1,
                 "scope_ref":"SOW-RWA-2026-001",
                 "acceptance_evidence":"https://docs.noetfield.com/signed/sow-001"}
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            denied=await client.post("/api/corporate-crm/deals/"+deal_id+"/commercial",json=payload)
        assert denied.status_code in (403,503)
        with patch("noetfield_governance.api._require_connect_desk_operator",return_value=None),patch(
            "noetfield_governance.corporate_crm.commercial_step",
            new_callable=AsyncMock,return_value={
                "intake_id":"INT-ABCDEF123456","stage":"SCOPE_ACCEPTED",
                "revision":2,"approved_checkout_url":"https://buy.stripe.com/approved",
            }
        ) as operation:
            async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
                authorized=await client.post("/api/corporate-crm/deals/"+deal_id+"/commercial",json=payload)
            assert authorized.status_code==200
            assert authorized.json()["stage"]=="SCOPE_ACCEPTED"
            assert operation.await_args.kwargs["deal_id"]==deal_id
            assert operation.await_args.kwargs["expected_revision"]==1
    asyncio.run(run())


def test_crm_source_guard_rejects_placeholder_website_and_has_identity_validation():
    for address in ("https://localhost/admin","https://127.0.0.1/internal","https://example.com/stub"):
        with pytest.raises(CorporateCRMError):
            source_url(address)
    from inspect import getsource
    from noetfield_governance.corporate_crm import deal_create
    source=getsource(deal_create)
    assert "SOURCE_ACCOUNT_MISMATCH" in source
    assert "SOURCE_CONTACT_MISMATCH" in source


def test_corporate_crm_console_has_source_based_paid_flow_not_fake_cash():
    from pathlib import Path
    path=Path(__file__).resolve().parents[2]/"services/governance/noetfield_governance/private_corporate_crm.html"
    html=path.read_text(encoding="utf-8")
    assert 'id="commercial-step"' in html
    assert "/api/corporate-crm/deals/" in html
    assert "Record verified commercial step" in html
    assert "Approved-scope Stripe payment link" in html
    assert "No automatic outreach or billing" in html
    assert 'id="remember">' in html and 'id="remember" checked' not in html


def test_corporate_readiness_is_operator_only_and_never_claims_fake_data():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            denied=await client.get("/api/corporate-crm/health")
        assert denied.status_code in (403,503)
        with patch("noetfield_governance.api._require_connect_desk_operator",return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
                response=await client.get("/api/corporate-crm/health")
        assert response.status_code==200
        assert response.json()["workspace"]=="NOETFIELD_CORPORATE_ONLY"
        assert response.json()["fieldwork_data_shared"] is False
        assert isinstance(response.json()["database_ready"],bool)
        assert "accounts" not in response.text and "email" not in response.text
    asyncio.run(run())


def test_corporate_bootstrap_disabled_in_tests_never_connects_to_database(monkeypatch):
    from noetfield_governance.api import _bootstrap_corporate_crm
    monkeypatch.delenv("NOETFIELD_CORPORATE_CRM_BOOTSTRAP_ENABLED",raising=False)
    with patch("asyncpg.connect",new_callable=AsyncMock) as connection:
        asyncio.run(_bootstrap_corporate_crm())
        assert not connection.await_count
        assert app.state.corporate_crm_ready is False
