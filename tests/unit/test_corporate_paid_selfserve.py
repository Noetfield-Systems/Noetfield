"""Real paid buyer self-service: strict Stripe, revocation and native RWA Clinic."""
from __future__ import annotations

import asyncio
import json
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import AsyncMock,patch
from uuid import uuid4

import pytest
from httpx import ASGITransport,AsyncClient

from noetfield_governance.api import app
from noetfield_governance.customer_portal import (
    CorporateCRMError,customer_email_hash,auto_grant_paid_original_customers,
    customer_submit_paid_native_rwa_case,
)

EXAMPLE_CONTEXT={"case_context":{
  "jurisdiction":"British Columbia, Canada",
  "issuer":"Example Asset Originator Inc.",
  "asset_value":"250000 CAD",
  "target_investors":"Qualified Canadian investors",
  "proposed_structure":"SPV-issued contractual units",
}}

def test_empty_stripe_intake_never_creates_any_customer_access():
    async def run():
        db=AsyncMock()
        db.fetch.return_value=[]
        with patch("noetfield_governance.customer_portal.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.customer_portal.ensure_customer_access_schema",
             new_callable=AsyncMock),patch(
             "noetfield_governance.customer_portal._database_url",
             return_value="postgresql://test"),patch(
             "noetfield_governance.corporate_workpacket._paid_row",
             new_callable=AsyncMock) as paid:
            outcome=await auto_grant_paid_original_customers(object())
        assert outcome["paid_cases_checked"]==0
        assert outcome["new_source_original_customer_memberships"]==0
        assert outcome["no_third_party_grants"] is True
        paid.assert_not_awaited()
        db.fetchrow.assert_not_awaited()
        query=db.fetch.await_args.args[0]
        for marker in ("e.livemode IS TRUE","e.reversed IS FALSE",
             "e.bound_at IS NOT NULL","acceptance_evidence",
             "payment_event_id","payment_session_id"):
            assert marker in query
    asyncio.run(run())


def test_payment_grants_only_original_customer_once_and_never_restores_revoked():
    from noetfield_governance.corporate_workpacket import validate_paid_case
    async def run():
        deal=uuid4()
        original={"contact_email":"ActualBuyer@Example.org"}
        db=AsyncMock()
        db.fetch.return_value=[{"id":deal}]
        db.fetchrow.return_value={"deal_id":deal}
        with patch("noetfield_governance.customer_portal.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.customer_portal.ensure_customer_access_schema",
             new_callable=AsyncMock),patch(
             "noetfield_governance.customer_portal._database_url",
             return_value="postgresql://test"),patch(
             "noetfield_governance.corporate_workpacket._paid_row",
             new_callable=AsyncMock,return_value=original) as paid,patch(
             "noetfield_governance.corporate_workpacket.validate_paid_case",
             return_value={"engine":"COMPANY_OS"}):
            result=await auto_grant_paid_original_customers(object())
        assert result["new_source_original_customer_memberships"]==1
        assert paid.await_count==1
        query=db.fetchrow.await_args.args[0]
        assert "ON CONFLICT(deal_id,email_hash) DO NOTHING" in query
        assert "DO UPDATE" not in query
        assert db.fetchrow.await_args.args[1]==deal
        assert db.fetchrow.await_args.args[2]==customer_email_hash("ActualBuyer@Example.org")
        assert "actualbuyer@example.org" not in json.dumps(result)
        assert result["revocations_restored"]==0
    asyncio.run(run())


def test_customer_rwa_submission_requires_active_deal_membership_before_native_job():
    async def run():
        deal=str(uuid4())
        identity={"email_hash":customer_email_hash("buyer@example.org"),
                  "provider_subject":"customer-supabase-uuid"}
        db=AsyncMock()
        db.fetchval.return_value=None
        with patch("noetfield_governance.customer_portal.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.customer_portal.ensure_customer_access_schema",
             new_callable=AsyncMock),patch(
             "noetfield_governance.customer_portal._database_url",
             return_value="postgresql://test"),patch(
             "noetfield_governance.corporate_rwa_execution.submit_paid_native_clinic_case",
             new_callable=AsyncMock) as native:
            with pytest.raises(CorporateCRMError,match="RWA_CUSTOMER_ACCESS_NOT_AUTHORIZED"):
                await customer_submit_paid_native_rwa_case(object(),deal_id=deal,
                    clinic_case=EXAMPLE_CONTEXT,identity=identity)
            native.assert_not_awaited()
        query=db.fetchval.await_args.args[0]
        assert "ca.email_hash=$2" in query
        assert "ca.active IS TRUE" in query
        assert "d.offer='rwa_technical_sprint'" in query
    asyncio.run(run())


def test_authorized_paid_original_buyer_invokes_canonical_native_clinic_unchanged():
    async def run():
        deal=str(uuid4())
        identity={"email_hash":customer_email_hash("buyer@example.org")}
        db=AsyncMock()
        db.fetchval.return_value=1
        accepted={"state":"PROVIDER_ACCEPTED","real_native_clinic_case":True,
                  "independently_verified_delivery":False}
        with patch("noetfield_governance.customer_portal.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.customer_portal.ensure_customer_access_schema",
             new_callable=AsyncMock),patch(
             "noetfield_governance.customer_portal._database_url",
             return_value="postgresql://test"),patch(
             "noetfield_governance.corporate_rwa_execution.submit_paid_native_clinic_case",
             new_callable=AsyncMock,return_value=accepted) as native:
            result=await customer_submit_paid_native_rwa_case(
                object(),deal_id=deal,clinic_case=EXAMPLE_CONTEXT,identity=identity)
            assert result==accepted
            assert native.await_args.kwargs["deal_id"]==deal
            assert native.await_args.kwargs["clinic_case"]==EXAMPLE_CONTEXT
    asyncio.run(run())


def test_customer_rwa_endpoint_is_auth_guarded_not_operator_key_guarded():
    async def run():
        deal=str(uuid4())
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
            guest=await c.post("/api/corporate-crm/customer/rwa/submit-case",
                json={"deal_id":deal,"clinic_case":EXAMPLE_CONTEXT})
            assert guest.status_code in (401,403,503)
        identity={"email_hash":customer_email_hash("buyer@example.org"),
                  "provider_subject":"verified"}
        with patch("noetfield_governance.customer_portal.authenticate_customer",
                   new_callable=AsyncMock,return_value=identity),patch(
             "noetfield_governance.customer_portal.customer_submit_paid_native_rwa_case",
             new_callable=AsyncMock,return_value={
               "state":"PROVIDER_ACCEPTED",
               "real_native_clinic_case":True}) as send:
            async with AsyncClient(transport=ASGITransport(app=app),
                                   base_url="http://test") as c:
                result=await c.post("/api/corporate-crm/customer/rwa/submit-case",
                 json={"deal_id":deal,"clinic_case":EXAMPLE_CONTEXT},
                 headers={"Authorization":"Bearer verified-token"})
                assert result.status_code==200
                assert result.json()["real_native_clinic_case"] is True
                assert send.await_args.kwargs["identity"]==identity
    asyncio.run(run())


def test_customer_case_input_is_own_access_scoped_without_browser_token_storage():
    html=(Path(__file__).resolve().parents[2]/
         "services/governance/noetfield_governance/private_customer_portal.html").read_text()
    assert 'data-rwa-case' in html
    assert 'x.payment_status==="PAID_LIVE"' in html
    assert "case_context:fields" in html
    assert "/api/corporate-crm/customer/rwa/submit-case" in html
    assert "real_native_clinic_case" in html
    assert "localStorage" not in html and "sessionStorage" not in html
    scripts=re.findall(r"<script>([\s\S]*?)</script>",html)
    assert len(scripts)==1
    with NamedTemporaryFile(mode="w",suffix=".js") as f:
        f.write(scripts[0]);f.flush()
        subprocess.run(["node","--check",f.name],check=True,capture_output=True,text=True)
