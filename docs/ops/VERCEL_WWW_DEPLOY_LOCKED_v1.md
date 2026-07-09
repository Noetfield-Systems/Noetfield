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

# VERCEL WWW DEPLOY — LOCKED v1

> **SUPERSEDED 2026-07-09 — Vercel retired, see [`docs/ops/CF_WWW_PROXY_LOCKED_v1.md`](./CF_WWW_PROXY_LOCKED_v1.md) for the current Cloudflare Pages deploy path.**
>
> This runbook described the Vercel project (`the-777-foundation` / `noetfield`) that served www.noetfield.com through 2026-07-09. On that date the founder retired Vercel from the Noetfield stack entirely: the Vercel project was deleted (team, dashboard, and all deployments below no longer exist), and `scripts/deploy-www-vercel.sh` plus related Vercel-provisioning scripts were removed from the repo.
>
> The current, canonical deploy path is:
> - **www.noetfield.com / noetfield.com (apex):** Cloudflare Pages, project `noetfield-www`, deployed via `scripts/deploy-www-cloudflare.sh` (builds `www-pages-dist/` via `scripts/build-www-pages-dist.sh`, then `npx wrangler pages deploy`). See `docs/ops/CF_WWW_PROXY_LOCKED_v1.md`.
> - **platform.noetfield.com / api.noetfield.com (backend):** Railway — already live there. See `docs/ops/CLOUD_INVENTORY_LOCKED_v1.md`.
>
> Everything below this notice is historical record only. Do not run these commands, do not use these links (the Vercel dashboard/project no longer exists), and do not treat this as a live fallback or rollback target.

**Status:** LOCKED (historical — superseded 2026-07-09)
**Date:** 2026-06-26  
**Audience:** Founder + agents — where www lived on Vercel (no longer current)

---

## Where to find it in Vercel *(historical — project deleted 2026-07-09)*

| Field | Value |
|-------|--------|
| **Team / scope** | `the-777-foundation` (The 777 Foundation) |
| **Project name** | `noetfield` ← **not** `www`, **not** `project-gc7lm` |
| **Production URL** | https://www.noetfield.com |
| **Dashboard** | https://vercel.com/the-777-foundation/noetfield |
| **GitHub repo** | https://github.com/Noetfield-Systems/Noetfield (connected) |
| **Production branch** | `main` |

---

## Deploy from Mac (CLI) *(historical — script deleted 2026-07-09, do not run)*

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield
bash scripts/deploy-www-vercel.sh
```

Or manually:

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield
npx vercel link --project noetfield --scope the-777-foundation --yes
npx vercel deploy --prod --scope the-777-foundation --yes
```

---

## Verify *(historical)*

```bash
curl -sS https://www.noetfield.com/health
curl -sS https://www.noetfield.com/api/intake/health | python3 -m json.tool
python3 ~/Projects/noetfeld-os/scripts/check_noetfield_com_e2e.py
```

Pass: `www_email_configured: true`, `delivery_mode: resend`.

---

## Common confusion *(historical)*

| Wrong | Right |
|-------|-------|
| Scope `noetfield-systems` | Scope **`the-777-foundation`** |
| Project `www` | Project **`noetfield`** |
| `project-gc7lm.vercel.app` | **Dead** — use `www.noetfield.com` |

---

## Latest production deploy (2026-06-26) *(historical — last known deploy before Vercel retirement)*

| Field | Value |
|-------|--------|
| Deployment ID | `dpl_4mWNMRWceW9ag4co5S6fsAPqJjj7` |
| Inspector | https://vercel.com/the-777-foundation/noetfield/4mWNMRWceW9ag4co5S6fsAPqJjj7 |
| Aliases | www.noetfield.com, noetfield.com, noetfield.vercel.app |

**Locked by:** noetfeld-os-cursor-chat

**Superseded by:** docs/ops/CF_WWW_PROXY_LOCKED_v1.md (2026-07-09)
