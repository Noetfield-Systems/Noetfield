"""Threat Monitor inspector."""

from noetfield_types import ConfidenceScore, InspectorFinding

from .base import InspectorContext, InspectorResult, NoetfieldInspector


class ThreatMonitorInspector(NoetfieldInspector):
    name = "threat_monitor"
    minimum_confidence = 0.85

    async def run(self, context: InspectorContext) -> InspectorResult:
        finding = InspectorFinding(
            tenant_id=context.tenant_id,
            organization_id=context.organization_id,
            inspector_name=self.name,
            finding_type="strategic_threat",
            summary="Threat monitor initialized; risk signals require ingestion sources.",
            confidence=ConfidenceScore(
                score=0.5,
                method="bootstrap_placeholder",
                rationale="No monitored risk feeds have been configured yet.",
            ),
            recommended_actions=["configure_risk_feeds", "define_escalation_policy"],
        )
        return InspectorResult(
            inspector_name=self.name,
            findings=[self.enforce_boundary(finding)],
            requires_human_review=True,
        )
