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

# CF WWW PROXY — LOCKED v1

**Status:** LOCKED  
**Date:** 2026-06-26  
**Worker:** `noetfield-www-proxy`  
**Path:** `infra/cf-www-proxy/`

---

## Current architecture (2026-06-26; corrected 2026-07-09)

| Path | Handler |
|------|---------|
| **www.noetfield.com** (live) | **Cloudflare Pages** → project `noetfield-www` (deployed via `scripts/deploy-www-cloudflare.sh`, which builds `www-pages-dist/` via `scripts/build-www-pages-dist.sh` and runs `npx wrangler pages deploy`) |
| **CF worker route** `www.noetfield.com/*` | Routing status vs. Pages needs confirmation post-Vercel-retirement — see follow-up below |

Vercel was retired 2026-07-09 (project `the-777-foundation/noetfield` fully deleted). Cloudflare Pages is now the canonical spine for `www.noetfield.com` / `noetfield.com`; Railway is canonical for backend/platform services (`platform.noetfield.com`, `api.noetfield.com`).

**Follow-up needed:** if this proxy worker is still in the routing path in front of Cloudflare Pages, its ORIGIN can no longer point at Vercel (that deployment no longer exists). It should be re-pointed at the Cloudflare Pages project (`noetfield-www`) directly, or the worker should be removed from the route entirely if Pages is serving `www.noetfield.com` without it. This doc does not confirm which of those is currently true — verify before relying on it.

---

## Worker ORIGIN law

| Value | Use |
|-------|-----|
| `https://noetfield-the-777-foundation.vercel.app` | **Retired 2026-07-09** — Vercel project deleted; this origin no longer resolves. Do not use. Follow-up: re-point to the Cloudflare Pages project (`noetfield-www`) directly, or remove this worker from the route. |
| `https://www.noetfield.com` | **Wrong** — infinite proxy loop if CF route active |
| `project-gc7lm.vercel.app` | **Dead** — retired |

---

## Deploy

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield
bash scripts/deploy-cf-www-proxy.sh
```

Requires `CF_NOETFIELD_API_TOKEN` in `~/.sina/secrets.env`.

---

## Verify

**Worker deployed:** `wrangler deployments list` in `infra/cf-www-proxy/`

**Live www (Cloudflare Pages):** response has `server: cloudflare` (confirmed via curl 2026-07-09). If this proxy worker is active in the routing path, responses also include `X-Noetfield-Proxy: cf-www-proxy` — check current curl output to determine whether the worker is actually in front of Pages before assuming either way.

**If CF route enabled and worker in path:** responses include `X-Noetfield-Proxy: cf-www-proxy`. If the worker's ORIGIN still points at the deleted Vercel deployment, treat this as broken/moot until re-pointed at the Cloudflare Pages project directly (see follow-up above).

---

**Locked by:** noetfeld-os-cursor-chat

**Corrected 2026-07-09 — Vercel retired.**
