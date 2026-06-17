"""Trust Brief diligence factory runner."""

from __future__ import annotations

import asyncio
from typing import Any, Protocol
from uuid import UUID, uuid4

from noetfield_events import AsyncEventBus, EventType, build_event
from noetfield_events.context import reset_request_context, set_request_context
from noetfield_governance.golden_edge_v3 import AgentLoopDecision
from noetfield_trust_brief import (
    FACTORY_ID,
    TrustBriefDiligenceCommand,
    TrustBriefDiligenceRuntime,
    TrustBriefPipelineState,
)

from .exceptions import FactoryValidationError
from .loader import factory_node_ids, load_factory_spec
from .models import FactoryStatus, TrustBriefFactoryOutput, TrustBriefFactoryRunRequest
from .nodes import factory_actor, intake_validate_trust_brief, package_trust_brief_deliverable


class TrustBriefFactoryRunner:
    FACTORY_ID = FACTORY_ID

    def __init__(
        self,
        *,
        diligence_runtime: TrustBriefDiligenceRuntime,
        event_bus: AsyncEventBus,
        audit_store: Any,
        graph_store: Any,
        governance_runtime: Any,
    ) -> None:
        self._runtime = diligence_runtime
        self._event_bus = event_bus
        self._audit_store = audit_store
        self._graph_store = graph_store
        self._governance_runtime = governance_runtime
        self._spec = load_factory_spec(self.FACTORY_ID)

    async def run(self, request: TrustBriefFactoryRunRequest) -> TrustBriefFactoryOutput:
        command = request.command
        if request.source_request_id:
            command = command.model_copy(update={"source_request_id": request.source_request_id})
        run_id = uuid4()
        rid_token, corr_token = set_request_context(
            source_request_id=command.source_request_id,
            correlation_id=run_id,
        )
        try:
            return await self._execute(run_id, command)
        finally:
            reset_request_context(rid_token, corr_token)

    async def _execute(
        self, run_id: UUID, command: TrustBriefDiligenceCommand
    ) -> TrustBriefFactoryOutput:
        node_ids = factory_node_ids(self.FACTORY_ID)
        await self._emit_event(
            EventType.FACTORY_RUN_STARTED,
            run_id=run_id,
            command=command,
            node_id=node_ids[0],
            payload={"factory_id": self.FACTORY_ID, "node_count": len(node_ids)},
        )
        validated = intake_validate_trust_brief(command)
        state = TrustBriefPipelineState(run_id=run_id, command=validated)
        await self._complete_node(run_id, command, "n01_intake_validate")

        state = await self._step(run_id, command, "n02_signal_ingest", state, self._runtime.step_signal_ingest)
        state = await self._step(run_id, command, "n03_graph_mutate", state, self._runtime.step_graph_mutate)
        state = await self._step(run_id, command, "n04_graph_reflect", state, self._runtime.step_graph_reflect)
        state = await self._step(
            run_id, command, "n05_inspector_collaborate", state, self._runtime.step_inspector_collaborate
        )
        state = await self._step(run_id, command, "n06_policy_evaluate", state, self._runtime.step_policy_evaluate)

        if (
            state.policy_decision is not None
            and state.policy_decision.decision == AgentLoopDecision.REJECT
        ):
            packaged = await package_trust_brief_deliverable(
                factory_id=self.FACTORY_ID,
                state=state,
                event_bus=self._event_bus,
                audit_store=self._audit_store,
                graph_store=self._graph_store,
                governance_runtime=self._governance_runtime,
            )
            return TrustBriefFactoryOutput(
                factory_id=self.FACTORY_ID,
                run_id=run_id,
                factory_status=FactoryStatus.VETOED,
                ic_appendix=packaged["ic_appendix"],
                checklist_map=packaged["checklist_map"],
                audit_package=packaged["audit_package"],
                replay_hint=packaged["replay_hint"],
                policy_decision=state.policy_decision.model_dump(mode="json"),
            )

        state = await self._step(run_id, command, "n07_workflow_govern", state, self._runtime.step_workflow_govern)
        packaged = await package_trust_brief_deliverable(
            factory_id=self.FACTORY_ID,
            state=state,
            event_bus=self._event_bus,
            audit_store=self._audit_store,
            graph_store=self._graph_store,
            governance_runtime=self._governance_runtime,
        )
        await self._complete_node(run_id, command, "n08_package_export")
        return TrustBriefFactoryOutput(
            factory_id=self.FACTORY_ID,
            run_id=run_id,
            factory_status=FactoryStatus(packaged["factory_status"]),
            ic_appendix=packaged["ic_appendix"],
            checklist_map=packaged["checklist_map"],
            audit_package=packaged["audit_package"],
            replay_hint=packaged["replay_hint"],
            policy_decision=(
                state.policy_decision.model_dump(mode="json")
                if state.policy_decision is not None
                else None
            ),
        )

    async def _step(self, run_id, command, node_id, state, fn):
        node_spec = self._node_spec(node_id)
        timeout_sec = int(node_spec.get("timeout_sec", 15))
        retries = int(node_spec.get("retries", 1))
        last_error = None
        for attempt in range(retries + 1):
            try:
                result = await asyncio.wait_for(fn(state), timeout=timeout_sec)
                await self._complete_node(run_id, command, node_id, attempt=attempt)
                return result
            except Exception as exc:
                last_error = exc
        assert last_error is not None
        raise last_error

    def _node_spec(self, node_id: str) -> dict[str, Any]:
        for node in self._spec.get("spec", {}).get("nodes", []):
            if isinstance(node, dict) and node.get("id") == node_id:
                return node
        return {}

    async def _complete_node(self, run_id, command, node_id, *, attempt=0):
        await self._emit_event(
            EventType.FACTORY_NODE_COMPLETED,
            run_id=run_id,
            command=command,
            node_id=node_id,
            payload={"attempt": attempt},
        )

    async def _emit_event(self, event_type, *, run_id, command, node_id, payload=None):
        event = build_event(
            event_type=event_type,
            tenant_id=command.tenant_id,
            organization_id=command.organization_id,
            actor=factory_actor(command.submitted_by),
            source_service=f"factory:{node_id}",
            entity_type="factory_run",
            entity_id=str(run_id),
            correlation_id=run_id,
            source_request_id=command.source_request_id,
            payload={"factory_id": self.FACTORY_ID, "node_id": node_id, **(payload or {})},
        )
        await self._event_bus.publish(event)
