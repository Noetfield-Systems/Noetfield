# Noetfield future plans library (NO ASF)

**Count:** 1000 plan stubs (`nf-future-*`)  
**Namespace:** `nf-future-0001` … `nf-future-1000` — see [DOCS_UNIFIED_MAP_LOCKED_v1.md](../../docs/ops/DOCS_UNIFIED_MAP_LOCKED_v1.md) for ID rules  
**Active ship:** [GTM_NEXT.md](../../docs/ops/plans/no-asf/GTM_NEXT.md) (`ship-*`) — **not** this library

## When you say “plan with no ASF”

1. Pick from **[GTM_NEXT.md](../../docs/ops/plans/no-asf/GTM_NEXT.md)** first (`ship-*` IDs).
2. If GTM_NEXT empty → wisdom backlog in [QUICK_PICK.md](../../docs/ops/plans/no-asf/QUICK_PICK.md) (`ship-fwd-*`).
3. Long-term stubs here (`nf-future-*`) via [REGISTRY.json](./REGISTRY.json) — bridge: [BRIDGE_NF_PLAN_TO_NF_FUTURE.json](../../docs/ops/plans/BRIDGE_NF_PLAN_TO_NF_FUTURE.json).

Agents must **not** wait for ASF commit, push, ingest, or SourceA edits.

## Organization

| Axis | Values |
|------|--------|
| **Phase** | `phase-0-ship-ops` … `phase-9-ecosystem-bridge` (10 phases × 100 plans) |
| **Tier** | `T0` Critical → `T3` Low (25 plans per phase×tier cell) |
| **ID** | `nf-future-0001` … `nf-future-1000` |

## Files

| File | Purpose |
|------|---------|
| `REGISTRY.json` | Machine index (all 1000 IDs, paths, phase, tier, domain) |
| `REGISTRY.md` | Human index |
| `phase-*/T*/nf-future-*.md` | Individual plan stubs |

## Active ship queue

**Authoritative:** [GTM_NEXT.md](../../docs/ops/plans/no-asf/GTM_NEXT.md) · [os/plan.json](../plan.json) · [os/SHIP_NOW.md](../SHIP_NOW.md).  
This library is **long-term backlog** (`nf-future-*`); move items into GTM_NEXT when ready.

## Maintenance

```bash
cd ~/Desktop/Noetfield
python3 scripts/generate-future-plans.py   # refresh all stubs + registry
```

After shipping a plan, set `status: done` in the plan markdown front matter and optionally add evidence paths. Do not delete plan files — history matters for ingest and audits.
