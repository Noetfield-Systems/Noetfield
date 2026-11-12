"""Advisory projection over the existing Noetfield Connect intake records."""
from datetime import date, datetime, timezone
from typing import Any

ROUTES = {
    "business": ("Revenue / customer", "Sales owner", "Qualify buyer, budget, and pilot scope"),
    "growth": ("Distribution / GTM", "Growth owner", "Validate reach, referral terms, and commercial upside"),
    "capital": ("Investor / capital", "Founder", "Verify investor mandate and terms"),
    "partnership": ("Strategic partnership", "Partnerships owner", "Define mutual value and a scoped next step"),
    "people": ("Talent / collaborators", "Workforce owner", "Qualify role, capabilities, and availability"),
    "events": ("Events / awards", "Partnerships owner", "Verify organizer, criteria, fees, deadline, and value"),
    "other": ("General opportunity", "Operations owner", "Clarify proposal and assign a qualified owner"),
}


def triage_connect_record(record: dict[str, Any], *, today: date | None = None) -> dict[str, Any] | None:
    meta = record.get("metadata") or {}
    if not isinstance(meta, dict) or meta.get("form_id") != "nfConnectWizard":
        return None
    kind = str(meta.get("topic") or meta.get("category") or "other").lower()
    if kind not in ROUTES:
        kind = "other"
    label, owner, action = ROUTES[kind]
    deadline = str(meta.get("deadline") or "").strip()[:32]
    today = today or datetime.now(timezone.utc).date()
    days_left = None
    if deadline:
        try:
            days_left = (date.fromisoformat(deadline) - today).days
        except ValueError:
            pass
    score = 35
    reasons = ["New unreviewed submission"]
    if meta.get("proposal_url"):
        score += 10
        reasons.append("Reference URL supplied, not verified")
    if meta.get("proposal_title"):
        score += 5
    if kind in ("business", "growth"):
        score += 20
        reasons.append("Potential near-term commercial relevance")
    elif kind in ("capital", "partnership"):
        score += 10
    if days_left is not None and days_left <= 7:
        score += 15
        reasons.append("Deadline within 7 days or overdue")
    if days_left is not None and days_left < 0:
        reasons.append("Deadline has passed")
    ops = meta.get("connect_ops") or {}
    if not isinstance(ops, dict):
        ops = {}
    return {
        "intake_id": record.get("intake_id"),
        "request_id": record.get("request_id"),
        "received_at": record.get("created_at"),
        "person": record.get("contact_name"),
        "organization": record.get("organization"),
        "email": record.get("contact_email"),
        "source": meta.get("lead_source") or record.get("source"),
        "initiative": meta.get("initiative") or "portfolio",
        "opportunity_type": kind,
        "opportunity_label": label,
        "title": meta.get("proposal_title"),
        "reference_url": meta.get("proposal_url"),
        "deadline": deadline or None,
        "days_remaining": days_left,
        "suggested_owner_role": owner,
        "suggested_next_action": action,
        "priority_score": min(100, score),
        "priority_reasons": reasons,
        "stage": ops.get("stage") or "NEW",
        "owner": ops.get("owner") or None,
        "next_action": ops.get("next_action") or None,
        "next_action_due": ops.get("due_date") or None,
        "operator_note": ops.get("note") or None,
        "revision": ops.get("revision", 0),
        "updated_at": ops.get("updated_at"),
        "activity": ops.get("history") or [],
        "assignment_status": "HUMAN_ASSIGNED" if ops.get("owner") else "ADVISORY_ONLY",
        "execution_status": "NOT_DISPATCHED",
        "verification_status": "NOT_VERIFIED",
        "outcome": None,
        "cash_collected": None,
    }
