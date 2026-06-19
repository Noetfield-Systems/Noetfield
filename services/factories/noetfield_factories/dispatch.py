"""Factory runner dispatch by catalog factory_id."""

from __future__ import annotations

from typing import Any, Protocol

from noetfield_aml_trace import AmlGovernanceTraceRuntime
from noetfield_copilot_governance import CopilotGovernanceDemoRuntime
from noetfield_events import AsyncEventBus
from noetfield_legal_review import LegalReviewRuntime
from noetfield_trust_brief import TrustBriefDiligenceRuntime

from .aml_runner import AmlFactoryRunner
from .catalog import is_factory_live
from .exceptions import FactoryNotFoundError
from .legal_runner import LegalFactoryRunner
from .runner import CopilotGovernanceFactoryRunner
from .trust_brief_runner import TrustBriefFactoryRunner

LIVE_RUNNERS = {
    "copilot_governance_readiness_v1": CopilotGovernanceFactoryRunner,
    "trust_brief_diligence_v1": TrustBriefFactoryRunner,
    "legal_review_v1": LegalFactoryRunner,
    "aml_governance_trace_v1": AmlFactoryRunner,
}


class FactoryRunner(Protocol):
    FACTORY_ID: str

    async def run(self, request: Any) -> Any: ...


def get_factory_runner(
    factory_id: str,
    *,
    demo_runtime: CopilotGovernanceDemoRuntime,
    trust_brief_runtime: TrustBriefDiligenceRuntime | None = None,
    legal_review_runtime: LegalReviewRuntime | None = None,
    aml_trace_runtime: AmlGovernanceTraceRuntime | None = None,
    event_bus: AsyncEventBus,
    audit_store: Any,
    graph_store: Any,
    governance_runtime: Any,
) -> FactoryRunner:
    if not is_factory_live(factory_id):
        raise FactoryNotFoundError(factory_id)
    if factory_id == CopilotGovernanceFactoryRunner.FACTORY_ID:
        return CopilotGovernanceFactoryRunner(
            demo_runtime=demo_runtime,
            event_bus=event_bus,
            audit_store=audit_store,
            graph_store=graph_store,
            governance_runtime=governance_runtime,
        )
    if factory_id == TrustBriefFactoryRunner.FACTORY_ID:
        if trust_brief_runtime is None:
            raise FactoryNotFoundError(factory_id)
        return TrustBriefFactoryRunner(
            diligence_runtime=trust_brief_runtime,
            event_bus=event_bus,
            audit_store=audit_store,
            graph_store=graph_store,
            governance_runtime=governance_runtime,
        )
    if factory_id == LegalFactoryRunner.FACTORY_ID:
        if legal_review_runtime is None:
            raise FactoryNotFoundError(factory_id)
        return LegalFactoryRunner(
            legal_runtime=legal_review_runtime,
            event_bus=event_bus,
            audit_store=audit_store,
            graph_store=graph_store,
            governance_runtime=governance_runtime,
        )
    if factory_id == AmlFactoryRunner.FACTORY_ID:
        if aml_trace_runtime is None:
            raise FactoryNotFoundError(factory_id)
        return AmlFactoryRunner(
            aml_runtime=aml_trace_runtime,
            event_bus=event_bus,
            audit_store=audit_store,
            graph_store=graph_store,
            governance_runtime=governance_runtime,
        )
    raise FactoryNotFoundError(factory_id)
