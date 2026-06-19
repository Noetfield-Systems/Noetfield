"""AML governance trace factory runtime."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from noetfield_governance import GovernanceActionCommand, GovernanceRuntime
from noetfield_governance.golden_edge_v3 import (
    GoldenEdgeEvaluateRequest,
    GoldenEdgeEvaluateResponse,
    GoldenEdgeV3Engine,
)
from noetfield_graph import GraphMutationCommand, LiveGraphMutationEngine, TemporalGraphReflectionCycle
from noetfield_inspectors import (
    InspectorCollaborationCommand,
    InspectorExecutionLoop,
    InspectorExecutionRecord,
)
from noetfield_signals import IngestSignalCommand, IngestedSignal, SignalIngestionPipeline
from noetfield_types import WorkflowState
from noetfield_workflow import WorkflowInstance, WorkflowStateMachine, WorkflowTransitionCommand

FACTORY_ID = "aml_governance_trace_v1"


class AmlGovernanceTraceCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    submitted_by: str
    signal_payload: dict[str, object]
    source_entity_id: UUID = Field(default_factory=uuid4)
    target_entity_id: UUID = Field(default_factory=uuid4)
    source_request_id: str | None = None


@dataclass
class AmlGovernanceTracePipelineState:
    run_id: UUID
    command: AmlGovernanceTraceCommand
    signal: IngestedSignal | None = None
    relationship_id: UUID | None = None
    reflection_id: UUID | None = None
    workflow_id: UUID | None = None
    workflow_state: WorkflowState | None = None
    approval_id: UUID | None = None
    inspector_run: InspectorExecutionRecord | None = None
    policy_decision: GoldenEdgeEvaluateResponse | None = None


class AmlGovernanceTraceRuntime:
    def __init__(
        self,
        *,
        signal_pipeline: SignalIngestionPipeline,
        graph_mutations: LiveGraphMutationEngine,
        graph_reflections: TemporalGraphReflectionCycle,
        workflow_state_machine: WorkflowStateMachine,
        governance_runtime: GovernanceRuntime | None = None,
        golden_edge: GoldenEdgeV3Engine | None = None,
        inspector_execution_loop: InspectorExecutionLoop | None = None,
    ) -> None:
        self._signal_pipeline = signal_pipeline
        self._graph_mutations = graph_mutations
        self._graph_reflections = graph_reflections
        self._workflow_state_machine = workflow_state_machine
        self._governance_runtime = governance_runtime
        self._golden_edge = golden_edge
        self._inspector_execution_loop = inspector_execution_loop

    async def step_signal_ingest(
        self, state: AmlGovernanceTracePipelineState
    ) -> AmlGovernanceTracePipelineState:
        signal, _ = await self._signal_pipeline.ingest(
            IngestSignalCommand(
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                signal_type="aml_governance_trace_signal",
                payload=state.command.signal_payload,
                provenance={"module": "aml_trace", "ingestion": "trace"},
                actor_id=state.command.submitted_by,
            )
        )
        state.signal = signal
        return state

    async def step_graph_mutate(
        self, state: AmlGovernanceTracePipelineState
    ) -> AmlGovernanceTracePipelineState:
        mutation = await self._graph_mutations.mutate_relationship(
            GraphMutationCommand(
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                source_entity_id=state.command.source_entity_id,
                target_entity_id=state.command.target_entity_id,
                relationship_type="aml_trace_for",
                confidence_delta=0.2,
                reason="AML governance trace signal linked to compliance graph.",
                actor_id=state.command.submitted_by,
            )
        )
        state.relationship_id = mutation.relationship.relationship_id
        return state

    async def step_graph_reflect(
        self, state: AmlGovernanceTracePipelineState
    ) -> AmlGovernanceTracePipelineState:
        reflection = await self._graph_reflections.run(
            state.command.tenant_id,
            state.command.organization_id,
        )
        state.reflection_id = reflection.reflection_id
        return state

    async def step_inspector_collaborate(
        self, state: AmlGovernanceTracePipelineState
    ) -> AmlGovernanceTracePipelineState:
        if self._inspector_execution_loop is None or state.relationship_id is None:
            return state
        inspector_run = await self._inspector_execution_loop.run_once(
            InspectorCollaborationCommand(
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                invoked_by=state.command.submitted_by,
                objective="Assess AML governance trace readiness, screening controls, and audit evidence.",
                inspector_names=["opportunity_hunter", "threat_monitor", "lead_scout"],
                graph_scope={
                    "module": "aml_trace",
                    "relationship_id": str(state.relationship_id),
                },
            )
        )
        state.inspector_run = inspector_run
        return state

    async def step_policy_evaluate(
        self, state: AmlGovernanceTracePipelineState
    ) -> AmlGovernanceTracePipelineState:
        if self._golden_edge is None:
            return state
        resource_id = str(state.workflow_id or state.reflection_id or state.run_id)
        decision = await self._golden_edge.evaluate(
            GoldenEdgeEvaluateRequest(
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                action="run_aml_governance_trace",
                resource_type="aml_governance_trace_run",
                resource_id=resource_id,
                actor_id=state.command.submitted_by,
                confidence=0.8,
                payload={"module": "aml_trace", "run_id": str(state.run_id)},
            )
        )
        state.policy_decision = decision
        return state

    async def step_workflow_govern(
        self, state: AmlGovernanceTracePipelineState
    ) -> AmlGovernanceTracePipelineState:
        assert state.signal is not None
        assert state.relationship_id is not None
        assert state.reflection_id is not None
        workflow = await self._workflow_state_machine.start(
            WorkflowInstance(
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                workflow_type="aml_governance_trace_review",
                target_entity_type="graph_reflection",
                target_entity_id=str(state.reflection_id),
                payload={
                    "factory_id": FACTORY_ID,
                    "run_id": str(state.run_id),
                    "signal_id": str(state.signal.signal_id),
                    "relationship_id": str(state.relationship_id),
                    "control_plane_state": "INITIATED",
                },
                created_by=state.command.submitted_by,
            )
        )
        workflow = await self._workflow_state_machine.transition(
            WorkflowTransitionCommand(
                workflow_id=workflow.workflow_id,
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                actor_id=state.command.submitted_by,
                next_state=WorkflowState.PENDING_REVIEW,
                reason="AML governance trace requires human review before audit package export.",
            )
        )
        state.workflow_id = workflow.workflow_id
        state.workflow_state = workflow.state
        if self._governance_runtime is not None:
            governed = await self._governance_runtime.execute(
                GovernanceActionCommand(
                    tenant_id=state.command.tenant_id,
                    organization_id=state.command.organization_id,
                    action="run_aml_governance_trace",
                    resource_type="aml_governance_trace_run",
                    resource_id=str(workflow.workflow_id),
                    actor_id=state.command.submitted_by,
                    confidence=0.8,
                    payload={
                        "factory_id": FACTORY_ID,
                        "run_id": str(state.run_id),
                        "module": "aml_trace",
                        "workflow_id": str(workflow.workflow_id),
                        "reflection_id": str(state.reflection_id),
                    },
                )
            )
            state.approval_id = governed.approval_id
        return state
