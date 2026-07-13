# CF WWW PROXY — LOCKED v1

**Status:** LOCKED  
**Date:** 2026-06-26 (updated 2026-07-13)  
**Worker:** `noetfield-www-proxy`  
**Path:** `infra/cf-www-proxy/`

---

## Current architecture

| Path | Handler |
|------|---------|
| **www.noetfield.com** (live) | **Cloudflare Pages** → project `noetfield-www` (deployed via `scripts/deploy-www-cloudflare.sh`) |
| **CF worker route** `www.noetfield.com/*` | Optional edge proxy in front of Pages — see ORIGIN law below |

Cloudflare Pages is the canonical spine for `www.noetfield.com` / `noetfield.com`. Railway is canonical for backend/platform services (`platform.noetfield.com`, `api.noetfield.com`).

---

## Worker ORIGIN law

| Value | Use |
|-------|-----|
| `https://noetfield-www.pages.dev` | **Correct** — Cloudflare Pages production alias |
| `https://www.noetfield.com` | **Wrong** — infinite proxy loop if CF route active |

Configured in `infra/cf-www-proxy/wrangler.toml` and `src/worker.js`.

---

## Deploy

```bash
bash scripts/deploy-cf-www-proxy.sh
```

Requires `CF_NOETFIELD_API_TOKEN` in `~/.sina/secrets.env`.

---

## Verify

**Worker deployed:** `wrangler deployments list` in `infra/cf-www-proxy/`

**Live www:** response has `server: cloudflare`. If this proxy worker is active, responses also include `X-Noetfield-Proxy: cf-www-proxy`.

---

**Locked by:** noetfeld-os-cursor-chat
