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


# A completeness rubric is not an AI or recruiter decision, a verified skill,
# an accepted match, or permission to share a profile with a different venture.
PROFILE_FIELDS: dict[str, tuple[tuple[str, str], ...]] = {
    "people": (("skills", "Demonstrable skills"), ("availability", "Availability"),
               ("work_model", "Collaboration model"), ("portfolio_url", "Portfolio evidence")),
    "business": (("proposal_title", "Customer problem / project"),
                 ("proposal_url", "Reference to buyer / scope")),
    "growth": (("proposal_title", "Distribution opportunity"),
               ("proposal_url", "Distribution evidence")),
    "capital": (("proposal_title", "Investor mandate / proposal"),
                ("proposal_url", "Mandate evidence")),
    "partnership": (("proposal_title", "Partnership proposal"),
                    ("proposal_url", "Partnership reference")),
    "events": (("deadline", "Application deadline"),
               ("proposal_url", "Event or organizer reference")),
    "other": (("proposal_title", "Proposed collaboration"),
              ("proposal_url", "Reference / evidence")),
}


def qualification_readiness(meta: dict[str, Any], kind: str) -> dict[str, Any]:
    """Transparent self-report completeness, not a talent/project match score."""
    fields = (
        ("consent_contact", "Permission to contact"),
        ("offering", "What the applicant offers"),
        ("requesting", "What the applicant needs"),
        *PROFILE_FIELDS.get(kind, PROFILE_FIELDS["other"]),
    )
    present: list[str] = []
    missing: list[str] = []
    for name, label in fields:
        value = meta.get(name)
        answered = (value is True if name == "consent_contact"
                    else isinstance(value, str) and bool(value.strip()))
        (present if answered else missing).append(label)
    return {
        "score": round(100 * len(present) / len(fields)),
        "answered_count": len(present),
        "required_count": len(fields),
        "missing_fields": missing,
        "provided_fields": present,
        "basis": "SELF_REPORTED_FIELD_COMPLETENESS_ONLY",
        "qualification_status": "READY_FOR_HUMAN_REVIEW" if not missing else "NEEDS_INFORMATION",
        "match_decision": "NOT_ASSESSED",
        "identity_verified": False,
        "external_evidence_verified": False,
    }


def triage_connect_record(record: dict[str, Any], *, today: date | None = None) -> dict[str, Any] | None:
    meta = record.get("metadata") or {}
    if not isinstance(meta, dict) or meta.get("form_id") != "nfConnectWizard":
        return None
    # Synthetic smoke requests must never inflate real relationship pipeline metrics.
    if meta.get("intake_kind") == "test":
        return None
    kind = str(meta.get("topic") or meta.get("category") or "other").lower()
    if kind not in ROUTES:
        kind = "other"
    label, owner, action = ROUTES[kind]
    readiness = qualification_readiness(meta, kind)
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
    # Operator state is stored in server-generated qualification_json, never in
    # public visitor-controlled metadata. A visitor cannot pre-assign an owner.
    qualification = record.get("qualification_json") or {}
    ops = qualification.get("connect_ops") if isinstance(qualification, dict) else {}
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
        "proposal": record.get("message") or "",
        "requested_next_step": meta.get("next_step"),
        "commercial_terms_supplied": "Commercial terms:" in str(record.get("message") or ""),
        "reference_url": meta.get("proposal_url"),
        "deadline": deadline or None,
        "days_remaining": days_left,
        "suggested_owner_role": owner,
        "qualification_readiness": readiness,
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
        "interactions": ops.get("interactions") or [],
        "invitations": [
            {key: value for key, value in inv.items() if key != "token_hash"}
            for inv in list(ops.get("invitations") or []) if isinstance(inv, dict)
        ],
        "offer": str(meta.get("offering") or "")[:1200],
        "ask": str(meta.get("requesting") or "")[:1200],
        "participant_role": str(meta.get("participant_role") or "")[:80],
        "consent_contact": meta.get("consent_contact") is True,
        "assignment_status": "HUMAN_ASSIGNED" if ops.get("owner") else "ADVISORY_ONLY",
        "execution_status": "NOT_DISPATCHED",
        "verification_status": "NOT_VERIFIED",
        "outcome": None,
        "reported_outcome": ops.get("reported_outcome") if isinstance(ops.get("reported_outcome"), dict) else None,
        "reported_outcomes_count": len(ops.get("reported_outcomes") or []),
        "cash_collected": None,
    }
