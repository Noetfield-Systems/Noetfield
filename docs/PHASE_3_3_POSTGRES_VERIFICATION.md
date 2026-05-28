# Phase 3.3 PostgreSQL Runtime Verification

Phase 3.3 proves that the backend runtime can execute against PostgreSQL as the
system of record.

## What this phase adds

- Idempotent migration runner using `noetfield.schema_migrations`
- Pytest memory-mode runtime verification
- Pytest PostgreSQL integration verification
- GitHub Actions workflow with `pgvector/pgvector:pg16`
- Repeatable local commands for migration and smoke verification

## Local fast verification

```bash
make phase33-verify
```

This runs the backend smoke path with in-memory stores.

## PostgreSQL verification

Start PostgreSQL/pgvector, then run:

```bash
make apply-migrations
make phase32-postgres-smoke
make phase33-postgres-verify
```

The PostgreSQL path verifies:

- migration application
- event persistence
- event replay
- audit-ledger subscription
- signal persistence
- graph mutation and reflection persistence
- workflow state persistence
- governance approval queue persistence
- inspector execution persistence
- Copilot Governance use-case run persistence

## CI

`.github/workflows/phase-3-runtime.yml` runs the PostgreSQL verification flow
with a real `pgvector/pgvector:pg16` service container.

## Current environment note

Some cloud agents do not include Docker. In that case, run memory-mode
verification locally in the agent and rely on the CI/service-container workflow
for PostgreSQL-backed verification.
