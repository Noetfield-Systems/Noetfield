# Partner onboarding e2e cockpit (v1)

**Added:** 2026-07-09 · **Owner:** operations@noetfield.com · **Boundary:** repo-local
automation only, per `governance/AUTOMATION_SURFACES_LOCKED.json`'s `adopt_only_repo_safe_patterns`
rule — this is one more scheduled GitHub Actions workflow writing into the existing
Supabase sink, not a new always-on runtime. `24_7_loop_fleet` / `cloud_cron_dispatcher`
are explicitly `not_adopted` in this repo; nothing here changes that.

## What this is

A live, browser-driven regression check for the two partner tracks the site actually
sells: commission/referral (Connector lane) and strategic/tiered (Co-partner, Partner/MSP,
Investor). It runs every 6 hours on GitHub Actions — no Mac, no always-on server, nothing
that needs to be "kept on" for this to keep running.

It found and now watches for the three critical bugs from the original manual audit:

1. The Quick Apply form on `/work-with-us/` throwing a JS `ReferenceError` on submit.
2. `/trust-brief/intake/?vector=work-with-us` leaking four required Trust-Brief pricing
   fields into the partner application (a `querySelector` vs `querySelectorAll` bug).
3. `/msp/` and `/next/` pointing their partner CTA at `/gate/partners/intake/`, which
   redirects to the unrelated `/enterprise/` page.

Plus lighter, advisory checks: whether a commission/referral figure is actually stated,
whether Partners/Work-with-us/Investors are reachable from primary nav, and whether the
two orphaned partner PDFs are linked from anywhere live.

## How it fits together

```
GitHub Actions cron (every 6h, *.yml)
  -> scripts/report_slo_health_v1.py (budget wrapper, matches every other nf-*.yml)
    -> scripts/nf_partner_onboarding_e2e_audit_v1.py
         - HTTP checks (stdlib urllib, always run)
         - Playwright/Chromium checks (real click, real console/network capture)
         -> reports/agent-auto/partner-onboarding-audit/latest.json  (committed to main)
         -> public.improvement_queue        (Kaizen-consumable findings)
         -> public.partner_onboarding_audit_runs  (score history)
         -> Telegram @noetfield_ops_bot     (critical findings only)

nf-kaizen-nightly (existing, unchanged cron)
  -> picks the single highest-ROI machine_safe row
  -> if recipe_key is "partner_apply_reference_error" or
     "ecosystem_estimator_fields_leak" -> runs the matching fix script, verifies,
     rolls back on failure (existing mechanism, two new recipes registered)

admin/partner-onboarding/  (X-Admin-Secret gated, read-only)
  -> api/admin/partner-onboarding-audit.js reads the committed latest.json
  -> no live backend call, no platform.noetfield.com dependency
```

Nothing here is a new reconciler or a new execution substrate. It's one more producer
into the `improvement_queue` table that `repo-health-daily`/`security-sweep-weekly`
already write to, one more scheduled workflow next to `nf-daily-heartbeat`/`nf-kaizen-nightly`,
and one more admin page next to `/admin/traction/`.

## Reading a result

- **Score** (0–100, in the receipt and the cockpit): 100 minus 25 per critical finding,
  10 per high, 5 per medium. A score below 75 means at least one critical finding.
- **Telegram alert** ("Noetfield partner funnel regression FAIL"): only fires on critical
  findings — the same `@noetfield_ops_bot` channel as deploy-check failures. Treat it the
  same way: something on the revenue path is broken right now.
- **`public.improvement_queue` rows** with `source` starting `github:partner-onboarding-e2e-audit:`:
  `machine_safe: true` rows will be picked up by the next `nf-kaizen-nightly` run
  automatically if a matching recipe exists (currently 2 of the ~8 possible findings do —
  see below). Everything else needs a human to read the finding and act.
- **Cockpit** (`/admin/partner-onboarding/`, needs the shared `X-Admin-Secret`): per-check
  pass/fail at a glance plus the full findings table. Read-only — it cannot trigger a run.

## What auto-fixes itself tonight vs. what needs a human

| Finding | `machine_safe` | Recipe |
|---|---|---|
| Quick Apply `ReferenceError` | yes | `partner_apply_reference_error` — patches the two broken `fields.role` references in `noetfield-partner-apply.js`, leaves `buildMessage(fields)`'s own use of `fields` untouched |
| Ecosystem estimator field leak | yes | `ecosystem_estimator_fields_leak` — switches `querySelector` to `querySelectorAll` in `noetfield-intake-ecosystem-mode.js` |
| Dead `/gate/partners/intake/` CTA on `/msp/`/`/next/` | no | Needs a human decision on the actual destination URL |
| Missing commission figure | no | Business decision, not a code bug |
| Nav discoverability | no | IA/design decision |
| Orphaned partner PDFs | no | Needs a human to confirm the PDFs are still accurate before re-linking |

Both recipes have their own verify script (`scripts/verify_partner_apply_reference_error_v1.py`,
`scripts/verify_ecosystem_estimator_leak_v1.py`) and roll back via `git checkout -- .` on
failure, matching the existing `greeting_coupling`/`drift_alignment` recipes exactly.

## Escalation

1. Telegram fires -> check the cockpit for the specific `check_id`.
2. If `machine_safe: true` (the two bugs above) -> next `nf-kaizen-nightly` run
   (daily, 02:00 PT) will attempt the fix automatically; no action needed unless it's
   urgent, in which case run the recipe manually:
   ```bash
   python3 scripts/nf_kaizen_fix_partner_apply_reference_error_v1.py
   python3 scripts/verify_partner_apply_reference_error_v1.py
   # or
   python3 scripts/nf_kaizen_fix_ecosystem_estimator_leak_v1.py
   python3 scripts/verify_ecosystem_estimator_leak_v1.py
   ```
3. If `machine_safe: false` -> read the finding, decide, fix by hand, ship. The next
   scheduled audit run confirms it.

## Required secrets

All four already exist as GitHub repo secrets — this workflow adds no new provisioning:
`NOETFIELD_SUPABASE_URL`, `NOETFIELD_SUPABASE_SERVICE_ROLE_KEY` (used by
`repo-health-daily`/`security-sweep-weekly`/`nf-kaizen-nightly` today),
`TELEGRAM_NOETFIELD_OPS_BOT_TOKEN`, `TELEGRAM_OPS_CHAT_ID` (used by deploy-check alerts
today). Nothing needs to be created or rotated to turn this on.

## Test-intake hygiene

Browser checks submit real forms against production using `e2e@noetfield.com` — the exact
email `api/_lib/intake-test.js` already recognizes as a test intake (`intake_kind: "test"`),
so these runs never appear as real leads, never page the founder through the normal
intake-Telegram path, and never pollute `lead_profiles`. This is the same mechanism
`nf_intake_e2e.py`/`nf-probe-cron` already rely on — nothing new was added to the intake
backend for this.

## What still needs founder sign-off

- **§8 of `L0-law/PUBLIC_WWW_BRAND_E2E_LAW_LOCKED_v1.md`** — added additively, flagged
  `pending founder sign-off` in the doc itself. Per that law's own §6, amendments need
  founder approval; this session could not grant that to itself.
- **`ROI_RANK` ordering** in `scripts/nf_improvement_queue_client.py` — `partner_conversion_integrity`
  was inserted second (right after `policy_compliance`), ahead of `repo_stability` and the
  rest. That's a judgment call (a broken revenue funnel outranks routine repo hygiene) —
  worth a second look, not a load-bearing decision that was hidden.
- **The two new Kaizen recipes** — `nf_kaizen_nightly_tick_v1.py` will now write to
  `assets/noetfield-partner-apply.js` and `assets/noetfield-intake-ecosystem-mode.js`
  autonomously the first time a matching row is queued and machine_safe. Both fixes were
  verified in this session (dry-run + a real local apply/rollback cycle — see the
  session's own verification output), but granting the nightly loop write access to
  customer-facing JS is worth a conscious "yes" rather than inheriting it silently.

## Known trade-off

The receipt commit-back step triggers a full site redeploy every time findings change
(same trade-off `nf-kaizen-nightly`'s existing commit-back step already accepts) — every
6 hours in the worst case, less often once the funnel is stable and receipts stop
changing. If that redeploy cadence becomes a problem, switch the cockpit from reading a
committed file to reading `public.partner_onboarding_audit_runs` directly (the table
already has every run) instead of removing the schedule.
