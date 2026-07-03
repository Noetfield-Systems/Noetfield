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

## Current architecture (2026-06-26)

| Path | Handler |
|------|---------|
| **www.noetfield.com** (live today) | **Direct Vercel DNS** → `the-777-foundation/noetfield` |
| **CF worker route** `www.noetfield.com/*` | Deployed + updated; **dormant** while DNS CNAME points to Vercel |

Do **not** point www CNAME to CF and Vercel at the same time. Pick one spine.

---

## Worker ORIGIN law

| Value | Use |
|-------|-----|
| `https://noetfield-the-777-foundation.vercel.app` | **Correct** — direct Vercel backend |
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

**Live www (direct Vercel):** response has `server: Vercel`, no `X-Noetfield-Proxy` header.

**If CF route ever enabled:** responses would include `X-Noetfield-Proxy: cf-www-proxy`.

---

**Locked by:** noetfeld-os-cursor-chat
