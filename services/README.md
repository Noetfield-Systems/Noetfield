# Noetfield Services

The v3.1 backend is a modular monolith with explicit service boundaries.

Current service boundaries:

- `identity`: SSO, RBAC, ABAC, tenant membership, and access decisions.
- `events`: canonical event contracts.
- `ledger`: append-only Trust Ledger boundary.
- `graph`: living knowledge graph inference boundary.
- `governance`: FastAPI entrypoint and policy evaluation boundary.
- `workflow`: Temporal-ready workflow orchestration boundary.
- `ai-runtime`: governed model provider abstraction.
- `inspectors`: bounded ambient inspector framework.

The boundary structure is designed for future extraction, but services should
remain deployable together until operational scale requires separation.
