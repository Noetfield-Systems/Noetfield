"""Real paid RWA Clinic invocation must use canonical external nine-gate API."""
from __future__ import annotations
import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport,AsyncClient,Response,Request
from noetfield_governance.api import app
from noetfield_governance.corporate_rwa_execution import (
  CLINIC_CASE_ENDPOINT,_case_bytes,_response_case_id,_genuine_clinic_verdict,
  submit_paid_native_clinic_case,
)
from noetfield_governance.corporate_workpacket import WorkPacketError


def case():
    return {
     "version":"rwa-readiness.v3",
     "case_context":{
        "jurisdiction":"Canada / BC",
        "issuer":"Verified Asset Sponsor Inc.",
        "asset_value":"CAD 2,400,000",
        "target_investors":"Qualified investors",
        "proposed_structure":"Proposed SPV secured loan"
     },
     "asset_existence":{"loan_agreement_status":"SUBMITTED"},
     "ownership":{"spv_lifecycle":"FORMATION"},
     "custody":{"custody_model":"LAW_FIRM_HOLD"}
    }


def test_native_clinic_case_requires_actual_scope_fields_never_synthetic():
    assert _case_bytes(case()).startswith(b"{")
    assert "scan.noetfield.com/v1/rwa/cases" in CLINIC_CASE_ENDPOINT
    for bad in [
      {"version":"rwa-readiness.v3"},
      {**case(),"case_context":{"jurisdiction":"Canada"}},
      {**case(),"training_flag":"DEMO-workpacket"},
      {**case(),"contact_email":"buyer@fake.invalid"},
      {**case(),"synthetic":True},
    ]:
        with pytest.raises(WorkPacketError):
            _case_bytes(bad)


def test_provider_case_receipt_requires_real_case_id_and_server_verdict():
    assert _response_case_id({"case":{"id":"rwa_case_20261117a"}})=="rwa_case_20261117a"
    assert _response_case_id({"ok":True}) is None
    assert _genuine_clinic_verdict({"clinical_verdict":{
       "status":"NO_GO","tokenization_recommendation":"DO_NOT_TOKENIZE"
    }})
    assert not _genuine_clinic_verdict({"clinical_verdict":{"status":"GO"}})


def test_no_rwa_clinic_payload_may_trigger_paid_execution_or_provider_call():
    async def run():
        with patch("noetfield_governance.corporate_rwa_execution.admit_paid_workpacket",
                   new_callable=AsyncMock) as admit, \
             patch("noetfield_governance.corporate_rwa_execution.httpx.AsyncClient") as provider:
            with pytest.raises(WorkPacketError):
                await submit_paid_native_clinic_case(object(),deal_id=str(uuid4()),
                    clinic_case={**case(),"unsafe":"DEMO-case"})
            admit.assert_not_awaited()
            provider.assert_not_called()
    asyncio.run(run())


def test_native_clinic_provider_ack_is_not_final_delivery_or_financial_approval():
    class Tx:
        async def __aenter__(self):return self
        async def __aexit__(self,*args):return False
    db=AsyncMock()
    db.transaction=lambda:Tx()
    identifier=uuid4()
    row={"id":identifier,"deal_id":uuid4(),"source_intake_id":"INT-ABCDEF123456",
         "payment_event_id":"evt_123456789","state":"READY"}
    db.fetchrow.side_effect=[row,None]
    accepted={"engine":"RWA_CLINIC","workpacket_id":str(identifier)}
    result={"ok":True,"case_id":"rwa_case_real_12345678",
       "clinical_verdict":{"status":"NO_GO",
                           "tokenization_recommendation":"DO_NOT_TOKENIZE"}}
    class Provider:
        async def __aenter__(self):return self
        async def __aexit__(self,*args):return False
        def __init__(self,**kwargs):pass
        async def post(self,url,*,content,headers):
            assert url==CLINIC_CASE_ENDPOINT
            assert b"DEMO" not in content
            return Response(201,json=result,request=Request("POST",url))
    async def run():
        with patch("noetfield_governance.corporate_rwa_execution.admit_paid_workpacket",
                   new_callable=AsyncMock,return_value=accepted), \
             patch("noetfield_governance.corporate_rwa_execution.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db), \
             patch("noetfield_governance.corporate_rwa_execution._database_url",
                   return_value="postgres://unused"), \
             patch("noetfield_governance.corporate_rwa_execution.prepare_clinic_submissions",
                   new_callable=AsyncMock), \
             patch("noetfield_governance.corporate_rwa_execution._paid_row",
                   new_callable=AsyncMock,return_value={}), \
             patch("noetfield_governance.corporate_rwa_execution.validate_paid_case",
                   return_value={"source_intake_id":row["source_intake_id"],
                                 "payment_event_id":row["payment_event_id"]}), \
             patch("noetfield_governance.corporate_rwa_execution.httpx.AsyncClient",Provider):
            result=await submit_paid_native_clinic_case(object(),
                  deal_id=str(row["deal_id"]),clinic_case=case())
            assert result["state"]=="PROVIDER_ACCEPTED"
            assert result["clinic_case_id"]=="rwa_case_real_12345678"
            assert result["actual_clinic_verdict_returned"]
            assert result["independently_verified_delivery"] is False
            assert result["customer_accepted"] is False
            assert result["second_scoring_engine_created"] is False
            assert db.execute.await_count>=2
    asyncio.run(run())


def test_native_rwa_execution_stays_private():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            assert (await client.post("/api/corporate-crm/workpackets/rwa/submit-case",
                json={"deal_id":str(uuid4()),"clinic_case":case()})).status_code in (403,503)
            assert (await client.get("/api/corporate-crm/workpackets/rwa/"+str(uuid4()))).status_code in (403,503)
    asyncio.run(run())


def test_private_ui_distinguishes_rwa_clinic_case_from_investment_or_final_delivery():
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    html=(root/"services/governance/noetfield_governance/private_corporate_crm.html").read_text()
    assert "Execute paid RWA Clinic v3 diagnosis" in html
    assert "/api/corporate-crm/workpackets/rwa/submit-case" in html
    assert "not an investment approval" in html
