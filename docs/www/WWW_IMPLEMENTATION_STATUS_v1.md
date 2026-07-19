# WWW IMPLEMENTATION STATUS v1 — AGENT SSOT

**Read this before editing noetfield.com www.**  
**Canonical path:** `noetfeld-OS/noetfield-org/WWW_IMPLEMENTATION_STATUS_v1.md`  
**Mirror (Noetfield repo):** `Noetfield/docs/www/WWW_IMPLEMENTATION_STATUS_v1.md`  
**Updated:** 2026-07-13  
**Deploy truth:** Cloudflare Pages `noetfield-www` via `Noetfield/scripts/deploy-www-cloudflare.sh`

---

## 0. Anti-downgrade rules (locked by founder)

1. **`/` is the corporate entry surface** — Noetfield Systems Inc. is a Vancouver-based AI-native systems company and product studio. The page presents governed AI execution, Custom AI Motors, Enterprise AI Governance, SourceA, SourceB, Investor Workflows, evidence boundaries and three contact paths. It contains no corporate-wide pricing, securities offering or unsupported traction claim.
2. **`/enterprise/` is frozen** — old institutional/Copilot homepage. **Do not edit** unless founder explicitly scopes it.
3. **One page = one subject** — do not cross-link unrelated directions (e.g. no Case Study / Roadmap / TrustField on `/motors/`; no diligence product on `/investors/`).
4. **Do not collapse `/` into one product lane** — product-specific pricing and commercial copy remain on their appropriate product pages; the corporate page must keep the portfolio and evidence boundaries coherent.
5. **Do not change global `header.html`** for product-lane pages — corporate pages use the standalone `nf-corp` shell.
6. **Vercel is removed** — use `www-pages-deploy.exclude` + `governance/www-pages-routes.json`. Never reintroduce `.vercelignore` / `vercel.json`.

---

## 1. Route map — live vs planned

| Route | Status | Purpose | Notes |
|-------|--------|---------|-------|
| `/` | **LIVE** | Corporate entry | Company, governed execution, portfolio, proof and contact paths |
| `/enterprise/` | **LIVE · FROZEN** | Field 1 — Enterprise AI Governance | Old homepage content; do not mutate |
| `/motors/` | **LIVE** | Field 2 — motors & custom workflows | Commission paths only |
| `/runways/` | **CANDIDATE** | Product — verified agentic execution catalog | Goal → verified output; honest status badges; no TrustField / vendor names / paid claims |
| `/investors/` | **LIVE · informational** | Evaluate **Noetfield the company** | Public evidence and support sought; not a securities offering |
| `/investor-workflows/` | **LIVE** | Field 3 — audit **your** deal/company | Public informational workflow surface |
| `/invest/` | **LIVE · GATED** | Private round materials | Supabase/Google auth; edge cookie — never on `/` |
| `/auth/sign-in/` | **LIVE** | Investor sign-in | portfolio-spine Supabase |
| `/proof/` | **LIVE** | Case study library index | |
| `/proof/noetfield/` | **LIVE** | Case Study #1 | v0.1 |
| `/proof/noetfield.json` | **LIVE** | Public evidence bundle | |
| `/proof/governed-replacement/` | **LIVE** | Case Study #2 · Client-Zero WRAP | v0.1 · not Fortune-500 claim |
| `/proof/governed-replacement.json` | **LIVE** | CS#2 machine evidence + hashes | |
| `/roadmap/` | **LIVE** | Milestone tiles | |
| `/about/` | **LIVE** | Company, operating model and portfolio boundaries | Corporate positioning and contact paths |
| `/company/` | **NOT BUILT** | Blueprint name | Use `/about/` |
| `/audit/start/` | **NOT BUILT** | Free external audit entry | Use `/investor-workflows/` + `/contact/` |
| `/proof/sourcea/` | **NOT BUILT** | Formal SourceA case study | Planned; SourceA product surface is live |
| `/proof/sourceb/` | **NOT BUILT** | Formal SourceB case study | Planned; SourceB.ca service is live |
| `/protocol/` | **DEFERRED** | Public protocol marketing | Do not ship |

---

## 2. Page content boundaries (what belongs where)

| Page | Allowed content | Forbidden on this page |
|------|-----------------|------------------------|
| `/` | Company identity, portfolio, evidence boundaries and contact paths | Corporate-wide pricing, securities offering, unsupported traction claims |
| `/motors/` | Commissioning, governed motor, custom workflow | Proof, roadmap, TrustField, SourceA pitch, investor paths |
| `/runways/` | Runway taxonomy, catalog, demonstrated receipts, three deploy paths | Vendor names, TrustField, invest/securities, invented agent counts, paid traction, margin claims |
| `/investors/` | Company thesis, portfolio state, evidence, roadmap and support sought | Private materials, securities solicitation or authentication bypass |
| `/investor-workflows/` | Request audit, diligence vault, workflow design | Invest in Noetfield, case study library |
| `/proof/*` | Evidence, case studies, JSON bundles | Invest CTAs, motor commissioning |
| `/roadmap/` | Milestones only | Cross-direction footer links |
| `/about/` | Company identity, operating model, portfolio boundaries and contact paths | Private invest materials |

---

## 3. Deploy & config (Cloudflare only)

| Artifact | Path | Role |
|----------|------|------|
| Static build output | `Noetfield/www-pages-dist/` | Pages deploy bundle |
| Deploy exclude list | `Noetfield/www-pages-deploy.exclude` | rsync exclusions (root `/data/` only — **not** `assets/data/`) |
| Public route deny rules | `Noetfield/governance/www-pages-routes.json` | Rewrites + 404 redirects → `_redirects` |
| Denylist purge | `governance/PUBLIC_OUTPUT_DENYLIST.json` | Internal paths never ship |
| Invest edge gate | `Noetfield/functions/invest/[[path]].js` | Cookie check before `/invest/` HTML |
| Session API | `Noetfield/api/auth/invest-session.js` | Sets `nf_invest_auth` cookie |
| Auth config (public) | `Noetfield/assets/noetfield-platform-auth-config-v1.json` | Supabase anon + URLs |

**Retired:** `.vercelignore`, `vercel.json`, Vercel deploy scripts, `functions/_lib/vercel-adapter.js` → `pages-node-handler-adapter.js`

---

## 4. Blueprint corrections (strategy doc vs reality)

`NOETFIELD_COMPANY_STRATEGY_v1_BLUEPRINT.md` §3 is **strategy target**, not live truth. Corrections:

| Blueprint says | Actual (2026-07-13) |
|----------------|---------------------|
| `/` = corporate homepage (3 fields) | `/` = **corporate entry surface** (NF-WEB-001) |
| Nav: Enterprise \| Motors \| Investor Workflows on homepage | Homepage presents the company portfolio, including Investor Workflows, with scoped product and contact links |
| `/company` | **`/about/`** implemented instead |
| `/audit/start` | **Not built** — contact + `/investor-workflows/` |
| Lane C “Rebuild homepage” pending | **Corporate entry surface shipped**; product pages remain scoped and unchanged |
| Case Study #1 publish pending | **Shipped** at `/proof/noetfield/` |

Product-lane strategy (three commercial fields, proof library model, naming table) remains **locked for its scoped product pages**. The corporate entry surface uses the portfolio posture above; site architecture in §3 must be read **through this status file**.

---

## 5. Not yet implemented (safe backlog)

- `/audit/start/` productized free audit funnel
- `/company/` (blueprint alias; `/about/` is the live corporate page)
- Formal SourceA and SourceB public case studies (`/proof/sourcea`, `/proof/sourceb`)
- `intelligence.noetfield.com` subdomain swap (advisor P0 — **not done**)
- `proof-page-live-receipt-v1` formal receipt emission
- SG ratification of company strategy blueprint (Lane B)
- `/protocol` public marketing (deferred)

---

## 6. Known doc pollution — do not propagate

These still mention Vercel or old architecture; **ignore or fix when touched**, do not treat as SSOT:

- `Noetfield/prompts/loop-suggestions-100.json` — **fixed** (was vercel.json prompts)
- `Noetfield/docs/ops/plans/NOETFIELD_E2E_SMART_UPGRADE_321_TASKS_v1.md` — fixed E2E-201 (was `.vercelignore`)
- `Noetfield/docs/ops/NOETFIELD_SYSTEM_NERVE_UPGRADE_100_PLANS_LOCKED_v1.md` — fixed (was vercel.json references)
- `Noetfield/graph-out/` — generated; may list deleted paths
- Historical reports under `Noetfield/reports/` — point-in-time only

---

## 7. Verify after www changes

```bash
cd Noetfield
bash scripts/build-www-pages-dist.sh
python3 scripts/verify-public-denylist-sync.py
bash scripts/verify-static-www.sh   # subset; gate pages may not all be in script yet
bash scripts/deploy-www-cloudflare.sh   # when founder requests deploy
curl -I https://www.noetfield.com/invest/   # expect 302 → sign-in
curl https://www.noetfield.com/assets/noetfield-platform-auth-config-v1.json  # expect 200 JSON
```

---

## 8. Related canonical docs

| Doc | Use |
|-----|-----|
| `NOETFIELD_COMPANY_STRATEGY_v1_BLUEPRINT.md` | Strategy + naming (not live route truth) |
| `DOC_INDEX_v1.md` | NOOS doc index — read first in noetfeld-OS |
| `Noetfield/DEPLOYMENT_ARCHITECTURE.md` | Domain split + Cloudflare deploy |
| `Noetfield/docs/ops/CF_WWW_PROXY_LOCKED_v1.md` | www proxy → Pages origin |
| `noetfeld-OS/docs/ops/NOOS_CLOUDFLARE_WWW_DEPLOY_v1.md` | NOOS probe contract |

---

**Next agent:** Match task to **§1 route status** and **§2 page boundaries**. If blueprint §3 conflicts with this file, **this file wins** for www execution.
