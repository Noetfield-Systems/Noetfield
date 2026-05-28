"""End-to-end Copilot Governance use-case test with policy enforcement."""

from __future__ import annotations

import asyncio
from uuid import uuid4

from noetfield_copilot_governance import (
    CopilotGovernanceCommand,
    CopilotGovernanceDemoRuntime,
    InMemoryCopilotGovernanceRunStore,
)
from noetfield_events import AsyncEventBus, EventReplayCursor, EventType, InMemoryDeadLetterStore, InMemoryEventStore
from noetfield_governance import GovernanceRuntime, HumanApprovalQueue
from noetfield_graph import (
    InMemoryGraphReflectionStore,
    InMemoryGraphStore,
    LiveGraphMutationEngine,
    TemporalGraphReflectionCycle,
)
from noetfield_ledger import AuditLedgerRuntime, InMemoryAuditLedgerStore
from noetfield_signals import InMemorySignalStore, SignalIngestionPipeline
from noetfield_types import WorkflowState
from noetfield_workflow import InMemoryWorkflowStore, WorkflowStateMachine


def test_copilot_governance_demo_requires_policy_review() -> None:
    async def run() -> None:
        tenant_id = uuid4()
        organization_id = uuid4()
        event_bus = AsyncEventBus(
            event_store=InMemoryEventStore(),
            dead_letter_store=InMemoryDeadLetterStore(),
        )
        audit_runtime = AuditLedgerRuntime(InMemoryAuditLedgerStore())
        await event_bus.subscribe(
            name="audit-ledger-runtime",
            event_types={"*"},
            handler=audit_runtime.record_event,
        )
        signal_pipeline = SignalIngestionPipeline(event_bus, InMemorySignalStore())
        graph_store = InMemoryGraphStore()
        graph_mutations = LiveGraphMutationEngine(event_bus, graph_store)
        graph_reflections = TemporalGraphReflectionCycle(
            event_bus,
            graph_store,
            InMemoryGraphReflectionStore(),
        )
        workflow_state_machine = WorkflowStateMachine(InMemoryWorkflowStore(), event_bus)
        governance_runtime = GovernanceRuntime(event_bus, HumanApprovalQueue())

        runtime = CopilotGovernanceDemoRuntime(
            signal_pipeline=signal_pipeline,
            graph_mutations=graph_mutations,
            graph_reflections=graph_reflections,
            workflow_state_machine=workflow_state_machine,
            governance_runtime=governance_runtime,
            run_store=InMemoryCopilotGovernanceRunStore(),
        )

        result = await runtime.run(
            CopilotGovernanceCommand(
                tenant_id=tenant_id,
                organization_id=organization_id,
                submitted_by="copilot-test",
                signal_payload={"copilot": "oversharing", "risk": "high"},
            )
        )
        replayed = await event_bus.replay(EventReplayCursor(after_sequence=0))

        assert result.workflow_state == WorkflowState.PENDING_REVIEW
        assert result.approval_id is not None
        assert any(event.event_type == EventType.POLICY_EVALUATED for event in replayed)
        assert any(event.event_type == EventType.HUMAN_APPROVAL_REQUESTED for event in replayed)

    asyncio.run(run())
