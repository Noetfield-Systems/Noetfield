"""Policy evaluation contracts for workflow-first governance."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PolicyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    context: dict[str, object] = Field(default_factory=dict)


class PolicyEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool
    requires_human_review: bool
    reason: str
    policy_refs: list[str] = Field(default_factory=list)
    obligations: list[str] = Field(default_factory=list)


class PolicyEvaluator:
    """OPA-ready policy boundary.

    This class defines the stable contract. A future adapter should delegate to
    OPA for tenant-specific policy bundles while preserving this response model.
    """

    def evaluate(self, policy_input: PolicyInput) -> PolicyEvaluation:
        high_impact_actions = {"approve_workflow", "execute_inspector_action", "publish_report"}
        return PolicyEvaluation(
            allowed=True,
            requires_human_review=policy_input.action in high_impact_actions,
            reason="baseline policy contract",
            policy_refs=["noetfield:governance-baseline:v1"],
            obligations=["emit_governance_event", "retain_audit_trace"],
        )
