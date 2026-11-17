"""Noetfield customer portal: independently verified identity, scoped membership and payment truth.

Never reuse an operator cookie as a customer session. The bearer is independently
checked by Supabase Auth /user on every read. Only an operator may grant/revoke
membership, which is keyed to one genuine canonical Noetfield intake.
"""
from __future__ import annotations

import hashlib
import os
import re
import uuid
from typing import Any

import asyncpg
import httpx
from fastapi import HTTPException

from noetfield_governance.commercial_pipeline import OFFER_TERMS, _database_url, _prepare, _as_dict
from noetfield_governance.corporate_crm import CorporateCRMError, schema, validate_intake
from noetfield_governance.operator_google_auth import _provider_settings


def customer_email_hash(email: str) -> str:
    email = email.strip().casefold()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or len(email) > 254:
        raise CorporateCRMError("INVALID_CUSTOMER_EMAIL")
    return hashlib.sha256(email.encode("utf-8")).hexdigest()


async def authenticate_customer(token: str) -> dict[str, str]:
    """Supabase Auth is authoritative; no local JWT decoding or self-declared email."""
    config = _provider_settings()
    if not config:
        raise HTTPException(status_code=503, detail="CUSTOMER_IDENTITY_PROVIDER_UNAVAILABLE")
    if not token or len(token) > 8192:
        raise HTTPException(status_code=401, detail="INVALID_CUSTOMER_SESSION")
    base, anon = config
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=False) as client:
            res = await client.get(base + "/auth/v1/user",
                 headers={"Authorization":"Bearer " + token,"apikey":anon})
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503,detail="CUSTOMER_IDENTITY_READ_UNAVAILABLE") from exc
    if res.status_code != 200:
        raise HTTPException(status_code=401,detail="CUSTOMER_SESSION_EXPIRED_OR_INVALID")
    try:
        user = res.json()
    except ValueError as exc:
        raise HTTPException(status_code=503,detail="CUSTOMER_IDENTITY_INVALID") from exc
    if not isinstance(user,dict) or not user.get("id") or not user.get("email_confirmed_at"):
        raise HTTPException(status_code=403,detail="VERIFIED_CUSTOMER_EMAIL_REQUIRED")
    try:
        email_hash = customer_email_hash(str(user.get("email") or ""))
    except CorporateCRMError as exc:
        raise HTTPException(status_code=403,detail="VERIFIED_CUSTOMER_EMAIL_REQUIRED") from exc
    return {"provider_subject":str(user["id"]),"email_hash":email_hash}


async def ensure_customer_access_schema(db: asyncpg.Connection) -> None:
    await schema(db)
    await _prepare(db)
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_customer_access (
        deal_id uuid NOT NULL REFERENCES noetfield.corp_crm_deals(id),
        email_hash text NOT NULL,
        granted_by text NOT NULL,
        evidence_url text NOT NULL DEFAULT '',
        active boolean NOT NULL DEFAULT true,
        created_at timestamptz NOT NULL DEFAULT now(),
        revoked_at timestamptz,
        PRIMARY KEY(deal_id,email_hash)
    )""")


async def grant_customer_access(settings: object, *, deal_id: str, email: str,
                                actor: str, evidence_url: str = "",
                                revoke: bool = False) -> dict[str, Any]:
    """Explicit per-deal membership. Direct-source email only by default.

    Other people require external authorization evidence and operator action.
    No invitation/email is sent by changing the ACL.
    """
    try:
        deal_uuid = uuid.UUID(str(deal_id))
        digest = customer_email_hash(email)
    except (ValueError, TypeError) as exc:
        raise CorporateCRMError("INVALID_CUSTOMER_GRANT") from exc
    if not actor.strip():
        raise CorporateCRMError("OPERATOR_ACTOR_REQUIRED")
    if evidence_url:
        from noetfield_governance.commercial_pipeline import evidence_url as check_url
        evidence_url = check_url(evidence_url)
    db=await asyncpg.connect(_database_url(settings))
    try:
        await ensure_customer_access_schema(db)
        record=await db.fetchrow("""SELECT d.source_intake_id,d.offer,
                    i.request_id,i.contact_email,i.organization,i.metadata,i.vector
              FROM noetfield.corp_crm_deals d
              JOIN noetfield.public_intakes i ON i.intake_id=d.source_intake_id
              WHERE d.id=$1""",deal_uuid)
        if record is None:
            raise CorporateCRMError("SOURCED_DEAL_REQUIRED_FOR_CUSTOMER_ACCESS")
        validate_intake(record)
        if record["offer"] not in OFFER_TERMS:
            raise CorporateCRMError("NO_SUPPORTED_CUSTOMER_OFFER")
        if not revoke and digest != customer_email_hash(record["contact_email"]) and not evidence_url:
            raise CorporateCRMError("THIRD_PARTY_CUSTOMER_ACCESS_REQUIRES_EVIDENCE")
        if revoke:
            row=await db.fetchrow("""UPDATE noetfield.corp_customer_access
                        SET active=false,revoked_at=now()
                        WHERE deal_id=$1 AND email_hash=$2 AND active=true
                        RETURNING deal_id""",deal_uuid,digest)
            return {"active":False,"changed":bool(row),"deal_id":str(deal_uuid),"message_sent":False}
        row=await db.fetchrow("""INSERT INTO noetfield.corp_customer_access
                 (deal_id,email_hash,granted_by,evidence_url,active)
                 VALUES($1,$2,$3,$4,true)
                 ON CONFLICT(deal_id,email_hash)
                 DO UPDATE SET active=true,granted_by=EXCLUDED.granted_by,
                   evidence_url=EXCLUDED.evidence_url,revoked_at=NULL
                 RETURNING deal_id""",deal_uuid,digest,actor[:120],evidence_url)
        return {"active":True,"changed":bool(row),"deal_id":str(deal_uuid),
                "message_sent":False, "payment_recorded":False}
    finally:
        await db.close()


async def auto_grant_paid_original_customers(settings:object,*,limit:int=5)->dict[str,Any]:
    """Grant a real paid original buyer self-service access without Founder typing.

    No unchecked third party or model-inferred email is ever added. The buyer
    must still authenticate using Supabase's verified email before seeing a
    scoped engagement. Never re-enable a manually REVOKED membership; the
    insert is ON CONFLICT DO NOTHING rather than an upsert.
    """
    if type(limit) is not int or not 1<=limit<=10:
        raise CorporateCRMError("INVALID_PAID_CUSTOMER_ACCESS_BATCH_LIMIT")
    from noetfield_governance.corporate_workpacket import (
        _paid_row,validate_paid_case,WorkPacketError
    )
    db=await asyncpg.connect(_database_url(settings))
    try:
        await ensure_customer_access_schema(db)
        candidates=await db.fetch("""SELECT DISTINCT d.id
            FROM noetfield.corp_crm_deals d
            JOIN noetfield.public_intakes i ON i.intake_id=d.source_intake_id
            JOIN noetfield.commercial_payment_evidence e
              ON e.source_intake_id=d.source_intake_id
            WHERE d.offer IN ('rwa_technical_sprint','ai_sales_os_pilot')
              AND e.livemode IS TRUE AND e.reversed IS FALSE
              AND e.bound_at IS NOT NULL
              AND i.qualification_json->'commercial_ops'->>'offer'=d.offer
              AND i.qualification_json->'commercial_ops'->>'payment_event_id'=e.event_id
              AND i.qualification_json->'commercial_ops'->>'payment_session_id'=e.session_id
              AND i.qualification_json->'commercial_ops'->>'stage'
                IN ('PAYMENT_CONFIRMED','IN_DELIVERY','DELIVERED','CLOSED')
              AND nullif(i.qualification_json->'commercial_ops'->>'acceptance_evidence','') IS NOT NULL
            ORDER BY d.id ASC LIMIT $1""",limit)
        granted=0
        blocked=0
        for item in candidates:
            try:
                original=await _paid_row(db,item["id"])
                validate_paid_case(original)
                email_hash=customer_email_hash(str(original.get("contact_email") or ""))
                created=await db.fetchrow("""INSERT INTO noetfield.corp_customer_access(
                      deal_id,email_hash,granted_by,evidence_url,active)
                    VALUES($1,$2,'SOURCE_BOUND_PAID_CUSTOMER_AUTO_GRANT','',true)
                    ON CONFLICT(deal_id,email_hash) DO NOTHING RETURNING deal_id""",
                    item["id"],email_hash)
                granted+=bool(created)
            except (CorporateCRMError,WorkPacketError,ValueError):
                blocked+=1
        return {"schema":"noetfield.corporate-paid-customer-access.v1",
           "state":"COMPLETE" if blocked==0 else "PARTIAL_OR_BLOCKED",
           "paid_cases_checked":len(candidates),
           "new_source_original_customer_memberships":int(granted),
           "blocked":blocked,"emails_sent":0,
           "no_third_party_grants":True,"revocations_restored":0,
           "customer_identity_still_requires_verified_login":True}
    finally:
        await db.close()


def customer_case_projection(row: dict[str, Any]) -> dict[str, Any]:
    case = _as_dict(row.get("commercial"))
    payment = row.get("payment")
    terms = OFFER_TERMS.get(str(row.get("offer")))
    paid = bool(payment and payment["livemode"] and
                not payment["reversed"] and
                payment["source_intake_id"] == row["source_intake_id"] and
                case.get("payment_session_id") == payment["session_id"] and
                terms and payment["payment_link_id"] == terms["payment_link_id"] and
                payment["amount_minor"] == terms["payment_minor"] and
                payment["currency"] == terms["currency"] and
                case.get("offer") == row["offer"] and
                case.get("acceptance_evidence"))
    reversed_payment = bool(payment and payment["reversed"])
    stage = str(case.get("stage") or "NOT_OPEN")
    scope_accepted = bool(case.get("acceptance_evidence") and
                          stage in {"SCOPE_ACCEPTED","PAYMENT_CONFIRMED","IN_DELIVERY","DELIVERED","CLOSED"})
    has_delivery = bool(paid and stage in {"DELIVERED","CLOSED"} and
                        case.get("customer_acceptance") and case.get("delivery_evidence"))
    output: dict[str,Any] = {
        "deal_id":str(row["id"]), "account_name":row["account_name"],
        "offer":row["offer"], "commercial_stage":stage,
        "scope_accepted":scope_accepted,
        "scope_ref":case.get("scope_ref") if scope_accepted else None,
        "scope_evidence":case.get("acceptance_evidence") if scope_accepted else None,
        "payment_status":"REVERSED" if reversed_payment else ("PAID_LIVE" if paid else "NOT_VERIFIED"),
        "bank_settlement_verified":False,
        "payment_amount_minor":terms["payment_minor"] if terms else None,
        "payment_currency":terms["currency"] if terms else None,
        "payment_event_id":str(payment["event_id"]) if paid else None,
        "approved_checkout_url":(terms["checkout_url"] if scope_accepted and
             stage == "SCOPE_ACCEPTED" and not paid and not reversed_payment and terms else None),
        "delivery_state":"ACCEPTED" if has_delivery else ("IN_PROGRESS" if paid and
             stage=="IN_DELIVERY" else "NOT_ACCEPTED"),
        "delivery_evidence":case.get("delivery_evidence") if has_delivery else None,
        "customer_acceptance":case.get("customer_acceptance") if has_delivery else None,
        "source":"canonical_intake_and_signed_stripe_only",
    }
    return output


async def customer_cases(settings: object, *, identity: dict[str,str]) -> dict[str,Any]:
    """Strict membership and source association, filtered by verified email only."""
    digest=identity["email_hash"]
    db=await asyncpg.connect(_database_url(settings))
    try:
        await ensure_customer_access_schema(db)
        from noetfield_governance.corporate_workpacket import prepare_workpackets
        await prepare_workpackets(db)
        rows=await db.fetch("""SELECT d.id,d.source_intake_id,d.offer,a.name AS account_name,
                    i.contact_email,i.qualification_json->'commercial_ops' AS commercial
                 FROM noetfield.corp_customer_access ca
                 JOIN noetfield.corp_crm_deals d ON d.id=ca.deal_id
                 JOIN noetfield.corp_crm_accounts a ON a.id=d.account_id
                 JOIN noetfield.public_intakes i ON i.intake_id=d.source_intake_id
                 WHERE ca.active=true AND ca.email_hash=$1
                 ORDER BY d.created_at DESC LIMIT 50""",digest)
        result=[]
        for row in rows:
            item=dict(row)
            case=_as_dict(item["commercial"])
            payment=None
            if case.get("payment_session_id"):
                proof=await db.fetchrow("""SELECT e.event_id,e.session_id,e.payment_link_id,
                       e.amount_minor,e.currency,e.livemode,e.reversed,e.source_intake_id
                       FROM noetfield.commercial_payment_evidence e
                       WHERE e.session_id=$1""",case["payment_session_id"])
                payment=dict(proof) if proof else None
            item["payment"]=payment
            projection=customer_case_projection(item)
            work=await db.fetchrow("""SELECT w.id,w.state,w.artifact_url,
                 w.verifier_receipt_url,w.external_workpacket_id,w.cost_minor,
                 EXISTS(SELECT 1 FROM noetfield.corp_workpacket_acceptances ca
                        WHERE ca.workpacket_id=w.id AND ca.customer_email_hash=$2)
                 AS accepted_by_customer
                 FROM noetfield.corp_workpackets w WHERE w.deal_id=$1""",
                 item["id"],digest)
            if work and projection["payment_status"]=="PAID_LIVE":
                projection["workpacket"]={
                    "workpacket_id":str(work["id"]),
                    "state":work["state"],
                    "verified_artifact_url":work["artifact_url"] if work["state"]=="VERIFIED" else None,
                    "verifier_receipt_url":work["verifier_receipt_url"] if work["state"]=="VERIFIED" else None,
                    "cost_minor":work["cost_minor"] if work["state"]=="VERIFIED" else None,
                    "independently_verified":work["state"]=="VERIFIED",
                    "customer_accepted":bool(work["accepted_by_customer"]),
                }
                if work["accepted_by_customer"] and work["state"]=="VERIFIED":
                    projection["delivery_state"]="ACCEPTED_BY_CUSTOMER"
            else:
                projection["workpacket"]=None
            result.append(projection)
        return {"schema":"noetfield.customer-portal.v1","cases":result,
                "scope":"AUTHENTICATED_CUSTOMER_MEMBERSHIP_ONLY","cash_source":"signed_stripe_intake_bound",
                "verified_customer_identity":True, "operator_session_used":False}
    finally:
        await db.close()
