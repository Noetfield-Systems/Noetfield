## Tier-1 Workflow Health Receipt (Hardened)

Schema: noetfield-workflow-health-v1

**Authority:** `.github/workflows/noetfield-www-ci.yml`, `.github/workflows/platform-deploy.yml`, `.github/workflows/supabase-heartbeat.yml`

**Workflows in this receipt:**

| Workflow | SLO Target | Owner | Check Interval |
|----------|-----------|-------|-----------------|
| noetfield-www-ci | pass_rate>99%, latency<60s, zero_critical_issues | site-health | push to main, PR |
| platform-deploy | pass_rate>95%, compile_ok, zero_breaking_changes, startup<10s | ecosystem-health + deploy-smoke | push to main, PR, manual |
| supabase-heartbeat | rest_200_or_401, sql_response<5s, weekly_pass_rate>95% | REST + SQL pings | weekly Mon 14:00 UTC, manual |

**Kaizen escalation:** 
- SLO miss (drift from target): auto-file low-priority proof receipt with workflow name, target, actual value, timestamp
- Consecutive failures (2+ runs): escalate to medium priority
- Pattern (weekly failures on specific day/time): escalate to high priority with remediation lane

**Receipt location:** `governance/WORKFLOW_HEALTH_RECEIPTS_LOCKED.json` (append-only, weekly rotation)

**No auto-filing implementation yet:** This schema defines the structure. Auto-file capability (filing proofs on SLO miss) requires secrets/permissions and is deferred to Phase 2 workflow hardening.
