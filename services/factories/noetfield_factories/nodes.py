"""Factory pipeline node helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from noetfield_aml_trace import AmlGovernanceTraceCommand, AmlGovernanceTracePipelineState
from noetfield_copilot_governance import CopilotGovernanceCommand, CopilotPipelineState
from noetfield_legal_review import LegalReviewCommand, LegalReviewPipelineState
from noetfield_trust_brief import TrustBriefDiligenceCommand, TrustBriefPipelineState
from noetfield_events import EventReplayCursor
from noetfield_governance.golden_edge_v3 import AgentLoopDecision
from noetfield_types import Actor, ActorType, WorkflowState

from .exceptions import FactoryValidationError


def intake_validate(command: CopilotGovernanceCommand) -> CopilotGovernanceCommand:
    """n01 — validate required factory input fields."""
    if not command.submitted_by.strip():
        raise FactoryValidationError("submitted_by is required")
    payload = dict(command.signal_payload)
    if not isinstance(payload, dict):
        raise FactoryValidationError("signal_payload must be an object")
    source = payload.get("source")
    summary = payload.get("summary")
    if not source or not summary:
        if payload.get("signal_type"):
            payload["source"] = "m365_copilot"
            payload["summary"] = str(
                payload.get("requested_outcome") or payload.get("signal_type")
            )
            return command.model_copy(update={"signal_payload": payload})
        raise FactoryValidationError(
            "signal_payload requires source and summary",
            details={"signal_payload": payload},
        )
    allowed_sources = {"m365_copilot", "manual", "webhook"}
    if str(source) not in allowed_sources:
        raise FactoryValidationError(
            f"signal_payload.source must be one of {sorted(allowed_sources)}"
        )
    return command


def intake_validate_legal(command: LegalReviewCommand) -> LegalReviewCommand:
    """n01 — validate Legal review intake."""
    if not command.submitted_by.strip():
        raise FactoryValidationError("submitted_by is required")
    payload = dict(command.signal_payload)
    source = payload.get("source")
    summary = payload.get("summary")
    if not source or not summary:
        if payload.get("policy_name") or payload.get("jurisdiction"):
            payload.setdefault("source", "legal_ops")
            payload.setdefault(
                "summary",
                str(payload.get("policy_name") or payload.get("jurisdiction")),
            )
            return command.model_copy(update={"signal_payload": payload})
        raise FactoryValidationError(
            "signal_payload requires source and summary",
            details={"signal_payload": payload},
        )
    allowed = {"legal_ops", "manual", "webhook"}
    if str(source) not in allowed:
        raise FactoryValidationError(f"signal_payload.source must be one of {sorted(allowed)}")
    return command


def intake_validate_aml(command: AmlGovernanceTraceCommand) -> AmlGovernanceTraceCommand:
    """n01 — validate AML governance trace intake."""
    if not command.submitted_by.strip():
        raise FactoryValidationError("submitted_by is required")
    payload = dict(command.signal_payload)
    source = payload.get("source")
    summary = payload.get("summary")
    if not source or not summary:
        if payload.get("screening_program") or payload.get("corridor"):
            payload.setdefault("source", "compliance_ops")
            payload.setdefault(
                "summary",
                str(payload.get("screening_program") or payload.get("corridor")),
            )
            return command.model_copy(update={"signal_payload": payload})
        raise FactoryValidationError(
            "signal_payload requires source and summary",
            details={"signal_payload": payload},
        )
    allowed = {"compliance_ops", "manual", "webhook"}
    if str(source) not in allowed:
        raise FactoryValidationError(f"signal_payload.source must be one of {sorted(allowed)}")
    return command


def intake_validate_trust_brief(command: TrustBriefDiligenceCommand) -> TrustBriefDiligenceCommand:
    """n01 — validate Trust Brief / M&A diligence intake."""
    if not command.submitted_by.strip():
        raise FactoryValidationError("submitted_by is required")
    payload = dict(command.signal_payload)
    source = payload.get("source")
    summary = payload.get("summary")
    if not source or not summary:
        if payload.get("target_name") or payload.get("thesis"):
            payload.setdefault("source", "investor_diligence")
            payload.setdefault(
                "summary",
                str(payload.get("thesis") or payload.get("target_name")),
            )
            return command.model_copy(update={"signal_payload": payload})
        raise FactoryValidationError(
            "signal_payload requires source and summary",
            details={"signal_payload": payload},
        )
    allowed = {"investor_diligence", "manual", "webhook"}
    if str(source) not in allowed:
        raise FactoryValidationError(f"signal_payload.source must be one of {sorted(allowed)}")
    return command


async def package_legal_deliverable(
    *,
    factory_id: str,
    state: LegalReviewPipelineState,
    event_bus: Any,
    audit_store: Any,
    graph_store: Any,
    governance_runtime: Any,
) -> dict[str, Any]:
    """n08 — policy review package for Legal factory."""
    command = state.command
    tenant_id = command.tenant_id
    organization_id = command.organization_id

    replayed_events = await event_bus.replay(
        EventReplayCursor(after_sequence=0, event_types=frozenset({"*"}))
    )
    events = [e for e in replayed_events if e.correlation_id == state.run_id] or replayed_events
    event_types = [event.event_type for event in events]

    pending_approvals = []
    if governance_runtime is not None:
        pending_approvals = await governance_runtime.approvals.list_pending(tenant_id)

    workflow_state = (
        state.workflow_state.value
        if state.workflow_state is not None
        else WorkflowState.PENDING_REVIEW.value
    )
    approval_required = state.approval_id is not None or workflow_state == "pending_review"

    policy_review_package = {
        "title": "Policy Review Package",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_summary": str(command.signal_payload.get("summary", "")),
        "executive_summary": (
            "Legal review signal ingested, linked to governance graph, evaluated by policy "
            "and inspectors, queued for human review before policy package export."
        ),
        "governance_state": {
            "workflow_state": workflow_state,
            "approval_required": approval_required,
            "approval_id": str(state.approval_id) if state.approval_id else None,
        },
        "orientation": "Policy review package for governance workflows — not legal advice.",
    }

    audit_records = getattr(audit_store, "records", [])
    audit_package: dict[str, Any] = {
        "tenant_id": str(tenant_id),
        "organization_id": str(organization_id),
        "signal_id": str(state.signal.signal_id) if state.signal else None,
        "workflow_id": str(state.workflow_id) if state.workflow_id else None,
        "event_count": len(events),
        "audit_record_count": len(audit_records),
        "event_types": event_types,
        "pending_approval_count": len(pending_approvals),
        "events": [event.model_dump(mode="json") for event in events],
    }

    if state.policy_decision and state.policy_decision.decision == AgentLoopDecision.REJECT:
        factory_status = "vetoed"
    elif approval_required:
        factory_status = "pending_approval"
    else:
        factory_status = "completed"

    return {
        "factory_id": factory_id,
        "factory_status": factory_status,
        "policy_review_package": policy_review_package,
        "audit_package": audit_package,
        "replay_hint": f"/events/replay?correlation_id={state.run_id}",
    }


async def package_aml_deliverable(
    *,
    factory_id: str,
    state: AmlGovernanceTracePipelineState,
    event_bus: Any,
    audit_store: Any,
    graph_store: Any,
    governance_runtime: Any,
) -> dict[str, Any]:
    """n08 — AML governance trace audit package."""
    command = state.command
    tenant_id = command.tenant_id
    organization_id = command.organization_id

    replayed_events = await event_bus.replay(
        EventReplayCursor(after_sequence=0, event_types=frozenset({"*"}))
    )
    events = [e for e in replayed_events if e.correlation_id == state.run_id] or replayed_events
    event_types = [event.event_type for event in events]

    pending_approvals = []
    if governance_runtime is not None:
        pending_approvals = await governance_runtime.approvals.list_pending(tenant_id)

    workflow_state = (
        state.workflow_state.value
        if state.workflow_state is not None
        else WorkflowState.PENDING_REVIEW.value
    )
    approval_required = state.approval_id is not None or workflow_state == "pending_review"

    aml_trace_audit_package = {
        "title": "AML Governance Trace Audit Package",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trace_summary": str(command.signal_payload.get("summary", "")),
        "executive_summary": (
            "AML governance trace signal ingested, linked to compliance graph, evaluated by "
            "policy and inspectors, queued for human review before audit package export."
        ),
        "governance_state": {
            "workflow_state": workflow_state,
            "approval_required": approval_required,
            "approval_id": str(state.approval_id) if state.approval_id else None,
        },
        "orientation": "Governance trace only — not MSB registration, screening execution, or payment routing.",
    }

    audit_records = getattr(audit_store, "records", [])
    audit_package: dict[str, Any] = {
        "tenant_id": str(tenant_id),
        "organization_id": str(organization_id),
        "signal_id": str(state.signal.signal_id) if state.signal else None,
        "workflow_id": str(state.workflow_id) if state.workflow_id else None,
        "event_count": len(events),
        "audit_record_count": len(audit_records),
        "event_types": event_types,
        "pending_approval_count": len(pending_approvals),
        "events": [event.model_dump(mode="json") for event in events],
    }

    if state.policy_decision and state.policy_decision.decision == AgentLoopDecision.REJECT:
        factory_status = "vetoed"
    elif approval_required:
        factory_status = "pending_approval"
    else:
        factory_status = "completed"

    return {
        "factory_id": factory_id,
        "factory_status": factory_status,
        "aml_trace_audit_package": aml_trace_audit_package,
        "audit_package": audit_package,
        "replay_hint": f"/events/replay?correlation_id={state.run_id}",
    }


async def package_trust_brief_deliverable(
    *,
    factory_id: str,
    state: TrustBriefPipelineState,
    event_bus: Any,
    audit_store: Any,
    graph_store: Any,
    governance_runtime: Any,
) -> dict[str, Any]:
    """n08 — IC appendix + checklist map for Trust Brief diligence."""
    command = state.command
    tenant_id = command.tenant_id
    organization_id = command.organization_id

    replayed_events = await event_bus.replay(
        EventReplayCursor(after_sequence=0, event_types=frozenset({"*"}))
    )
    events = [e for e in replayed_events if e.correlation_id == state.run_id] or replayed_events
    event_types = [event.event_type for event in events]

    pending_approvals = []
    if governance_runtime is not None:
        pending_approvals = await governance_runtime.approvals.list_pending(tenant_id)

    workflow_state = (
        state.workflow_state.value
        if state.workflow_state is not None
        else WorkflowState.PENDING_REVIEW.value
    )
    approval_required = state.approval_id is not None or workflow_state == "pending_review"

    ic_appendix = {
        "title": "Investor Governance IC Appendix",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_summary": str(command.signal_payload.get("summary", "")),
        "executive_summary": (
            "Diligence signal ingested, linked to governance graph, evaluated by policy "
            "and inspectors, queued for human IC review before export."
        ),
        "governance_state": {
            "workflow_state": workflow_state,
            "approval_required": approval_required,
            "approval_id": str(state.approval_id) if state.approval_id else None,
        },
        "orientation": "Not legal advice. Maps to INVESTOR_GOVERNANCE_CHECKLIST_MAP_v1.",
    }

    checklist_map = {
        "map_version": "INVESTOR_GOVERNANCE_CHECKLIST_MAP_v1",
        "groups": [
            {"id": "policy_documentation", "item_count": 5},
            {"id": "bias_fairness_harm", "item_count": 5},
            {"id": "data_ip", "item_count": 4},
            {"id": "regulatory_exposure", "item_count": 4},
        ],
        "honest_gaps_documented": True,
        "noetfield_deliverables": ["/trust-brief/", "/gate/diligence/"],
    }

    audit_records = getattr(audit_store, "records", [])
    audit_package: dict[str, Any] = {
        "tenant_id": str(tenant_id),
        "organization_id": str(organization_id),
        "signal_id": str(state.signal.signal_id) if state.signal else None,
        "workflow_id": str(state.workflow_id) if state.workflow_id else None,
        "event_count": len(events),
        "audit_record_count": len(audit_records),
        "event_types": event_types,
        "pending_approval_count": len(pending_approvals),
        "events": [event.model_dump(mode="json") for event in events],
    }

    if state.policy_decision and state.policy_decision.decision == AgentLoopDecision.REJECT:
        factory_status = "vetoed"
    elif approval_required:
        factory_status = "pending_approval"
    else:
        factory_status = "completed"

    return {
        "factory_id": factory_id,
        "factory_status": factory_status,
        "ic_appendix": ic_appendix,
        "checklist_map": checklist_map,
        "audit_package": audit_package,
        "replay_hint": f"/events/replay?correlation_id={state.run_id}",
    }


async def package_copilot_deliverable(
    *,
    factory_id: str,
    state: CopilotPipelineState,
    event_bus: Any,
    audit_store: Any,
    graph_store: Any,
    governance_runtime: Any,
) -> dict[str, Any]:
    """n08 — assemble board_brief and audit_package from pipeline state."""
    command = state.command
    tenant_id = command.tenant_id
    organization_id = command.organization_id

    replayed_events = await event_bus.replay(
        EventReplayCursor(after_sequence=0, event_types=frozenset({"*"}))
    )
    correlation_events = [
        event
        for event in replayed_events
        if event.correlation_id == state.run_id
        or (
            state.signal is not None
            and event.entity_id == str(state.signal.signal_id)
        )
    ]
    events = correlation_events if correlation_events else replayed_events
    event_types = [event.event_type for event in events]

    pending_approvals = []
    if governance_runtime is not None:
        pending_approvals = await governance_runtime.approvals.list_pending(tenant_id)

    relationships = await graph_store.relationships_for_tenant(tenant_id)

    workflow_state = (
        state.workflow_state.value
        if state.workflow_state is not None
        else WorkflowState.PENDING_REVIEW.value
    )
    approval_required = state.approval_id is not None or workflow_state == "pending_review"

    board_brief: dict[str, Any] = {
        "title": "Copilot Governance Readiness Brief",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "positioning": "AI Trust Infrastructure for regulated enterprises",
        "executive_summary": (
            "The governed signal was ingested, linked into the governance graph, "
            "evaluated by policy and inspectors, moved into workflow review, and "
            "preserved in a replayable audit trail."
        ),
        "risk_findings": [
            "Copilot usage creates oversharing and evidence-readiness exposure.",
            "Governance policy requires human review before publication or board use.",
            "Audit replay is available for signal, graph, workflow, and approval events.",
        ],
        "governance_state": {
            "workflow_state": workflow_state,
            "approval_required": approval_required,
            "approval_id": str(state.approval_id) if state.approval_id else None,
            "policy_enforced": "POLICY_EVALUATED" in event_types,
        },
        "graph_state": {
            "relationship_count": len(relationships),
            "relationship_id": str(state.relationship_id) if state.relationship_id else None,
            "reflection_id": str(state.reflection_id) if state.reflection_id else None,
        },
        "inspector_state": {
            "run_id": str(state.inspector_run.run_id) if state.inspector_run else None,
            "status": state.inspector_run.status if state.inspector_run else None,
            "finding_count": len(state.inspector_run.findings) if state.inspector_run else 0,
            "requires_human_review": (
                state.inspector_run.requires_human_review if state.inspector_run else True
            ),
        },
    }

    audit_records = getattr(audit_store, "records", [])
    audit_package: dict[str, Any] = {
        "tenant_id": str(tenant_id),
        "organization_id": str(organization_id),
        "signal_id": str(state.signal.signal_id) if state.signal else None,
        "workflow_id": str(state.workflow_id) if state.workflow_id else None,
        "event_count": len(events),
        "audit_record_count": len(audit_records),
        "event_types": event_types,
        "pending_approval_count": len(pending_approvals),
        "events": [event.model_dump(mode="json") for event in events],
    }

    if state.policy_decision and state.policy_decision.decision == AgentLoopDecision.REJECT:
        factory_status = "vetoed"
    elif approval_required:
        factory_status = "pending_approval"
    else:
        factory_status = "completed"

    return {
        "factory_id": factory_id,
        "factory_status": factory_status,
        "board_brief": board_brief,
        "audit_package": audit_package,
        "replay_hint": f"/events/replay?correlation_id={state.run_id}",
    }


def factory_actor(submitted_by: str) -> Actor:
    return Actor(actor_type=ActorType.SERVICE, actor_id=submitted_by, display_name=submitted_by)
