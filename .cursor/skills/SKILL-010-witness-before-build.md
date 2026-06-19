# SKILL-010 — Witness before build (R-013)

**When:** Every session start, **before** planning or implementing any feature.

## Steps

1. Run `./scripts/witness-session-start.sh` (or read outputs if already run).
2. Read [governance/OPS_LIVE_STATUS_LOCKED.json](../../governance/OPS_LIVE_STATUS_LOCKED.json) — **founder ops truth on disk**.
3. Read [docs/ops/OPS_WITNESS_AUDIT_LOCKED_v1.md](../../docs/ops/OPS_WITNESS_AUDIT_LOCKED_v1.md) if first time this week.
4. Check open work: `os/plan.json` `next_tasks` where `status` ≠ `done`; open PRs on current branch family.
5. **Do not conflate:**
   - Google Workspace inbox **live** ≠ form Resend **deferred**
   - Stripe Payment Links **live** ≠ webhook fulfillment optional
6. If founder said something in chat that contradicts OPS_LIVE → **update OPS_LIVE first**, then build.

## Fail (to user)

```
BLOCKED — witness incomplete.
I need to read governance/OPS_LIVE_STATUS_LOCKED.json and confirm ops layers before building.
```

## Pass (internal)

```
witness: PASS
ops_live_version: <status_version>
```
