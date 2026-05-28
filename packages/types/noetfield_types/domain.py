"""Core domain models for the Noetfield governed intelligence runtime."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RiskTier(StrEnum):
    """Enterprise risk tiers used across governance and intelligence workflows."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActorType(StrEnum):
    HUMAN = "human"
    SERVICE = "service"
    AI = "ai"
    INSPECTOR = "inspector"


class AIProvider(StrEnum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"


class WorkflowState(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TenantScopedModel(BaseModel):
    """Base class for records that must never cross tenant boundaries."""

    model_config = ConfigDict(extra="forbid", frozen=False)

    tenant_id: UUID
    organization_id: UUID


class Actor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_type: ActorType
    actor_id: str
    display_name: str


class ConfidenceScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0.0, le=1.0)
    method: str
    rationale: str


class GovernanceBoundary(BaseModel):
    """Human governance boundary for AI and inspector execution."""

    requires_human_review: bool = True
    minimum_confidence: float = Field(default=0.75, ge=0.0, le=1.0)
    allowed_actions: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=list)


class GovernanceEvent(TenantScopedModel):
    """Canonical event envelope for append-only governance memory."""

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    event_version: str = "1.0"
    source_service: str
    source_request_id: str | None = None
    correlation_id: UUID = Field(default_factory=uuid4)
    causation_id: UUID | None = None
    actor: Actor
    entity_type: str
    entity_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    policy_context: dict[str, Any] = Field(default_factory=dict)
    risk_context: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    integrity_hash: str | None = None


class Entity(TenantScopedModel):
    entity_id: UUID = Field(default_factory=uuid4)
    entity_type: str
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    confidence: ConfidenceScore
    attributes: dict[str, Any] = Field(default_factory=dict)


class EntityRelationship(TenantScopedModel):
    relationship_id: UUID = Field(default_factory=uuid4)
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: str
    confidence: ConfidenceScore
    evidence_ids: list[UUID] = Field(default_factory=list)
    inferred: bool = False


class AIDecision(TenantScopedModel):
    decision_id: UUID = Field(default_factory=uuid4)
    provider: AIProvider
    model: str
    prompt_hash: str
    output_hash: str
    citations: list[str] = Field(default_factory=list)
    confidence: ConfidenceScore
    reasoning_chain_ref: str | None = None
    human_review_state: WorkflowState = WorkflowState.PENDING_REVIEW

    @model_validator(mode="after")
    def ensure_review_for_low_confidence(self) -> "AIDecision":
        if self.confidence.score < 0.85:
            self.human_review_state = WorkflowState.PENDING_REVIEW
        return self


class InspectorFinding(TenantScopedModel):
    finding_id: UUID = Field(default_factory=uuid4)
    inspector_name: str
    finding_type: str
    summary: str
    confidence: ConfidenceScore
    citations: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    governance_boundary: GovernanceBoundary = Field(default_factory=GovernanceBoundary)
