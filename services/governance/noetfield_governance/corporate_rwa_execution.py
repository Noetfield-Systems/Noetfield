"""Paid Noetfield RWA Clinic v3 bridge to its actual canonical diagnostics API.

This is NOT a second scoring engine. Only the real Clinic server may evaluate
Gates 1-9 and derive Gate 10. Real paid origin + accepted SOW is required;
Clinic 201 means accepted case, not an independently verified deliverable.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from typing import Any
from urllib.parse import urlsplit

import asyncpg
import httpx

from noetfield_governance.commercial_pipeline import _database_url
from noetfield_governance.corporate_workpacket import (
  WorkPacketError,admit_paid_workpacket,prepare_workpackets,
  validate_paid_case,_paid_row,
)

CLINIC_CASE_ENDPOINT="https://scan.noetfield.com/v1/rwa/cases"
_VALID_ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{5,140}$")
_CASE_LIMIT=50_000


def _case_bytes(payload:Any)->bytes:
    if not isinstance(payload,dict) or not payload:
        raise WorkPacketError("NATIVE_RWA_V3_CASE_PAYLOAD_REQUIRED")
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,
       separators=(",",":"),allow_nan=False).encode("utf-8")
    if len(raw)>_CASE_LIMIT:
        raise WorkPacketError("RWA_CLINIC_CASE_PAYLOAD_TOO_LARGE")
    if any(flag in raw.upper() for flag in (
        b"DEMO-",b"MOCK-",b".INVALID",b'"SYNTHETIC":TRUE',
        b'"IS_TEST":TRUE'
    )):
        raise WorkPacketError("TRAINING_RWA_RECORDS_NOT_PERMITTED_FOR_PAID_EXECUTION")
    ctx=payload.get("case_context")
    if not isinstance(ctx,dict):
        raise WorkPacketError("CANONICAL_RWA_V3_CASE_CONTEXT_REQUIRED")
    for key in ("jurisdiction","issuer","asset_value","target_investors","proposed_structure"):
        if not isinstance(ctx.get(key),str) or len(ctx[key].strip())<2:
            raise WorkPacketError("RWA_CASE_CONTEXT_INCOMPLETE_"+key.upper())
    # Native Clinic owns nested evidence validation and 9+1 gate policy.
    # Do not invent a second local evidence schema that rejects genuine v3 cases.
    return raw


async def prepare_clinic_submissions(db:asyncpg.Connection)->None:
    await prepare_workpackets(db)
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_rwa_clinic_submissions (
        workpacket_id uuid PRIMARY KEY REFERENCES noetfield.corp_workpackets(id),
        case_sha256 text NOT NULL,
        case_payload_json jsonb,
        state text NOT NULL DEFAULT 'CLAIMED',
        clinic_case_id text,
        provider_status_code integer,
        provider_response_json jsonb,
        received_at timestamptz,
        created_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""ALTER TABLE noetfield.corp_rwa_clinic_submissions
        ADD COLUMN IF NOT EXISTS case_payload_json jsonb""")


def _response_case_id(data:dict[str,Any])->str|None:
    for item in (data,data.get("case"),data.get("result"),data.get("data"),data.get("created_case")):
        if not isinstance(item,dict):
            continue
        for key in ("case_id","id"):
            found=item.get(key)
            if isinstance(found,str) and _VALID_ID.fullmatch(found):
                return found
    return None


def _genuine_clinic_verdict(data:dict[str,Any])->bool:
    output=data.get("clinical_verdict") or data.get("verdict")
    if not isinstance(output,dict):
        return False
    gate_state=str(output.get("status") or "").upper()
    return gate_state in {"GO","CONDITIONAL","NO_GO"} and (
       output.get("tokenization_recommendation") in
       {"PROCEED","PROCEED_AFTER_REVIEW","DO_NOT_TOKENIZE"})


async def submit_paid_native_clinic_case(settings:object,*,deal_id:str,
                                         clinic_case:dict[str,Any])->dict[str,Any]:
    raw=_case_bytes(clinic_case)
    digest=hashlib.sha256(raw).hexdigest()
    admitted=await admit_paid_workpacket(settings,deal_id=deal_id)
    if admitted["engine"]!="RWA_CLINIC":
        raise WorkPacketError("PAID_RWA_CLINIC_SOW_REQUIRED")
    workpacket=uuid.UUID(admitted["workpacket_id"])
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_clinic_submissions(db)
        async with db.transaction():
            record=await db.fetchrow("""SELECT id,deal_id,source_intake_id,
                   payment_event_id,state FROM noetfield.corp_workpackets
                   WHERE id=$1 FOR UPDATE""",workpacket)
            paid=validate_paid_case(await _paid_row(db,record["deal_id"]))
            if (paid["source_intake_id"]!=record["source_intake_id"] or
                 paid["payment_event_id"]!=record["payment_event_id"]):
                raise WorkPacketError("RWA_PAID_SCOPE_CHANGED")
            prior=await db.fetchrow("""SELECT * FROM noetfield.corp_rwa_clinic_submissions
                     WHERE workpacket_id=$1 FOR UPDATE""",workpacket)
            if prior:
                if prior["case_sha256"]!=digest:
                    raise WorkPacketError("RWA_CLINIC_CASE_REPLAY_PAYLOAD_CONFLICT")
                return {"workpacket_id":str(workpacket),
                        "state":prior["state"],
                        "clinic_case_id":prior["clinic_case_id"],
                        "idempotent":True,
                        "provider_acknowledged":prior["state"]=="PROVIDER_ACCEPTED",
                        "independently_verified_delivery":False}
            await db.execute("""INSERT INTO noetfield.corp_rwa_clinic_submissions
                 (workpacket_id,case_sha256,case_payload_json)
                 VALUES($1,$2,$3::jsonb)""",workpacket,digest,raw.decode("utf-8"))
    finally:
        await db.close()
    status="SUBMISSION_UNCONFIRMED";case_id=None;upstream_status=None
    result:dict[str,Any]={}
    try:
        async with httpx.AsyncClient(timeout=25,follow_redirects=False) as client:
            response=await client.post(CLINIC_CASE_ENDPOINT,content=raw,
                         headers={"Content-Type":"application/json","Accept":"application/json"})
        upstream_status=response.status_code
        if response.status_code in (200,201,202):
            received=response.json()
            if isinstance(received,dict):
                result=received
                if received.get("ok") is not False:
                    case_id=_response_case_id(received)
                    if case_id:
                        status="PROVIDER_ACCEPTED"
    except (httpx.RequestError,ValueError,TypeError):
        status="SUBMISSION_UNCONFIRMED"
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_clinic_submissions(db)
        async with db.transaction():
            await db.execute("""UPDATE noetfield.corp_rwa_clinic_submissions
                SET state=$2,clinic_case_id=$3,provider_status_code=$4,
                    provider_response_json=$5::jsonb,received_at=now()
                WHERE workpacket_id=$1""",
                workpacket,status,case_id,upstream_status,
                _bounded_response_json(result) if result else None)
            if status=="PROVIDER_ACCEPTED":
                await db.execute("""UPDATE noetfield.corp_workpackets SET
                  state='ACKNOWLEDGED',external_workpacket_id=$2,
                  provider_receipt_url=NULL,last_error_code=NULL,updated_at=now()
                  WHERE id=$1 AND state='READY'""",workpacket,case_id)
    finally:
        await db.close()
    return {"workpacket_id":str(workpacket),
       "state":status,"provider_status_code":upstream_status,
       "clinic_case_id":case_id,"real_native_clinic_case":status=="PROVIDER_ACCEPTED",
       "actual_clinic_verdict_returned":bool(case_id and _genuine_clinic_verdict(result)),
       "independently_verified_delivery":False,"customer_accepted":False,
       "second_scoring_engine_created":False}


async def native_clinic_case_readback(settings:object,*,deal_id:str)->dict[str,Any]:
    try:
        identifier=uuid.UUID(deal_id)
    except (TypeError,ValueError) as exc:
        raise WorkPacketError("INVALID_DEAL_ID") from exc
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_clinic_submissions(db)
        row=await db.fetchrow("""SELECT s.state,s.clinic_case_id,s.provider_status_code,
            s.provider_response_json,s.case_sha256,w.id AS workpacket_id
            FROM noetfield.corp_workpackets w
            LEFT JOIN noetfield.corp_rwa_clinic_submissions s
              ON s.workpacket_id=w.id
            WHERE w.deal_id=$1 AND w.engine='RWA_CLINIC'""",identifier)
        if not row or not row["state"]:
            return {"state":"NOT_SUBMITTED","clinic_case_id":None,
                    "independently_verified_delivery":False}
        response=row["provider_response_json"]
        if isinstance(response,str):
            try:response=json.loads(response)
            except ValueError:response={}
        output=response if isinstance(response,dict) else {}
        return {"workpacket_id":str(row["workpacket_id"]),"state":row["state"],
                "clinic_case_id":row["clinic_case_id"],
                "case_sha256":row["case_sha256"],
                "provider_status_code":row["provider_status_code"],
                "clinical_verdict":output.get("clinical_verdict") or output.get("verdict"),
                "clinical_gates":output.get("gates"),
                "native_clinic_verdict":_genuine_clinic_verdict(output),
                "independently_verified_delivery":False,
                "token_issuance_or_investment_approval":False}
    finally:
        await db.close()


def _bounded_response_json(result: dict[str,Any]) -> str:
    """Preserve valid JSON, never truncate an external receipt mid-character."""
    raw=json.dumps(result,ensure_ascii=False,separators=(",",":"),allow_nan=False)
    if len(raw.encode("utf-8"))>80000:
        return json.dumps({"ok":False,"error":"PROVIDER_RESPONSE_EXCEEDS_STORAGE_LIMIT"})
    return raw


async def native_clinic_verifier_source(settings:object,*,workpacket_id:str)->dict[str,Any]:
    """Private service-to-service source payload for independent Clinic replay.

    No customer contacts or unbound source records are exposed. Real original
    payload plus provider outcome allow the separate Verifier to check both
    the evidence fingerprint and the nine actual Clinic gate responses.
    """
    try:
        wid=uuid.UUID(workpacket_id)
    except (TypeError,ValueError) as exc:
        raise WorkPacketError("INVALID_RWA_WORKPACKET_ID") from exc
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_clinic_submissions(db)
        row=await db.fetchrow("""SELECT w.id,w.deal_id,w.source_intake_id,
                w.scope_ref,w.payment_event_id,w.engine,w.state,
                s.case_sha256,s.case_payload_json,s.clinic_case_id,
                s.state AS submission_state,s.provider_response_json
             FROM noetfield.corp_workpackets w
             JOIN noetfield.corp_rwa_clinic_submissions s ON s.workpacket_id=w.id
             WHERE w.id=$1""",wid)
        if (not row or row["engine"]!="RWA_CLINIC"
                or row["state"] not in {"ACKNOWLEDGED","RUNNING","VERIFIED"}
                or row["submission_state"]!="PROVIDER_ACCEPTED"
                or not row["clinic_case_id"] or not row["case_payload_json"]):
            raise WorkPacketError("NATIVE_RWA_PROVIDER_ACK_AND_SOURCE_REQUIRED")
        info=validate_paid_case(await _paid_row(db,row["deal_id"]))
        if (info["payment_event_id"]!=row["payment_event_id"]
                or info["source_intake_id"]!=row["source_intake_id"]
                or info["scope_ref"]!=row["scope_ref"]):
            raise WorkPacketError("NATIVE_RWA_PAID_SOURCE_CHANGED")
        payload=row["case_payload_json"]
        if isinstance(payload,str):
            payload=json.loads(payload)
        provider=row["provider_response_json"]
        if isinstance(provider,str):
            provider=json.loads(provider)
        if not isinstance(provider,dict) or not isinstance(payload,dict):
            raise WorkPacketError("NATIVE_RWA_RESULT_INCOMPLETE")
        if (not _genuine_clinic_verdict(provider)
                or _response_case_id(provider)!=row["clinic_case_id"]
                or provider.get("schema_version")!="rwa-readiness.v3"):
            raise WorkPacketError("NATIVE_RWA_VERDICT_AND_SCHEMA_REQUIRED")
        digest=hashlib.sha256(_case_bytes(payload)).hexdigest()
        if digest!=row["case_sha256"]:
            raise WorkPacketError("NATIVE_RWA_ORIGINAL_PAYLOAD_HASH_MISMATCH")
        return {
            "schema":"noetfield.rwa-clinic-verifier-source.v1",
            "workpacket_id":str(row["id"]),
            "deal_id":str(row["deal_id"]),
            "source_intake_id":row["source_intake_id"],
            "scope_ref":row["scope_ref"],
            "payment_event_id":row["payment_event_id"],
            "engine":"RWA_CLINIC",
            "clinic_case_id":row["clinic_case_id"],
            "original_case_sha256":digest,
            "clinic_case":payload,
            "provider_outcome":provider,
            "independently_verified":False,
            "authenticated_customer_acceptance":False,
        }
    finally:
        await db.close()


async def customer_rwa_report(settings:object,*,deal_id:str,
                              identity:dict[str,str])->dict[str,Any]:
    """Only approved buyer with current paid case may read their verified report."""
    try:
        identifier=uuid.UUID(deal_id)
    except (TypeError,ValueError) as exc:
        raise WorkPacketError("INVALID_DEAL_ID") from exc
    from noetfield_governance.customer_portal import ensure_customer_access_schema
    db=await asyncpg.connect(_database_url(settings))
    try:
        await ensure_customer_access_schema(db)
        await prepare_clinic_submissions(db)
        row=await db.fetchrow("""SELECT w.id,w.deal_id,w.source_intake_id,
                w.state,w.scope_ref,w.payment_event_id,s.clinic_case_id,
                s.provider_response_json,s.state AS clinic_state
            FROM noetfield.corp_customer_access ca
            JOIN noetfield.corp_workpackets w ON w.deal_id=ca.deal_id
            JOIN noetfield.corp_rwa_clinic_submissions s ON s.workpacket_id=w.id
            WHERE ca.deal_id=$1 AND ca.email_hash=$2 AND ca.active=true
                 AND w.engine='RWA_CLINIC'""",
                 identifier,identity["email_hash"])
        if not row:
            raise WorkPacketError("CUSTOMER_MEMBERSHIP_OR_CLINIC_CASE_NOT_FOUND")
        info=validate_paid_case(await _paid_row(db,row["deal_id"]))
        if (info["source_intake_id"]!=row["source_intake_id"] or
            info["payment_event_id"]!=row["payment_event_id"]):
            raise WorkPacketError("CURRENT_SIGNED_LIVE_PAYMENT_REQUIRED")
        if row["clinic_state"]!="PROVIDER_ACCEPTED" or row["state"]!="VERIFIED":
            raise WorkPacketError("INDEPENDENT_RWA_CLINIC_VERDICT_NOT_READY")
        outcome=row["provider_response_json"]
        if isinstance(outcome,str):
            outcome=json.loads(outcome)
        if not isinstance(outcome,dict) or not _genuine_clinic_verdict(outcome):
            raise WorkPacketError("NATIVE_CLINIC_VERDICT_NOT_READABLE")
        return {
          "schema":"noetfield.rwa-client-readiness-report.v1",
          "status":"INDEPENDENTLY_VERIFIED_TECHNICAL_ASSESSMENT",
          "deal_id":str(row["deal_id"]),
          "case_id":row["clinic_case_id"],
          "scope_ref":row["scope_ref"],
          "source_intake_id":row["source_intake_id"],
          "schema_version":outcome.get("schema_version"),
          "clinical_verdict":outcome.get("clinical_verdict"),
          "gate_results":outcome.get("gate_results"),
          "asset_passport":outcome.get("asset_passport"),
          "evidence_receipts":outcome.get("evidence_receipts"),
          "customer_acceptance_recorded":False,
          "tokenization_or_investment_approval":False,
          "real_stripe_payment_rechecked":True
        }
    finally:
        await db.close()


INDEPENDENT_RWA_VERIFIER="https://verify.noetfield.com/api/internal/commercial/verify-rwa"


async def verify_paid_rwa_clinic(settings:object,*,deal_id:str)->dict[str,Any]:
    """Native nine-gate re-evaluation by separate Verifier, accepted delivery remains buyer-only."""
    import os
    token=os.environ.get("CORPORATE_VERIFIER_INVOKE_TOKEN","").strip()
    if len(token)<32:
        return {"state":"INDEPENDENT_VERIFIER_NOT_CONFIGURED",
                "customer_accepted":False}
    try:
        deal_uuid=uuid.UUID(deal_id)
    except (TypeError,ValueError) as exc:
        raise WorkPacketError("INVALID_DEAL_ID") from exc
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_clinic_submissions(db)
        row=await db.fetchrow("""SELECT w.id,w.deal_id,w.source_intake_id,
            w.scope_ref,w.payment_event_id,w.state,w.external_workpacket_id,
            s.state AS submission_state,s.clinic_case_id
          FROM noetfield.corp_workpackets w
          JOIN noetfield.corp_rwa_clinic_submissions s ON s.workpacket_id=w.id
          WHERE w.deal_id=$1 AND w.engine='RWA_CLINIC'""",deal_uuid)
        if not row:
            raise WorkPacketError("PAID_RWA_CASE_NOT_SUBMITTED")
        if row["state"]=="VERIFIED":
            return {"state":"ALREADY_INDEPENDENTLY_VERIFIED",
                    "workpacket_id":str(row["id"]),
                    "independently_verified_technical_report":True,
                    "customer_accepted":False}
        if (row["state"]!="ACKNOWLEDGED"
            or row["submission_state"]!="PROVIDER_ACCEPTED"
            or row["external_workpacket_id"]!=row["clinic_case_id"]):
            return {"state":"REAL_NATIVE_PROVIDER_RECEIPT_REQUIRED",
                    "independently_verified_technical_report":False,
                    "customer_accepted":False}
        info=validate_paid_case(await _paid_row(db,row["deal_id"]))
        if (info["source_intake_id"]!=row["source_intake_id"]
             or info["scope_ref"]!=row["scope_ref"]
             or info["payment_event_id"]!=row["payment_event_id"]):
            raise WorkPacketError("SIGNED_PAID_RWA_SOURCE_RECHECK_FAILED")
        request={
          "platform_workpacket_id":str(row["id"]),
          "source_intake_id":row["source_intake_id"],
          "payment_event_id":row["payment_event_id"],
          "engine":"RWA_CLINIC",
        }
    finally:
        await db.close()
    try:
        async with httpx.AsyncClient(timeout=35,follow_redirects=False) as client:
            response=await client.post(
                INDEPENDENT_RWA_VERIFIER,json=request,
                headers={"Authorization":"Bearer "+token,"Accept":"application/json"})
    except httpx.RequestError:
        return {"state":"INDEPENDENT_RWA_VERIFIER_TRANSPORT_UNCONFIRMED",
                "customer_accepted":False}
    if response.status_code!=200:
        return {"state":"INDEPENDENT_RWA_VERIFIER_NOT_ACKNOWLEDGED",
                "provider_status":response.status_code,
                "independently_verified_technical_report":False,
                "customer_accepted":False}
    try:
        result=response.json()
    except ValueError as exc:
        raise WorkPacketError("UNREADABLE_RWA_VERIFIER_ACK") from exc
    if (not isinstance(result,dict)
        or result.get("schema")!="noetfield.rwa-independent-verification-result.v1"
        or result.get("state")!="VERIFIED"
        or result.get("clinic_case_id")!=row["clinic_case_id"]
        or result.get("callback_acknowledged") is not True
        or result.get("independent_replay_passed") is not True
        or result.get("customer_accepted") is not False
        or result.get("no_investment_approval") is not True):
        raise WorkPacketError("INDEPENDENT_CLINIC_VERIFIER_ACK_MISMATCH")
    return {"state":"INDEPENDENT_TECHNICAL_REPORT_VERIFIED",
            "clinic_case_id":row["clinic_case_id"],
            "workpacket_id":str(row["id"]),
            "verifier_receipt_url":result["verifier_receipt_url"],
            "independently_verified_technical_report":True,
            "customer_accepted":False,"investment_approval":False}


async def reconcile_pending_native_rwa_cases(settings:object,*,limit:int=2)->dict[str,Any]:
    """Only actual provider-accepted, paid RWA cases; zero synthetic jobs."""
    import os
    if len(os.environ.get("CORPORATE_RWA_VERIFIER_READ_TOKEN",""))<32:
        return {"state":"NOT_CONFIGURED","checked":0}
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_clinic_submissions(db)
        rows=await db.fetch("""SELECT w.deal_id FROM noetfield.corp_workpackets w
            JOIN noetfield.corp_rwa_clinic_submissions s ON s.workpacket_id=w.id
            WHERE w.engine='RWA_CLINIC' AND w.state='ACKNOWLEDGED'
                AND s.state='PROVIDER_ACCEPTED'
            ORDER BY w.updated_at ASC LIMIT $1""",max(1,min(5,limit)))
    finally:
        await db.close()
    states=[]
    for row in rows:
        try:
            outcome=await verify_paid_rwa_clinic(settings,deal_id=str(row["deal_id"]))
            states.append(outcome["state"])
        except (WorkPacketError,ValueError):
            states.append("REJECTED")
    return {"state":"COMPLETE","checked":len(rows),
            "independently_verified_technical_reports":
                states.count("INDEPENDENT_TECHNICAL_REPORT_VERIFIED"),
            "customer_acceptance_auto_granted":False}
