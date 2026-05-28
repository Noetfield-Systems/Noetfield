"""Temporal-ready workflow orchestration boundaries."""

from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from noetfield_types import GovernanceBoundary, WorkflowState


class WorkflowCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    workflow_type: str
    requested_by: str
    target_entity_type: str
    target_entity_id: str
    payload: dict[str, object] = Field(default_factory=dict)


class WorkflowDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_id: UUID = Field(default_factory=uuid4)
    state: WorkflowState
    requires_human_review: bool
    next_actions: list[str] = Field(default_factory=list)
    governance_boundary: GovernanceBoundary = Field(default_factory=GovernanceBoundary)


class WorkflowOrchestrator:
    """Deterministic workflow boundary before introducing Temporal workers."""

    def start(self, command: WorkflowCommand) -> WorkflowDecision:
        return WorkflowDecision(
            state=WorkflowState.PENDING_REVIEW,
            requires_human_review=True,
            next_actions=["emit_WORKFLOW_STARTED", "assign_human_reviewer"],
        )
