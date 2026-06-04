# Noetfield agent context and read order (LOCKED v1)

| Field | Value |
|-------|--------|
| Agent id | `noetfield_cloud` |
| Lane | `noetfield_cloud` (semi-separate — see Desktop `SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md`) |
| Thread | `THREAD-PORTFOLIO` |
| Plane | `[DELIVERY]` |
| Repo | `kazemnezhadsina144-dot/Noetfield` |
| Authority | ASF — ship from this repo; ingest after; do not idle for next order |

**Index of all links (ecosystem + this repo):** [AGENT_READ_LINKS_INDEX.md](../../AGENT_READ_LINKS_INDEX.md)

---

## What this lane is

- **Ship** product, GTM, APIs, www, governance console, CI in **this** git remote.
- **Coordinate** with Sina Prompt OS via ingest (YAML + inbox) — **do not** modify Prompt OS code.
- **Respect** ecosystem SSOT on Mac for structure disputes; **public/product truth** in this repo wins for buyer-facing scope.

**ACE v3 (when mirror present):** `[DESIGN]` SSOT describes · `[EXECUTION]` Runtime proves · `[DELIVERY]` this repo ships. Delivery may ship without mono registry gate. Tag plane when stating “docs only” vs “executable.”

---

## Read order — every session

### A. Always (in git — cloud-safe)

1. [AGENT_READ_LINKS_INDEX.md](../../AGENT_READ_LINKS_INDEX.md) — Noetfield cloud section
2. [os/SHIP_NOW.md](../../os/SHIP_NOW.md) — ingest vs idle table
3. [os/plan.json](../../os/plan.json) — `next_tasks`, `ship_rule`
4. [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) · [POSITIONING.md](../../POSITIONING.md) · [OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md)
5. [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) — Copilot audit-trail positioning, TLE v1 mandate
6. [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md)
7. [.cursor/AGENT_TRACKING.md](../../.cursor/AGENT_TRACKING.md)
8. Active task: GitHub Issue / PR description / Prompt OS task string

### B. If `ops/private/` exists (founder bootstrap / sync)

9. [ops/private/sourceA/NOETFIELD_REPO_ALIGNMENT.md](../../ops/private/sourceA/NOETFIELD_REPO_ALIGNMENT.md)
10. [ops/private/sourceA/AUTO_CONFLICT_ENGINE_V3_LOCKED.md](../../ops/private/sourceA/AUTO_CONFLICT_ENGINE_V3_LOCKED.md)
11. [ops/private/sourceA/SINA_OS_SSOT_LOCKED.md](../../ops/private/sourceA/SINA_OS_SSOT_LOCKED.md) — ecosystem map only, not a build freeze on this repo
12. `ops/private/todolist/NEXT_MOVES.md` — P0/P1 when present

### C. Mac founder only (not in cloud VM)

- Hub: http://127.0.0.1:13020/ — `~/Desktop/SourceA/scripts/serve-sina-command.sh`
- `~/Desktop/SourceA/SEMI_NOTICE_noetfield_cloud_v1.md`
- Mandatory chain 1→14 — [AGENT_READ_LINKS_INDEX.md](../../AGENT_READ_LINKS_INDEX.md)

---

## Ship vs ingest (locked)

| Action | Blocks shipping? |
|--------|------------------|
| **Ingest** — send reply YAML (`reported_at` required) to Prompt OS / inbox | **No** — required **after** you ship |
| **Wait for next order** — stop until Prompt OS / M8 dispatch | **Yes** — do **not** |

Full footer: [docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md](../spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md)

---

## Verify commands (typical)

```bash
make ship-verify          # when stack relevant
make dev-local            # founder Mac or cloud with ports
make verify-local-dev     # unified proxy :13080
```

Production founder steps: [docs/WAVE0_SHIP_CHECKLIST.md](../WAVE0_SHIP_CHECKLIST.md)

---

## Paste pack

Chat bootstrap: [ready_to_paste_noetfield_cloud.txt](./ready_to_paste_noetfield_cloud.txt)

---

## Document control

| Version | Date | Note |
|---------|------|------|
| v1 | 2026-06-03 | Locked for `noetfield_cloud` lane; hub alias filenames preserved in index |

*Supersedes ad-hoc “read README first” for cloud agents. Desktop canonical copies may exist under `~/Desktop/SourceA/` with the same basename — if they diverge on product locks, **this repo’s** `PRODUCT_TRUTH` + blueprint win for `[DELIVERY]`.*
