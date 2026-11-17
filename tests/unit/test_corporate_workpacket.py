"""P2: signed real cash, idempotent WorkPacket and verified customer acceptance."""
from __future__ import annotations
import asyncio
import hashlib
import hmac
import json
from unittest.mock import AsyncMock,patch
from uuid import uuid4

import pytest
from httpx import ASGITransport,AsyncClient
from noetfield_governance.api import app
from noetfield_governance.corporate_workpacket import (
  WorkPacketError,validate_paid_case,verify_signed_result,
  _dispatch_config,dispatch_paid_workpacket,
  check_accepted_delivery,
)


def _case(*,stage="PAYMENT_CONFIRMED",reversed=False,amount=47500,
          source="INT-ABCDEF123456",other_source=None):
    offer="rwa_technical_sprint"
    return {
      "source_intake_id":source, "offer":offer,
      "commercial":{
        "stage":stage,"offer":offer,"scope_ref":"SOW-RWA-001",
        "acceptance_evidence":"https://docs.noetfield.com/sow/signed",
        "payment_session_id":"cs_live_123456789",
        "payment_event_id":"evt_123456789",
      },
      "payment":{
        "event_id":"evt_123456789","session_id":"cs_live_123456789",
        "payment_link_id":"plink_1UbG9CJ03eJkL57JNNK0P3cY",
        "amount_minor":amount,"currency":"usd","livemode":True,
        "reversed":reversed,"bound_at":"2026-11-17T00:00:00Z",
        "source_intake_id":other_source or source,
      },
    }


def test_paid_gate_requires_original_accepted_scope_and_exact_live_bound_stripe():
    assert validate_paid_case(_case())["engine"]=="RWA_CLINIC"
    variations=[
      _case(stage="QUALIFY"),_case(reversed=True),_case(amount=2),
      _case(other_source="INT-XBCDEF123456"),
    ]
    bad=_case();bad["payment"]["bound_at"]=None;variations.append(bad)
    bad=_case();bad["payment"]["payment_link_id"]="plink_other";variations.append(bad)
    bad=_case();bad["commercial"]["acceptance_evidence"]=None;variations.append(bad)
    bad=_case();bad["payment"]["livemode"]=False;variations.append(bad)
    for record in variations:
        with pytest.raises(WorkPacketError):
            validate_paid_case(record)


def test_independent_verifier_signature_required_and_replay_event_id_bounded(monkeypatch):
    secret="verifier-secret-with-at-least-32-characters-2026"
    monkeypatch.setenv("CORPORATE_WORKPACKET_VERIFIER_SECRET",secret)
    event={
      "provider_event_id":"runway:proof-123456789",
      "status":"VERIFIED","source_intake_id":"INT-ABCDEF123456",
      "engine":"RWA_CLINIC","external_workpacket_id":"wp_external_123",
      "workpacket_id":str(uuid4()),
      "artifact_url":"https://docs.noetfield.com/verified/deliverable",
      "verifier_receipt_url":"https://docs.noetfield.com/receipts/verified",
      "cost_minor":12,
    }
    raw=json.dumps(event,separators=(",",":")).encode()
    signature="sha256="+hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest()
    assert verify_signed_result(raw,signature)==event
    for badsig in ("","sha256="+"0"*64,"Bearer "+secret):
        with pytest.raises(WorkPacketError):
            verify_signed_result(raw,badsig)
    # A signed status alone is not enough: verified artifact and numeric cost required.
    event.pop("cost_minor")
    alt=json.dumps(event).encode()
    sig="sha256="+hmac.new(secret.encode(),alt,hashlib.sha256).hexdigest()
    with pytest.raises(WorkPacketError,match="VERIFIED_COST"):
        verify_signed_result(alt,sig)


def test_no_unconfigured_provider_dispatch_claims_even_when_case_paid():
    async def run():
        candidate={"workpacket_id":str(uuid4()),"engine":"COMPANY_OS",
                   "source_intake_id":"INT-ABCDEF123456",
                   "state":"READY","created":True,"deal_id":str(uuid4())}
        with patch("noetfield_governance.corporate_workpacket.admit_paid_workpacket",
                   new_callable=AsyncMock,return_value=candidate),\
             patch("noetfield_governance.corporate_workpacket._dispatch_config",
                   return_value=None):
            result=await dispatch_paid_workpacket(object(),deal_id=candidate["deal_id"])
        assert result["state"]=="READY"
        assert result["dispatch_state"]=="PROVIDER_CONTRACT_NOT_CONFIGURED"
        assert not result["provider_acknowledged"]
    asyncio.run(run())


def test_delivery_requires_independent_verifier_and_buyer_acceptance():
    async def run():
        db=AsyncMock()
        db.fetchrow.return_value=None
        with patch("noetfield_governance.corporate_workpacket.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),\
             patch("noetfield_governance.corporate_workpacket.prepare_workpackets",
                   new_callable=AsyncMock),\
             patch("noetfield_governance.corporate_workpacket._database_url",
                   return_value="postgresql://unused"):
            with pytest.raises(WorkPacketError,match="INDEPENDENT_VERIFIER_AND_CUSTOMER"):
                await check_accepted_delivery(object(),deal_id=str(uuid4()),
                   delivery_evidence="https://docs.noetfield.com/report",
                   acceptance_url="")
    asyncio.run(run())


def test_new_workpacket_api_denies_guests_including_unsigned_verifier_callback():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            invalid=str(uuid4())
            assert (await client.post("/api/corporate-crm/workpackets/admit",
                json={"deal_id":invalid})).status_code in (403,503)
            assert (await client.post("/api/corporate-crm/workpackets/dispatch",
                json={"deal_id":invalid})).status_code in (403,503)
            assert (await client.get("/api/corporate-crm/workpackets/"+invalid)).status_code in (403,503)
            assert (await client.post("/api/corporate-crm/workpackets/verifier-result",
                json={"status":"VERIFIED"})).status_code==401
            assert (await client.post("/api/corporate-crm/customer/accept",
                json={"deal_id":invalid})).status_code in (401,403,503)
    asyncio.run(run())


def test_sales_crm_delivery_flow_calls_independent_evidence_gate():
    from inspect import getsource
    from pathlib import Path
    from noetfield_governance.corporate_crm import commercial_step
    src=getsource(commercial_step)
    assert "if action==\"deliver\"" in src
    assert "check_accepted_delivery(" in src
    root=Path(__file__).resolve().parents[2]
    crm=(root/"services/governance/noetfield_governance/private_corporate_crm.html").read_text()
    portal=(root/"services/governance/noetfield_governance/private_customer_portal.html").read_text()
    assert "Admit paid WorkPacket" in crm
    assert "independent verifier" in crm
    assert "Accept independently verified work" in portal
    assert "/api/corporate-crm/customer/accept" in portal


def test_production_company_os_receiver_only_allowlisted_exact_route(monkeypatch):
    secret="real-provider-route-private-secret-at-least-32-characters"
    monkeypatch.setenv("CORPORATE_WORKPACKET_DISPATCH_TOKEN",secret)
    production="https://business-os-core-production.up.railway.app/api/internal/commercial/workpackets"
    monkeypatch.setenv("CORPORATE_COMPANY_OS_WORKPACKET_URL",production)
    assert _dispatch_config("COMPANY_OS")== (production,secret)
    for candidate in [
        "https://company-os-staging-staging.up.railway.app/api/internal/commercial/workpackets",
        production+"/evil",
        "http://business-os-core-production.up.railway.app/api/internal/commercial/workpackets",
        "https://business-os-core-production.up.railway.app/api/internal/commercial/workpackets?redirect=1",
        "https://business-os-core-production.up.railway.app.evil.org/api/internal/commercial/workpackets",
    ]:
        monkeypatch.setenv("CORPORATE_COMPANY_OS_WORKPACKET_URL",candidate)
        assert _dispatch_config("COMPANY_OS") is None


def test_independent_draft_verifier_is_noop_without_provider_configuration(monkeypatch):
    from noetfield_governance.corporate_workpacket import verify_company_os_draft
    monkeypatch.delenv("CORPORATE_VERIFIER_INVOKE_TOKEN",raising=False)
    async def exercise():
        with patch("noetfield_governance.corporate_workpacket.asyncpg.connect",
                   new_callable=AsyncMock) as connect:
            result=await verify_company_os_draft(object(),deal_id=str(uuid4()))
            assert result["state"]=="VERIFIER_NOT_CONFIGURED"
            assert not result["independently_verified_delivery"]
            connect.assert_not_awaited()
    asyncio.run(exercise())


def test_independent_verifier_only_accepts_real_paid_draft_callback(monkeypatch):
    from noetfield_governance.corporate_workpacket import verify_company_os_draft
    from httpx import Response,Request
    secret="private-verifier-invocation-token-with-40-characters"
    monkeypatch.setenv("CORPORATE_VERIFIER_INVOKE_TOKEN",secret)
    deal_id=uuid4();platform_id=uuid4()
    raw={"id":platform_id,"deal_id":deal_id,"engine":"COMPANY_OS","state":"ACKNOWLEDGED",
         "source_intake_id":"INT-ABCDEF123456","payment_event_id":"evt_live_123456789",
         "external_workpacket_id":"cwp_0123456789abcdef0123456789abcdef"}
    db=AsyncMock()
    db.fetchrow.return_value=raw
    paid={"source_intake_id":raw["source_intake_id"],"payment_event_id":raw["payment_event_id"]}
    response={
        "schema":"noetfield.commercial-draft-verified.v1",
        "state":"RUNNING","source_workpacket_id":raw["external_workpacket_id"],
        "callback_acknowledged":True,"draft_integrity_passed":True,
        "product_delivered":False,"customer_accepted":False,
        "verifier_receipt_url":"https://verify.noetfield.com/api/internal/commercial/receipts/"+raw["external_workpacket_id"]
    }
    sent=[]
    class FakeClient:
        def __init__(self,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,url,*,json,headers):
            sent.append((url,json,headers))
            return Response(200,json=response,request=Request("POST",url))
    async def exercise():
        with patch("noetfield_governance.corporate_workpacket._database_url",
                   return_value="postgresql://unused"),\
             patch("noetfield_governance.corporate_workpacket.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),\
             patch("noetfield_governance.corporate_workpacket.prepare_workpackets",
                   new_callable=AsyncMock),\
             patch("noetfield_governance.corporate_workpacket._paid_row",
                   new_callable=AsyncMock,return_value={}),\
             patch("noetfield_governance.corporate_workpacket.validate_paid_case",
                   return_value=paid),\
             patch("noetfield_governance.corporate_workpacket.httpx.AsyncClient",
                   FakeClient):
            result=await verify_company_os_draft(object(),deal_id=str(deal_id))
            assert result["state"]=="DRAFT_INDEPENDENTLY_ATTESTED"
            assert result["independently_verified_draft"]
            assert not result["independently_verified_delivery"]
            assert not result["customer_acceptance"]
    asyncio.run(exercise())
    assert len(sent)==1
    assert sent[0][1]["payment_event_id"]==raw["payment_event_id"]
    assert sent[0][1]["platform_workpacket_id"]==str(platform_id)
    assert sent[0][2]["Authorization"]=="Bearer "+secret


def test_independent_verifier_ui_and_api_deny_guest():
    async def exercise():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            r=await client.post("/api/corporate-crm/workpackets/verify-draft",
                json={"deal_id":str(uuid4())})
            assert r.status_code in (403,503)
    asyncio.run(exercise())
    from pathlib import Path
    doc=(Path(__file__).resolve().parents[2]/
        "services/governance/noetfield_governance/private_corporate_crm.html").read_text()
    assert "Independent draft verification" in doc
    assert "final customer delivery: NOT VERIFIED" in doc
