---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
agent_alias: nf-local-agent
doc_id: drift-blueprints-cloud-read-order
doc_revision: 2
last_edited_at: "2026-06-06"
status: locked
committed: true
reviewed_by: nf-cloud-agent-pending
---

> **Authored by:** `[NF-LOCAL-REPO-AGENT]` — committed cloud read order. Cloud: path verify + index wiring with `[NF-CLOUD-AGENT]` only.

# Drift Blueprints — Cloud Agent Read Order (LOCKED v1)

**Canonical path:** `docs/references/` (plural)

---

## Read order

1. [docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md](../references/GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md) — taxonomy (boss)
2. [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) — product mandate
3. [docs/references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md) — router
4. Docs 1–4 in index order (engine → trust ledger → LLM → enterprise framework)
5. Code truth (private): `ops/private/agent-reference/NOETFIELD_DRIFT_IMPLEMENTATION_MAP.md`

## Committed blueprint files

| File |
|------|
| `docs/references/GOVERNANCE_DRIFT_ENGINE_BLUEPRINT_LOCKED_v1.md` |
| `docs/references/TRUST_LEDGER_FOR_DRIFT_BLUEPRINT_LOCKED_v1.md` |
| `docs/references/LLM_DRIFT_DETECTION_ARCHITECTURE_LOCKED_v1.md` |
| `docs/references/ENTERPRISE_GOVERNANCE_DRIFT_FRAMEWORK_LOCKED_v1.md` |

## Private (workspace disk — gitignored)

`ops/private/agent-reference/blueprints/` — implementation annexes (`[NF-LOCAL-REPO-AGENT]` only)

## Cloud edit scope (LOCKED)

- Path fixes, `LOCKED_REFERENCE_INDEX` wiring, shipped vs roadmap tables  
- **Do not** overwrite private annexes without UKE  
- Run `make ship-verify` if code touched

## GTM line

Noetfield records governance drift decisions before external execution—against signed Trust Ledger baseline, exported as audit evidence. We do not host customer models or ML observability lakes.
