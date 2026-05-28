"""Phase 3.4 governance policy pack tests."""

from __future__ import annotations

from uuid import uuid4

from noetfield_governance import PolicyDecisionCode, PolicyEvaluator, PolicyInput


def make_input(action: str, context: dict[str, object] | None = None) -> PolicyInput:
    return PolicyInput(
        tenant_id=uuid4(),
        actor_id="policy-test",
        action=action,
        resource_type="test_resource",
        resource_id=str(uuid4()),
        context=context or {},
    )


def test_policy_allows_low_impact_action_without_review() -> None:
    evaluation = PolicyEvaluator().evaluate(
        make_input("read_signal", {"actor_type": "human", "confidence": 0.95})
    )

    assert evaluation.allowed is True
    assert evaluation.requires_human_review is False
    assert evaluation.reason_code == PolicyDecisionCode.ALLOW
    assert "emit_governance_event" in evaluation.obligations


def test_policy_requires_review_for_low_confidence() -> None:
    evaluation = PolicyEvaluator().evaluate(
        make_input("mutate_graph", {"actor_type": "service", "confidence": 0.5})
    )

    assert evaluation.allowed is True
    assert evaluation.requires_human_review is True
    assert evaluation.reason_code == PolicyDecisionCode.VETO_LOW_CONFIDENCE
    assert "queue_human_review" in evaluation.obligations


def test_policy_vetoes_autonomous_publication() -> None:
    evaluation = PolicyEvaluator().evaluate(
        make_input("publish_report", {"actor_type": "service", "confidence": 0.95})
    )

    assert evaluation.allowed is False
    assert evaluation.requires_human_review is False
    assert evaluation.reason_code == PolicyDecisionCode.VETO_AUTONOMOUS_PUBLICATION


def test_policy_vetoes_inspector_limit() -> None:
    evaluation = PolicyEvaluator().evaluate(
        make_input(
            "execute_inspector_action",
            {"actor_type": "human", "confidence": 0.95, "inspector_count": 5},
        )
    )

    assert evaluation.allowed is False
    assert evaluation.reason_code == PolicyDecisionCode.VETO_INSPECTOR_LIMIT


def test_policy_requires_review_for_copilot_governance() -> None:
    evaluation = PolicyEvaluator().evaluate(
        make_input(
            "run_copilot_governance_demo",
            {"actor_type": "human", "confidence": 0.95, "module": "copilot_governance"},
        )
    )

    assert evaluation.allowed is True
    assert evaluation.requires_human_review is True
    assert evaluation.reason_code == PolicyDecisionCode.REQUIRE_HUMAN_REVIEW
