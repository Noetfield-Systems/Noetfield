"""Bounded inspector framework for ambient intelligence."""

from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from noetfield_types import GovernanceBoundary, InspectorFinding


class InspectorContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    invoked_by: str
    objective: str
    graph_scope: dict[str, object] = Field(default_factory=dict)
    governance_boundary: GovernanceBoundary = Field(default_factory=GovernanceBoundary)


class InspectorResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID = Field(default_factory=uuid4)
    inspector_name: str
    findings: list[InspectorFinding] = Field(default_factory=list)
    audit_event_refs: list[str] = Field(default_factory=list)
    requires_human_review: bool = True


class NoetfieldInspector(ABC):
    """Base class for collaborative, governed ambient inspectors."""

    name: str
    minimum_confidence: float = 0.75

    @abstractmethod
    async def run(self, context: InspectorContext) -> InspectorResult:
        """Run the inspector within explicit governance boundaries."""

    def enforce_boundary(self, finding: InspectorFinding) -> InspectorFinding:
        if finding.confidence.score < self.minimum_confidence:
            finding.governance_boundary.requires_human_review = True
        return finding
