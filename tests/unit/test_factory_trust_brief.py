"""Tests for Trust Brief / M&A factory and platform catalog API."""

from __future__ import annotations

import asyncio
from uuid import UUID, uuid5, NAMESPACE_URL

import yaml

from noetfield_events import AsyncEventBus, InMemoryDeadLetterStore, InMemoryEventStore
from noetfield_factories import (
    FactoryStatus,
    TrustBriefFactoryRunRequest,
    get_factory_runner,
    is_factory_live,
    load_platform_catalog,
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
from noetfield_signals import InMemorySignalStore, SignalIngestionPipeline
from noetfield_trust_brief import TrustBriefDiligenceCommand, TrustBriefDiligenceRuntime
from noetfield_workflow import InMemoryWorkflowStore, WorkflowStateMachine

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]


def stable_uuid(name: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"https://noetfield.local/trust-brief/{name}")


def test_trust_brief_factory_is_live() -> None:
    assert is_factory_live("trust_brief_diligence_v1")
    meta = yaml.safe_load(
        (ROOT / "packages/schemas/factories/trust_brief_diligence_v1.yaml").read_text()
    )["metadata"]
    assert meta["status"] == "live"
    assert meta["alias"] == "M&A Factory"


def test_platform_catalog_tree_has_factory_children() -> None:
    catalog = load_platform_catalog()
    tree = catalog["platform_tree"]
    factory_node = next(c for c in tree["children"] if c["id"] == "factory_catalog")
    child_ids = {c["factory_id"] for c in factory_node["children"]}
    assert "trust_brief_diligence_v1" in child_ids
    assert "copilot_governance_readiness_v1" in child_ids
    ma = next(c for c in factory_node["children"] if c["id"] == "ma_diligence")
    assert ma["status"] == "live"
    assert ma["display_name"] == "M&A Factory"


def test_trust_brief_factory_run_produces_ic_appendix() -> None:
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
        trust_rt = TrustBriefDiligenceRuntime(
            signal_pipeline=signal_pipeline,
            graph_mutations=graph_mutations,
            graph_reflections=graph_reflections,
            workflow_state_machine=workflow_sm,
            governance_runtime=governance,
            golden_edge=golden,
            inspector_execution_loop=inspector_loop,
        )
        runner = get_factory_runner(
            "trust_brief_diligence_v1",
            demo_runtime=copilot_rt,
            trust_brief_runtime=trust_rt,
            event_bus=event_bus,
            audit_store=audit_store,
            graph_store=graph_store,
            governance_runtime=governance,
        )
        result = await runner.run(
            TrustBriefFactoryRunRequest(
                command=TrustBriefDiligenceCommand(
                    tenant_id=stable_uuid("tenant"),
                    organization_id=stable_uuid("org"),
                    submitted_by="diligence.lead@noetfield.local",
                    signal_payload={
                        "source": "investor_diligence",
                        "summary": "Series B AI governance diligence on target portco",
                        "target_name": "Example Portco",
                    },
                    source_entity_id=stable_uuid("thesis"),
                    target_entity_id=stable_uuid("portco"),
                ),
                source_request_id="RID-trust-brief-test",
            )
        )
        assert result.factory_status == FactoryStatus.PENDING_APPROVAL
        assert result.ic_appendix["title"] == "Investor Governance IC Appendix"
        assert result.checklist_map["map_version"] == "INVESTOR_GOVERNANCE_CHECKLIST_MAP_v1"
        assert result.audit_package["event_count"] >= 10

    asyncio.run(_run())
