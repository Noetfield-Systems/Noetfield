"""Corporate revenue operations on top of the canonical Noetfield CRM.

P0 recovery of missed historical intakes, P1 evidence-labeled revenue
intelligence and P2 agent-ready next-action queue. No parallel CRM, raw
Fieldwork contact migration, unverified outreach or fabricated receipts.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo
from typing import Any

import asyncpg

from noetfield_governance.commercial_pipeline import _database_url
from noetfield_governance.corporate_crm import (
    CorporateCRMError, dashboard, import_intake, inbound_offer, schema, validate_intake,
)

_VANCOUVER = ZoneInfo("America/Vancouver")
_TERMINAL = frozenset({"DELIVERED", "RETAINED", "LOST"})
_MAX_SCAN = 200


def today() -> str:
    return datetime.now(_VANCOUVER).date().isoformat()


def outreach_draft(deal: dict[str, Any]) -> dict[str, str]:
    """Draft only; no claims of prior contact, ROI, budget, or signed consent."""
    company = str(deal.get("account_name") or "").strip()[:160]
    offer = deal.get("offer")
    if offer == "rwa_technical_sprint":
        subject = "RWA technical readiness discussion"
        opening = ("We help asset operators examine ownership, data, investor-facing "
                   "controls and execution readiness before committing to a larger mandate.")
        question = "Would a short discussion about a scoped RWA Technical Sprint be useful?"
    elif offer == "ai_sales_os_pilot":
        subject = "AI Sales OS pilot — workflow discovery"
        opening = ("Noetfield helps teams assess lead qualification, follow-up "
                   "and sales operations workflows through a bounded AI Sales OS pilot.")
        question = "Would a brief workflow discovery call be relevant?"
    elif offer == "strategic_partnership":
        subject = "Potential corporate collaboration"
        opening = ("Noetfield is exploring practical delivery and referral "
                   "partnerships linked to defined customer outcomes.")
        question = "Is there an appropriate person to discuss potential collaboration?"
    else:
        subject = "Operations workflow discussion"
        opening = ("Noetfield supports scoped operational automation "
                   "and AI implementation for commercial teams.")
        question = "Would it be useful to compare your current workflow priorities?"
    return {
        "subject": subject,
        "body": ("Hello" + (" " + company + " team" if company else "") + ",\n\n"
                 + opening + "\n\n" + question
                 + "\n\nBest,\nNoetfield Systems"),
        "status": "DRAFT_ONLY_NOT_SENT",
        "delivery_provider_ack": False,
    }


def build_revenue_plan(board: dict[str, Any], *, as_of: str | None = None) -> dict[str, Any]:
    """Deterministic, explainable task recommendations from verified CRM state."""
    current = as_of or today()
    rows = board.get("deals") or []
    tasks: list[dict[str, Any]] = []
    forecast: dict[str, int] = {"USD": 0, "CAD": 0}
    stages: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    for item in rows:
        stage = str(item.get("stage") or "NEW")
        stages[stage] += 1
        sources["sourced" if item.get("source_intake_id") else "manual"] += 1
        currency = str(item.get("currency") or "cad").upper()
        value = int(item.get("estimated_minor") or 0)
        if currency in forecast and value >= 0 and stage not in _TERMINAL:
            forecast[currency] += value
        if stage in _TERMINAL:
            continue
        score, reasons = 0, []
        due = str(item.get("next_date") or "")
        paid = (item.get("payment") or {}).get("status")
        if paid == "REVERSED":
            score += 100
            reasons.append("Payment reversal: verify ledger and contact the owner")
        if due and due <= current:
            score += 45
            reasons.append("Follow-up is due or overdue")
        if not due:
            score += 30
            reasons.append("Follow-up date missing")
        if not item.get("source_intake_id"):
            score += 20
            reasons.append("Manually sourced; qualify buyer before scope or checkout")
        if stage in ("SIGNED", "IN_DELIVERY") and paid != "PAID_LIVE":
            score += 40
            reasons.append("Advanced stage without independently verified paid Checkout")
        if not item.get("contact_name"):
            score += 10
            reasons.append("Decision-maker not linked")
        if not reasons:
            score += 5
            reasons.append("Continue the existing next action")
        tasks.append({
            "deal_id": str(item.get("id") or ""), "account": str(item.get("account_name") or ""),
            "offer": str(item.get("offer") or ""), "stage": stage,
            "owner": str(item.get("owner") or "UNASSIGNED"),
            "due": due or None, "next_action": str(item.get("next_action") or ""),
            "score": score,
            "priority": "CRITICAL" if score >= 90 else ("HIGH" if score >= 45 else "NORMAL"),
            "reasons": reasons, "draft": outreach_draft(item),
            "execution_state": "SUGGESTED_NOT_EXECUTED",
        })
    tasks.sort(key=lambda r: (-r["score"], r["due"] or "9999-12-31", r["deal_id"]))
    metrics = board.get("metrics") or {}
    paid = metrics.get("paid_verified_by_currency_minor") or {}
    return {
        "schema": "noetfield.corporate-revenue-ops.v1",
        "as_of_vancouver": current,
        "scope": "NOETFIELD_CORPORATE_ONLY",
        "source": "canonical_corporate_crm_and_signed_stripe_projection",
        "sampled_deals": len(rows), "total_deals": int(board.get("total_deals") or 0),
        "sample_is_complete": len(rows) >= int(board.get("total_deals") or 0),
        "sales_stages_sample": dict(sorted(stages.items())),
        "source_coverage_sample": dict(sorted(sources.items())),
        "forecast_estimated_minor_sample": forecast,
        "matched_paid_checkouts_minor_all": {
            "USD": int(paid.get("USD") or 0), "CAD": int(paid.get("CAD") or 0)
        },
        "paid_is_not_bank_settlement": True,
        "ownerless_count_all": int(metrics.get("without_owner") or 0),
        "due_count_all": int(metrics.get("due") or 0),
        "actions": tasks[:60],
        "next_step": "Work real sourced leads toward qualification, accepted scope, verified Stripe payment, and accepted delivery",
        "external_outreach_sent": False, "customer_billing_initiated": False,
        "delivery_dispatched": False, "provider_acknowledgements": 0,
    }


async def revenue_plan(settings: object) -> dict[str, Any]:
    # Existing board independently verifies cash by signed Stripe event.
    data = await dashboard(settings, limit=200)
    return build_revenue_plan(data)


async def recover_intakes(settings: object, *, execute: bool = False, limit: int = 80) -> dict[str, Any]:
    """Idempotent backfill; preview by default, never sends customer communications.

    Only historical Noetfield capital or corporate Connect inbound is eligible.
    Every proposed record passes the same synthetic/venture/source checks used
    for online intake and remains tied to its canonical INT ID.
    """
    if type(limit) is not int or not 1 <= limit <= 100:
        raise CorporateCRMError("INVALID_BACKFILL_LIMIT")
    db = await asyncpg.connect(_database_url(settings))
    try:
        await schema(db)
        source_rows = await db.fetch("""SELECT i.intake_id,i.request_id,i.contact_email,
                  i.vector,i.metadata
             FROM noetfield.public_intakes i
             WHERE ((i.vector='onchain-project' AND i.metadata->>'form_id'='nfCapitalIntake')
               OR (i.vector='external-opportunities' AND i.metadata->>'form_id'='nfConnectWizard'
                   AND i.metadata->>'initiative'='noetfield'))
               AND NOT EXISTS (
                 SELECT 1 FROM noetfield.corp_crm_deals d
                  WHERE d.source_intake_id=i.intake_id)
             ORDER BY i.created_at ASC, i.intake_id ASC
             LIMIT $1""", _MAX_SCAN)
    finally:
        await db.close()
    candidates = []
    rejected = 0
    for item in source_rows:
        record = dict(item)
        try:
            validate_intake(record)
            offer = inbound_offer(SimpleNamespace(**record))
            if not offer:
                rejected += 1
                continue
            candidates.append({"intake_id": str(record["intake_id"]),
                               "offer": offer[0], "currency": offer[1],
                               "estimated_minor": offer[2]})
        except (CorporateCRMError, TypeError, ValueError):
            rejected += 1
        if len(candidates) >= limit:
            break
    report: dict[str, Any] = {
        "mode": "EXECUTE" if execute else "PREVIEW", "scanned": len(source_rows),
        "eligible": len(candidates), "excluded_or_invalid": rejected,
        "candidates": candidates if not execute else [],
        "imported": 0, "failed": 0, "imported_ids": [], "failed_ids": [],
        "outreach_sent": False, "payment_claimed": False,
        "has_more_to_scan": len(source_rows) == _MAX_SCAN,
    }
    if not execute:
        return report
    due = (datetime.now(_VANCOUVER).date() + timedelta(days=1)).isoformat()
    for candidate in candidates:
        try:
            result = await import_intake(
                settings, intake_id=candidate["intake_id"],
                offer=candidate["offer"], currency=candidate["currency"],
                estimated_minor=candidate["estimated_minor"],
                owner="Noetfield Revenue",
                next_action="Review sourced enquiry; qualify buyer, decision-maker and scope",
                next_date=due,
            )
            if result.get("deal", {}).get("id"):
                report["imported"] += 1
                report["imported_ids"].append(candidate["intake_id"])
            else:
                report["failed"] += 1
                report["failed_ids"].append(candidate["intake_id"])
        except Exception:
            # Missing source or DB issue is not a sales success. Preserve IDs for retry.
            report["failed"] += 1
            report["failed_ids"].append(candidate["intake_id"])
    return report
