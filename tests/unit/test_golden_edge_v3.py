"""Golden Edge v3 evaluate and agent loop tests."""

import asyncio
from uuid import uuid4

from noetfield_events import AsyncEventBus
from noetfield_governance.golden_edge_v3 import (
    AgentLoopDecision,
    GoldenEdgeEvaluateRequest,
    GoldenEdgeV3Engine,
)
from noetfield_governance.runtime import GovernanceRuntime, HumanApprovalQueue


def test_evaluate_rejects_forbidden_financial_action() -> None:
    event_bus = AsyncEventBus()
    runtime = GovernanceRuntime(event_bus=event_bus, approvals=HumanApprovalQueue())
    engine = GoldenEdgeV3Engine(governance_runtime=runtime)
    tenant_id = uuid4()
    org_id = uuid4()

    async def run() -> None:
        result = await engine.evaluate(
            GoldenEdgeEvaluateRequest(
                tenant_id=tenant_id,
                organization_id=org_id,
                action="submit_payment_intent",
                resource_type="financial_probe",
                resource_id="probe-1",
            )
        )
        assert result.decision == AgentLoopDecision.REJECT
        assert result.allowed is False

    asyncio.run(run())


def test_agent_loop_rejects_before_execute() -> None:
    event_bus = AsyncEventBus()
    runtime = GovernanceRuntime(event_bus=event_bus, approvals=HumanApprovalQueue())
    engine = GoldenEdgeV3Engine(governance_runtime=runtime)
    tenant_id = uuid4()
    org_id = uuid4()

    async def run() -> None:
        result = await engine.agent_loop(
            GoldenEdgeEvaluateRequest(
                tenant_id=tenant_id,
                organization_id=org_id,
                action="execute_payment",
                resource_type="financial_probe",
                resource_id="probe-2",
            )
        )
        assert result.decision == AgentLoopDecision.REJECT

    asyncio.run(run())


def test_policy_pack_blocks_submit_payment_intent() -> None:
    from noetfield_governance.policies import PolicyEvaluator, PolicyInput

    tenant_id = uuid4()
    evaluation = PolicyEvaluator().evaluate(
        PolicyInput(
            tenant_id=tenant_id,
            actor_id="test",
            action="submit_payment_intent",
            resource_type="probe",
            resource_id="1",
        )
    )
    assert evaluation.allowed is False
