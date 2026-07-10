# PUBLIC WWW BRAND & E2E LAW (LOCKED v1)

**Layer:** L0-adjacent operational law (public deploy boundary)
**Updated:** 2026-06-26
**Owner:** Noetfield Systems Inc. (holding company · www.noetfield.com)
**Enforcement:** `scripts/verify-static-www.sh` (offline disk) · `scripts/check_noetfield_com_e2e.py` (production smoke)

---

## 1. Purpose

www.noetfield.com is the **institutional buyer surface** for Noetfield Intelligence and Enterprise Copilot governance. It must read as a **credible holding-company-grade** vendor to regulated buyers, investors, and partners — never as an internal agent repo, founder ops log, or engineering catalog.

Repo copies of internal docs **stay on disk for agents** — they are **not www**.

---

## 2. Public brand posture (613 Intelligence + enterprise governance)

| Lane | Primary CTA | Enterprise sub-lane |
|------|-------------|---------------------|
| **Intelligence** | Book Diagnostic Sprint · from $2,500 | — |
| **Governance** | Apply for pilot ($2k–10k) · Copilot Governance Pack | Trust Brief · Bank Pilot · board PDF |

**Required homepage phrases (disk + live E2E):**

- Board-grade trust
- tamper-evident decision records
- Apply for pilot ($2k–10k)
- Copilot Governance Pack · Trust Brief · Bank Pilot
- Commercial path · Diagnostic Sprint · 01 · Diagnose → 04 · Govern

**Forbidden on public HTML** (buyer-visible pages):

- Founder/agent ops: `founder never`, `Hub approve`, `613 GTM`, `AGENT_SELF_AUDIT`, `plan-with-no-asf`, `RESEND_API_KEY`, `docs/ops/`, `make nf-prove`, portfolio wave counts
- Internal repo language: `OFFERINGS_LOCKED`, `SourceA`, `W3 economic signal`, `design partner`
- Engineering surfaces linked from marketing: `/platform/factories/`, `services/governance/README`

---

## 3. Deploy boundary (vercel.json + .vercelignore)

### Must return 404 on www (redirect or exclude)

| Path | Reason |
|------|--------|
| `/docs/ops/*` | Agent runbooks |
| `/docs/platform/*` | Living system charter · internal platform SSOT |
| `/governance/*.json`, `/governance/*.md` (except public HTML hub) | OPS_LIVE · LAW_STACK · factory catalogs |
| `/OFFERINGS_LOCKED.md` | Internal SKU lock file |
| `/platform/*` | Engineering factory catalog · repo path leaks |
| `/.cursor/*`, `/scripts/*`, `/services/*`, `/os/*`, `/reports/*` | Engineering |

### Must remain public (200)

| Path | Reason |
|------|--------|
| `/governance/` | Enterprise buyer hub (HTML) |
| `/`, `/copilot/*`, `/trust/*`, `/investors/*`, `/pricing/*`, `/start/*` | GTM surfaces |
| `/docs/api/`, `/docs/diligence/*`, `/docs/copilot/*` | Procurement diligence (buyer-facing) |

---

## 4. Production E2E contract

Run: `python3 scripts/check_noetfield_com_e2e.py`
Optional base override: `NOETFIELD_E2E_BASE=https://www.noetfield.com`

### HTTP 200 required

`/`, `/start/`, `/pricing/`, `/copilot/`, `/copilot/pilot/`, `/copilot/demo/`, `/copilot/proof-case/`, `/trust/`, `/trust-brief/intake/`, `/trust-ledger/sample-report/`, `/investors/`, `/work-with-us/`, `/health` (or `/api/health`), `/governance/`, `/ai-factories/`, `/ai-factories/spec/`, `/openapi.json`, `/config/gate-ai-factory-design.json`, `/config/status-ai-factory.json`, `/noetfield-ai-factory-lanes.json`

### HTTP 404 required (internal leak regression)

`/docs/platform/NF_LIVING_SYSTEM_CHARTER_DRAFT_v3.md`, `/governance/OPS_LIVE_STATUS_LOCKED.json`, `/OFFERINGS_LOCKED.md`, `/platform/factories/`

### API smoke

- `/api/health` — `status: ok`, `service: noetfield-www`
- `/api/intake/health` — `www_email_configured: true`, `delivery_mode: resend`, honest `platform_reachable`
- `/api/public/chat/health` — `ok: true`, `mode: www-local` or `platform-proxy`
- POST `/api/public/chat` — contextual assistant response or routing-only fallback; never a static rule script
- GET `/api/ecosystem/public` — `chat_api_base` same-origin (`""`) until platform DNS live
- POST `/evaluate` — returns `rid`
- POST `/api/gate/ai-factory-design` — returns `gate_lane: AI Factory Design` and a policy decision
- GET `/api/status/ai-factory?request_id=...` — returns an AI Factory status preview

**Out of www E2E scope:** dedicated platform/GEL health probes for `platform.noetfield.com` and `api.noetfield.com`. The public www E2E remains focused on website behavior and leak prevention.

### Copy smoke (homepage + pilot)

- Homepage: Apply for pilot, Copilot Governance Pack, Trust Brief, **Board-grade trust**, operations@noetfield.com
- Pilot: nfPilotApplyForm, Copilot Governance Pack, tamper-evident

---

## 5. Offline disk mirror

Before every www deploy merge: **`make verify-static-www`** must PASS.

Disk HTML, partials, `vercel.json`, and `.vercelignore` are the **source of truth** for what may ship. Production E2E confirms live deploy matches this law.

---

## 6. Amendment

Changes to this law require updating **both** enforcement scripts in the same PR. Do not weaken block lists without founder approval.

---

## 7. WWW spine tiers & next upgrade plan

www.noetfield.com must **never hard-depend** on subdomains that are not DNS-provisioned. Buyer-facing status must reflect www-owned contracts honestly.

| Tier | Host | Status (2026-06-26) | Next action |
|------|------|---------------------|-------------|
| **L0 — Institutional www** | `www.noetfield.com` | **Live** — marketing, intake (Resend), sandbox evaluate, www-local FAQ chat | Maintain E2E law |
| **L1 — Platform spine** | `platform.noetfield.com` | **Live** — Railway platform API health 200 | Keep platform smoke separate from www E2E |
| **L2 — GEL API lane** | `api.noetfield.com` | **Live** — noetfeld-os Railway `gel-api`, local port `8001` | Keep `/health` and `/readiness` in separate GEL smoke |
| **L3 — LLM chat proxy** | platform `/api/public/chat` | Deferred until L1 | UPG-WWW-003: env keys on platform; www health `mode: platform-proxy` |
| **L4 — Telegram + ecosystem** | platform webhooks | Deferred | UPG-WWW-004: footer `@username` when bot live |

### Enforcement rules

1. **No vercel.json rewrites** to `platform.noetfield.com` unless L1 passes dedicated platform smoke.
2. **`platform_reachable`** on intake health must be boolean from successful fetch — never inferred from `{}`.
3. **`chat_api_base`** in ecosystem JSON stays same-origin until L3.
4. Production E2E (`check_noetfield_com_e2e.py`) asserts **www spine only**; platform/GEL probes belong in dedicated platform/GEL smoke checks.

### Run after platform/GEL changes

```bash
PLATFORM_BASE=https://platform.noetfield.com python3 scripts/verify_platform_health.py
NOETFIELD_E2E_BASE=https://www.noetfield.com python3 scripts/check_noetfield_com_e2e.py
```

---

## 8. Partner onboarding browser-behavioral contract (ADDITIVE — pending founder sign-off)

**Added:** 2026-07-09 · **Status:** proposed, not yet founder-approved per §6 amendment rule — flagged for review, not silently authoritative.

`check_noetfield_com_e2e.py` is pure-HTTP (status codes + copy needles) and cannot see a JS
exception thrown inside an onsubmit handler, or a form field that is `required` but hidden
by a CSS/JS bug. Those failure modes are real (found live on `/work-with-us/` and
`/trust-brief/intake/`) and need a real browser. This section documents the *new*,
separate enforcement layer — it does not change anything in §1–§7.

**Enforcement:** `scripts/nf_partner_onboarding_e2e_audit_v1.py` (Playwright + Chromium),
run every 6 hours by `.github/workflows/nf-partner-onboarding-e2e-audit.yml`.

**Must hold true in production:**

| Check | Pass condition |
|---|---|
| Quick Apply (Connector) submit | Clicking submit on `#nfPartnerApplyForm` fires `POST /api/intake` and throws no `pageerror` |
| Ecosystem apply form | `/trust-brief/intake/?interest=partner&vector=work-with-us&role=<lane>` hides every `.tb-estimator-fields` element — no required Trust-Brief pricing field is visible |
| Investor inquiry | `#nfInvestorForm` submit reaches a success state within 8s |
| MSP / next-step CTAs | `/msp/` and `/next/` never link their partner CTA to `/gate/partners/intake/` while that path meta-refreshes to `/enterprise/` |

**Out of scope:** commission-figure disclosure and nav-placement checks in the same
script are advisory (high/medium severity, non-blocking) — content and IA decisions stay
founder-gated, only the four rows above are pass/fail.

**Amendment note:** this section was added by an automated audit session, not by the
founder. Per §6, changes to this law require founder approval — treat §8 as a proposal to
ratify or reject, not as already-locked law.
