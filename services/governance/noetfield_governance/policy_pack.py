"""Executable governance policy pack for Phase 3.4.

The policy pack is deterministic and intentionally conservative. OPA can later
load equivalent rules, but this Python pack is the authoritative fallback used
by the backend runtime and tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PolicyDecisionCode(StrEnum):
    ALLOW = "ALLOW"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    VETO_BLOCKED_ACTION = "VETO_BLOCKED_ACTION"
    VETO_LOW_CONFIDENCE = "VETO_LOW_CONFIDENCE"
    VETO_AUTONOMOUS_PUBLICATION = "VETO_AUTONOMOUS_PUBLICATION"
    VETO_INSPECTOR_LIMIT = "VETO_INSPECTOR_LIMIT"


@dataclass(frozen=True)
class GovernancePolicyRule:
    rule_id: str
    description: str


@dataclass(frozen=True)
class GovernancePolicyPack:
    """Deterministic policy thresholds and guarded action sets."""

    version: str = "phase-3.4"
    minimum_confidence: float = 0.75
    high_impact_actions: frozenset[str] = frozenset(
        {
            "approve_workflow",
            "execute_inspector_action",
            "publish_report",
            "publish_board_report",
            "export_audit_package",
            "run_copilot_governance_demo",
        }
    )
    blocked_autonomous_actions: frozenset[str] = frozenset(
        {
            "publish_report",
            "publish_board_report",
            "export_audit_package",
            "approve_workflow",
        }
    )
    inspector_execution_limit: int = 3
    base_obligations: tuple[str, ...] = (
        "emit_governance_event",
        "retain_audit_trace",
        "preserve_actor_attribution",
    )
    rules: tuple[GovernancePolicyRule, ...] = field(
        default_factory=lambda: (
            GovernancePolicyRule(
                "confidence:min-threshold",
                "Runtime actions below the minimum confidence require review or veto.",
            ),
            GovernancePolicyRule(
                "human-review:high-impact",
                "High-impact governance actions require human review.",
            ),
            GovernancePolicyRule(
                "autonomy:no-silent-publication",
                "AI/service/inspector actors cannot silently publish or approve high-impact artifacts.",
            ),
            GovernancePolicyRule(
                "inspectors:bounded-execution",
                "Inspector collaborations are bounded to the configured execution limit.",
            ),
            GovernancePolicyRule(
                "copilot:review-required",
                "Copilot Governance demo outputs require human review before publication.",
            ),
        )
    )

    def policy_refs(self) -> list[str]:
        return [f"noetfield:{self.version}:{rule.rule_id}" for rule in self.rules]

    def obligations_for(self, *, requires_human_review: bool) -> list[str]:
        obligations = list(self.base_obligations)
        if requires_human_review:
            obligations.extend(["queue_human_review", "capture_reviewer_rationale"])
        return obligations


def context_float(context: dict[str, Any], key: str, default: float) -> float:
    value = context.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def context_int(context: dict[str, Any], key: str, default: int) -> int:
    value = context.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
