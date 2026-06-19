# Ops witness audit — audit before build (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | LOCKED |
| **Updated** | 2026-06-03 |
| **Rule** | R-013 in `MEMORY_LOCKED.yaml` |
| **SSOT** | [governance/OPS_LIVE_STATUS_LOCKED.json](../../governance/OPS_LIVE_STATUS_LOCKED.json) |

---

## Why this exists

Founder told agents: **Google Workspace inbox is live**, **Stripe is live**, **email form sending is deferred after factory build**.

Agents still built sandbox/factory work and treated inbox as "pending go-live" because:

1. Updates lived in **chat**, not on disk.
2. **SourceA mirror** (`ops/private/sourceA/`) is missing on cloud VM — SEMI_NOTICE never reached agents.
3. **Stale www copy** (`/status/`, `/next/`) said "enable Resend" without distinguishing inbox vs form delivery.
4. **Split branches** — Stripe on `cursor/stripe-gtm-setup-37f0`, sandbox on `cursor/sandbox-v2-37f0`, deploy lagging.
5. **TrustField is isolated** (R-001) — Noetfield rules do not propagate to TrustField agents unless founder syncs separately.

This is **not** a Cursor bug. It is an **ecosystem wiring gap**: no machine-readable ops truth that agents must read first.

---

## Witness protocol (every session, before edits)

```bash
./scripts/witness-session-start.sh
```

Or manually:

1. Read `governance/OPS_LIVE_STATUS_LOCKED.json`
2. Read `MEMORY_LOCKED.yaml` + open PRs / `os/plan.json` `next_tasks` (status ≠ done)
3. If production reachable: `curl https://www.noetfield.com/api/intake/health`
4. **Then** plan or build — never reverse this order

---

## Email layers (do not conflate)

| Layer | Status (2026-06-03) | Agent action |
|-------|----------------------|--------------|
| **Google Workspace inbox** | **Live** | Do not say "inbox pending" |
| **Form auto-notify (Resend)** | **Deferred post-factory** | Do not block factory work; document fallback (mailto + direct email) |
| **Agentic outbound email** | Hub only (R-011) | NF-CLOUD never sends as founder |

---

## TrustField did not see this rule — honest answer

| Factor | Explanation |
|--------|-------------|
| **R-001** | Noetfield cloud agent is forbidden from TrustField scope |
| **No shared ops file** | `OPS_LIVE_STATUS_LOCKED.json` is Noetfield-repo only until founder mirrors |
| **SourceA not synced** | `SEMI_NOTICE_noetfield_cloud_v1.md` is gitignored; cloud VM has no mirror |
| **Separate repos** | TrustField agent reads TrustField repo + SourceA index — not Noetfield MEMORY_LOCKED |

**Fix for dual-brand:** Founder runs `sync-sourceA-desktop.sh` and adds ops deltas to **both** `SEMI_NOTICE_noetfield_cloud_v1.md` and TrustField's notice file — or maintain `OPS_LIVE_STATUS` in SourceA and sync to both repos.

---

## Anti-staleness forever (founder + agent checklist)

| # | Fix | Owner |
|---|-----|-------|
| 1 | **Ops truth on disk** — bump `governance/OPS_LIVE_STATUS_LOCKED.json` when anything goes live | Founder + agent after each ops change |
| 2 | **Witness before build** — R-013 + `make verify-ops-live` in pre-commit | Agent |
| 3 | **Sync SourceA** — `./scripts/sync-sourceA-desktop.sh` after founder Mac decisions | Founder |
| 4 | **One deploy branch** — merge stripe/sandbox/ops PRs; don't let `gate/sales` redirect while Stripe is live | Founder |
| 5 | **Health API as truth** — `www_email_configured` for form delivery; don't infer from copy | Agent |
| 6 | **Cross-repo bridge** — duplicate ops deltas to TrustField notice or shared SourceA ops file | Founder |
| 7 | **Incident on repeat** — M-005 in MEMORY_LOCKED if agent builds before witness | Agent |

---

## Verify

```bash
make verify-ops-live
./scripts/verify-agent-scope.sh
```
