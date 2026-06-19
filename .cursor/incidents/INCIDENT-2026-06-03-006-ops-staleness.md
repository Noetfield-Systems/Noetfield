# INCIDENT-2026-06-03-006 — Ops staleness: agents built before witness

| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| Severity | **P1** |
| Status | **closed** (controls shipped: OPS_LIVE + R-013 + verify-ops-live) |
| Closed | 2026-06-03 |
| Reporter | founder |

---

## Summary

Founder stated **operations@noetfield.com is live in Google Workspace**, **Stripe is live**, and **email form sending is deferred after factory build**.

Noetfield cloud agent and prior sessions still:
- Treated inbox as pending go-live
- Built sandbox/factory before auditing ops
- Left `/gate/sales/` redirecting while Stripe Payment Links were live

TrustField agents did not see updates — **by architecture**, not accident alone.

---

## Root cause (honest)

| # | Cause | Type |
|---|-------|------|
| 1 | Founder ops updates in **chat only** — not in git SSOT | Process gap |
| 2 | No `OPS_LIVE_STATUS` file — agents had no machine-readable witness | System design gap |
| 3 | `ops/private/sourceA/` **missing on cloud VM** — SEMI_NOTICE never synced | Infra gap (INCIDENT-003) |
| 4 | Stale `/status/` + `/next/` copy conflated inbox vs Resend | Repo drift |
| 5 | Work split across branches without merge to deploy | Git workflow gap |
| 6 | **R-001** isolates TrustField — Noetfield MEMORY_LOCKED does not propagate | Intentional boundary |

**Not a Cursor hallucination bug.** Agents read what was on disk; disk was wrong or incomplete.

---

## Corrective actions

| # | Action | Status |
|---|--------|--------|
| 1 | `governance/OPS_LIVE_STATUS_LOCKED.json` | Done |
| 2 | R-013 + SKILL-010 witness before build | Done |
| 3 | `make verify-ops-live` in verify-www | Done |
| 4 | `OPS_WITNESS_AUDIT_LOCKED_v1.md` + TrustField bridge notes | Done |
| 5 | Founder: sync SourceA + bump OPS_LIVE on every ops change | **Ongoing** |
| 6 | Merge PR #76 (ops + stripe + witness) to main | **Pending founder** |

---

## Prevention

```
IF founder says ops layer is live:
  UPDATE governance/OPS_LIVE_STATUS_LOCKED.json SAME SESSION
  RUN make verify-ops-live
  THEN build
```

**END**
