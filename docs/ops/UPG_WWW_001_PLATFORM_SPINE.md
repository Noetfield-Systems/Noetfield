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

# UPG-WWW-001 — Platform spine go-live

**Goal:** `https://platform.noetfield.com/health` → 200 with governance FastAPI on Railway; www chat upgrades to LLM proxy automatically when platform is reachable.

## Prerequisites

- Railway CLI logged in (`railway whoami`)
- Cloudflare DNS token in `~/.sina/secrets.env` (`CF_NOETFIELD_API_TOKEN` or `CF_API_TOKEN`)
- Vault keys: `OPENROUTER_API_KEY`, `RESEND_API_KEY`, `EVENT_INTEGRITY_SECRET` (recommended)

## Blocker (2026-06-26)

Railway **trial resource limit** hit on workspace `Noetfield-Systems's Projects` — trial caps **1 GB RAM / 2 vCPU / 1 GB disk**; `mergepack-api` is **4/4 services** (~$1.97/mo usage); orphan `npx @railway/cli@latest up` has Postgres only; adding `platform-api` fails with *resource provision limit exceeded*.

**Separate Supabase project (email 2026-06-26):** **Noetfield Systems** Supabase ref `tkgpapowwplupyekpivy` under **`Noetfield-Systems's Org`** is flagged for auto-pause due to inactivity — platform currently uses **Railway Postgres**, not Supabase cloud. See **`docs/ops/UPG_SUPABASE_001_ACTIVATION.md`** to apply migrations + wire DATABASE_URL.

**Railway org note:** deploy platform API in the org where Hobby/trial quota allows (`noetfield-platform` project `94ade24c-…` on kazemnezhadsina144@gmail.com workspace after Hobby unlock).

**Unblock options (pick one):**

| Option | Action |
|--------|--------|
| **A — Noetfield Systems org (recommended)** | Dashboard → switch to **Org** (not Projects) → open **Noetfield Systems** → deploy platform API + link CLI with `railway link -w "<Org name>" -p tkgpapowwplupyekpivy` |
| **B — Trial → Hobby** | **Unlock Hobby Plan** (~$3.03 trial credit left) → add `platform-api` to renamed `noetfield-platform` project |
| **C — Render** | Connect repo → deploy `render.yaml` → DNS cutover script |
| **D — Free RAM** | Stop/delete unused mergepack service → re-run `./scripts/deploy-platform-railway.sh` |

## One-command bootstrap (Railway, after upgrade)

```bash
./scripts/deploy-platform-railway.sh
```

Creates (if missing):

| Resource | Name |
|----------|------|
| Railway project | `noetfield-platform` |
| Postgres | `postgres` |
| Redis | `redis` |
| API service | `platform-api` (Dockerfile.api, port `$PORT`) |

## DNS cutover (manual if bootstrap skips)

```bash
# After deploy — get Railway hostname
railway domain --service platform-api

# Point Cloudflare (does NOT touch www)
PLATFORM_API_CNAME=platform-api-production-xxxx.up.railway.app \
  ./scripts/setup-platform-api-dns.sh
```

## Verify

```bash
PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh
# or lighter:
PLATFORM_HEALTH_BASE=https://platform.noetfield.com python3 scripts/verify_platform_health.py
```

## www chat upgrade (no breaking change)

www `api/public/chat/index.js` already tries platform first, then falls back to www-local FAQ. When platform DNS is live + LLM keys set:

- `GET https://www.noetfield.com/api/public/chat/health` → `mode: platform-proxy`
- `POST /api/public/chat` → LLM replies from platform

## Rollback

Point `platform.noetfield.com` CNAME back to Vercel bridge only if emergency — www remains independent (L0-law §7).
