"""Lead Scout inspector."""

from noetfield_types import ConfidenceScore, InspectorFinding

from .base import InspectorContext, InspectorResult, NoetfieldInspector


class LeadScoutInspector(NoetfieldInspector):
    name = "lead_scout"
    minimum_confidence = 0.78

    async def run(self, context: InspectorContext) -> InspectorResult:
        finding = InspectorFinding(
            tenant_id=context.tenant_id,
            organization_id=context.organization_id,
            inspector_name=self.name,
            finding_type="qualified_lead_signal",
            summary="Lead scout initialized; target account graph is not populated yet.",
            confidence=ConfidenceScore(
                score=0.5,
                method="bootstrap_placeholder",
                rationale="No account graph or lead sources have been configured yet.",
            ),
            recommended_actions=["connect_crm_or_account_sources", "define_icp_policy"],
        )
        return InspectorResult(
            inspector_name=self.name,
            findings=[self.enforce_boundary(finding)],
            requires_human_review=True,
        )
