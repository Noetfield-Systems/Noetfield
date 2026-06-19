"""Tests for Legal review factory."""

from __future__ import annotations

import asyncio
from uuid import UUID, uuid5, NAMESPACE_URL

import yaml

from noetfield_events import AsyncEventBus, InMemoryDeadLetterStore, InMemoryEventStore
from noetfield_factories import (
    FactoryStatus,
    LegalFactoryRunRequest,
    get_factory_runner,
    is_factory_live,
)
from noetfield_governance import GovernanceRuntime, HumanApprovalQueue
from noetfield_governance.golden_edge_v3 import GoldenEdgeV3Engine
from noetfield_graph import (
    InMemoryGraphReflectionStore,
    InMemoryGraphStore,
    LiveGraphMutationEngine,
    TemporalGraphReflectionCycle,
)
from noetfield_inspectors import (
    InMemoryInspectorRunStore,
    InspectorCollaborationRuntime,
    InspectorExecutionLoop,
    LeadScoutInspector,
    OpportunityHunterInspector,
    ThreatMonitorInspector,
)
from noetfield_ledger import AuditLedgerRuntime, InMemoryAuditLedgerStore
from noetfield_legal_review import LegalReviewCommand, LegalReviewRuntime
from noetfield_signals import InMemorySignalStore, SignalIngestionPipeline
from noetfield_workflow import InMemoryWorkflowStore, WorkflowStateMachine

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]


def stable_uuid(name: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"https://noetfield.local/legal-review/{name}")


def test_legal_factory_is_live() -> None:
    assert is_factory_live("legal_review_v1")
    meta = yaml.safe_load(
        (ROOT / "packages/schemas/factories/legal_review_v1.yaml").read_text()
    )["metadata"]
    assert meta["status"] == "live"


def test_legal_factory_run_produces_policy_review_package() -> None:
    async def _run() -> None:
        event_bus = AsyncEventBus(
            event_store=InMemoryEventStore(),
            dead_letter_store=InMemoryDeadLetterStore(),
        )
        audit_store = InMemoryAuditLedgerStore()
        await event_bus.subscribe(
            name="audit",
            event_types={"*"},
            handler=AuditLedgerRuntime(audit_store).record_event,
        )
        signal_pipeline = SignalIngestionPipeline(event_bus, InMemorySignalStore())
        graph_store = InMemoryGraphStore()
        graph_mutations = LiveGraphMutationEngine(event_bus, graph_store)
        graph_reflections = TemporalGraphReflectionCycle(
            event_bus, graph_store, InMemoryGraphReflectionStore()
        )
        workflow_sm = WorkflowStateMachine(InMemoryWorkflowStore(), event_bus)
        governance = GovernanceRuntime(event_bus, HumanApprovalQueue())
        golden = GoldenEdgeV3Engine(governance_runtime=governance)
        inspector_rt = InspectorCollaborationRuntime(event_bus)
        for insp in (OpportunityHunterInspector(), ThreatMonitorInspector(), LeadScoutInspector()):
            inspector_rt.register(insp)
        inspector_loop = InspectorExecutionLoop(inspector_rt, InMemoryInspectorRunStore())

        from noetfield_copilot_governance import CopilotGovernanceDemoRuntime

        copilot_rt = CopilotGovernanceDemoRuntime(
            signal_pipeline=signal_pipeline,
            graph_mutations=graph_mutations,
            graph_reflections=graph_reflections,
            workflow_state_machine=workflow_sm,
            governance_runtime=governance,
            golden_edge=golden,
            inspector_execution_loop=inspector_loop,
        )
        legal_rt = LegalReviewRuntime(
            signal_pipeline=signal_pipeline,
            graph_mutations=graph_mutations,
            graph_reflections=graph_reflections,
            workflow_state_machine=workflow_sm,
            governance_runtime=governance,
            golden_edge=golden,
            inspector_execution_loop=inspector_loop,
        )
        runner = get_factory_runner(
            "legal_review_v1",
            demo_runtime=copilot_rt,
            legal_review_runtime=legal_rt,
            event_bus=event_bus,
            audit_store=audit_store,
            graph_store=graph_store,
            governance_runtime=governance,
        )
        result = await runner.run(
            LegalFactoryRunRequest(
                command=LegalReviewCommand(
                    tenant_id=stable_uuid("tenant"),
                    organization_id=stable_uuid("org"),
                    submitted_by="legal.ops@noetfield.local",
                    signal_payload={
                        "source": "legal_ops",
                        "summary": "Cross-border data policy review before export",
                        "policy_name": "EU-US Data Transfer Policy",
                    },
                    source_entity_id=stable_uuid("policy"),
                    target_entity_id=stable_uuid("jurisdiction"),
                ),
                source_request_id="RID-legal-review-test",
            )
        )
        assert result.factory_status == FactoryStatus.PENDING_APPROVAL
        assert result.policy_review_package["title"] == "Policy Review Package"
        assert "not legal advice" in result.policy_review_package["orientation"].lower()
        assert result.audit_package["event_count"] >= 10

    asyncio.run(_run())
