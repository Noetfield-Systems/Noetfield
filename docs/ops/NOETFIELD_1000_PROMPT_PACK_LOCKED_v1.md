# Noetfield 1000 Prompt Pack — LOCKED v1

**Status:** LOCKED  
**Locked:** 2026-06-03  
**Agent tag:** `NF-CLOUD-AGENT`  
**Authority:** Noetfield cloud agent (founder-maintained pack)

**Do not edit** without explicit founder unlock. Agents **implement** against this pack; do not rewrite strategy locks.

---

## Trigger: PLAN WITH NO ASF

> **CLOUD AGENTS:** Read the **Appendix — post-sync era** and **Step table overlay** below before the locked step table. Post-sync queue = GTM_NEXT, not GTM_PRIORITY outreach rows.

When the founder says **PLAN WITH NO ASF**, run this fixed sequence — no ASF wait, no TrustField, no fluff.

| Step | Action |
|------|--------|
| 0 | Read [.cursor/agent-memory/MEMORY_LOCKED.yaml](../../.cursor/agent-memory/MEMORY_LOCKED.yaml) + SKILL-001 — **Noetfield only** |
| 1 | Read [DOCS_UNIFIED_MAP_LOCKED_v1.md](./DOCS_UNIFIED_MAP_LOCKED_v1.md) if fragmented (SKILL-009) |
| 2 | Merge open ship PR to `main` if one exists |
| 3 | Read [os/SHIP_NOW.md](../../os/SHIP_NOW.md) → **[GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md) first** → [QUICK_PICK.md](./plans/no-asf/QUICK_PICK.md) wisdom backlog if GTM_NEXT empty |
| 4 | Pick **max 3** tasks from **GTM_NEXT** (`ship-*` IDs) — exclude `agentic_only` / **026** |
| 5 | Write `next_tasks` in [os/plan.json](../../os/plan.json) |
| 6 | Branch `cursor/<slug>-37f0` → implement → `npm run build` if console touched |
| 7 | Run **`./scripts/plan-with-no-asf-verify.sh`** |
| 8 | `python3 scripts/sync-prompt-pack-status.py` → update plan stubs → [reports/cursor-reply-latest.txt](../../reports/cursor-reply-latest.txt) |
| 9 | `./scripts/verify-agent-scope.sh` → commit `[NF-CLOUD-AGENT]` → push → draft PR |

---

## Pack location map

| Asset | Path |
|-------|------|
| **Machine registry (1000)** | [docs/ops/plans/registry.json](./plans/registry.json) |
| **Bridge NF-PLAN ↔ nf-future** | [docs/ops/plans/BRIDGE_NF_PLAN_TO_NF_FUTURE.json](./plans/BRIDGE_NF_PLAN_TO_NF_FUTURE.json) |
| **Quick pick** | [docs/ops/plans/no-asf/QUICK_PICK.md](./plans/no-asf/QUICK_PICK.md) — GTM_NEXT wins; wisdom backlog second |
| **Active ship queue** | [docs/ops/plans/no-asf/GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md) |
| **GTM priority 100** | [plans/PROMPT_PACK_LOCKED/GTM_PRIORITY_100.md](./plans/PROMPT_PACK_LOCKED/GTM_PRIORITY_100.md) (historical) |
| **Agent ops 50** | [plans/PROMPT_PACK_LOCKED/AGENT_OPS_50.md](./plans/PROMPT_PACK_LOCKED/AGENT_OPS_50.md) |
| **Drift & research 100** | [plans/PROMPT_PACK_LOCKED/DRIFT_AND_RESEARCH_100.md](./plans/PROMPT_PACK_LOCKED/DRIFT_AND_RESEARCH_100.md) |
| **Tier B/C gates** | [plans/PROMPT_PACK_LOCKED/TIER_GATES.md](./plans/PROMPT_PACK_LOCKED/TIER_GATES.md) |
| **Sources & verdicts** | [plans/PROMPT_PACK_LOCKED/SOURCES_AND_VERDICTS.md](./plans/PROMPT_PACK_LOCKED/SOURCES_AND_VERDICTS.md) |
| **Shipped manifest** | [plans/PROMPT_PACK_LOCKED/ENGINEERING_DONE_MANIFEST.md](./plans/PROMPT_PACK_LOCKED/ENGINEERING_DONE_MANIFEST.md) |
| **Unified 500 (FQ-001–500)** | [plans/PROMPT_PACK_LOCKED/UNIFIED_500_MASTER_v1.md](./plans/PROMPT_PACK_LOCKED/UNIFIED_500_MASTER_v1.md) |
| **Success model tiers** | [plans/PROMPT_PACK_LOCKED/SUCCESS_MODEL_TIERS_v1.md](./plans/PROMPT_PACK_LOCKED/SUCCESS_MODEL_TIERS_v1.md) |
| **Enriched next 50 picks** | [plans/PROMPT_PACK_LOCKED/ENRICHED_PICKS_NEXT_50_v1.md](./plans/PROMPT_PACK_LOCKED/ENRICHED_PICKS_NEXT_50_v1.md) |
| **Wisdom pick rules (v4)** | [plans/PROMPT_PACK_LOCKED/WISDOM_PICK_RULES_v1.md](./plans/PROMPT_PACK_LOCKED/WISDOM_PICK_RULES_v1.md) |
| **Executive synthesis** | [plans/PROMPT_PACK_LOCKED/PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md](./plans/PROMPT_PACK_LOCKED/PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md) |
| **All 500 tier index** | [plans/PROMPT_PACK_LOCKED/ALL_500_TIER_INDEX_v1.md](./plans/PROMPT_PACK_LOCKED/ALL_500_TIER_INDEX_v1.md) |
| **Machine index (JSON)** | [plans/PROMPT_PACK_LOCKED/unified_500_index.json](./plans/PROMPT_PACK_LOCKED/unified_500_index.json) |
| **Markdown stubs** | [os/plans/](../../os/plans/) (`nf-future-*`) |

**Regenerate:** `python3 scripts/generate-prompt-pack-v2.py`  
**Regenerate unified 500:** `python3 scripts/generate_unified_prompt_pack_500.py`  
**Sync done status:** `python3 scripts/sync-prompt-pack-status.py`

---

## Sources index (read before implement)

| Layer | Document |
|-------|----------|
| GTM 60-day | [docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md](../strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md) |
| Positioning | [docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md](../strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md) |
| Agent context | [docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](./NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md) |
| Agent memory | [.cursor/agent-memory/MEMORY_LOCKED.yaml](../../.cursor/agent-memory/MEMORY_LOCKED.yaml) |
| Self-audit loop | [docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md](./AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md) |
| Drift blueprints | [docs/references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md) |
| Architecture verdict | [docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-010/noetfield-architecture-verdict-postgres-first-fa.md](../SOURCE_OF_TRUTH/uploaded/2026-05-batch-010/noetfield-architecture-verdict-postgres-first-fa.md) |
| Ship queue | [os/SHIP_NOW.md](../../os/SHIP_NOW.md) · [GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md) · [os/plan.json](../../os/plan.json) |
| Doc map | [DOCS_UNIFIED_MAP_LOCKED_v1.md](./DOCS_UNIFIED_MAP_LOCKED_v1.md) |

---

## GTM priority fence (Tier A / B / C)

From GTM 60-day lock:

| Tier | When | Build |
|------|------|-------|
| **A — Now** | Before customer #2 | Demo URL, procurement zip, confidence on PDF cover (outreach = agentic Hub — R-011) |
| **B — After first customer** | Paid pilot | Real M365 read-only, Google Workspace stub |
| **C — After revenue** | 3+ customers | SSO, multi-tenant hardening |

Pack prompts with `tier_gate: B` or `C` are **blocked** until unlock conditions are met.

---

## Honest scorecard (2026-06-04)

| Area | Score |
|------|-------|
| Vision | 9/10 |
| Architecture | 8.5/10 |
| Product (pilot) | 8/10 |
| Technical execution | 8.5/10 |
| GTM | 4/10 until external demo + distribution |
| Customer validation | 2/10 until one contracted pilot |

**Bottleneck:** proof and buyer validation — not product features.

---

## Model benchmark (vs best-in-class agents)

| Best practice (top agents) | Noetfield status |
|----------------------------|------------------|
| Hard scope gate before work | MEMORY_LOCKED v5 + SKILL-001 + `verify-agent-scope` |
| Versioned incident memory | `.cursor/incidents/` + INCIDENT-2026-06-06-001 |
| Single verify bundle entrypoint | `plan-with-no-asf-verify.sh` (UI + pilot + audit + procurement) |
| Locked strategy read-order | `plan.json` locked_references + LOCKED_REFERENCE_INDEX |
| ≤3 tasks, no infra sprawl | GTM lock rule #4 |
| Prompt-ready long-term backlog | **This pack (1000 entries with `prompt`, `sources`, `verify_command`)** |
| Customer pipeline automation | **~200 GTM-weighted slots in pack** — primary gap to close |

---

## Per-plan schema (registry v2)

Every `NF-PLAN-*` entry includes:

- `prompt` — copy-paste agent instruction
- `sources[]` — locked refs to read
- `verify_command` — `./scripts/plan-with-no-asf-verify.sh`
- `gtm_priority` — 1 (highest) to 5
- `tier_gate` — A | B | C | none
- `nf_future_id` — bridge to `os/plans` stub
- `critic_note` — ship gate / GTM honesty check

---

## Critics & verdicts wired

- **Postgres-first architecture verdict** — ship only what supports pilot proof; defer scale infra
- **GTM scorecard** — validation 2/10 until board PDF used in real governance meeting
- **Scope incident** — TrustField bleed closed; Noetfield-only hard lock (R-001)
- **Drift blueprints** — implementation deferred to P9 / governance-drift area until Tier A customer proof

---

## Verify bundles (taxonomy)

| Bundle | When |
|--------|------|
| `./scripts/plan-with-no-asf-verify.sh` | Every PLAN WITH NO ASF closeout |
| `make verify-gtm` | Pre-demo with design partner |
| `make ship-verify` | Merge/deploy readiness (superset) |

---

## Appendix — post-sync era (GTM_NEXT queue)

**Added:** 2026-06-10 · **Agent-maintained addendum** (founder lock body unchanged)

When `sync-prompt-pack-status.py` reports **1000/1000 `done`**, the registry is fully deduped — **not** “no work left.”

| Era | Queue source | Pick rule |
|-----|--------------|-----------|
| Pre-sync | `QUICK_PICK.md` top 25 from registry backlog | `gtm_priority` ascending |
| Post-sync | [GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md) + `os/plan.json` `next_tasks` | ≤3 Tier A www/verify tasks |
| Agentic commercial | Hub / agentic layer only | e.g. `ship-design-partner-outreach-026` — **not** NF-CLOUD disk |

**Verify:** `./scripts/plan-with-no-asf-verify.sh` includes `verify-no-asf-coherence.sh` for queue/doc alignment.

### Step table overlay (post-audit — supersedes locked steps 1–4 for cloud agents)

| Step | Action (current) |
|------|------------------|
| 0 | MEMORY_LOCKED + SKILL-001 + SKILL-007 — stop after propose if no founder `implement` |
| 1 | Merge open ship PR **only inside approved implement bundle** |
| 2 | Read `os/SHIP_NOW.md` + [GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md) + QUICK_PICK |
| 3 | Pick **≤3** from **GTM_NEXT** Tier A — exclude agentic-only (026) |
| 4 | Write `next_tasks` in `os/plan.json` **after** founder `implement` |
| 5–8 | Unchanged (branch → verify → sync → cursor-reply → ASK) |

---

## Appendix — unified 500 forward queue (FQ-001–500)

**Added:** 2026-06-13 · **Agent-maintained addendum** · **v2 intelligence engine**

The **500 forward-queue prompts** (FQ-001–500) are re-tiered with **v2 pick intelligence**: weighted success tiers, GTM impact scoring (0–100), ship-aware status (`open` / `partial`), and structured `prompt_structured` fields per plan.

| Asset | Path |
|-------|------|
| Pick intelligence | [PICK_INTELLIGENCE_v1.md](./plans/PROMPT_PACK_LOCKED/PICK_INTELLIGENCE_v1.md) |
| Machine index (500 plans) | [unified_500_index.json](./plans/PROMPT_PACK_LOCKED/unified_500_index.json) |
| Human master + top 25 | [UNIFIED_500_MASTER_v1.md](./plans/PROMPT_PACK_LOCKED/UNIFIED_500_MASTER_v1.md) |
| Success tier taxonomy | [SUCCESS_MODEL_TIERS_v1.md](./plans/PROMPT_PACK_LOCKED/SUCCESS_MODEL_TIERS_v1.md) |
| Next 50 enriched picks | [ENRICHED_PICKS_NEXT_50_v1.md](./plans/PROMPT_PACK_LOCKED/ENRICHED_PICKS_NEXT_50_v1.md) |

### Pick order (success model — supersedes raw FQ number)

1. **S0-proof** — demo · TLE · procurement (customer #1)
2. **S6-tle-wedge** — receipt differentiation
3. **S2-copilot-complement** — Agent 365 / Purview
4. **S4-trust-ui** — trust center / diligence
5. **S1-positioning** — www copy (Form PICK first)
6. **S3-msp** or **S5-federal** — lane-locked when ICP matches
7. **S7-hardening** — engineering hygiene (after S0–S4)
8. **S8-agentic** — Hub only (R-011)

### ICP batch locks

| Batch | FQ range | Lane |
|-------|----------|------|
| v1–v3 | 001–300 | Mixed SME / trust / board |
| v4 | 301–400 | **F** federal only |
| v5 | 401–500 | **M** MSP only |

### Regenerate

```bash
python3 scripts/generate_unified_prompt_pack_500.py
```

**Verify:** `verify-no-asf-coherence.sh` checks unified 500 index count + QUICK_PICK alignment.

---

## Related

- [docs/ops/plans/README.md](./plans/README.md)
- [os/LOCKED_REFERENCE_INDEX.md](../../os/LOCKED_REFERENCE_INDEX.md)
- [GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md)
