# Noetfield agent context and read order (LOCKED v1)

| Field | Value |
|-------|--------|
| Workspace | `~/Desktop/Noetfield` — **Noetfield cloud / GitHub ship** |
| Agent id | `noetfield_cloud` |
| **Not** | `noetfield_local` (All-Documents), SourceA, wire, MergePack, Cursor OS Pro |
| Lane | `noetfield_cloud` — semi-separate |
| Thread | `THREAD-PORTFOLIO` |
| Plane | `[DELIVERY]` |
| Authority | ASF — bounded ship from [GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md) + `os/plan.json`; registry synced (not engineering done); ingest after; no self-start (R-007/R-011) |

**Link index (in-repo):** [AGENT_READ_LINKS_LOCKED_v1.md](./AGENT_READ_LINKS_LOCKED_v1.md) → § Cloud ship  
**Canonical index (Mac):** `~/Desktop/SourceA/founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md`

---

## Read order — every session

### A. Git (cloud-safe)

1. [AGENT_READ_LINKS_LOCKED_v1.md](./AGENT_READ_LINKS_LOCKED_v1.md) — § Cloud ship
2. [DOCS_UNIFIED_MAP_LOCKED_v1.md](./DOCS_UNIFIED_MAP_LOCKED_v1.md) — if fragmented (SKILL-009)
3. [NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md](./NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md) — local↔cloud bridge (committed)
4. This file
5. [os/SHIP_NOW.md](../../os/SHIP_NOW.md) → [os/plan.json](../../os/plan.json) → [GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md)
6. [plans/no-asf/QUICK_PICK.md](./plans/no-asf/QUICK_PICK.md) when user says **PLAN WITH NO ASF** (wisdom backlog only if GTM_NEXT empty)
7. [os/sprint-trust-ledger-v1.2.md](../../os/sprint-trust-ledger-v1.2.md) or [lane_a_sprint_map.md](./lane_a_sprint_map.md)
8. [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) · [POSITIONING.md](../../POSITIONING.md) · [OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md)
9. [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md)
10. **Diligence / frameworks (LOCKED):** [docs/references/README.md](../references/README.md)
11. **Drift blueprints:** [NOETFIELD_DRIFT_BLUEPRINTS_CLOUD_READ_ORDER_LOCKED_v1.md](./NOETFIELD_DRIFT_BLUEPRINTS_CLOUD_READ_ORDER_LOCKED_v1.md)
12. [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md)
13. [.cursor/AGENT_TRACKING.md](../../.cursor/AGENT_TRACKING.md)
14. Active task (Issue / PR / Prompt OS task string)

---

## § Post-audit addendum (2026-06-10 — agent-maintained)

Does **not** replace locked authority line above without founder unlock. Cloud agents also read:

- [FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md](./FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md) — R-011
- [GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md) — active ship queue (registry synced ≠ done)
- [AGENTIC_COMMERCIAL_HANDOFF_v1.md](./AGENTIC_COMMERCIAL_HANDOFF_v1.md) — outreach = agentic layer

**Ship rule (bounded):** Founder explicit `implement` + ≤3 tasks from GTM_NEXT — not self-start from `plan.json` or GTM_PRIORITY outreach rows alone.

**Locked header note:** The Authority line above ("ship from plan.json; do not idle") is **superseded for cloud agents** by bounded ship per post-audit addendum — founder unlock required to edit the locked header row.

### B. After founder sync (`ops/private/`)

12. `ops/private/agent-reference/IN_CHARGE_NOW.md` → `AGENT_TEAM_STATE.yaml` → `plans/LOCKED_PLANS_INTERNAL.yaml`
13. `ops/private/sourceA/founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md`
14. `ops/private/sourceA/NOETFIELD_REPO_ALIGNMENT.md`
15. `ops/private/sourceA/AUTO_CONFLICT_ENGINE_V3_LOCKED.md` (optional)
16. `docs/internal/AUTO_CONFIDENTIAL_PORTFOLIO_POSITIONING.md` — **[AUTO] confidential** (optional, gitignored) — **never quote publicly**; index `ops/private/agent-reference/AUTO_INDEX_LOCKED.md`
17. `ops/private/todolist/NEXT_MOVES.md` (optional)

### C. Mac founder session only

- Hub http://127.0.0.1:13020/ — only when founder says Mac session is active
- SourceA mandatory chain 1→14 — Desktop canonical

---

## Ship vs ingest

| Action | Blocks shipping? |
|--------|------------------|
| Ingest (YAML + `reported_at`) | **No** — after ship |
| Wait for next Prompt OS order | **Yes** — forbidden |

[docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md](../spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md)

---

## Paste / semi notice

| Artifact | Path |
|----------|------|
| Paste | [ready_to_paste_noetfield_cloud.txt](./ready_to_paste_noetfield_cloud.txt) |
| Semi notice | `ops/private/sourceA/founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md` (synced) |

**Not** `REPO_NOTICE_noetfield_v1.md` — that is **noetfield_local** only.

---

## Verify

```bash
./scripts/verify-local-dev.sh
./scripts/tle-smoke.sh
make ship-verify
```

---

| v1 | 2026-06-03 | `docs/ops/` only — founder correction |
