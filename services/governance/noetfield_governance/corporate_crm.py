"""Noetfield Corporate CRM: its own accounts, people and enterprise opportunities.

Company-specific PostgreSQL records, built on the existing Platform API, not the
Web3 Fieldwork contact database. Public Connect intakes remain the canonical
inbound source. Live cash is read from the signed Stripe commercial ledger only.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, date, datetime
from typing import Any
from urllib.parse import urlsplit

import asyncpg

from noetfield_governance.commercial_pipeline import _database_url, _prepare as prepare_payment_evidence
from noetfield_governance.intake_test import is_test_intake

KIND = frozenset({"buyer", "asset_originator", "referral_partner", "delivery_partner",
                  "capital_partner", "advisor", "other"})
SECTOR = frozenset({"private_credit", "real_estate", "business_acquisition",
                    "financial_services", "professional_services", "technology",
                    "industry", "other"})
OFFER = frozenset({"rwa_technical_sprint", "ai_sales_os_pilot", "asset_administration",
                   "business_automation", "strategic_partnership", "other"})
STAGE = frozenset({"NEW", "QUALIFYING", "DISCOVERY", "SCOPE_SENT", "NEGOTIATING",
                   "SIGNED", "IN_DELIVERY", "DELIVERED", "RETAINED", "LOST"})
ACTIVITY = frozenset({"NOTE", "CALL_ATTEMPT", "EMAIL_SENT_REPORTED", "REPLY_REPORTED",
                      "MEETING_BOOKED_REPORTED", "MEETING_HELD", "SCOPE_SENT",
                      "SCOPE_SIGNED", "REFERRAL_PROPOSED", "REFERRAL_ACCEPTED",
                      "DELIVERY_ACCEPTED", "FOLLOWUP_COMPLETED"})
EVIDENCE_ACTIVITY = frozenset({"EMAIL_SENT_REPORTED", "REPLY_REPORTED",
    "MEETING_BOOKED_REPORTED", "MEETING_HELD", "SCOPE_SIGNED",
    "REFERRAL_ACCEPTED", "DELIVERY_ACCEPTED"})
SOURCE_VECTORS = frozenset({"onchain-project", "external-opportunities", "contact",
                             "web-intake", "enterprise", "ai-value-governance-os", "general"})
INTAKE_RE = re.compile(r"^INT-[A-Z0-9]{12}$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class CorporateCRMError(ValueError):
    pass


def required(value: str, max_length: int, label: str) -> str:
    if not isinstance(value, str):
        raise CorporateCRMError("INVALID_" + label)
    result = value.strip()
    if not result or len(result) > max_length:
        raise CorporateCRMError("INVALID_" + label)
    return result


def bounded(value: str | None, limit: int) -> str:
    if not isinstance(value, str) or len(value) > limit:
        raise CorporateCRMError("INVALID_TEXT_LENGTH")
    return value.strip()


def source_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlsplit(url)
    if (len(url) > 1000 or parsed.scheme != "https" or not parsed.hostname
            or parsed.username or parsed.password or any(x.isspace() for x in url)):
        raise CorporateCRMError("HTTPS_SOURCE_REQUIRED")
    return url


def choices(value: str, allowed: frozenset[str], label: str) -> str:
    if value not in allowed:
        raise CorporateCRMError("INVALID_" + label)
    return value


def date_only(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CorporateCRMError("INVALID_NEXT_DATE") from exc


def uuid_text(value: str, label: str) -> str:
    if not UUID_RE.fullmatch(value):
        raise CorporateCRMError("INVALID_" + label)
    return value


def normalize_account(value: str) -> str:
    return re.sub(r"\s+", " ", required(value, 200, "ACCOUNT_NAME")).casefold()


def json_obj(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        value = json.loads(value)
    return dict(value) if isinstance(value, dict) else {}


def as_row(row: Any) -> dict[str, Any]:
    data = dict(row)
    for key, value in tuple(data.items()):
        if isinstance(value, uuid.UUID):
            data[key] = str(value)
        elif isinstance(value, (datetime, date)):
            data[key] = value.isoformat()
    return data


async def schema(db: asyncpg.Connection) -> None:
    """Isolated corporate identities with canonical intake and cash crossrefs."""
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_crm_accounts (
        id uuid PRIMARY KEY, normalized_name text NOT NULL UNIQUE,
        name text NOT NULL, website text NOT NULL DEFAULT '',
        kind text NOT NULL, sector text NOT NULL, country text NOT NULL DEFAULT '',
        owner text NOT NULL, notes text NOT NULL DEFAULT '',
        created_at timestamptz NOT NULL DEFAULT now(),
        updated_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_crm_people (
        id uuid PRIMARY KEY, account_id uuid NOT NULL
          REFERENCES noetfield.corp_crm_accounts(id),
        full_name text NOT NULL, email text NOT NULL DEFAULT '',
        role text NOT NULL DEFAULT '', consent_marketing boolean NOT NULL DEFAULT false,
        source_ref text NOT NULL DEFAULT '',
        created_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS corp_crm_people_email_unique
        ON noetfield.corp_crm_people (account_id, lower(email)) WHERE email <> ''""")
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_crm_deals (
        id uuid PRIMARY KEY, account_id uuid NOT NULL REFERENCES noetfield.corp_crm_accounts(id),
        person_id uuid REFERENCES noetfield.corp_crm_people(id),
        source_intake_id text, referrer_account_id uuid REFERENCES noetfield.corp_crm_accounts(id),
        offer text NOT NULL, stage text NOT NULL DEFAULT 'NEW',
        estimated_minor bigint NOT NULL DEFAULT 0, currency text NOT NULL,
        owner text NOT NULL, next_action text NOT NULL, next_date date,
        source_channel text NOT NULL DEFAULT 'manual',
        summary text NOT NULL DEFAULT '',
        accepted_scope_url text NOT NULL DEFAULT '',
        revision integer NOT NULL DEFAULT 0,
        created_at timestamptz NOT NULL DEFAULT now(),
        updated_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS corp_crm_intake_offer_unique
        ON noetfield.corp_crm_deals(source_intake_id,offer)
        WHERE source_intake_id IS NOT NULL""")
    await db.execute("""CREATE INDEX IF NOT EXISTS corp_crm_due_idx
        ON noetfield.corp_crm_deals(stage,next_date,owner)""")
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_crm_activities (
        id uuid PRIMARY KEY, deal_id uuid NOT NULL REFERENCES noetfield.corp_crm_deals(id),
        kind text NOT NULL, actor text NOT NULL,
        note text NOT NULL, evidence_url text NOT NULL DEFAULT '',
        source_status text NOT NULL DEFAULT 'OPERATOR_REPORTED',
        created_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""CREATE INDEX IF NOT EXISTS corp_crm_activity_timeline
        ON noetfield.corp_crm_activities(deal_id,created_at DESC)""")


async def account_create(settings: object, *, name: str, kind: str, sector: str,
                         owner: str, website: str = "", country: str = "",
                         notes: str = "") -> dict[str, Any]:
    clean_name = required(name, 200, "ACCOUNT_NAME")
    clean_owner = required(owner, 100, "OWNER")
    domain = source_url(website)
    record_id = uuid.uuid4()
    db = await asyncpg.connect(_database_url(settings))
    try:
        await schema(db)
        row = await db.fetchrow("""INSERT INTO noetfield.corp_crm_accounts
          (id,normalized_name,name,website,kind,sector,country,owner,notes)
          VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)
          ON CONFLICT(normalized_name) DO UPDATE
          SET updated_at = noetfield.corp_crm_accounts.updated_at
          RETURNING *""",
          record_id, normalize_account(clean_name), clean_name, domain,
          choices(kind,KIND,"ACCOUNT_KIND"),choices(sector,SECTOR,"SECTOR"),
          bounded(country,80), clean_owner, bounded(notes,2000))
        return as_row(row)
    finally:
        await db.close()


async def person_create(settings: object, *, account_id: str, full_name: str,
                        email: str = "", role: str = "", source_ref: str = "",
                        consent_marketing: bool = False) -> dict[str, Any]:
    account = uuid.UUID(uuid_text(account_id, "ACCOUNT_ID"))
    person = required(full_name,140,"PERSON_NAME")
    clean_email = bounded(email,254).lower()
    if clean_email and not EMAIL_RE.fullmatch(clean_email):
        raise CorporateCRMError("INVALID_CONTACT_EMAIL")
    db = await asyncpg.connect(_database_url(settings))
    try:
        await schema(db)
        if not await db.fetchval("SELECT 1 FROM noetfield.corp_crm_accounts WHERE id=$1",account):
            raise CorporateCRMError("ACCOUNT_NOT_FOUND")
        row = await db.fetchrow("""INSERT INTO noetfield.corp_crm_people
          (id,account_id,full_name,email,role,consent_marketing,source_ref)
          VALUES($1,$2,$3,$4,$5,$6,$7)
          ON CONFLICT (account_id, lower(email)) WHERE email <> ''
          DO UPDATE SET full_name=EXCLUDED.full_name,role=EXCLUDED.role,
                        source_ref=EXCLUDED.source_ref
          RETURNING *""", uuid.uuid4(),account,person,clean_email,
          bounded(role,140),bool(consent_marketing),source_url(source_ref))
        return as_row(row)
    finally:
        await db.close()


async def deal_create(settings: object, *, account_id: str, offer: str,
                      owner: str, next_action: str, currency: str,
                      estimated_minor: int = 0, next_date: str = "",
                      person_id: str = "", source_intake_id: str = "",
                      source_channel: str = "manual",
                      referrer_account_id: str = "", summary: str = "") -> dict[str, Any]:
    account = uuid.UUID(uuid_text(account_id,"ACCOUNT_ID"))
    person = uuid.UUID(uuid_text(person_id,"PERSON_ID")) if person_id else None
    referral = uuid.UUID(uuid_text(referrer_account_id,"REFERRER_ACCOUNT_ID")) if referrer_account_id else None
    source_id = source_intake_id.strip().upper() or None
    if source_id and not INTAKE_RE.fullmatch(source_id):
        raise CorporateCRMError("INVALID_SOURCE_INTAKE_ID")
    if type(estimated_minor) is not int or not 0 <= estimated_minor <= 10**12:
        raise CorporateCRMError("INVALID_ESTIMATED_AMOUNT")
    if currency not in {"cad","usd"}:
        raise CorporateCRMError("INVALID_CURRENCY")
    db = await asyncpg.connect(_database_url(settings))
    try:
        await schema(db)
        if not await db.fetchval("SELECT 1 FROM noetfield.corp_crm_accounts WHERE id=$1",account):
            raise CorporateCRMError("ACCOUNT_NOT_FOUND")
        if person and not await db.fetchval("""SELECT 1 FROM noetfield.corp_crm_people
                WHERE id=$1 AND account_id=$2""",person,account):
            raise CorporateCRMError("PERSON_ACCOUNT_MISMATCH")
        if source_id:
            original = await db.fetchrow("""SELECT request_id,contact_email,metadata,vector
                FROM noetfield.public_intakes WHERE intake_id=$1""",source_id)
            validate_intake(original)
        row=await db.fetchrow("""INSERT INTO noetfield.corp_crm_deals(
            id,account_id,person_id,source_intake_id,referrer_account_id,
            offer,stage,estimated_minor,currency,owner,next_action,next_date,
            source_channel,summary)
            VALUES($1,$2,$3,$4,$5,$6,'NEW',$7,$8,$9,$10,$11,$12,$13)
            ON CONFLICT (source_intake_id,offer) WHERE source_intake_id IS NOT NULL
            DO UPDATE SET updated_at=noetfield.corp_crm_deals.updated_at
            RETURNING *""",uuid.uuid4(),account,person,source_id,referral,
            choices(offer,OFFER,"OFFER"),estimated_minor,currency,
            required(owner,120,"OWNER"),required(next_action,400,"NEXT_ACTION"),
            date_only(next_date),bounded(source_channel,80),bounded(summary,2200))
        return as_row(row)
    finally:
        await db.close()


def validate_intake(row: Any) -> None:
    if row is None:
        raise CorporateCRMError("SOURCE_INTAKE_NOT_FOUND")
    meta = json_obj(row["metadata"])
    if is_test_intake(metadata=meta,request_id=row["request_id"],
                      contact_email=str(row["contact_email"] or "")):
        raise CorporateCRMError("SYNTHETIC_INTAKE_NOT_A_CUSTOMER")
    if str(row["vector"] or "") not in SOURCE_VECTORS:
        raise CorporateCRMError("NON_CORPORATE_SOURCE_VECTOR")
    initiative=str(meta.get("initiative") or "").lower()
    if initiative not in ("","noetfield"):
        raise CorporateCRMError("CROSS_VENTURE_IMPORT_NOT_AUTHORIZED")


async def import_intake(settings: object, *, intake_id: str, offer: str, owner: str,
                        next_action: str, currency: str, estimated_minor: int = 0,
                        next_date: str = "") -> dict[str, Any]:
    """Import once by canonical source ID, never by merging Fieldwork identities."""
    source_id=required(intake_id,32,"SOURCE_INTAKE_ID").upper()
    if not INTAKE_RE.fullmatch(source_id):
        raise CorporateCRMError("INVALID_SOURCE_INTAKE_ID")
    db=await asyncpg.connect(_database_url(settings))
    try:
        await schema(db)
        row=await db.fetchrow("""SELECT intake_id,request_id,organization,contact_name,
                contact_email,metadata,vector FROM noetfield.public_intakes
                WHERE intake_id=$1""",source_id)
        validate_intake(row)
        org=required(row["organization"],200,"SOURCE_ORGANIZATION")
        # Existing source is never copied into Fieldwork or a venture contact route.
        account=await account_create(settings,name=org,owner=owner,
                kind="asset_originator" if offer=="rwa_technical_sprint" else "buyer",
                sector="private_credit" if offer=="rwa_technical_sprint" else "professional_services")
        person=None
        if row["contact_name"] and row["contact_email"]:
            person=await person_create(settings,account_id=account["id"],
                    full_name=row["contact_name"],email=row["contact_email"],
                    consent_marketing=False)
        deal=await deal_create(settings,account_id=account["id"],
                person_id=person["id"] if person else "",source_intake_id=source_id,
                offer=offer,owner=owner,next_action=next_action,currency=currency,
                estimated_minor=estimated_minor,next_date=next_date,
                source_channel="noetfield_connect",summary="Imported canonical Noetfield customer enquiry")
        return {"account":account,"person":person,"deal":deal,"imported_from":source_id,
                "outreach_sent":False,"payment_verified":False}
    finally:
        await db.close()


async def deal_update(settings: object, *, deal_id: str, expected_revision: int,
                      stage: str, owner: str, next_action: str,
                      next_date: str = "", estimated_minor: int = 0,
                      summary: str = "", accepted_scope_url: str = "") -> dict[str, Any]:
    identifier=uuid.UUID(uuid_text(deal_id,"DEAL_ID"))
    target=choices(stage,STAGE,"STAGE")
    if type(estimated_minor) is not int or not 0 <= estimated_minor <= 10**12:
        raise CorporateCRMError("INVALID_ESTIMATED_AMOUNT")
    scope=source_url(accepted_scope_url)
    if target in {"SIGNED","IN_DELIVERY","DELIVERED","RETAINED"} and not scope:
        raise CorporateCRMError("SIGNED_SCOPE_EVIDENCE_REQUIRED")
    db=await asyncpg.connect(_database_url(settings))
    try:
        await schema(db)
        row=await db.fetchrow("""UPDATE noetfield.corp_crm_deals SET
          stage=$3,owner=$4,next_action=$5,next_date=$6,estimated_minor=$7,
          summary=$8,accepted_scope_url=$9,revision=revision+1,updated_at=now()
          WHERE id=$1 AND revision=$2 RETURNING *""",identifier,expected_revision,target,
          required(owner,120,"OWNER"),required(next_action,400,"NEXT_ACTION"),
          date_only(next_date),estimated_minor,bounded(summary,2200),scope)
        if row is None:
            raise CorporateCRMError("DEAL_NOT_FOUND_OR_REVISION_CONFLICT")
        return as_row(row)
    finally:
        await db.close()


async def activity_create(settings: object, *, deal_id: str, kind: str,
                          actor: str, note: str, evidence_url: str = "") -> dict[str, Any]:
    identifier=uuid.UUID(uuid_text(deal_id,"DEAL_ID"))
    event=choices(kind,ACTIVITY,"ACTIVITY_KIND")
    evidence=source_url(evidence_url)
    if event in EVIDENCE_ACTIVITY and not evidence:
        raise CorporateCRMError("EXTERNAL_ACTIVITY_NEEDS_EVIDENCE")
    db=await asyncpg.connect(_database_url(settings))
    try:
        await schema(db)
        if not await db.fetchval("SELECT 1 FROM noetfield.corp_crm_deals WHERE id=$1",identifier):
            raise CorporateCRMError("DEAL_NOT_FOUND")
        row=await db.fetchrow("""INSERT INTO noetfield.corp_crm_activities(
           id,deal_id,kind,actor,note,evidence_url)
           VALUES($1,$2,$3,$4,$5,$6) RETURNING *""",
           uuid.uuid4(),identifier,event,required(actor,120,"ACTOR"),
           required(note,2000,"ACTIVITY_NOTE"),evidence)
        return as_row(row)
    finally:
        await db.close()


async def dashboard(settings: object, *, search: str = "", stage: str = "",
                    offer: str = "", limit: int = 100) -> dict[str, Any]:
    """Corporate-only private workspace with Stripe-backed actual cash status."""
    if stage and stage not in STAGE:
        raise CorporateCRMError("INVALID_STAGE")
    if offer and offer not in OFFER:
        raise CorporateCRMError("INVALID_OFFER")
    query=bounded(search,160)
    db=await asyncpg.connect(_database_url(settings))
    try:
        await schema(db)
        await prepare_payment_evidence(db)
        accounts=await db.fetch("""SELECT * FROM noetfield.corp_crm_accounts
                                     ORDER BY updated_at DESC LIMIT 120""")
        contacts=await db.fetch("""SELECT * FROM noetfield.corp_crm_people
                                     ORDER BY created_at DESC LIMIT 160""")
        rows=await db.fetch("""SELECT d.*,a.name AS account_name,
                   p.full_name AS contact_name, r.name AS referrer_name,
                   ci.qualification_json->'commercial_ops' AS commercial_case
                   FROM noetfield.corp_crm_deals d
                   JOIN noetfield.corp_crm_accounts a ON a.id=d.account_id
                   LEFT JOIN noetfield.corp_crm_people p ON p.id=d.person_id
                   LEFT JOIN noetfield.corp_crm_accounts r ON r.id=d.referrer_account_id
                   LEFT JOIN noetfield.public_intakes ci ON ci.intake_id=d.source_intake_id
                   WHERE ($1='' OR d.stage=$1) AND ($2='' OR d.offer=$2)
                     AND ($3='' OR a.name ILIKE ('%'||$3||'%')
                               OR d.summary ILIKE ('%'||$3||'%'))
                   ORDER BY CASE WHEN d.next_date IS NULL THEN 1 ELSE 0 END,
                         d.next_date ASC,d.updated_at DESC
                   LIMIT $4""",stage,offer,query,max(1,min(int(limit),200)))
        items=[]
        for row in rows:
            item=as_row(row)
            commercial=json_obj(item.pop("commercial_case"))
            receipt=None
            session=str(commercial.get("payment_session_id") or "")
            if session and item["source_intake_id"]:
                proof=await db.fetchrow("""SELECT e.event_id,e.amount_minor,e.currency,
                      e.reversed,e.livemode,e.source_intake_id
                      FROM noetfield.commercial_payment_evidence e
                      WHERE e.session_id=$1""",session)
                if proof and proof["livemode"] and proof["source_intake_id"]==item["source_intake_id"]:
                    receipt={"status":"REVERSED" if proof["reversed"] else "PAID_LIVE",
                             "amount_minor":proof["amount_minor"],
                             "currency":proof["currency"],"event_id":proof["event_id"]}
            item["payment"]=receipt
            item["scope_accepted"]=bool(commercial.get("acceptance_evidence"))
            item["commercial_stage"]=commercial.get("stage")
            item["next_due"]=bool(item["next_date"] and item["next_date"]<=date.today().isoformat()
                                 and item["stage"] not in {"LOST","DELIVERED","RETAINED"})
            items.append(item)
        amounts={}
        for item in items:
            receipt=item["payment"]
            if receipt and receipt["status"]=="PAID_LIVE":
                currency=receipt["currency"].upper()
                amounts[currency]=amounts.get(currency,0)+int(receipt["amount_minor"])
        total=await db.fetchval("SELECT count(*) FROM noetfield.corp_crm_deals")
        return {"schema":"noetfield.corporate-crm.v1","scope":"NOETFIELD_CORPORATE_ONLY",
                "accounts":[as_row(a) for a in accounts],
                "people":[as_row(p) for p in contacts],
                "deals":items,"total_deals":int(total),
                "metrics":{"open":sum(1 for d in items if d["stage"] not in {"LOST","RETAINED","DELIVERED"}),
                           "due":sum(bool(d["next_due"]) for d in items),
                           "without_owner":sum(not bool(d["owner"]) for d in items),
                           "paid_verified_by_currency_minor":amounts},
                "cash_source":"signed Stripe webhook ledger, matched to canonical scope and intake",
                "operator_activity_claims":"OPERATOR_REPORTED_NOT_PROVIDER_ATTESTED",
                "fieldwork_contact_data_included":False}
    finally:
        await db.close()


async def detail(settings: object, *, deal_id: str) -> dict[str, Any]:
    identifier=uuid.UUID(uuid_text(deal_id,"DEAL_ID"))
    db=await asyncpg.connect(_database_url(settings))
    try:
        await schema(db)
        row=await db.fetchrow("""SELECT d.*,a.name AS account_name,p.full_name AS contact_name,
              p.email AS contact_email FROM noetfield.corp_crm_deals d
              JOIN noetfield.corp_crm_accounts a ON a.id=d.account_id
              LEFT JOIN noetfield.corp_crm_people p ON p.id=d.person_id
              WHERE d.id=$1""",identifier)
        if not row:
            raise CorporateCRMError("DEAL_NOT_FOUND")
        events=await db.fetch("""SELECT * FROM noetfield.corp_crm_activities
                    WHERE deal_id=$1 ORDER BY created_at DESC LIMIT 100""",identifier)
        return {"deal":as_row(row),"activity":[as_row(x) for x in events],
                "source":"NOETFIELD_CORPORATE_CRM_ONLY"}
    finally:
        await db.close()
