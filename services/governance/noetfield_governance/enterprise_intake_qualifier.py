"""Deterministic enterprise intake qualification for AI Value Governance OS briefing lane."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

QUALIFICATION_SCHEMA = "noetfield.enterprise-intake-qualified.v0.1"
QUALIFIER_VERSION = "enterprise-intake-qualifier-v1"

EnterpriseTier = Literal["A", "B", "C", "defer"]
Urgency = Literal["immediate", "standard", "low"]
NextStep = Literal[
    "schedule_briefing",
    "founder_review",
    "async_nurture",
    "clarify_scope",
    "polite_decline",
]

_CONSUMER_EMAIL_DOMAINS = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com",
        "live.com",
        "icloud.com",
        "proton.me",
        "protonmail.com",
        "aol.com",
    }
)

_FIT_POSITIVE = (
    ("regulated institution", 18, r"\b(regulated|financial services|insurance|healthcare|hospital|bank|credit union)\b"),
    ("copilot governance", 16, r"\b(copilot|m365|microsoft 365|purview|teams)\b"),
    ("governance evidence", 14, r"\b(governance|compliance|audit|board|grc|risk committee)\b"),
    ("enterprise scope", 12, r"\b(enterprise|institution|procurement|diligence)\b"),
    ("framework orientation", 10, r"\b(eu ai act|nist|iso 42001|dora|nis2)\b"),
    ("trust brief lane", 10, r"\b(trust brief|trust ledger|tle)\b"),
    ("deployment timeline", 8, r"\b(deadline|timeline|rollout|production|pilot)\b"),
)

_BLOCKER_PATTERNS: tuple[tuple[str, str], ...] = (
    ("payment_rails", r"\b(payment rails?|custody|msb|money transmitter|wire transfer|withdraw)\b"),
    ("certification_claim", r"\b(certif(y|ication)|iso 27001 certification|soc 2 certification).{0,40}\b(from you|from noetfield|issue)\b"),
    ("mailbox_surveillance", r"\b(full mailbox|content surveillance|read all email)\b"),
    ("generic_chatbot", r"\b(generic chatbot catalog|build me a chatbot)\b"),
)

_NURTURE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("consumer_email", r""),  # handled separately
    ("minimal_context", r""),
)


@dataclass(frozen=True)
class EnterpriseIntakeQualification:
    schema: str
    tier: EnterpriseTier
    fit_score: int
    urgency: Urgency
    next_step: NextStep
    owner_sla_hours: int
    reasons: tuple[str, ...]
    blockers: tuple[str, ...]
    qualifier_version: str = QUALIFIER_VERSION

    def to_qualification_json(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "tier": self.tier,
            "fit_score": self.fit_score,
            "urgency": self.urgency,
            "next_step": self.next_step,
            "owner_sla_hours": self.owner_sla_hours,
            "reasons": list(self.reasons),
            "blockers": list(self.blockers),
            "qualifier_version": self.qualifier_version,
        }


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _meta_value(metadata: dict[str, Any] | None, key: str) -> str:
    if not metadata:
        return ""
    raw = metadata.get(key)
    return _norm(str(raw)) if raw is not None else ""


def is_enterprise_intake(
    *,
    vector: str,
    sku: str,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """True when intake belongs to the enterprise AI Value OS briefing lane."""
    vec = _norm(vector)
    sku_l = _norm(sku)
    interest = _meta_value(metadata, "interest")
    meta_vector = _meta_value(metadata, "vector")

    if vec in {"ai-value-governance-os", "enterprise"} or "ai-value-governance" in vec:
        return True
    if meta_vector in {"ai-value-governance-os", "enterprise"} or "ai-value-governance" in meta_vector:
        return True
    if interest == "enterprise":
        return True
    if sku_l == "trust_brief" and interest == "enterprise":
        return True
    if sku_l == "trust_brief" and vec == "ai-value-governance-os":
        return True
    return False


def qualify_enterprise_intake(
    *,
    organization: str,
    contact_email: str,
    message: str,
    vector: str = "",
    sku: str = "trust_brief",
    request_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> EnterpriseIntakeQualification:
    """Score enterprise intake deterministically — no LLM."""
    org = _norm(organization)
    body = _norm(message)
    combined = f"{org}\n{body}"
    reasons: list[str] = []
    blockers: list[str] = []
    score = 20

    if request_id and request_id.strip().upper().startswith("RID-"):
        score += 8
        reasons.append(f"request_id:{request_id.strip().upper()}")

    vec = _norm(vector)
    interest = _meta_value(metadata, "interest")
    if vec == "ai-value-governance-os" or "ai-value-governance" in vec:
        score += 15
        reasons.append("vector:ai-value-governance-os")
    if interest == "enterprise":
        score += 12
        reasons.append("interest:enterprise")
    if _norm(sku) == "trust_brief":
        score += 8
        reasons.append("sku:trust_brief")

    preferred_tier = _meta_value(metadata, "preferred_tier") or _meta_value(metadata, "tier")
    if preferred_tier == "enterprise":
        score += 10
        reasons.append("preferred_tier:enterprise")
    elif preferred_tier == "pro":
        score += 6
        reasons.append("preferred_tier:pro")

    buyer_role = _meta_value(metadata, "buyer_role") or _meta_value(metadata, "role")
    if buyer_role in {"ciso", "grc", "legal", "procurement", "board"}:
        score += 8
        reasons.append(f"buyer_role:{buyer_role}")

    for label, weight, pattern in _FIT_POSITIVE:
        if re.search(pattern, combined, re.IGNORECASE):
            score += weight
            reasons.append(f"fit:{label}")

    for code, pattern in _BLOCKER_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            blockers.append(code)

    email_domain = contact_email.strip().lower().split("@")[-1] if "@" in contact_email else ""
    if email_domain in _CONSUMER_EMAIL_DOMAINS:
        score -= 18
        blockers.append("consumer_email_domain")
        reasons.append(f"email_domain:{email_domain}")

    if len(body) < 40:
        score -= 12
        reasons.append("minimal_message_context")

    if not org:
        score -= 10
        blockers.append("missing_organization")

    score = max(0, min(100, score))

    if blockers:
        tier: EnterpriseTier = "defer"
        urgency: Urgency = "low"
        next_step: NextStep = "polite_decline" if any(
            b in {"payment_rails", "mailbox_surveillance"} for b in blockers
        ) else "clarify_scope"
        sla = 120
    elif score >= 72:
        tier = "A"
        urgency = "immediate"
        next_step = "schedule_briefing"
        sla = 24
    elif score >= 48:
        tier = "B"
        urgency = "standard"
        next_step = "founder_review"
        sla = 48
    else:
        tier = "C"
        urgency = "low"
        next_step = "async_nurture"
        sla = 72

    if tier == "A" and not blockers:
        reasons.append("route:ai_value_os_briefing")

    return EnterpriseIntakeQualification(
        schema=QUALIFICATION_SCHEMA,
        tier=tier,
        fit_score=score,
        urgency=urgency,
        next_step=next_step,
        owner_sla_hours=sla,
        reasons=tuple(dict.fromkeys(reasons)),
        blockers=tuple(dict.fromkeys(blockers)),
    )
