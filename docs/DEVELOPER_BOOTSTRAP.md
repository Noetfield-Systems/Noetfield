# Developer Bootstrap

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker
- Make

## Local environment

Copy the environment template:

```bash
cp .env.example .env
```

Start local dependencies:

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

Install Python and frontend dependencies:

```bash
make bootstrap
```

Run backend API:

```bash
PYTHONPATH=packages/types:packages/config:services/events:services/ledger:services/graph:services/governance:services/workflow:services/ai-runtime:services/inspectors:services/identity \
  uvicorn noetfield_governance.api:app --reload --app-dir services/governance
```

Run app shells:

```bash
npm run dev:web
npm run dev:platform
npm run dev:admin
```

## Validation

```bash
make validate
```

## Governance development rules

- Do not add silent autonomous execution.
- Emit canonical governance events for consequential actions.
- Preserve raw signals and governance events as append-only records.
- Treat AI outputs as governed artifacts with citations, confidence, and review
  state.
- Add tenant boundaries to new data models from the beginning.
