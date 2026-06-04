# Noetfield plan library (1000 plans)

**Lane:** `noetfield_cloud` · **Thread:** THREAD-PORTFOLIO  
**Use when:** Founder or agent says **PLAN WITH NO ASF** — do not wait for ASF; pick from agent-ready backlog.

## Start here

| File | Purpose |
|------|---------|
| [no-asf/QUICK_PICK.md](./no-asf/QUICK_PICK.md) | **PLAN WITH NO ASF** — next 25 agent plans |
| [INDEX.md](./INDEX.md) | Counts, phase/tier map |
| [registry.json](./registry.json) | All 1000 plans (machine-readable) |
| [by-phase/](./by-phase/) | 100 plans per phase P0–P9 |
| [by-tier/](./by-tier/) | 200 plans per tier T1–T5 |

## Phases (P0–P9)

| Phase | Theme |
|-------|--------|
| P0 | Foundation — ship, dev stack, ops, CI |
| P1 | Trust Ledger — TLE, evidence, export |
| P2 | Governance API — evaluate, audit, pilot |
| P3 | Connectors live — Purview, Entra, M365 |
| P4 | Workspace & GTM — UI, www |
| P5 | Enterprise — tenant, RBAC, KMS |
| P6 | Compliance — retention, SOC narratives |
| P7 | Scale — perf, observability |
| P8 | Integrations — MSB, partners |
| P9 | Horizon — research, ML confidence |

## Tiers (T1–T5)

| Tier | Horizon |
|------|---------|
| T1 | Critical — revenue / prod ship |
| T2 | Near-term — 1–2 sprints |
| T3 | Medium — quarters 2–4 |
| T4 | Strategic — 12–24 months |
| T5 | Horizon — experimental |

## Update policy (agents must follow)

1. **After each ship session** — mark completed plan IDs:
   ```bash
   python3 scripts/update-plan-status.py NF-PLAN-0123 NF-PLAN-0456 --status done
   ```
2. **Refresh quick pick** (optional, if structure changed):
   ```bash
   python3 scripts/generate-plans-registry.py
   ```
3. **Do not** delete the registry; append status changes only.
4. **ASF-only** items have `"asf_only": true` in registry — skip for no-ASF plans.
5. Align active execution with [os/plan.json](../../os/plan.json) and [lane_a_sprint_map.md](../lane_a_sprint_map.md); use this library for **long-term** backlog.

## Relation to SourceA

- Desktop canonical index: `~/Desktop/SourceA/founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md`
- This directory is the **in-repo** long-term plan bank for cloud agents.
- Never copy registry to SourceA (direction: SourceA → `ops/private/` only).
