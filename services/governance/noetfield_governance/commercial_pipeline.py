"""Commercial intake-to-cash ledger on existing Noetfield PostgreSQL.

A *projection* of canonical public_intakes, not a new CRM or checkout.
Only the existing HMAC-verified Stripe webhook can create payment evidence.
Every operator transition is authenticated by the existing admin-secret route.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, date, datetime
from typing import Any
from urllib.parse import urlsplit

import asyncpg

OFFER_TERMS = {
    "rwa_technical_sprint": {
        "amount_minor": 95000, "payment_minor": 47500, "currency": "usd",
        "kind": "deposit", "payment_link_id": "plink_1UbG9CJ03eJkL57JNNK0P3cY",
        "checkout_url": "https://buy.stripe.com/7sY6oI3iUaa06qmcDi1Nu0h",
    },
    "ai_sales_os_pilot": {
        "amount_minor": 75000, "payment_minor": 75000, "currency": "cad",
        "kind": "full", "payment_link_id": "plink_1UcS8RJ03eJkL57J4IMvmFuD",
        "checkout_url": "https://buy.stripe.com/14AbJ2f1C5TK6qm32I1Nu0i",
    },
}
VALID_INTAKE = re.compile(r"^INT-[A-Z0-9]{12}$")
VALID_SESSION = re.compile(r"^cs_(?:live|test)_[A-Za-z0-9]{8,}$")
VALID_SCOPE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{4,100}$")
ALLOWED_SOURCE_VECTORS = {"onchain-project", "web-intake", "external-opportunities", "general", "enterprise"}
ALLOWED_STAGES = {"QUALIFY", "SCOPE_ACCEPTED", "PAYMENT_CONFIRMED", "IN_DELIVERY", "DELIVERED", "CLOSED"}

class CommercialError(ValueError):
    """A non-sensitive, intentional operator/ledger rejection."""


def evidence_url(value: str) -> str:
    candidate = (value or "").strip()
    parsed = urlsplit(candidate)
    if (len(candidate) > 1200 or parsed.scheme != "https" or not parsed.hostname
            or parsed.username or parsed.password or parsed.fragment
            or parsed.hostname.lower() in {"localhost", "127.0.0.1", "example.com"}):
        raise CommercialError("HTTPS_EVIDENCE_URL_REQUIRED")
    return candidate


def email_hash(email: str) -> str:
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()


def paid_checkout_evidence(event: dict[str, Any]) -> dict[str, Any] | None:
    """Only paid, live, Stripe-authenticated checkout data qualifies as cash evidence."""
    event_type = str(event.get("type") or "")
    if event_type not in {"checkout.session.completed", "checkout.session.async_payment_succeeded"}:
        return None
    if event.get("livemode") is not True:
        return None
    obj = (event.get("data") or {}).get("object") or {}
    if not isinstance(obj, dict) or obj.get("payment_status") != "paid":
        return None
    session = str(obj.get("id") or "")
    event_id = str(event.get("id") or "")
    currency = str(obj.get("currency") or "").lower()
    amount = obj.get("amount_total")
    if (not VALID_SESSION.fullmatch(session) or not session.startswith("cs_live_")
            or not event_id.startswith("evt_") or type(amount) is not int
            or amount <= 0 or currency not in {"usd", "cad"}):
        return None
    customer = obj.get("customer_details") or {}
    if not isinstance(customer, dict):
        customer = {}
    return {
        "event_id": event_id[:100], "session_id": session[:140],
        "payment_intent": str(obj.get("payment_intent") or "")[:140],
        "payment_link_id": str(obj.get("payment_link") or "")[:140],
        "customer_email_hash": email_hash(str(customer.get("email") or obj.get("customer_email") or "")),
        "amount_minor": amount, "currency": currency, "livemode": True,
    }


def check_payment_match(case: dict[str, Any], evidence: dict[str, Any], *,
                        intake_email: str, payer_authorization_url: str = "") -> None:
    terms = OFFER_TERMS.get(str(case.get("offer")))
    if not terms or case.get("stage") != "SCOPE_ACCEPTED" or not case.get("acceptance_evidence"):
        raise CommercialError("ACCEPTED_SCOPE_REQUIRED")
    if evidence.get("livemode") is not True:
        raise CommercialError("LIVE_STRIPE_PAYMENT_REQUIRED")
    if (evidence.get("amount_minor") != terms["payment_minor"]
            or evidence.get("currency") != terms["currency"]):
        raise CommercialError("PAYMENT_AMOUNT_OR_CURRENCY_MISMATCH")
    # Pin to a product-specific *live Stripe account* Payment Link, not merely
    # a matching amount from some unrelated checkout or service.
    expected_link = str(terms["payment_link_id"])
    if (str(case.get("payment_link_id") or "") != expected_link
            or str(evidence.get("payment_link_id") or "") != expected_link):
        raise CommercialError("WRONG_APPROVED_PAYMENT_LINK")
    if evidence.get("customer_email_hash") != email_hash(intake_email):
        if not payer_authorization_url:
            raise CommercialError("PAYER_DIFFERENT_FROM_INTAKE_REQUIRE_AUTHORIZATION")
        evidence_url(payer_authorization_url)


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        value = json.loads(value)
    return dict(value) if isinstance(value, dict) else {}


def _database_url(settings: object) -> str:
    url = getattr(settings, "database_url", "")
    getter = getattr(url, "get_secret_value", None)
    if callable(getter):
        url = getter()
    url = str(url or "").replace("postgresql+asyncpg://", "postgresql://")
    if not url.startswith(("postgresql://", "postgres://")):
        raise CommercialError("POSTGRES_COMMERCIAL_LEDGER_NOT_CONFIGURED")
    return url


async def _prepare(db: asyncpg.Connection) -> None:
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.commercial_payment_evidence (
      event_id text PRIMARY KEY,
      session_id text UNIQUE NOT NULL,
      payment_intent text,
      payment_link_id text,
      customer_email_hash text NOT NULL,
      amount_minor bigint NOT NULL,
      currency text NOT NULL,
      livemode boolean NOT NULL,
      source_intake_id text UNIQUE,
      payer_authorization_url text,
      reversed boolean NOT NULL DEFAULT false,
      received_at timestamptz NOT NULL DEFAULT now(),
      bound_at timestamptz
    )""")
    await db.execute("""CREATE INDEX IF NOT EXISTS commercial_payment_intent_idx
      ON noetfield.commercial_payment_evidence (payment_intent)""")


async def capture_stripe_payment(settings: object, event: dict[str, Any]) -> dict[str, object]:
    """Called only *after* Stripe signature verification, on the existing webhook."""
    receipt = paid_checkout_evidence(event)
    if not receipt:
        # A refund/dispute must not silently preserve an apparently current deposit.
        obj = (event.get("data") or {}).get("object") or {}
        event_type = str(event.get("type") or "")
        if (event.get("livemode") is True and event_type in {
            "charge.refunded", "charge.dispute.created", "charge.dispute.funds_withdrawn"
        } and isinstance(obj, dict)):
            intent = str(obj.get("payment_intent") or "")
            if intent.startswith("pi_"):
                db = await asyncpg.connect(_database_url(settings))
                try:
                    await _prepare(db)
                    await db.execute("""UPDATE noetfield.commercial_payment_evidence
                      SET reversed=true WHERE payment_intent=$1""", intent)
                finally:
                    await db.close()
                return {"captured": False, "risk": "payment_reversed", "intent": intent}
        return {"captured": False}
    db = await asyncpg.connect(_database_url(settings))
    try:
        await _prepare(db)
        await db.execute("""INSERT INTO noetfield.commercial_payment_evidence (
             event_id,session_id,payment_intent,payment_link_id,
             customer_email_hash,amount_minor,currency,livemode
           ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
           ON CONFLICT DO NOTHING""",
           receipt["event_id"], receipt["session_id"], receipt["payment_intent"],
           receipt["payment_link_id"], receipt["customer_email_hash"],
           receipt["amount_minor"], receipt["currency"], True)
    finally:
        await db.close()
    return {"captured": True, "event_id": receipt["event_id"]}


async def operate(settings: object, *, intake_id: str, action: str,
                  expected_revision: int | None = None, offer: str = "",
                  owner: str = "", next_action: str = "", due_date: str = "",
                  scope_ref: str = "", acceptance_evidence: str = "",
                  payment_link_id: str = "", session_id: str = "",
                  payer_authorization_url: str = "", delivery_evidence: str = "",
                  acceptance_url: str = "") -> dict[str, Any]:
    """Optimistic, operator-owned lifecycle over the canonical intake source row."""
    if not VALID_INTAKE.fullmatch(intake_id):
        raise CommercialError("INVALID_SOURCE_INTAKE")
    if action not in {"open", "scope", "reconcile_payment", "start_delivery", "deliver", "close"}:
        raise CommercialError("INVALID_COMMERCIAL_ACTION")
    if due_date:
        try:
            date.fromisoformat(due_date)
        except ValueError as exc:
            raise CommercialError("INVALID_DUE_DATE") from exc
    accepted_delivery: tuple[str, str] | None = None
    if action in {"deliver", "close"}:
        # Centralize the only permitted DELIVERED/CLOSED evidence transition.
        # The legacy intake-level route must not bypass the CRM's independent
        # verifier, signed paid Checkout, or authenticated buyer acceptance.
        from noetfield_governance.corporate_workpacket import (
            check_accepted_delivery_for_intake, WorkPacketError,
        )
        try:
            accepted_delivery = await check_accepted_delivery_for_intake(
                settings, intake_id=intake_id,
                delivery_evidence=delivery_evidence if action == "deliver" else "",
                acceptance_url=acceptance_url if action == "deliver" else "",
            )
        except WorkPacketError as exc:
            raise CommercialError(str(exc)) from exc
    db = await asyncpg.connect(_database_url(settings))
    try:
        await _prepare(db)
        async with db.transaction():
            row = await db.fetchrow("""SELECT intake_id,request_id,contact_email,vector,metadata,
                  qualification_json FROM noetfield.public_intakes
                  WHERE intake_id=$1 FOR UPDATE""", intake_id)
            if row is None:
                raise CommercialError("SOURCE_INTAKE_NOT_FOUND")
            metadata = _as_dict(row["metadata"])
            from noetfield_governance.intake_test import is_test_intake
            if (is_test_intake(metadata=metadata,request_id=row["request_id"],
                               contact_email=str(row["contact_email"] or "")) or
                str(row["vector"] or "") not in ALLOWED_SOURCE_VECTORS):
                raise CommercialError("UNSUPPORTED_OR_SYNTHETIC_INTAKE")
            qual = _as_dict(row["qualification_json"])
            case = _as_dict(qual.get("commercial_ops"))
            revision = int(case.get("revision") or 0)
            if expected_revision is not None and expected_revision != revision:
                raise CommercialError("COMMERCIAL_REVISION_CONFLICT")
            if action == "open":
                if offer not in OFFER_TERMS or not owner.strip() or not next_action.strip():
                    raise CommercialError("OFFER_OWNER_NEXT_ACTION_REQUIRED")
                if case and case.get("offer") != offer:
                    raise CommercialError("CASE_ALREADY_OPEN_DIFFERENT_OFFER")
                if not case:
                    case = {"offer": offer, "stage": "QUALIFY"}
                case.update(owner=owner.strip()[:120], next_action=next_action.strip()[:350],
                            due_date=due_date or None)
            elif not case:
                raise CommercialError("COMMERCIAL_CASE_NOT_OPEN")
            elif action == "scope":
                if case.get("stage") not in {"QUALIFY", "SCOPE_ACCEPTED"}:
                    raise CommercialError("SCOPE_STAGE_CONFLICT")
                if not VALID_SCOPE.fullmatch(scope_ref):
                    raise CommercialError("SIGNED_SCOPE_REFERENCE_REQUIRED")
                expected_link = OFFER_TERMS[case["offer"]]["payment_link_id"]
                if payment_link_id and payment_link_id != expected_link:
                    raise CommercialError("WRONG_APPROVED_PAYMENT_LINK")
                case.update(scope_ref=scope_ref, acceptance_evidence=evidence_url(acceptance_evidence),
                            payment_link_id=expected_link, stage="SCOPE_ACCEPTED",
                            next_action="Reconcile the approved Stripe payment using a signed paid Checkout event")
            elif action == "reconcile_payment":
                if not VALID_SESSION.fullmatch(session_id):
                    raise CommercialError("CHECKOUT_SESSION_ID_REQUIRED")
                evidence = await db.fetchrow("""SELECT event_id,session_id,payment_link_id,
                    customer_email_hash,amount_minor,currency,livemode,source_intake_id,reversed
                    FROM noetfield.commercial_payment_evidence WHERE session_id=$1 FOR UPDATE""",
                    session_id)
                if evidence is None:
                    raise CommercialError("SIGNED_STRIPE_EVENT_NOT_FOUND")
                evidence = dict(evidence)
                if evidence["reversed"]:
                    raise CommercialError("PAYMENT_REFUNDED_OR_DISPUTED")
                if evidence["source_intake_id"] not in (None, intake_id):
                    raise CommercialError("STRIPE_SESSION_BOUND_TO_ANOTHER_CASE")
                if (case.get("stage") in {"PAYMENT_CONFIRMED","IN_DELIVERY","DELIVERED","CLOSED"}
                        and case.get("payment_session_id") == session_id):
                    return {"intake_id": intake_id, **case, "idempotent": True}
                check_payment_match(case, evidence, intake_email=str(row["contact_email"]),
                                    payer_authorization_url=payer_authorization_url)
                await db.execute("""UPDATE noetfield.commercial_payment_evidence
                  SET source_intake_id=$2,payer_authorization_url=$3,bound_at=now()
                  WHERE session_id=$1""",session_id,intake_id,payer_authorization_url or None)
                case.update(stage="PAYMENT_CONFIRMED",payment_session_id=session_id,
                            payment_event_id=evidence["event_id"],
                            next_action="Open a delivery workpacket in the existing RWA Clinic / Company OS")
            elif action == "start_delivery":
                if case.get("stage") != "PAYMENT_CONFIRMED":
                    raise CommercialError("CONFIRMED_PAYMENT_REQUIRED_FOR_DELIVERY")
                receipt = await db.fetchrow("""SELECT reversed,livemode,source_intake_id
                    FROM noetfield.commercial_payment_evidence
                    WHERE session_id=$1""",case.get("payment_session_id"))
                if not receipt or receipt["reversed"] or not receipt["livemode"] or receipt["source_intake_id"]!=intake_id:
                    raise CommercialError("PAYMENT_NO_LONGER_CLEAR_FOR_DELIVERY")
                case.update(stage="IN_DELIVERY",next_action=next_action.strip()[:350] or
                            "Produce and independently check the scoped deliverable")
            elif action in {"deliver", "close"}:
                if (action == "deliver" and case.get("stage") != "IN_DELIVERY"):
                    raise CommercialError("DELIVERY_NOT_IN_PROGRESS")
                if (action == "close" and case.get("stage") != "DELIVERED"):
                    raise CommercialError("ACCEPTED_DELIVERY_REQUIRED_TO_CLOSE")
                if accepted_delivery is None:
                    raise CommercialError("INDEPENDENT_DELIVERY_EVIDENCE_REQUIRED")
                actual_artifact, actual_acceptance = accepted_delivery
                # Source-bound live payment is rechecked and row-locked inside
                # the canonical intake transaction before state is persisted.
                proof = await db.fetchrow("""SELECT reversed,livemode,source_intake_id,bound_at,
                    event_id FROM noetfield.commercial_payment_evidence
                    WHERE session_id=$1 FOR UPDATE""",case.get("payment_session_id"))
                if (not proof or proof["reversed"] or not proof["livemode"]
                        or proof["source_intake_id"] != intake_id
                        or not proof["bound_at"]
                        or proof["event_id"] != case.get("payment_event_id")):
                    raise CommercialError("CURRENT_BOUND_LIVE_PAYMENT_REQUIRED")
                if action == "deliver":
                    case.update(stage="DELIVERED",delivery_evidence=actual_artifact,
                                customer_acceptance=actual_acceptance,
                                next_action="Invite a repeat engagement or a permitted customer referral")
                else:
                    if (case.get("delivery_evidence") != actual_artifact
                            or case.get("customer_acceptance") != actual_acceptance):
                        raise CommercialError("RECORDED_DELIVERY_EVIDENCE_MISMATCH")
                    case["stage"] = "CLOSED"
            case["revision"] = revision + 1
            case["terms"] = OFFER_TERMS[case["offer"]]
            case["updated_at"] = datetime.now(UTC).isoformat()
            qual["commercial_ops"] = case
            await db.execute("""UPDATE noetfield.public_intakes SET qualification_json=$2::jsonb
                WHERE intake_id=$1""", intake_id, json.dumps(qual))
            return {"intake_id": intake_id, **case}
    finally:
        await db.close()


async def readback(settings: object, *, limit: int = 50) -> dict[str, Any]:
    """Admin-only, PII-free case funnel; no inferred money or claimed conversions."""
    db = await asyncpg.connect(_database_url(settings))
    try:
        await _prepare(db)
        rows = await db.fetch("""SELECT intake_id,created_at,
            qualification_json->'commercial_ops' AS commercial
            FROM noetfield.public_intakes
            WHERE qualification_json ? 'commercial_ops'
            ORDER BY created_at DESC LIMIT $1""",max(1,min(limit,100)))
        items = []
        for row in rows:
            case = _as_dict(row["commercial"])
            session = case.get("payment_session_id")
            payment = None
            if session:
                evidence = await db.fetchrow("""SELECT event_id,amount_minor,currency,
                    livemode,reversed,source_intake_id
                    FROM noetfield.commercial_payment_evidence WHERE session_id=$1""",session)
                if evidence:
                    payment = {"event_id": evidence["event_id"],
                               "amount_minor": evidence["amount_minor"],
                               "currency": evidence["currency"],
                               "status": "REVERSED" if evidence["reversed"] else "PAID_LIVE",
                               "bound_to_source": evidence["source_intake_id"] == row["intake_id"]}
            items.append({"intake_id":row["intake_id"],"stage":case.get("stage"),
                          "offer":case.get("offer"),"owner":case.get("owner"),
                          "next_action":case.get("next_action"),"due_date":case.get("due_date"),
                          "revision":case.get("revision"),"scope_ref":case.get("scope_ref"),
                          "delivery_evidence":case.get("delivery_evidence"),
                          "customer_acceptance":case.get("customer_acceptance"),"payment":payment})
        return {"schema":"noetfield.commercial-funnel.v1", "items":items,
                "case_count":len(items), "source":"noetfield.public_intakes + signed Stripe webhook evidence",
                "no_customer_pii":True, "cash_definition":"paid_live_receipt_and_bound_scope_not_refund"}
    finally:
        await db.close()
