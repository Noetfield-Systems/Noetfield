---
id: trust-ledger-product-blueprint
status: locked
version: 1.2
locked_at: 2026-06-06
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
---

# Trust Ledger Product Blueprint (LOCKED v1.2)

**Status:** LOCKED — **product mandate** (L2). Architecture drift blueprints are supplements only.  
**Full positioning:** [NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md](../strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md)  
**Taxonomy:** [GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md](../references/GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md)

---

## Mandate (one line)

**evaluate → TLE → audit-export** — every engagement produces at least one signed Trust Ledger Entry (TLE v1).

---

## Core modules (shipped kernel)

| Module | Responsibility |
|--------|----------------|
| Trust Ledger Core | Append-only TLE store; signed digests; board pack / procurement ZIP |
| Evidence Index | Metadata catalog (sources, hashes, `ingested_at`) |
| Connector layer | M365 OAuth stub; `last_sync` on connectors |
| Workspace UI | TLE viewer, confidence badge, export links |
| Evaluate path | Draft TLE from evaluation + `compute_confidence_score()` |

---

## Drift blueprints relationship

| Doc | Relationship to this mandate |
|-----|------------------------------|
| [TRUST_LEDGER_FOR_DRIFT_BLUEPRINT_LOCKED_v1.md](../references/TRUST_LEDGER_FOR_DRIFT_BLUEPRINT_LOCKED_v1.md) | **TLE v1.3 extension** — richer entries, optional `prev_tle_digest`; not a second ledger |
| [GOVERNANCE_DRIFT_ENGINE_BLUEPRINT_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_ENGINE_BLUEPRINT_LOCKED_v1.md) | Enterprise surround — trajectory + response narrative |
| [LLM_DRIFT_DETECTION_ARCHITECTURE_LOCKED_v1.md](../references/LLM_DRIFT_DETECTION_ARCHITECTURE_LOCKED_v1.md) | Cite and record — customer observability; Noetfield records decision |
| [GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md) | Router — read after this doc |

---

## GTM honesty

Noetfield records governance drift **decisions** against signed TLE baseline — not a hosted ML observability platform.

---

## P0 ship queue (from cloud + local review)

| Priority | Work |
|----------|------|
| P0 | Drift Contract v0 — `drift_class`, `baseline_tle_id`, `delta_summary`, `severity` on evaluate/TLE paths |
| P0 | Evaluate vs last TLE diff helper |
| P0 | `risk_summary` + drift class in `confidence_factors` |
| P1 | Optional `prev_tle_digest` in schema + migration |
| P1 | Wire observability middleware → `observability_*` tables |
| P2 | Link `GET /events/replay` to audit-export narrative |

**Schema:** `packages/schemas/tle-v1.schema.json` · **Sprint:** `os/sprint-trust-ledger-v1.2.md`
