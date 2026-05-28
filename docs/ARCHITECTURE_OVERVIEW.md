# Noetfield v3.1 Architecture Overview

Noetfield v3.1 introduces an executable foundation beside the existing static
site. The initial implementation is intentionally a modular monolith: service
boundaries are explicit, but deployment remains simple until scale and customer
isolation requirements justify separation.

## Primary layers

1. Public and product applications under `apps/`.
2. Domain services under `services/`.
3. Shared contracts and configuration under `packages/`.
4. Infrastructure scaffolding under `infrastructure/`.
5. Constitutional architecture documents under `docs/SOURCE_OF_TRUTH/`.

## Runtime posture

The backend begins with FastAPI, Pydantic contracts, PostgreSQL/Supabase,
Redis, structured governance events, and an append-only ledger boundary.
LangGraph and model provider abstractions are introduced as interfaces for
governed intelligence workflows, not as uncontrolled autonomous agents.

## Data posture

The database is layered:

1. Raw Signal Layer
2. Normalized Intelligence Layer
3. Living Knowledge Graph Layer
4. Governance Ledger Layer
5. Cognitive Memory Layer
6. Operational Runtime Layer

These layers preserve original truth, support inference, accumulate strategic
memory, and retain audit-grade execution history.

## Governance posture

Every consequential action should be attributable, timestamped, explainable,
reviewable, traceable, and exportable. AI outputs are governed artifacts that
carry citations, confidence, reasoning chains, and human review state.
