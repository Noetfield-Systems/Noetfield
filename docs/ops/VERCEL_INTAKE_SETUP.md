<!-- ADVISOR_ARCHITECT_CHECKLIST_STUB (auto-inserted) -->
Advisor / Architect Minimal Checklist (AUTO-STUB)
-----------------------------------------------

- protects: Which founder goal does this protect? (pick one)
- sina_workload: reduces / increases + short rationale
- permission_loop: yes / no + explanation
- sandbox_autonomy: yes / no + where/how (sandbox lane path)
- target_to_blocker: yes / no + mitigation
- canon_version: (string)
- sandbox_evidence: link(s) to sandbox receipt(s)

# Vercel www — intake email go-live

**Status:** **SUPERSEDED 2026-07-09 — Vercel retired**

> This runbook described intake-email setup for the Vercel project (`the-777-foundation/noetfield`), which has been fully deleted. `scripts/auto-heal-www.sh` (referenced throughout the old version of this doc) is deleted in the same change. Nothing below is live — kept only as a pointer to the current setup.

## Current setup

Intake email config now lives as **Cloudflare Pages secrets** on the `noetfield-www` project (`RESEND_API_KEY`, `INTAKE_EMAIL_FROM`, `INTAKE_EMAIL_TO`, `INTAKE_AUTO_ACK_ENABLED`, etc.).

There is no separate manual setup step anymore. `scripts/deploy-www-cloudflare.sh` syncs these secrets automatically on every deploy via its `sync_pages_secrets()` function, which reads from `~/.sina/secrets.env` — the same founder vault used before. Before deploying, just confirm the vault has the right keys; the deploy script pushes them to Cloudflare Pages for you.

For the full current deploy path (build via `scripts/build-www-pages-dist.sh`, deploy via `npx wrangler pages deploy`), see [CF_WWW_PROXY_LOCKED_v1.md](CF_WWW_PROXY_LOCKED_v1.md) and [CLOUD_INVENTORY_LOCKED_v1.md](CLOUD_INVENTORY_LOCKED_v1.md).

See [INTAKE_OPS.md](../INTAKE_OPS.md) for the intake vectors routed to ops.
