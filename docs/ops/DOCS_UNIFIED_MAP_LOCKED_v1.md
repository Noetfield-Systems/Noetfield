# Docs unified map (LOCKED v1)

| Field | Value |
|-------|--------|
| Agent tag | `NF-CLOUD-AGENT` |
| Updated | 2026-06-12 |
| Role | **Single-page map** — silos, entry points, precedence, forbidden paths |

Read this when docs feel fragmented. **Leaf docs stay separate; this file routes only.**

---

## Entry points (pick one)

| Audience | Start | Then |
|----------|-------|------|
| **Human founder** | [README.md](../../README.md) | [SSOT_INDEX.md](../SSOT_INDEX.md) → [os/SHIP_NOW.md](../../os/SHIP_NOW.md) |
| **Cloud agent** | [AGENT_READ_LINKS_LOCKED_v1.md](./AGENT_READ_LINKS_LOCKED_v1.md) § Cloud ship | [SSOT_INDEX.md](../SSOT_INDEX.md) → [MEMORY_LOCKED.yaml](../../.cursor/agent-memory/MEMORY_LOCKED.yaml) |
| **Ship execution** | [os/SHIP_NOW.md](../../os/SHIP_NOW.md) | [os/plan.json](../../os/plan.json) → [GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md) |
| **PLAN WITH NO ASF** | [QUICK_PICK.md](./plans/no-asf/QUICK_PICK.md) | **Active queue = GTM_NEXT** (see precedence below) |

---

## Canonical chain

```
README.md
  └─ docs/SSOT_INDEX.md          ← master index (constitutional + strategy + spec)
       ├─ Root locks             PRODUCT_TRUTH · OFFERINGS_LOCKED · PLATFORM_BLUEPRINT
       ├─ docs/site/             PAGE_AUTHORITY_MAP · ACTIVE_SITE_POLICY
       ├─ docs/spec/             TLE blueprint · sprint backlog · schemas
       ├─ docs/strategy/         GTM · institutional UI · market roadmap
       ├─ docs/references/       Governance handbook · drift (LOCKED only)
       └─ docs/ops/              Agent locks · ship queues · prompt pack

os/SHIP_NOW.md → os/plan.json → GTM_NEXT.md → QUICK_PICK.md
```

**Verify gate:** `./scripts/plan-with-no-asf-verify.sh`

---

## Silos (what lives where)

| Silo | Path | Use when |
|------|------|----------|
| **SSOT index** | `docs/SSOT_INDEX.md` | Any doc lookup |
| **This map** | `docs/ops/DOCS_UNIFIED_MAP_LOCKED_v1.md` | Fragmentation / “where do I start?” |
| **Router** | `docs/INDEX.md` | Fast jump table |
| **Curated locks** | `os/LOCKED_REFERENCE_INDEX.md` | Agent session — top 30 links |
| **Ship runtime** | `os/SHIP_NOW.md` · `os/plan.json` | What ships this iter |
| **Active queue** | `docs/ops/plans/no-asf/GTM_NEXT.md` | Tier A disk tasks (authoritative) |
| **Pick helper** | `docs/ops/plans/no-asf/QUICK_PICK.md` | PLAN WITH NO ASF — ≤3 tasks |
| **NF-PLAN registry** | `docs/ops/plans/registry.json` | Engineering IDs NF-PLAN-* |
| **nf-future library** | `os/plans/nf-future-*.md` | Long-horizon stubs nf-future-* |
| **Market roadmap** | `docs/strategy/MARKET_SUCCESS_1000_ROADMAP_v1.md` | Archetype steps mr-* (SM-01–10) |
| **Forward queues** | `docs/strategy/NOETFIELD_FORWARD_QUEUE_100_v*.md` | Strategy backlog FQ-* |
| **Unified 500 pack** | `docs/ops/plans/PROMPT_PACK_LOCKED/` | Pattern-ranked picks |
| **Agent governance** | `.cursor/rules/` · `.cursor/skills/` · `MEMORY_LOCKED.yaml` | Session law |
| **Incidents** | `.cursor/incidents/REGISTRY.md` | Boundary history |
| **Corpus (read-only)** | `docs/SOURCE_OF_TRUTH/uploaded/` | Context — never www primary |

---

## Plan ID namespaces (do not mix)

| Prefix | File | Meaning |
|--------|------|---------|
| `ship-*` | `GTM_NEXT.md` | **Active ship tasks** — implement now |
| `ship-fwd-*` | `UNIFIED_500_MASTER` / forward queues | Wisdom-ranked backlog — pick after GTM_NEXT empty |
| `NF-PLAN-*` | `registry.json` | Engineering registry (990 agent items) |
| `nf-future-*` | `os/plans/` | Future stub library |
| `mr-*` | `MARKET_SUCCESS_1000_ROADMAP` | Market archetype roadmap |
| `FQ-*` | `NOETFIELD_FORWARD_QUEUE_100_v*` | Strategy forward queue |
| `bank-ui-*` | `INSTITUTIONAL_BANK_GRADE_100_PLAN` | UI execution items |

**Bridge:** `docs/ops/plans/BRIDGE_NF_PLAN_TO_NF_FUTURE.json`

---

## QUICK_PICK precedence (LOCKED)

When founder says **PLAN WITH NO ASF**:

1. **If `GTM_NEXT.md` has open `ship-*` tasks** → pick from GTM_NEXT (max 3).
2. **Else** → pick from wisdom `ship-fwd-*` table in QUICK_PICK (max 3).
3. **Never** pick `asf_only` / S8 Hub items in cloud repo.
4. **Agentic outreach** (`ship-design-partner-outreach-026`) = Hub only — list, do not execute.

---

## UI & institutional docs (one ladder)

| Layer | Doc | Granularity |
|-------|-----|-------------|
| Client-safe site plan | `INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md` | 10 steps |
| Bank-grade execution | `INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md` | 100 items |
| Tier-1 world-class target | `UI_TIER1_10_UPGRADES_v1.md` | 10 big upgrades |
| Market archetypes | `MARKET_SUCCESS_1000_ROADMAP_v1.md` | 1000 steps |
| Design tokens | `DESIGN_SYSTEM.md` | Components (update with v4/v5) |
| Checklist | `BANK_GRADE_CHECKLIST.md` | Ship gates |

**Shipped UI baseline:** `assets/noetfield-institutional-v4.css` · `verify-ui-visual-e2e.sh`

---

## Forbidden / redirect only

| Path | Rule |
|------|------|
| `docs/SHIP_NOW.md` | Redirect → `os/SHIP_NOW.md` |
| `docs/reference/` | Redirect → `docs/references/` (LOCKED) |
| `Noetfield-All-Documents/` | `noetfield_local` mirror — not cloud primary |
| `ops/private/` | Gitignored — founder machine only |
| `L2-knowledge/strategy/full/` | Duplicate corpus — prefer `docs/SOURCE_OF_TRUTH/` |

---

## Skills & memory (agent)

| Asset | Path | When |
|-------|------|------|
| Hard rules | `.cursor/agent-memory/MEMORY_LOCKED.yaml` | Every session start |
| Procedures | `.cursor/skills/SKILL-001` … `SKILL-009` | Before commit / new docs |
| Task priority | `.cursor/AGENT_TRACKING.md` | After memory |
| Incidents | `.cursor/incidents/REGISTRY.md` | On boundary cross |

**Precedence:** Founder order > R-001–R-011 > incidents > `GTM_NEXT` > wisdom backlog.

---

## Coherence scripts

| Script | Catches |
|--------|---------|
| `plan-with-no-asf-verify.sh` | Master bundle |
| `verify-no-asf-coherence.sh` | Ship pointers · GTM_NEXT sync · agentic fence |
| `verify-ui-e2e.sh` | Buyer copy on served routes |
| `verify-ui-visual-e2e.sh` | Homepage v4 structure |
| `verify-market-success-roadmap.sh` | mr-0001–1000 integrity |
| `verify-agent-scope.sh` | Noetfield-only before commit |

---

## Adding new docs (light rule)

1. Tag with agent header if agent-authored ([AGENT_DOC_TAGGING_LOCKED_v1.md](./AGENT_DOC_TAGGING_LOCKED_v1.md)).
2. Add **one line** to [SSOT_INDEX.md](../SSOT_INDEX.md) — not a new index file.
3. If ship-related → add to `GTM_NEXT` or registry, not a third queue.
4. Run `./scripts/plan-with-no-asf-verify.sh` if touching ops/ship/verify paths.

---

## Flat `docs/` root files (taxonomy)

| Category | Examples |
|----------|----------|
| **Entry / index** | `INDEX.md`, `SSOT_INDEX.md`, `SHIP_NOW.md` (redirect) |
| **Runbooks** | `GO_LIVE.md`, `RUNBOOK.md`, `LOCAL_DEV.md`, `STAGING.md` |
| **GTM / launch** | `GTM_COPYBOOK.md`, `MARKET_ENTRY_30_DAY.md`, `GTM_BANK_GRADE_FINAL.md` |
| **Checklists** | `BANK_GRADE_CHECKLIST.md`, `WAVE0_SHIP_CHECKLIST.md` |
| **Site policy** | `CANONICAL_WWW.md`, `FINAL_PUBLIC_SITE.md`, `SITE_ARCHITECTURE.md` |
| **Design** | `DESIGN_SYSTEM.md` |
| **Public roadmap** | `ROADMAP.md` |
| **Phase archives** | `PHASE_3_*.md` — superseded by `docs/spec/`; context only |
| **MSB channel** | `MSB_DEPLOY_AND_PILOT.md`, `MSB_STAGING_INTEGRATION.md` |

Prefer subfolder READMEs: `ops/`, `strategy/`, `spec/`, `references/`, `diligence/`.
