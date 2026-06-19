"""Factory models."""

from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from noetfield_copilot_governance import CopilotGovernanceCommand, CopilotGovernanceDemoResult


class FactoryStatus(StrEnum):
    COMPLETED = "completed"
    PENDING_APPROVAL = "pending_approval"
    VETOED = "vetoed"


class CopilotFactoryRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: CopilotGovernanceCommand
    source_request_id: str | None = None


# Backward-compatible alias
FactoryRunRequest = CopilotFactoryRunRequest


class TrustBriefFactoryRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: "TrustBriefDiligenceCommand"
    source_request_id: str | None = None


class LegalFactoryRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: "LegalReviewCommand"
    source_request_id: str | None = None


class AmlFactoryRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: "AmlGovernanceTraceCommand"
    source_request_id: str | None = None


class TrustBriefFactoryOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factory_id: str
    run_id: UUID
    factory_status: FactoryStatus
    ic_appendix: dict[str, Any]
    checklist_map: dict[str, Any]
    audit_package: dict[str, Any]
    replay_hint: str
    policy_decision: dict[str, Any] | None = None


class LegalFactoryOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factory_id: str
    run_id: UUID
    factory_status: FactoryStatus
    policy_review_package: dict[str, Any]
    audit_package: dict[str, Any]
    replay_hint: str
    policy_decision: dict[str, Any] | None = None


class AmlFactoryOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factory_id: str
    run_id: UUID
    factory_status: FactoryStatus
    aml_trace_audit_package: dict[str, Any]
    audit_package: dict[str, Any]
    replay_hint: str
    policy_decision: dict[str, Any] | None = None


class CopilotGovernanceFactoryOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factory_id: str
    run_id: UUID
    factory_status: FactoryStatus
    board_brief: dict[str, Any]
    audit_package: dict[str, Any]
    replay_hint: str
    runtime_result: CopilotGovernanceDemoResult | None = None
    policy_decision: dict[str, Any] | None = None


# Resolve forward refs
from noetfield_aml_trace import AmlGovernanceTraceCommand  # noqa: E402
from noetfield_legal_review import LegalReviewCommand  # noqa: E402
from noetfield_trust_brief import TrustBriefDiligenceCommand  # noqa: E402

TrustBriefFactoryRunRequest.model_rebuild()
LegalFactoryRunRequest.model_rebuild()
AmlFactoryRunRequest.model_rebuild()
