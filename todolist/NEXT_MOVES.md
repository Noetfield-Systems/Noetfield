# Next moves — master action list

**Last reviewed:** 2026-05-29 · **Repo state:** `main` has platform upgrades (chat, Telegram, intake, Redis, Docker). **Prod:** not verified from CI (DNS/deploy founder-owned).

Use this file as the **single checklist** for what to do next. Detail lives in sibling trackers.

---

## Roadmap (three horizons)

| Horizon | Goal | Outcome |
|---------|------|---------|
| **Now (0–2 weeks)** | Go live safely | www + platform reachable; assistant + intake work; Telegram optional; no false regulatory claims |
| **Next (1–2 months)** | Operate like a product | Postgres backups, ops alerts, legal clean, staging, CRM optional |
| **Later** | Scale governance OS | RAG/pgvector, pilot auth, Bank Pilot console hardening, deprecate duplicate frontends |

---

## Analysis summary

### What is already strong (code on `main`)

- Institutional www simplified (5 surfaces, 3 SKUs, `operations@noetfield.com`).
- Platform API: public chat (OpenRouter + Gemini fallback), Telegram webhook, `POST /api/intake`, ecosystem health.
- Postgres migration for intakes + knowledge chunk table; Redis for sessions/rate limits.
- Docs: `RUNBOOK.md`, `PRACTICAL_PLAYBOOK.md`, `todolist/` trackers.
- CI: unit tests + ecosystem smoke + ephemeral health check.

### What is still weak (gaps)

| Gap | Why it matters |
|-----|----------------|
| **Production not wired** | Code ≠ live; DNS/platform host may not resolve |
| **Secrets in chat history** | Must rotate OpenRouter / Telegram / Gemini on server |
| **Telegram not end-to-end verified** | Token + webhook + `@username` on www |
| **www deploy automation** | No Cloudflare/Pages workflow in repo |
| **Legal pages stale** | Gate/Partners language; MSB only if registered |
| **Formspree hardcoded** | Intake depends on third-party ID in HTML |
| **Two “products” in one founder head** | Noetfield (governance GTM) vs VIRLUX (payments) — separate repos, same todolist |

### VIRLUX (separate repo — do not mix with Noetfield deploy)

Real-money blockers are **founder/compliance**, not Noetfield HTML: Interac webhook, KYC admin UI, httpOnly cookies, Circle prod, legal/MSB.

---

## P0 — Do first (launch blockers)

### Noetfield — founder / ops

- [ ] **NF-SECRET-01** — Rotate API keys that were ever pasted in chat; set only on platform host env.
- [ ] **NF-DEPLOY-02** — Confirm DNS: `platform.noetfield.com` and `www.noetfield.com` resolve with TLS.
- [ ] **NF-DEPLOY-01** — Deploy API: `make platform-migrate` → `make platform-up` (or your host’s equivalent).
- [ ] **NF-LLM-01** — Set `OPENROUTER_API_KEY` + optional `GEMINI_API_KEY`; run `./scripts/deploy_platform_smoke.sh` against prod URL.
- [ ] **NF-WWW-01** — Deploy static www from `main` (CDN); include `assets/noetfield-ecosystem.json`.

### Noetfield — Telegram (if you want the bot live)

- [ ] **NF-TG-01** — `TELEGRAM_BOT_TOKEN` + `POST /api/telegram/register-webhook` → `/api/telegram/health` shows `ready: true`.
- [ ] **NF-TG-02** — `TELEGRAM_BOT_USERNAME=... python3 scripts/publish_ecosystem_config.py` → redeploy www.

### Noetfield — legal (before scaling ads)

- [ ] **NF-WWW-02** — Legal review `privacy/`, `terms/` (3 SKUs only, no custody/payments).
- [ ] **NF-WWW-05** — Remove or qualify any MSB/regulatory claims unless registered.

### VIRLUX (other repo — before real money)

- [ ] **VL-FIN-01** — Interac / banking confirmation webhook.
- [ ] **VL-FIN-02** — KYC admin approve/reject UI.
- [ ] **VL-FIN-03** — httpOnly cookie auth (no JWT in localStorage).
- [ ] **VL-FIN-04** — Terms + privacy legal sign-off.
- [ ] **VL-FIN-06** — Circle production + transfer status webhooks.

---

## P1 — Fix in repo (engineering, next sprints)

| # | ID | Task | Effort |
|---|-----|------|--------|
| 1 | NF-WWW-04 | Regenerate `sitemap.xml` from live routes; add to CI `site-health` | S |
| 2 | NF-WWW-03 | Move Formspree ID to env/doc; or intake API-only path | M |
| 3 | NF-WWW-14 | Complete `/gate/intake/` Copilot + Bank Pilot cards | S |
| 4 | NF-ENG-10 | Document intake backup/retention; ensure prod uses `INTAKE_PERSISTENCE=postgres` | S |
| 5 | NF-ENG-14 | GitHub Action or deploy hook: build + push platform image on `main` | M |
| 6 | NF-ENG-15 | Staging host + CORS + `publish_ecosystem_config.py` for staging | M |
| 7 | NF-WWW-02 | Engineering pass: strip “procurement” labels on intake pages (readiness report warnings) | S |
| 8 | NF-ENG-17 | `/intake` Telegram command → `POST /api/intake` | M |
| 9 | NF-WWW-13 | Decision: archive or align `apps/web` Next.js with static site | L |

---

## P2 — Improve (nice to have)

- [ ] **NF-ENG-12** — pgvector embeddings + RAG retrieval from `knowledge_chunks`.
- [ ] **NF-ENG-11** — CRM webhook from intake.
- [ ] **NF-ENG-13** — Langfuse in production.
- [ ] **NF-ENG-16** — Edge WAF / rate limits.
- [ ] **NF-WWW-10** — `/pricing` page for ads.
- [ ] **NF-WWW-15** — CDN 301 map for redirect stubs.
- [ ] **NF-ENG-19** — Gmail / ops email automation (if still desired).

---

## Verification checklist (after P0)

```bash
# Platform
PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh

# Manual
# - Open www → chat → ask "What is Trust Brief?"
# - Submit trust-brief intake → check GET /api/intake/recent (admin secret)
# - Telegram /start (if configured)
```

---

## Suggested order this week

| Day | Focus |
|-----|--------|
| 1 | Secrets rotate + DNS + platform deploy + smoke script |
| 2 | www deploy + ecosystem JSON + chat CORS test |
| 3 | Telegram OR skip; legal skim on privacy/terms |
| 4 | Formspree/sitemap small fixes (P1 #1–3) |
| 5 | VIRLUX local dev only if payments are priority; else Bank Pilot console demo prep |

---

## Track updates

When you complete an item, update:

1. This file (check the box).
2. The row in `noetfield-platform.md` / `noetfield-public-site.md` / `virlux-*.md`.
3. Optional: move to `todolist/archive/`.
