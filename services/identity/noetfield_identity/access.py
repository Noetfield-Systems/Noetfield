"""Identity, RBAC, and ABAC boundary contracts."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    subject_id: str
    subject_roles: list[str] = Field(default_factory=list)
    subject_attributes: dict[str, str] = Field(default_factory=dict)
    action: str
    resource_type: str
    resource_id: str
    resource_attributes: dict[str, str] = Field(default_factory=dict)


class AccessDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool
    reason: str
    policy_refs: list[str] = Field(default_factory=list)


class AccessService:
    """OPA-ready access boundary.

    The initial implementation is conservative: deny by default unless a caller
    provides an explicit role that maps to the requested action.
    """

    def evaluate(self, request: AccessRequest) -> AccessDecision:
        if "tenant_admin" in request.subject_roles:
            return AccessDecision(allowed=True, reason="tenant_admin role", policy_refs=["rbac:v1"])
        if request.action in request.subject_roles:
            return AccessDecision(allowed=True, reason="role grants action", policy_refs=["rbac:v1"])
        return AccessDecision(allowed=False, reason="deny by default", policy_refs=["rbac:v1"])
