"""Graph inference engine skeleton for Noetfield v3.1.

The engine is intentionally bounded: it produces structured candidates,
confidence scores, and audit-ready reasoning references. It does not silently
mutate authoritative graph state without a repository adapter and governance
events.
"""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from noetfield_types import ConfidenceScore, Entity, EntityRelationship


class GraphRepository(Protocol):
    """Persistence boundary for graph entities, relationships, and evidence."""

    async def find_entity(self, tenant_id: UUID, canonical_name: str) -> Entity | None:
        ...

    async def create_entity(self, entity: Entity) -> Entity:
        ...

    async def upsert_relationship(self, relationship: EntityRelationship) -> EntityRelationship:
        ...

    async def existing_relationships(self, tenant_id: UUID) -> list[EntityRelationship]:
        ...


class EntityCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    entity_type: str
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    attributes: dict[str, object] = Field(default_factory=dict)


class RelationshipCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: str
    evidence_ids: list[UUID] = Field(default_factory=list)
    confidence_inputs: dict[str, float] = Field(default_factory=dict)
    inferred: bool = False


class InferenceRunInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    entity_candidates: list[EntityCandidate] = Field(default_factory=list)
    relationship_candidates: list[RelationshipCandidate] = Field(default_factory=list)
    minimum_confidence: float = Field(default=0.65, ge=0.0, le=1.0)


class InferenceRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID = Field(default_factory=uuid4)
    entities_resolved: int
    relationships_upserted: int
    inferred_relationships: int
    conflicts_detected: int
    governance_event_refs: list[str] = Field(default_factory=list)


@dataclass
class GraphInferenceEngine:
    """LangGraph-ready graph inference boundary.

    A future implementation can wrap `run_full_inference` in a LangGraph state
    graph. The deterministic methods below remain the testable domain core.
    """

    repository: GraphRepository

    async def resolve_or_create_entity(self, candidate: EntityCandidate) -> Entity:
        existing = await self.repository.find_entity(candidate.tenant_id, candidate.canonical_name)
        if existing:
            return existing

        entity = Entity(
            tenant_id=candidate.tenant_id,
            organization_id=candidate.organization_id,
            entity_type=candidate.entity_type,
            canonical_name=candidate.canonical_name,
            aliases=candidate.aliases,
            source_refs=candidate.source_refs,
            attributes=candidate.attributes,
            confidence=ConfidenceScore(
                score=0.75,
                method="candidate_baseline",
                rationale="Entity created from structured candidate awaiting enrichment.",
            ),
        )
        return await self.repository.create_entity(entity)

    async def upsert_relationship(
        self, candidate: RelationshipCandidate
    ) -> EntityRelationship:
        confidence = self.calculate_confidence(candidate.confidence_inputs)
        relationship = EntityRelationship(
            tenant_id=candidate.tenant_id,
            organization_id=candidate.organization_id,
            source_entity_id=candidate.source_entity_id,
            target_entity_id=candidate.target_entity_id,
            relationship_type=candidate.relationship_type,
            evidence_ids=candidate.evidence_ids,
            confidence=confidence,
            inferred=candidate.inferred,
        )
        return await self.repository.upsert_relationship(relationship)

    async def infer_multi_hop_relationships(
        self, tenant_id: UUID, organization_id: UUID
    ) -> list[EntityRelationship]:
        relationships = await self.repository.existing_relationships(tenant_id)
        inferred: list[EntityRelationship] = []
        by_source: dict[UUID, list[EntityRelationship]] = {}

        for relationship in relationships:
            by_source.setdefault(relationship.source_entity_id, []).append(relationship)

        for first in relationships:
            for second in by_source.get(first.target_entity_id, []):
                if first.source_entity_id == second.target_entity_id:
                    continue
                inferred.append(
                    EntityRelationship(
                        tenant_id=tenant_id,
                        organization_id=organization_id,
                        source_entity_id=first.source_entity_id,
                        target_entity_id=second.target_entity_id,
                        relationship_type=f"inferred::{first.relationship_type}->{second.relationship_type}",
                        evidence_ids=[*first.evidence_ids, *second.evidence_ids],
                        confidence=ConfidenceScore(
                            score=min(first.confidence.score, second.confidence.score) * 0.85,
                            method="multi_hop_minimum_decay",
                            rationale="Two-hop inference with confidence decay.",
                        ),
                        inferred=True,
                    )
                )

        return inferred

    def calculate_confidence(self, inputs: dict[str, float]) -> ConfidenceScore:
        if not inputs:
            return ConfidenceScore(
                score=0.5,
                method="default_low_information",
                rationale="No confidence inputs supplied.",
            )

        bounded = [max(0.0, min(1.0, value)) for value in inputs.values()]
        score = sum(bounded) / len(bounded)
        return ConfidenceScore(
            score=score,
            method="weighted_average_placeholder",
            rationale="Baseline confidence until graph-specific calibration is implemented.",
        )

    async def run_full_inference(self, run_input: InferenceRunInput) -> InferenceRunResult:
        entities_resolved = 0
        relationships_upserted = 0

        for candidate in run_input.entity_candidates:
            await self.resolve_or_create_entity(candidate)
            entities_resolved += 1

        for candidate in run_input.relationship_candidates:
            relationship = await self.upsert_relationship(candidate)
            if relationship.confidence.score >= run_input.minimum_confidence:
                relationships_upserted += 1

        inferred = await self.infer_multi_hop_relationships(
            run_input.tenant_id, run_input.organization_id
        )

        return InferenceRunResult(
            entities_resolved=entities_resolved,
            relationships_upserted=relationships_upserted,
            inferred_relationships=len(inferred),
            conflicts_detected=0,
        )
