# Noetfield SSOT Index

**Status:** Canonical entry point for humans and agents  
**Agent tag:** `NF-CLOUD-AGENT`  
**Updated:** 2026-06-12  
**Supremacy:** GCIP v4 (L0) → [NORTH_STAR.md](../NORTH_STAR.md) → locks in this table

---

## Read order (60 seconds)

1. [PRODUCT_TRUTH.md](../PRODUCT_TRUTH.md) — one sentence + hard negatives  
2. [UNIFIED_ENGINE_COMMERCIAL_MODEL_LOCKED_v1.md](./architecture/UNIFIED_ENGINE_COMMERCIAL_MODEL_LOCKED_v1.md) — commercial front vs portfolio engine (internal)  
3. [NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md](./architecture/NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md) — SME-grade product blueprint  
4. [OFFERINGS_LOCKED.md](../OFFERINGS_LOCKED.md) — three contract SKUs only  
5. [PLATFORM_BLUEPRINT.md](../PLATFORM_BLUEPRINT.md) — architecture constitution  
6. [PAGE_AUTHORITY_MAP.md](./site/PAGE_AUTHORITY_MAP.md) — URL → governing doc  

---

## Layer model (two planes)

| Plane | What it is | Buyer sees? | Governing docs |
|-------|------------|-------------|----------------|
| **Commercial front** | `noetfield.com` www, offerings, Copilot funnel, procurement | **Yes** | `PRODUCT_TRUTH`, `OFFERINGS_LOCKED`, `public-surface-map`, `PAGE_AUTHORITY_MAP` |
| **Portfolio engine** | Pre-LLM gate · policy BLOCK/ALLOW · receipt spine · validators · agentic runtime | **No** — never SKU, never hero | `UNIFIED_ENGINE_*` § Internal only; SourceA on founder Mac |
| **Ship runtime** | `services/governance/`, `governance-console/`, verify scripts | Partial (API/docs only) | `PLATFORM_BLUEPRINT` §8, `services/governance/README.md` |

**Direction:** Portfolio engine informs product; **only LOCKED repo files + verify** govern www copy.

---

## Constitutional locks (repo root)

| Doc | Role | www-safe |
|-----|------|----------|
| [PRODUCT_TRUTH.md](../PRODUCT_TRUTH.md) | Product identity | Yes |
| [STRATEGIC_LOCK.md](../STRATEGIC_LOCK.md) | Boundaries + surfaces | Yes |
| [NORTH_STAR.md](../NORTH_STAR.md) | Production alignment | Partial — filter for www |
| [POSITIONING.md](../POSITIONING.md) | External one-liner | Yes |
| [OFFERINGS_LOCKED.md](../OFFERINGS_LOCKED.md) | Revenue SKUs | Yes |
| [PROJECT_BOUNDARIES_LOCKED.md](../PROJECT_BOUNDARIES_LOCKED.md) | NF / TF / VIRLUX fence | Internal |
| [PLATFORM_BLUEPRINT.md](../PLATFORM_BLUEPRINT.md) | Architecture constitution | Partial |

---

## Architecture & SME blueprint

| Doc | Role |
|-----|------|
| [UNIFIED_ENGINE_COMMERCIAL_MODEL_LOCKED_v1.md](./architecture/UNIFIED_ENGINE_COMMERCIAL_MODEL_LOCKED_v1.md) | Engine-in-basement · Noetfield at the door |
| [NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md](./architecture/NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md) | High-grade SME provider: modules, flows, W3 package |
| [NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md](./strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md) | Lane A/B/C domain split |
| [trustfield-noetfield-conflict-matrix.md](./spec/trustfield-noetfield-conflict-matrix.md) | Dual-brand handoff |

---

## Strategy & GTM

| Doc | Role |
|-----|------|
| [MARKET_ANALYSIS_2026_LOCKED_v1.md](./strategy/MARKET_ANALYSIS_2026_LOCKED_v1.md) | Live research synthesis (June 2026) |
| [INSTITUTIONAL_BENCHMARK_10_STEP_PLAN_v1.md](./strategy/INSTITUTIONAL_BENCHMARK_10_STEP_PLAN_v1.md) | Benchmark map + 10-step institutional redesign |
| [NOETFIELD_FORWARD_QUEUE_100_v1.md](./strategy/NOETFIELD_FORWARD_QUEUE_100_v1.md) | 100 forward plans FQ-001–100 |
| [NOETFIELD_GTM_60_DAY_LOCKED_v1.md](./strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md) | 60-day CEO fence |

---

## Runtime & spec

| Doc | Role |
|-----|------|
| [TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](./spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) | TLE product spec |
| [services/governance/README.md](../services/governance/README.md) | Production FastAPI |
| [governance-console/README.md](../governance-console/README.md) | Golden Edge dev stack |

---

## Agent / under-hood (not buyer-facing)

| Doc | Role |
|-----|------|
| [AGENT_READ_LINKS_LOCKED_v1.md](./ops/AGENT_READ_LINKS_LOCKED_v1.md) | Cloud read order |
| [SOURCEA_MANDATORY_SYNC_STATUS_v1.md](./ops/SOURCEA_MANDATORY_SYNC_STATUS_v1.md) | SourceA mirror status |
| [GTM_NEXT.md](./ops/plans/no-asf/GTM_NEXT.md) | Tier A ship queue |
| [os/LOCKED_REFERENCE_INDEX.md](../os/LOCKED_REFERENCE_INDEX.md) | Curated lock index |

---

## Corpus (read-only context — never www primary)

| Location | Rule |
|----------|------|
| `docs/SOURCE_OF_TRUTH/uploaded/` | Filter at implement; `PRODUCT_TRUTH` wins |
| `L2-knowledge/strategy/` | Internal research |
| `Noetfield-All-Documents/` | `noetfield_local` lane — not cloud primary |

---

## Verify bundle

```bash
./scripts/plan-with-no-asf-verify.sh
make verify-gtm
python3 scripts/audit_intake_email.py
```

---

## Founder one-liner (external)

> Noetfield governs Copilot execution — invalid changes blocked, allowed changes receipted, tamper fails on export.

## Founder one-liner (internal)

> Portfolio governance engine powers commercial fronts; Noetfield is primary earner; TrustField is second face; engine is not sold as SKU.
