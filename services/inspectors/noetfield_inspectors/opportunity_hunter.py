"""Opportunity Hunter inspector."""

from noetfield_types import ConfidenceScore, InspectorFinding

from .base import InspectorContext, InspectorResult, NoetfieldInspector


class OpportunityHunterInspector(NoetfieldInspector):
    name = "opportunity_hunter"
    minimum_confidence = 0.8

    async def run(self, context: InspectorContext) -> InspectorResult:
        finding = InspectorFinding(
            tenant_id=context.tenant_id,
            organization_id=context.organization_id,
            inspector_name=self.name,
            finding_type="market_opportunity",
            summary="Opportunity scan initialized; connect signal sources to produce findings.",
            confidence=ConfidenceScore(
                score=0.5,
                method="bootstrap_placeholder",
                rationale="No signal corpus has been attached yet.",
            ),
            recommended_actions=["connect_signal_sources", "run_graph_inference"],
        )
        return InspectorResult(
            inspector_name=self.name,
            findings=[self.enforce_boundary(finding)],
            requires_human_review=True,
        )
