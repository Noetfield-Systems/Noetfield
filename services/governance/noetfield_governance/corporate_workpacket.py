"""Stripe-backed, scope-bound commercial WorkPacket ledger and signed verifier.

One WorkPacket per existing corporate CRM deal, no new payment engine. Only
provider-accepted jobs and signed external verifier results can establish
execution. A signed receipt is NOT customer acceptance or money settlement.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import uuid
from datetime import UTC,datetime
from typing import Any
from urllib.parse import urlsplit

import asyncpg
import httpx

from noetfield_governance.commercial_pipeline import (
 OFFER_TERMS,_database_url,_prepare as prepare_commercial,_as_dict,
 check_payment_match,evidence_url,CommercialError,
)
from noetfield_governance.corporate_crm import schema as prepare_crm,validate_intake,CorporateCRMError


class WorkPacketError(ValueError):
    pass


def _engine(offer:str)->str:
    return {"rwa_technical_sprint":"RWA_CLINIC",
            "ai_sales_os_pilot":"COMPANY_OS"}.get(offer,"")


async def prepare_workpackets(db:asyncpg.Connection)->None:
    await prepare_crm(db)
    await prepare_commercial(db)
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_workpackets(
      id uuid PRIMARY KEY,
      deal_id uuid NOT NULL UNIQUE REFERENCES noetfield.corp_crm_deals(id),
      source_intake_id text NOT NULL,
      engine text NOT NULL CHECK(engine IN('RWA_CLINIC','COMPANY_OS')),
      scope_ref text NOT NULL,
      payment_session_id text NOT NULL,
      payment_event_id text NOT NULL,
      state text NOT NULL DEFAULT 'READY',
      external_workpacket_id text,
      provider_receipt_url text,
      verifier_receipt_url text,
      artifact_url text,
      cost_minor bigint,
      dispatch_attempts integer NOT NULL DEFAULT 0,
      last_error_code text,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_workpacket_events (
       provider_event_id text PRIMARY KEY,
       workpacket_id uuid NOT NULL REFERENCES noetfield.corp_workpackets(id),
       status text NOT NULL,
       verifier_receipt_url text,
       created_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_workpacket_acceptances (
       id uuid PRIMARY KEY,
       deal_id uuid NOT NULL REFERENCES noetfield.corp_crm_deals(id),
       customer_email_hash text NOT NULL,
       customer_subject_hash text NOT NULL,
       workpacket_id uuid NOT NULL REFERENCES noetfield.corp_workpackets(id),
       artifact_url text NOT NULL,
       accepted_at timestamptz NOT NULL DEFAULT now(),
       UNIQUE(deal_id,customer_email_hash)
    )""")


def validate_paid_case(row:dict[str,Any])->dict[str,Any]:
    offer=str(row.get("offer") or "")
    terms=OFFER_TERMS.get(offer)
    intake=str(row.get("source_intake_id") or "")
    case=_as_dict(row.get("commercial"))
    receipt=row.get("payment")
    if not terms or not _engine(offer):
        raise WorkPacketError("SUPPORTED_SCOPED_OFFER_REQUIRED")
    if not re.fullmatch(r"INT-[A-Z0-9]{12}",intake):
        raise WorkPacketError("CANONICAL_INTAKE_REQUIRED")
    if (case.get("stage") not in {"PAYMENT_CONFIRMED","IN_DELIVERY","DELIVERED","CLOSED"}
        or case.get("offer")!=offer or not case.get("scope_ref") or
        not case.get("acceptance_evidence") or
        not case.get("payment_session_id") or not case.get("payment_event_id")):
        raise WorkPacketError("ACCEPTED_SCOPE_AND_PAID_CASE_REQUIRED")
    if not receipt or not isinstance(receipt,dict) or receipt.get("reversed"):
        raise WorkPacketError("SIGNED_CLEAR_STRIPE_RECEIPT_REQUIRED")
    if (receipt.get("livemode") is not True or
        receipt.get("source_intake_id")!=intake or
        receipt.get("session_id")!=case["payment_session_id"] or
        receipt.get("event_id")!=case["payment_event_id"] or
        receipt.get("payment_link_id")!=terms["payment_link_id"] or
        receipt.get("currency")!=terms["currency"] or
        receipt.get("amount_minor")!=terms["payment_minor"]):
        raise WorkPacketError("SIGNED_STRIPE_RECEIPT_MISMATCH")
    # Existing intake-to-checkout verification already handles alternate payer
    # authorization evidence when the session is bound by the commercial ledger.
    if not receipt.get("bound_at"):
        raise WorkPacketError("BOUND_PAID_CHECKOUT_REQUIRED")
    return {"source_intake_id":intake,"engine":_engine(offer),
            "scope_ref":case["scope_ref"],"payment_event_id":case["payment_event_id"],
            "session_id":case["payment_session_id"]}


async def _paid_row(db:asyncpg.Connection,deal_uuid:uuid.UUID,*,lock:bool=False)->dict[str,Any]:
    row=await db.fetchrow("""SELECT d.id,d.source_intake_id,d.offer,
        i.request_id,i.contact_email,i.organization,i.metadata,i.vector,
        i.qualification_json->'commercial_ops' AS commercial,
        e.event_id,e.session_id,e.payment_link_id,e.amount_minor,e.currency,
        e.livemode,e.reversed,e.source_intake_id AS evidence_intake_id,e.bound_at
      FROM noetfield.corp_crm_deals d
      JOIN noetfield.public_intakes i ON i.intake_id=d.source_intake_id
      LEFT JOIN noetfield.commercial_payment_evidence e
       ON e.session_id = i.qualification_json->'commercial_ops'->>'payment_session_id'
      WHERE d.id=$1
      """+(" FOR UPDATE OF d" if lock else ""),deal_uuid)
    if row is None:
        raise WorkPacketError("SOURCED_CORPORATE_DEAL_NOT_FOUND")
    raw=dict(row)
    validate_intake(raw)
    payment=None
    if raw.get("session_id"):
        payment={"event_id":raw["event_id"],"session_id":raw["session_id"],
          "payment_link_id":raw["payment_link_id"],"amount_minor":raw["amount_minor"],
          "currency":raw["currency"],"livemode":raw["livemode"],"reversed":raw["reversed"],
          "source_intake_id":raw["evidence_intake_id"],"bound_at":raw["bound_at"]}
    raw["payment"]=payment
    return raw


async def admit_paid_workpacket(settings:object,*,deal_id:str)->dict[str,Any]:
    try:
        deal_uuid=uuid.UUID(deal_id)
    except (TypeError,ValueError) as exc:
        raise WorkPacketError("INVALID_DEAL_ID") from exc
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_workpackets(db)
        async with db.transaction():
            info=validate_paid_case(await _paid_row(db,deal_uuid,lock=True))
            created=await db.fetchrow("""INSERT INTO noetfield.corp_workpackets(
              id,deal_id,source_intake_id,engine,scope_ref,
              payment_session_id,payment_event_id)
              VALUES($1,$2,$3,$4,$5,$6,$7)
              ON CONFLICT(deal_id) DO NOTHING RETURNING id""",
              uuid.uuid4(),deal_uuid,info["source_intake_id"],info["engine"],
              info["scope_ref"],info["session_id"],info["payment_event_id"])
            row=await db.fetchrow("SELECT * FROM noetfield.corp_workpackets WHERE deal_id=$1",deal_uuid)
            if not row:
                raise WorkPacketError("WORKPACKET_PERSISTENCE_UNCONFIRMED")
            if (row["source_intake_id"]!=info["source_intake_id"] or
                row["payment_session_id"]!=info["session_id"] or
                row["scope_ref"]!=info["scope_ref"]):
                raise WorkPacketError("WORKPACKET_SOURCE_CONFLICT")
            return {"workpacket_id":str(row["id"]),"deal_id":str(deal_uuid),
                    "state":row["state"],"engine":row["engine"],
                    "source_intake_id":row["source_intake_id"],
                    "created":bool(created),"idempotent":not bool(created),
                    "external_dispatch_confirmed":row["state"] in {"ACKNOWLEDGED","RUNNING","VERIFIED"}}
    finally:
        await db.close()


def _dispatch_config(engine:str)->tuple[str,str]|None:
    route=os.getenv("CORPORATE_"+engine+"_WORKPACKET_URL","").strip()
    secret=os.getenv("CORPORATE_WORKPACKET_DISPATCH_TOKEN","").strip()
    u=urlsplit(route)
    allowed={
      "COMPANY_OS":{"business-os-core-production.up.railway.app"},
      "RWA_CLINIC":{"rwa-clinic-production.up.railway.app","rwa-clinic.up.railway.app"},
    }.get(engine,set())
    if (len(secret)<32 or u.scheme!="https" or u.hostname not in allowed
        or u.username or u.password or u.port not in (None,443)
        or u.path!="/api/internal/commercial/workpackets"
        or u.query or u.fragment):
        return None
    return route,secret


async def dispatch_paid_workpacket(settings:object,*,deal_id:str)->dict[str,Any]:
    admitted=await admit_paid_workpacket(settings,deal_id=deal_id)
    wid=uuid.UUID(admitted["workpacket_id"])
    engine=admitted["engine"]
    config=_dispatch_config(engine)
    if not config:
        return {**admitted,"state":"READY","dispatch_state":"PROVIDER_CONTRACT_NOT_CONFIGURED",
                "provider_acknowledged":False}
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_workpackets(db)
        row=await db.fetchrow("""UPDATE noetfield.corp_workpackets
              SET state='DISPATCHING',dispatch_attempts=dispatch_attempts+1,
                  updated_at=now()
              WHERE id=$1 AND state IN('READY','DISPATCH_UNCONFIRMED')
              RETURNING *""",wid)
        if not row:
            row=await db.fetchrow("SELECT * FROM noetfield.corp_workpackets WHERE id=$1",wid)
            return {"workpacket_id":str(wid),"state":row["state"],
                    "provider_acknowledged":row["state"] in {"ACKNOWLEDGED","RUNNING","VERIFIED"},
                    "idempotent":True}
    finally:
        await db.close()
    route,token=config
    status="DISPATCH_UNCONFIRMED"
    ext_id=receipt_url=""
    try:
        async with httpx.AsyncClient(timeout=15,follow_redirects=False) as client:
            reply=await client.post(route,json={
             "idempotency_key":str(wid),
             "source_intake_id":row["source_intake_id"],
             "scope_ref":row["scope_ref"],
             "payment_event_id":row["payment_event_id"],
             "engine":row["engine"],
             "requested_work":"Perform accepted, paid, narrowly scoped commercial deliverable"
            },headers={"Authorization":"Bearer "+token,
               "Idempotency-Key":str(wid),"Accept":"application/json"})
        data=reply.json() if reply.status_code in (200,201,202) else {}
        if (isinstance(data,dict) and
             data.get("status")=="ACCEPTED" and
             data.get("source_intake_id")==row["source_intake_id"] and
             data.get("engine")==row["engine"] and
             isinstance(data.get("workpacket_id"),str) and
             3<=len(data["workpacket_id"])<=180):
            ext_id=data["workpacket_id"]
            receipt_url=evidence_url(str(data.get("provider_receipt_url") or ""))
            status="ACKNOWLEDGED"
    except (httpx.RequestError,ValueError,CommercialError):
        status="DISPATCH_UNCONFIRMED"
    db=await asyncpg.connect(_database_url(settings))
    try:
        await db.execute("""UPDATE noetfield.corp_workpackets SET state=$2,
             external_workpacket_id=CASE WHEN $2='ACKNOWLEDGED' THEN $3 ELSE external_workpacket_id END,
             provider_receipt_url=CASE WHEN $2='ACKNOWLEDGED' THEN $4 ELSE provider_receipt_url END,
             last_error_code=CASE WHEN $2='ACKNOWLEDGED' THEN NULL ELSE 'UPSTREAM_ACK_UNCONFIRMED' END,
             updated_at=now() WHERE id=$1""",wid,status,ext_id,receipt_url)
    finally:
        await db.close()
    return {"workpacket_id":str(wid),"state":status,
            "engine":engine,"provider_acknowledged":status=="ACKNOWLEDGED",
            "external_workpacket_id":ext_id if status=="ACKNOWLEDGED" else None,
            "provider_receipt_url":receipt_url if status=="ACKNOWLEDGED" else None}


def verify_signed_result(raw:bytes,signature:str)->dict[str,Any]:
    secret=os.getenv("CORPORATE_WORKPACKET_VERIFIER_SECRET","").strip()
    if len(secret)<32 or len(raw)>25000 or not signature.startswith("sha256="):
        raise WorkPacketError("VERIFIER_UNAVAILABLE_OR_SIGNATURE_MISSING")
    expected="sha256="+hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,signature):
        raise WorkPacketError("INVALID_INDEPENDENT_VERIFIER_SIGNATURE")
    try:
        event=json.loads(raw)
    except (ValueError,UnicodeDecodeError) as exc:
        raise WorkPacketError("INVALID_VERIFIER_PAYLOAD") from exc
    if not isinstance(event,dict) or event.get("status") not in {"RUNNING","FAILED","VERIFIED"}:
        raise WorkPacketError("INVALID_VERIFIER_STATUS")
    if not re.fullmatch(r"[A-Za-z0-9:_-]{10,180}",str(event.get("provider_event_id") or "")):
        raise WorkPacketError("INVALID_PROVIDER_EVENT_ID")
    if event["status"]=="VERIFIED":
        evidence_url(str(event.get("artifact_url") or ""))
        evidence_url(str(event.get("verifier_receipt_url") or ""))
        if (type(event.get("cost_minor")) is not int or
              not 0<=event["cost_minor"]<=10000000000):
            raise WorkPacketError("VERIFIED_COST_MISSING_OR_INVALID")
    return event


async def record_signed_result(settings:object,event:dict[str,Any])->dict[str,Any]:
    try:
        wid=uuid.UUID(str(event.get("workpacket_id") or ""))
    except ValueError as exc:
        raise WorkPacketError("INVALID_WORKPACKET_ID") from exc
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_workpackets(db)
        async with db.transaction():
            row=await db.fetchrow("SELECT * FROM noetfield.corp_workpackets WHERE id=$1 FOR UPDATE",wid)
            if not row or row["state"] not in {"ACKNOWLEDGED","RUNNING","VERIFIED"}:
                raise WorkPacketError("DISPATCH_ACK_REQUIRED_FOR_VERIFICATION")
            if event.get("source_intake_id")!=row["source_intake_id"] or event.get("engine")!=row["engine"] or event.get("external_workpacket_id")!=row["external_workpacket_id"]:
                raise WorkPacketError("VERIFIER_SOURCE_OR_ENGINE_MISMATCH")
            # Re-check the signed live source-bound Stripe payment before accepting
            # even an independently signed verifier result.
            paid=validate_paid_case(await _paid_row(db,row["deal_id"]))
            if paid["session_id"]!=row["payment_session_id"] or paid["payment_event_id"]!=row["payment_event_id"]:
                raise WorkPacketError("VERIFIER_PAYMENT_CHANGED")
            event_id=event["provider_event_id"]
            inserted=await db.fetchrow("""INSERT INTO noetfield.corp_workpacket_events(
                     provider_event_id,workpacket_id,status,verifier_receipt_url)
                     VALUES($1,$2,$3,$4) ON CONFLICT DO NOTHING RETURNING provider_event_id""",
                     event_id,wid,event["status"],str(event.get("verifier_receipt_url") or ""))
            if not inserted:
                return {"state":row["state"],"idempotent":True,"workpacket_id":str(wid)}
            if row["state"]=="VERIFIED":
                return {"state":"VERIFIED","idempotent":True,"workpacket_id":str(wid)}
            target={"RUNNING":"RUNNING","FAILED":"FAILED","VERIFIED":"VERIFIED"}[event["status"]]
            await db.execute("""UPDATE noetfield.corp_workpackets
                 SET state=$2,artifact_url=$3,verifier_receipt_url=$4,cost_minor=$5,
                   updated_at=now() WHERE id=$1""",
                 wid,target,str(event.get("artifact_url") or "") if target=="VERIFIED" else None,
                 str(event.get("verifier_receipt_url") or "") if target=="VERIFIED" else None,
                 int(event["cost_minor"]) if target=="VERIFIED" else None)
            return {"state":target,"idempotent":False,
                    "workpacket_id":str(wid),"independent_signed_result":True,
                    "customer_acceptance_verified":False}
    finally:
        await db.close()


async def workpacket_for_deal(settings:object,*,deal_id:str)->dict[str,Any]:
    try:
        deal_uuid=uuid.UUID(deal_id)
    except ValueError as exc:
        raise WorkPacketError("INVALID_DEAL_ID") from exc
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_workpackets(db)
        r=await db.fetchrow("""SELECT id,source_intake_id,engine,state,external_workpacket_id,
                   provider_receipt_url,verifier_receipt_url,artifact_url,
                   cost_minor,dispatch_attempts,last_error_code,updated_at
              FROM noetfield.corp_workpackets WHERE deal_id=$1""",deal_uuid)
        if not r:
            return {"state":"NOT_CREATED","workpacket_id":None,
                    "provider_acknowledged":False,"independently_verified":False}
        return {"workpacket_id":str(r["id"]),"source_intake_id":r["source_intake_id"],
                "engine":r["engine"],"state":r["state"],
                "external_workpacket_id":r["external_workpacket_id"],
                "provider_receipt_url":r["provider_receipt_url"],
                "verifier_receipt_url":r["verifier_receipt_url"],
                "artifact_url":r["artifact_url"],
                "cost_minor":r["cost_minor"],"dispatch_attempts":r["dispatch_attempts"],
                "last_error_code":r["last_error_code"],
                "provider_acknowledged":r["state"] in {"ACKNOWLEDGED","RUNNING","VERIFIED"},
                "independently_verified":r["state"]=="VERIFIED",
                "customer_acceptance_verified":False}
    finally:
        await db.close()


async def customer_accept_workpacket(settings:object,*,deal_id:str,
                                     identity:dict[str,str])->dict[str,Any]:
    """Explicit verified buyer action; independently verified artifact first."""
    try:
        identifier=uuid.UUID(deal_id)
    except (ValueError,TypeError) as exc:
        raise WorkPacketError("INVALID_DEAL_ID") from exc
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_workpackets(db)
        from noetfield_governance.customer_portal import ensure_customer_access_schema
        await ensure_customer_access_schema(db)
        async with db.transaction():
            membership=await db.fetchrow("""SELECT ca.deal_id,w.id AS workpacket_id,
               w.state,w.artifact_url,w.verifier_receipt_url,w.payment_event_id
               FROM noetfield.corp_customer_access ca
               JOIN noetfield.corp_workpackets w ON w.deal_id=ca.deal_id
               WHERE ca.deal_id=$1 AND ca.email_hash=$2 AND ca.active=true
               FOR UPDATE OF w""",identifier,identity["email_hash"])
            if not membership:
                raise WorkPacketError("CUSTOMER_MEMBERSHIP_OR_WORKPACKET_NOT_FOUND")
            if membership["state"]!="VERIFIED" or not membership["artifact_url"] or not membership["verifier_receipt_url"]:
                raise WorkPacketError("INDEPENDENT_VERIFIED_DELIVERABLE_REQUIRED")
            paid=validate_paid_case(await _paid_row(db,identifier))
            if paid["payment_event_id"]!=membership["payment_event_id"]:
                raise WorkPacketError("CURRENT_LIVE_PAYMENT_REQUIRED")
            ack=await db.fetchrow("""INSERT INTO noetfield.corp_workpacket_acceptances(
                   id,deal_id,customer_email_hash,customer_subject_hash,workpacket_id,artifact_url)
                   VALUES($1,$2,$3,$4,$5,$6)
                   ON CONFLICT(deal_id,customer_email_hash) DO NOTHING
                   RETURNING id""",uuid.uuid4(),identifier,identity["email_hash"],
                   hashlib.sha256(identity["provider_subject"].encode()).hexdigest(),
                   membership["workpacket_id"],membership["artifact_url"])
            created=bool(ack)
            if not created:
                ack=await db.fetchrow("""SELECT id FROM noetfield.corp_workpacket_acceptances
                        WHERE deal_id=$1 AND customer_email_hash=$2""",
                        identifier,identity["email_hash"])
            return {"accepted":True,"receipt_id":str(ack["id"]),
                    "idempotent":not created,
                    "workpacket_id":str(membership["workpacket_id"]),
                    "verified_customer_identity":True,
                    "contract_signing_not_automated":True}
    finally:
        await db.close()


async def check_accepted_delivery(settings:object,*,deal_id:str,
                                  delivery_evidence:str,acceptance_url:str)->tuple[str,str]:
    """Operator delivery transition must match signed verifier + actual customer acceptance."""
    try:
        identifier=uuid.UUID(deal_id)
    except (ValueError,TypeError) as exc:
        raise WorkPacketError("INVALID_DEAL_ID") from exc
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_workpackets(db)
        row=await db.fetchrow("""SELECT w.artifact_url,w.state,w.verifier_receipt_url,
                       a.id AS receipt_id,a.artifact_url AS accepted_artifact
                 FROM noetfield.corp_workpackets w
                 JOIN noetfield.corp_workpacket_acceptances a ON a.workpacket_id=w.id
                 JOIN noetfield.corp_customer_access ca ON ca.deal_id=a.deal_id
                      AND ca.email_hash=a.customer_email_hash AND ca.active=true
                 WHERE w.deal_id=$1 ORDER BY a.accepted_at ASC LIMIT 1""",identifier)
        if not row or row["state"]!="VERIFIED" or not row["verifier_receipt_url"]:
            raise WorkPacketError("INDEPENDENT_VERIFIER_AND_CUSTOMER_ACCEPTANCE_REQUIRED")
        if row["accepted_artifact"]!=row["artifact_url"]:
            raise WorkPacketError("ACCEPTED_ARTIFACT_MISMATCH")
        artifact=evidence_url(row["artifact_url"])
        supplied=evidence_url(delivery_evidence) if delivery_evidence else artifact
        if supplied!=artifact:
            raise WorkPacketError("DELIVERY_EVIDENCE_MUST_MATCH_INDEPENDENT_ARTIFACT")
        canonical_acceptance=("https://platform.noetfield.com/api/corporate-crm/"
                              "customer/acceptance/"+str(row["receipt_id"]))
        if acceptance_url and acceptance_url!=canonical_acceptance:
            raise WorkPacketError("CUSTOMER_ACCEPTANCE_RECEIPT_MISMATCH")
        paid=validate_paid_case(await _paid_row(db,identifier))
        return artifact,canonical_acceptance
    finally:
        await db.close()


async def acceptance_receipt(settings:object,*,receipt_id:str)->dict[str,Any]:
    """Private, immutable receipt readback used by the canonical commercial ledger."""
    try:
        ident=uuid.UUID(receipt_id)
    except (ValueError,TypeError) as exc:
        raise WorkPacketError("INVALID_CUSTOMER_ACCEPTANCE_ID") from exc
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_workpackets(db)
        row=await db.fetchrow("""SELECT a.id,a.deal_id,a.workpacket_id,a.artifact_url,
                a.accepted_at,w.state,w.verifier_receipt_url
            FROM noetfield.corp_workpacket_acceptances a
            JOIN noetfield.corp_workpackets w ON w.id=a.workpacket_id
            WHERE a.id=$1""",ident)
        if not row:
            raise WorkPacketError("CUSTOMER_ACCEPTANCE_NOT_FOUND")
        return {"schema":"noetfield.customer-delivery-acceptance.v1",
                "receipt_id":str(row["id"]),"deal_id":str(row["deal_id"]),
                "workpacket_id":str(row["workpacket_id"]),
                "accepted_artifact":row["artifact_url"],
                "accepted_at":row["accepted_at"].isoformat(),
                "independent_verifier_receipt":row["verifier_receipt_url"],
                "workpacket_state":row["state"],
                "verified_customer_identity":True,
                "private_customer_email_not_exposed":True}
    finally:
        await db.close()


async def check_accepted_delivery_for_intake(
    settings: object, *, intake_id: str, delivery_evidence: str = "", acceptance_url: str = ""
) -> tuple[str, str]:
    """Resolve the ONE canonical commercial deal; do not trust operator-provided URLs.

    Both the legacy intake-level command and the Corporate CRM route must pass
    through this same evidence gate before they can set DELIVERED or CLOSED.
    """
    if not re.fullmatch(r"INT-[A-Z0-9]{12}", intake_id):
        raise WorkPacketError("INVALID_SOURCE_INTAKE")
    db = await asyncpg.connect(_database_url(settings))
    try:
        await prepare_workpackets(db)
        rows = await db.fetch("""SELECT d.id
          FROM noetfield.corp_crm_deals d
          JOIN noetfield.public_intakes i ON i.intake_id=d.source_intake_id
          WHERE d.source_intake_id=$1
            AND d.offer=(i.qualification_json->'commercial_ops'->>'offer')
          ORDER BY d.created_at ASC LIMIT 2""", intake_id)
        if len(rows) != 1:
            raise WorkPacketError("UNIQUE_SOURCED_COMMERCIAL_DEAL_REQUIRED")
        deal_id = str(rows[0]["id"])
    finally:
        await db.close()
    return await check_accepted_delivery(settings, deal_id=deal_id,
                                          delivery_evidence=delivery_evidence,
                                          acceptance_url=acceptance_url)


INDEPENDENT_DRAFT_VERIFIER = "https://verify.noetfield.com/api/internal/commercial/verify-draft"


async def verify_company_os_draft(settings:object,*,deal_id:str)->dict[str,Any]:
    """Independent origin-pulled draft hash check; never marks client delivery."""
    try:
        deal_uuid=uuid.UUID(deal_id)
    except (TypeError,ValueError) as exc:
        raise WorkPacketError("INVALID_DEAL_ID") from exc
    invoke_token=os.environ.get("CORPORATE_VERIFIER_INVOKE_TOKEN","").strip()
    if len(invoke_token)<32:
        return {"state":"VERIFIER_NOT_CONFIGURED","independently_verified_delivery":False}
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_workpackets(db)
        row=await db.fetchrow("""SELECT id,deal_id,engine,state,source_intake_id,
             external_workpacket_id,payment_event_id
           FROM noetfield.corp_workpackets WHERE deal_id=$1""",deal_uuid)
        if row is None:
            raise WorkPacketError("PAID_WORKPACKET_NOT_ADMITTED")
        if row["engine"]!="COMPANY_OS":
            return {"state":"RWA_CLINIC_VERIFIER_NOT_CONNECTED","independently_verified_delivery":False}
        if row["state"]=="VERIFIED":
            return {"state":"ALREADY_INDEPENDENTLY_VERIFIED","independently_verified_delivery":True}
        if row["state"]=="RUNNING":
            return {"state":"DRAFT_REVIEW_ALREADY_RECORDED","independently_verified_delivery":False}
        if row["state"]!="ACKNOWLEDGED" or not row["external_workpacket_id"]:
            return {"state":"PROVIDER_DISPATCH_ACK_REQUIRED","independently_verified_delivery":False}
        paid=validate_paid_case(await _paid_row(db,row["deal_id"]))
        if (paid["source_intake_id"]!=row["source_intake_id"] or
            paid["payment_event_id"]!=row["payment_event_id"]):
            raise WorkPacketError("PAID_SCOPE_CHANGED_BEFORE_DRAFT_VERIFIER")
        outgoing={
          "platform_workpacket_id":str(row["id"]),
          "external_workpacket_id":row["external_workpacket_id"],
          "source_intake_id":row["source_intake_id"],
          "payment_event_id":row["payment_event_id"],
          "engine":"COMPANY_OS"
        }
    finally:
        await db.close()
    try:
        async with httpx.AsyncClient(timeout=25,follow_redirects=False) as client:
            response=await client.post(
              INDEPENDENT_DRAFT_VERIFIER,
              json=outgoing,
              headers={"Authorization":"Bearer "+invoke_token,
                       "Accept":"application/json"})
    except httpx.RequestError:
        return {"state":"VERIFIER_TRANSPORT_UNCONFIRMED",
                "independently_verified_delivery":False}
    if response.status_code==409:
        return {"state":"ARTIFACT_NOT_YET_VERIFIABLE","independently_verified_delivery":False}
    if response.status_code!=200:
        return {"state":"VERIFIER_PROVIDER_UNAVAILABLE",
                "provider_http_status":response.status_code,
                "independently_verified_delivery":False}
    try:
        result=response.json()
    except ValueError:
        raise WorkPacketError("UNPARSABLE_VERIFIER_ACK") from None
    if (not isinstance(result,dict) or
         result.get("schema")!="noetfield.commercial-draft-verified.v1" or
         result.get("state")!="RUNNING" or
         result.get("source_workpacket_id")!=outgoing["external_workpacket_id"] or
         result.get("callback_acknowledged") is not True or
         result.get("draft_integrity_passed") is not True or
         result.get("product_delivered") is not False or
         result.get("customer_accepted") is not False):
        raise WorkPacketError("INDEPENDENT_VERIFIER_CALLBACK_UNCONFIRMED")
    return {"state":"DRAFT_INDEPENDENTLY_ATTESTED",
            "external_workpacket_id":outgoing["external_workpacket_id"],
            "verifier_receipt_url":evidence_url(str(result.get("verifier_receipt_url") or "")),
            "independently_verified_draft":True,
            "independently_verified_delivery":False,
            "customer_acceptance":False,
            "provider_acknowledged":True}


async def reconcile_pending_company_os_drafts(settings:object,*,limit:int=3)->dict[str,Any]:
    """Bounded background verification of actual ACKed Company OS jobs, never simulations."""
    if not 1<=limit<=10:
        raise WorkPacketError("INVALID_DRAFT_RECONCILIATION_LIMIT")
    if len(os.environ.get("CORPORATE_VERIFIER_INVOKE_TOKEN",""))<32:
        return {"state":"NOT_CONFIGURED","checked":0,"verified_drafts":0}
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_workpackets(db)
        rows=await db.fetch("""SELECT deal_id FROM noetfield.corp_workpackets
             WHERE engine='COMPANY_OS' AND state='ACKNOWLEDGED'
             ORDER BY updated_at ASC LIMIT $1""",limit)
    finally:
        await db.close()
    statuses=[]
    for row in rows:
        try:
            result=await verify_company_os_draft(settings,deal_id=str(row["deal_id"]))
            statuses.append(result["state"])
        except (WorkPacketError,CommercialError):
            statuses.append("SOURCE_OR_VERIFIER_REJECTED")
    return {"state":"COMPLETE","checked":len(rows),
            "verified_drafts":statuses.count("DRAFT_INDEPENDENTLY_ATTESTED"),
            "pending":statuses.count("ARTIFACT_NOT_YET_VERIFIABLE"),
            "no_customer_deliveries_claimed":True}
