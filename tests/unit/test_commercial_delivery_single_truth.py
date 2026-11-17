"""Regression: legacy intake-level commercial route cannot bypass signed delivery."""
from __future__ import annotations
import asyncio
from unittest.mock import AsyncMock, patch
from noetfield_governance.commercial_pipeline import CommercialError,operate
from noetfield_governance.corporate_workpacket import WorkPacketError

INTAKE="INT-ABCDEF123456"
ARTIFACT="https://docs.noetfield.com/verified/artifact-123"
ACCEPTANCE="https://platform.noetfield.com/api/corporate-crm/customer/acceptance/00000000-0000-4000-8000-000000000001"

class Tx:
    async def __aenter__(self): return self
    async def __aexit__(self,*args): return False

def db_with_case(*,stage="IN_DELIVERY",reversed=False,receipt=True,
                 saved_delivery="",saved_acceptance=""):
    db=AsyncMock()
    db.transaction=lambda:Tx()
    commercial={
      "offer":"rwa_technical_sprint","stage":stage,"revision":3,
      "scope_ref":"SOW-RWA-0001",
      "acceptance_evidence":"https://docs.noetfield.com/sow/confirmed",
      "payment_session_id":"cs_live_123456789",
      "payment_event_id":"evt_live_12345",
      "delivery_evidence":saved_delivery,"customer_acceptance":saved_acceptance,
    }
    row={"intake_id":INTAKE,"request_id":"REQ-REAL-12345",
      "contact_email":"verified@example.org","vector":"enterprise",
      "metadata":{},"qualification_json":{"commercial_ops":commercial}}
    proof={"reversed":reversed,"livemode":True,"source_intake_id":INTAKE,
      "bound_at":"2026-11-17T03:00:00Z" if receipt else None,
      "event_id":"evt_live_12345"}
    db.fetchrow.side_effect=[row,proof]
    return db


def _exercise(action,db,proof=(ARTIFACT,ACCEPTANCE)):
    async def task():
        with patch("noetfield_governance.commercial_pipeline._database_url",
                    return_value="postgresql://unused"),\
             patch("noetfield_governance.commercial_pipeline.asyncpg.connect",
                    new_callable=AsyncMock,return_value=db) as connect,\
             patch("noetfield_governance.commercial_pipeline._prepare",new_callable=AsyncMock),\
             patch("noetfield_governance.intake_test.is_test_intake",return_value=False),\
             patch("noetfield_governance.corporate_workpacket.check_accepted_delivery_for_intake",
                   new_callable=AsyncMock,return_value=proof) as gate:
            result=await operate(object(),intake_id=INTAKE,action=action,
                       expected_revision=3,delivery_evidence=ARTIFACT,
                       acceptance_url=ACCEPTANCE)
            return result,connect,gate
    return asyncio.run(task())


def test_verified_signed_artifact_and_customer_acceptance_can_deliver():
    db=db_with_case()
    result,connect,gate=_exercise("deliver",db)
    assert result["stage"]=="DELIVERED"
    assert result["delivery_evidence"]==ARTIFACT
    assert result["customer_acceptance"]==ACCEPTANCE
    assert db.execute.await_count==1
    assert gate.await_count==1
    assert gate.await_args.kwargs["intake_id"]==INTAKE
    assert connect.await_count==1


def test_closed_delivery_rechecks_original_verified_artifact_and_payment():
    db=db_with_case(stage="DELIVERED",saved_delivery=ARTIFACT,
                   saved_acceptance=ACCEPTANCE)
    result,*_=_exercise("close",db)
    assert result["stage"]=="CLOSED"


def test_reversed_payment_stops_delivered_claim_even_with_signed_artifact():
    db=db_with_case(reversed=True)
    try:_exercise("deliver",db)
    except CommercialError as exc:assert "CURRENT_BOUND_LIVE_PAYMENT_REQUIRED" in str(exc)
    else:raise AssertionError("Reversed payment was allowed")
    db.execute.assert_not_awaited()


def test_existing_delivery_mismatch_cannot_be_closed():
    db=db_with_case(stage="DELIVERED",saved_delivery="https://unverified.example.org/copy",
                    saved_acceptance=ACCEPTANCE)
    try:_exercise("close",db)
    except CommercialError as exc:assert "RECORDED_DELIVERY_EVIDENCE_MISMATCH" in str(exc)
    else:raise AssertionError("Unverified historical delivery was allowed to close")
    db.execute.assert_not_awaited()


def test_missing_customer_verifier_evidence_fails_before_database_write():
    async def task():
        with patch("noetfield_governance.corporate_workpacket.check_accepted_delivery_for_intake",
                   new_callable=AsyncMock,side_effect=WorkPacketError("INDEPENDENT_VERIFIER_AND_CUSTOMER_ACCEPTANCE_REQUIRED")),\
             patch("noetfield_governance.commercial_pipeline.asyncpg.connect",
                   new_callable=AsyncMock) as connect:
            try:
                await operate(object(),intake_id=INTAKE,action="deliver",expected_revision=3,
                              delivery_evidence=ARTIFACT,acceptance_url=ACCEPTANCE)
            except CommercialError as exc:
                assert "INDEPENDENT_VERIFIER_AND_CUSTOMER_ACCEPTANCE_REQUIRED" in str(exc)
            else:raise AssertionError("Bypass to DELIVERED accepted")
            connect.assert_not_awaited()
    asyncio.run(task())
