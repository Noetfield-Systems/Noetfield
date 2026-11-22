"""BIJAN sidecar: evidence-backed advisor preparation for Noetfield's OWN corporate CRM.

This module is NOT the portfolio CRM, does NOT import Fieldwork contacts,
and does not claim private client preferences, messages or settled money.
"""
from __future__ import annotations
from datetime import UTC, datetime
from typing import Any

SCHEMA = "bijan.noetfield-native-crm-brief.v1"
SUPPORTED_STAGES = frozenset({
    "NEW", "QUALIFYING", "DISCOVERY", "SCOPE_SENT", "NEGOTIATING",
    "SIGNED", "IN_DELIVERY", "DELIVERED", "RETAINED", "LOST"
})
OPERATED_EVENTS = frozenset({
    "NOTE", "CALL_ATTEMPT", "EMAIL_SENT_REPORTED", "REPLY_REPORTED",
    "MEETING_BOOKED_REPORTED", "MEETING_HELD", "SCOPE_SENT",
    "SCOPE_SIGNED", "REFERRAL_PROPOSED", "REFERRAL_ACCEPTED",
    "DELIVERY_ACCEPTED", "FOLLOWUP_COMPLETED"
})

def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""

def compile_bijan_corporate_brief(snapshot: dict[str, Any], *,
                                  as_of: str | None = None) -> dict[str, Any]:
    """Stateless original-deal briefing. Caller must authenticate before reading snapshot."""
    if not isinstance(snapshot, dict) or snapshot.get("source") != "NOETFIELD_CORPORATE_CRM_ONLY":
        raise ValueError("NATIVE_CRM_SOURCE_REQUIRED")
    deal = snapshot.get("deal")
    if not isinstance(deal, dict) or not _text(deal.get("id")):
        raise ValueError("ORIGINAL_DEAL_REQUIRED")
    stage = _text(deal.get("stage"))
    if stage not in SUPPORTED_STAGES:
        raise ValueError("INVALID_ORIGINAL_STAGE")
    account = _text(deal.get("account_name"))
    if not account:
        raise ValueError("ORIGINAL_ACCOUNT_REQUIRED")
    commercial = snapshot.get("commercial_case") or {}
    activities = snapshot.get("activity") or []
    if not isinstance(commercial, dict) or not isinstance(activities, list):
        raise ValueError("INVALID_NATIVE_EVIDENCE")

    stopped = stage == "LOST"
    signed = stage in {"SIGNED", "IN_DELIVERY", "DELIVERED", "RETAINED"}
    if stopped:
        action = "NO_FURTHER_OUTREACH_WITHOUT_NEW_AUTHORIZED_CONTEXT"
    elif stage in {"IN_DELIVERY", "DELIVERED"}:
        action = "PREPARE_DELIVERY_ACCEPTANCE_AND_NEXT_CLIENT_SERVICE"
    elif signed:
        action = "PREPARE_AUTHORIZED_SERVICE_DELIVERY"
    elif stage in {"SCOPE_SENT", "NEGOTIATING"}:
        action = "REVIEW_SCOPE_OBJECTIONS_AND_PREPARE_ONE_CLEAR_DECISION"
    elif stage == "DISCOVERY":
        action = "PREPARE_ACCOUNT_SPECIFIC_DISCOVERY_BRIEF"
    else:
        action = "VERIFY_BUYER_CONTEXT_AND_PREPARE_A_USEFUL_FIRST_CONVERSATION"

    recent = []
    for a in activities[:15]:
        if not isinstance(a, dict) or a.get("kind") not in OPERATED_EVENTS:
            continue
        # All activities in original CRM are operator-reported, even where URLs exist.
        recent.append({
            "kind": a["kind"],
            "at": a.get("created_at"),
            "source_status": _text(a.get("source_status")) or "OPERATOR_REPORTED",
            "provider_attested": False,
            "evidence_url": _text(a.get("evidence_url")) or None
        })
    source_ref = _text(deal.get("source_intake_id")) or None
    scope_ref = _text(deal.get("accepted_scope_url")) or None
    next_due = deal.get("next_date")
    fact_sources = [
        {"field": "account", "value": account, "source": "NOETFIELD_CORPORATE_CRM"},
        {"field": "contact_name", "value": _text(deal.get("contact_name")) or None,
         "source": "NOETFIELD_CORPORATE_CRM"},
        {"field": "offer", "value": _text(deal.get("offer")),
         "source": "ORIGINAL_CORPORATE_OPPORTUNITY"},
        {"field": "deal_summary", "value": _text(deal.get("summary")) or None,
         "source": "OPERATOR_RECORDED_UNVERIFIED"}
    ]
    checklist = [
        {"task": "VERIFY_BUYER_AND_ROLE", "required": not stopped,
         "note": "Confirm who is deciding and who is preparing; do not guess preferences."},
        {"task": "REVIEW_PERSONALIZED_CONTEXT", "required": not stopped,
         "note": "Use only current, supported CRM facts for this one company's deal."},
        {"task": "PREPARE_TAILORED_DECISION", "required": not stopped,
         "note": "Present one primary actionable next step, with any material alternatives."},
        {"task": "CHECK_SCOPE_AND_REAL_PROOF", "required": True,
         "note": "A commercial stage, document or note does not prove an external payment."},
        {"task": "HUMAN_ADVISOR_REVIEW", "required": True,
         "note": "Original CRM owner authorizes any actual customer interaction."}
    ]
    return {
        "schema": SCHEMA,
        "scope": {"crm": "NOETFIELD_CORPORATE_ONLY", "deal_id": deal["id"],
                  "account_id": deal.get("account_id"), "source_intake_id": source_ref},
        "generated_at": as_of or datetime.now(UTC).isoformat(),
        "relationship": {
            "account": account, "assigned_owner": _text(deal.get("owner")) or None,
            "stage": stage, "next_due": next_due,
            "operator_next_action": _text(deal.get("next_action")) or None,
            "source_receipts": {"accepted_scope": scope_ref,
                                "acceptance_evidence": commercial.get("acceptance_evidence")}
        },
        "verified_customer_preferences": [],
        "research_facts": fact_sources,
        "recent_operator_activities": recent,
        "next_best_action": action,
        "preparation_checklist": checklist,
        "advisor_review_required": True,
        "communication_authorized_by_this_output": False,
        "checkout_or_payment_performed": False,
        "verified_settled_cash_minor": None,
        "no_fieldwork_identity_inherited": True,
        "confidence": "ORIGINAL_CRM_FACTS_WITH_UNVERIFIED_OPERATOR_NOTES",
        "metric": "ADVISOR_PREPARATION_NOT_A_CUSTOMER_OUTCOME"
    }

async def native_corporate_bijan_brief(settings: object, *, deal_id: str) -> dict[str, Any]:
    """Read original CRM through its existing validated detail method, no new table."""
    from noetfield_governance.corporate_crm import detail
    original = await detail(settings, deal_id=deal_id)
    return compile_bijan_corporate_brief(original)
