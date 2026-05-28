"""Model-provider abstraction for governed AI execution."""

from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from noetfield_types import AIProvider, ConfidenceScore, GovernanceBoundary


class AICompletionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    provider: AIProvider
    model: str
    prompt: str
    system_prompt: str | None = None
    context_refs: list[str] = Field(default_factory=list)
    governance_boundary: GovernanceBoundary = Field(default_factory=GovernanceBoundary)


class AICompletionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: AIProvider
    model: str
    output: str
    citations: list[str] = Field(default_factory=list)
    confidence: ConfidenceScore
    requires_human_review: bool = True
    audit_event_refs: list[str] = Field(default_factory=list)


class AIProviderClient(ABC):
    """Provider contract for Ollama, Azure OpenAI, OpenAI, and Anthropic."""

    @abstractmethod
    async def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        """Return a governed completion response."""
