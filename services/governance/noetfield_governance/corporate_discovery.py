"""Fieldwork CORPORATE original-source readback into Noetfield research staging.

The Fieldwork source database remains canonical. Staging contains public
organization evidence, not private Fieldwork contacts or verified customers.
Only explicitly qualified sourced organizations are promoted to existing
Noetfield Corporate CRM accounts/person/deals; no automatic outreach.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urlsplit, urlunsplit
import os
import re
import uuid

import asyncpg
import httpx

from noetfield_governance.commercial_pipeline import _database_url
from noetfield_governance.corporate_crm import (
 CorporateCRMError, account_create, person_create, deal_create, schema, source_url,
)

_ALLOWED = {"fieldwork-outreach-arqant.up.railway.app"}
_CONTACT_BASIS = frozenset({
 "OPTED_IN","EXISTING_RELATIONSHIP","PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL",
 "INTRODUCED_BY_MUTUAL_CONTACT","OTHER_DOCUMENTED_BASIS",
})


def _fieldwork_config() -> tuple[str,str]:
    base=os.getenv("FIELDWORK_NOETFIELD_BRIDGE_URL","").strip().rstrip("/")
    key=os.getenv("FIELDWORK_NOETFIELD_BRIDGE_KEY","").strip()
    u=urlsplit(base)
    if (len(key)<32 or u.scheme!="https" or u.hostname not in _ALLOWED
            or u.username or u.password or u.port not in (None,443)
            or u.path not in ("","/") or u.query or u.fragment):
        raise CorporateCRMError("FIELDWORK_SCOPED_SOURCE_BRIDGE_UNCONFIGURED")
    return base,key


def _canonical(url: str) -> str:
    checked=source_url(url)
    u=urlsplit(checked)
    if not u.hostname or len(u.path)>250:
        raise CorporateCRMError("INVALID_PUBLIC_ORGANIZATION_SOURCE")
    # No source attribution query strings leak into dedup keys.
    return urlunsplit(("https",u.netloc.lower(),u.path.rstrip("/") or "/","",""))


def _valid_source(item: dict[str,Any]) -> dict[str,Any] | None:
    if not isinstance(item,dict) or item.get("identity_status")!="SOURCE_ACCOUNT_NOT_VERIFIED_CUSTOMER":
        return None
    if item.get("person_contact_exported") is not False or item.get("message_sent") is not False:
        return None
    key=str(item.get("original_source_id") or "")
    if not re.fullmatch(r"[A-Za-z0-9:_./-]{5,200}",key):
        return None
    lane=item.get("research_lane")
    if lane not in ("RWA","CORPORATE"):
        return None
    name=str(item.get("organization") or "").strip()
    if not 2<=len(name)<=180:
        return None
    try:
        profile=_canonical(str(item.get("official_source_url") or ""))
        website=source_url(str(item.get("company_website") or "")) if item.get("company_website") else ""
        evidence=source_url(str(item.get("evidence_url") or ""))
    except CorporateCRMError:
        return None
    status=str(item.get("review_status") or "DISCOVERED_ACCOUNT")
    if status in {"DO_NOT_CONTACT","DISQUALIFIED"}:
        return None
    return {"source_key":key,"organization":name,"lane":lane,
            "original_url":profile,"website":website,"evidence_url":evidence,
            "review_status":status,"score":int(item.get("original_public_research_score") or 0),
            "provider":str(item.get("source_provider") or "")[:120],
            "reviewed_at":str(item.get("reviewed_at") or "")[:80]}


async def _schema(db: asyncpg.Connection) -> None:
    await schema(db)
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_research_sources (
       source_key text PRIMARY KEY,
       organization text NOT NULL,
       lane text NOT NULL CHECK(lane IN('RWA','CORPORATE')),
       original_url text NOT NULL UNIQUE,
       website text NOT NULL DEFAULT '',
       evidence_url text NOT NULL,
       review_status text NOT NULL,
       provider text NOT NULL DEFAULT '',
       score integer NOT NULL DEFAULT 0,
       reviewed_at text NOT NULL DEFAULT '',
       imported_at timestamptz NOT NULL DEFAULT now(),
       last_sync_at timestamptz NOT NULL DEFAULT now(),
       promoted_deal_id uuid REFERENCES noetfield.corp_crm_deals(id),
       contact_basis text NOT NULL DEFAULT '',
       contact_evidence text NOT NULL DEFAULT '',
       outreach_role_relevance text NOT NULL DEFAULT '',
       publication_no_solicitation_confirmed boolean NOT NULL DEFAULT false,
       promoted_at timestamptz
    )""")
    await db.execute("""ALTER TABLE noetfield.corp_research_sources
       ADD COLUMN IF NOT EXISTS outreach_role_relevance text NOT NULL DEFAULT ''""")
    await db.execute("""ALTER TABLE noetfield.corp_research_sources
       ADD COLUMN IF NOT EXISTS publication_no_solicitation_confirmed boolean
       NOT NULL DEFAULT false""")


async def sync_corporate_research(settings: object, *, limit: int = 100,
                                  offset: int = 0) -> dict[str,Any]:
    if type(limit) is not int or not 1<=limit<=100 or type(offset) is not int or not 0<=offset<=10000:
        raise CorporateCRMError("INVALID_FIELDWORK_SOURCE_PAGE")
    base,key=_fieldwork_config()
    try:
        async with httpx.AsyncClient(timeout=10,follow_redirects=False) as client:
            response=await client.get(
              base+"/api/integrations/noetfield/corporate-sources",
              params={"limit":limit,"offset":offset},
              headers={"X-Noetfield-Corporate-Bridge":key,"Accept":"application/json"})
    except httpx.RequestError as exc:
        raise CorporateCRMError("FIELDWORK_BRIDGE_PROVIDER_UNAVAILABLE") from exc
    if response.status_code != 200:
        raise CorporateCRMError("FIELDWORK_SOURCE_BRIDGE_NOT_AUTHORIZED_OR_UNAVAILABLE")
    try:
        data=response.json()
    except ValueError as exc:
        raise CorporateCRMError("FIELDWORK_INVALID_RESPONSE") from exc
    if (not isinstance(data,dict) or
        data.get("schema")!="fieldwork.noetfield-corporate-source.v1" or
        data.get("scope")!="PUBLIC_ORGANIZATION_RESEARCH_ONLY" or
        data.get("private_contacts_exported")!=0 or
        data.get("sent_messages")!=0 or
        not isinstance(data.get("items"),list) or len(data["items"])>limit):
        raise CorporateCRMError("FIELDWORK_BRIDGE_SCOPE_VIOLATION")
    clean=[s for v in data["items"] if (s:=_valid_source(v))]
    db=await asyncpg.connect(_database_url(settings))
    try:
        await _schema(db)
        inserted=0
        async with db.transaction():
            for item in clean:
                row=await db.fetchrow("""INSERT INTO noetfield.corp_research_sources(
                    source_key,organization,lane,original_url,website,evidence_url,
                    review_status,score,provider,reviewed_at)
                    VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                    ON CONFLICT DO NOTHING RETURNING source_key""",
                    item["source_key"],item["organization"],item["lane"],
                    item["original_url"],item["website"],item["evidence_url"],
                    item["review_status"],item["score"],item["provider"],item["reviewed_at"])
                inserted+=int(bool(row))
        count=await db.fetchval("SELECT count(*)::int FROM noetfield.corp_research_sources")
        by_lane=await db.fetch("SELECT lane,count(*)::int n FROM noetfield.corp_research_sources GROUP BY lane")
        return {"provider":"FIELDWORK_ORIGINAL_PUBLIC_SOURCE",
                "scope":"RESEARCH_ONLY_NOT_VERIFIED_LEAD",
                "scanned":len(data["items"]),"accepted":len(clean),
                "created":inserted,"already_staged":len(clean)-inserted,
                "rejected":len(data["items"])-len(clean),
                "total_staged":int(count or 0),
                "staged_by_lane":{r["lane"]:int(r["n"]) for r in by_lane},
                "next_offset":data.get("next_offset"),
                "messages_sent":0,"verified_customers":0,"checkout_created":0}
    finally:
        await db.close()


async def research_board(settings: object, *, limit: int=100) -> dict[str,Any]:
    db=await asyncpg.connect(_database_url(settings))
    try:
        await _schema(db)
        rows=await db.fetch("""SELECT source_key,organization,lane,original_url,website,
                    evidence_url,review_status,score,provider,reviewed_at,imported_at,
                    promoted_deal_id
                    FROM noetfield.corp_research_sources
                    ORDER BY (promoted_deal_id IS NOT NULL),score DESC,imported_at DESC
                    LIMIT $1""",max(1,min(int(limit),100)))
        return {"schema":"noetfield.corporate-research.v1",
          "items":[{**dict(row),"promoted_deal_id":str(row["promoted_deal_id"]) if row["promoted_deal_id"] else None,
                    "imported_at":row["imported_at"].isoformat()} for row in rows],
          "total_staged":await db.fetchval("SELECT count(*)::int FROM noetfield.corp_research_sources"),
          "private_fieldwork_people_imported":0,
          "buyer_relationships_verified_by_research":0}
    finally:
        await db.close()


async def promote_corporate_source(settings: object, *, source_key: str,
            contact_name: str, contact_email: str, contact_basis: str,
            contact_evidence: str, owner: str, next_action: str,
            role_relevance: str = "", publication_no_solicitation: bool = False) -> dict[str,Any]:
    if contact_basis not in _CONTACT_BASIS:
        raise CorporateCRMError("INVALID_OUTREACH_PERMISSION_BASIS")
    if contact_basis == "PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL":
        if publication_no_solicitation is not True or len(role_relevance.strip()) < 20:
            raise CorporateCRMError("PUBLICATION_NO_SOLICITATION_AND_ROLE_RELEVANCE_REVIEW_REQUIRED")
    proof=source_url(contact_evidence)
    if not proof or not owner.strip() or not next_action.strip():
        raise CorporateCRMError("REVIEW_AND_NEXT_ACTION_REQUIRED")
    db=await asyncpg.connect(_database_url(settings))
    try:
        await _schema(db)
        # Serialize promotion for a single source while the existing CRM helpers
        # write the canonical account/contact/deal in their own DB transactions.
        await db.execute("SELECT pg_advisory_lock(hashtext($1))",source_key)
        try:
            row=await db.fetchrow("""SELECT * FROM noetfield.corp_research_sources
                                    WHERE source_key=$1""",source_key)
            if row is None:
                raise CorporateCRMError("UNKNOWN_FIELDWORK_SOURCE")
            if row["promoted_deal_id"]:
                return {"promoted":False,"idempotent":True,
                        "deal_id":str(row["promoted_deal_id"]),"outreach_sent":False}
            if row["review_status"] in {"DO_NOT_CONTACT","DISQUALIFIED"}:
                raise CorporateCRMError("SOURCE_SUPPRESSED")
            offer="rwa_technical_sprint" if row["lane"]=="RWA" else "ai_sales_os_pilot"
            account=await account_create(settings,name=row["organization"],
                  kind="asset_originator" if row["lane"]=="RWA" else "buyer",
                  sector="private_credit" if row["lane"]=="RWA" else "professional_services",
                  owner=owner,website=row["website"],notes="Source research: "+row["original_url"])
            person=await person_create(settings,account_id=account["id"],
                  full_name=contact_name,email=contact_email,
                  role="Business contact",source_ref=proof,consent_marketing=False)
            deal=await deal_create(settings,account_id=account["id"],person_id=person["id"],
                  offer=offer,owner=owner,next_action=next_action,
                  currency="usd" if row["lane"]=="RWA" else "cad",
                  estimated_minor=0,source_channel="FIELDWORK_OPERATOR_QUALIFIED",
                  summary="Source: "+row["original_url"]+" · Contact basis: "+contact_basis)
            await db.execute("""UPDATE noetfield.corp_research_sources SET
                 promoted_deal_id=$2,contact_basis=$3,contact_evidence=$4,
                 outreach_role_relevance=$5,publication_no_solicitation_confirmed=$6,
                 promoted_at=now()
                 WHERE source_key=$1""",source_key,uuid.UUID(deal["id"]),contact_basis,proof,
                 role_relevance.strip()[:500],publication_no_solicitation is True)
            return {"promoted":True,"deal_id":deal["id"],"account_id":account["id"],
                    "source_key":source_key,"contact_basis":contact_basis,"outreach_sent":False,
                    "payment_verified":False}
        finally:
            await db.execute("SELECT pg_advisory_unlock(hashtext($1))",source_key)
    finally:
        await db.close()
