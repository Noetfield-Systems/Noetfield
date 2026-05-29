# Source-of-Truth Registry

This registry organizes uploaded Noetfield blueprint documents into a governed
inventory.

## Files

- `source_document_inventory.json` lists every uploaded source document.
- `source_of_truth_registry.json` records active source-of-truth decisions by
  domain.
- `active_rule_candidates.json` extracts design rules that can become active
  runtime policy.

## Current active decisions

- Context Graph: `wp01-context-graph-runtime-edition-v2`
- NPL: `wp03-npl-formal-grammar-2026-05-npl-1`
- Developer OS strategy: `orchestration-policy-layer-source-of-truth-2026`
- Work packages: `developer-os-addendum-work-packages-2026`
- Security Agent: `security-agent-source-persian-normalized` as active
  reference pending formal WP-05 specification

## Database loading

Apply migrations first:

```bash
make apply-migrations
```

Dry-run inventory load:

```bash
PYTHONPATH=packages/types:packages/config:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance \
  python3 scripts/ingest_source_inventory.py --dry-run
```

Load into PostgreSQL:

```bash
PYTHONPATH=packages/types:packages/config:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance \
  DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/noetfield \
  python3 scripts/ingest_source_inventory.py
```

