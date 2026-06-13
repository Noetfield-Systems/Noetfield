# Noetfield Forward Queue — 100 Plans (v2 · upgraded)

**Status:** Research-derived forward queue · **proven patterns** — Form PICK before implement  
**Path:** `docs/strategy/NOETFIELD_FORWARD_QUEUE_100_v2.md`  
**Updated:** 2026-06-03  
**Grounding:** [MARKET_ANALYSIS_2026_LOCKED_v1.md](./MARKET_ANALYSIS_2026_LOCKED_v1.md) · [NOETFIELD_FORWARD_QUEUE_100_v1.md](./NOETFIELD_FORWARD_QUEUE_100_v1.md) · institutional UI branch `cursor/ui-high-grade-e2e-37f0`  
**ID namespace:** `ship-fwd-160` … `ship-fwd-259` (continues v1 post–`ship-fwd-159`)

**Lane key:** **A** = NF-CLOUD disk · **H** = Hub/agentic only · **D** = docs/spec only

**v2 upgrade thesis:** v1 named *what* to ship; v2 names **proven buyer-grade patterns** — Vanta-style trust transparency, Playwright evidence retention, Fiddler/Gateplex-grade console polish, and procurement automation — scoped to Noetfield law (receipt export, no custody, complement Agent 365).

---

## Wave 11 — Trust Center & proactive diligence (FQ-101–110)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-160 | 101 | T1 | A | `/trust-center/` live posture page | Public-safe control status + last verify run | verify-gtm | Vanta Trust Center |
| ship-fwd-161 | 102 | T1 | D | Trust Center content policy | What may appear live vs Form PICK | spec review | continuous verification |
| ship-fwd-162 | 103 | T1 | A | Procurement ZIP checksum badge | SHA-256 + manifest on `/copilot/procurement/` | verify-gtm | buyer diligence |
| ship-fwd-163 | 104 | T2 | A | Control status API stub | `GET /api/v1/controls/status` mock | pytest | Vanta 1400+ tests pattern |
| ship-fwd-164 | 105 | T1 | D | Security FAQ auto-answer index | Map 20 buyer questions → doc anchors | verify-gtm | questionnaire deflection |
| ship-fwd-165 | 106 | T2 | A | Subprocessor list page | Metadata-only vendors table | verify-gtm | enterprise procurement |
| ship-fwd-166 | 107 | T1 | D | Trust Center vs SOC2 claim fence | No certification claims on www | verify-no-asf | PROJECT_BOUNDARIES |
| ship-fwd-167 | 108 | T2 | H | TPRM outreach: MSP security leads | Hub list — complement not compete | agentic | Vanta TPRM network |
| ship-fwd-168 | 109 | T1 | A | `last_verified_at` in openapi.json | Status endpoint cites verify bundle time | plan-with-no-asf | continuous proof |
| ship-fwd-169 | 110 | T2 | D | Buyer “read before questionnaire” guide | 1-pager linked from trust center | verify-gtm | 87% deflection pattern |

---

## Wave 12 — Playwright E2E & evidence retention (FQ-111–120)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-170 | 111 | T1 | A | Playwright smoke suite v1 | 5 routes: www + console dashboard | playwright | TestCollab evidence gap |
| ship-fwd-171 | 112 | T1 | A | `make verify-playwright` gate | CI artifact retention 90 days | plan-with-no-asf | evidence at scale |
| ship-fwd-172 | 113 | T2 | A | Requirement → test ID map | FQ rows tagged in playwright specs | docs+pytest | Qualigentic audit chain |
| ship-fwd-173 | 114 | T1 | A | Copilot funnel browser E2E | quickscan → readiness → pilot 200s | playwright | SME journey |
| ship-fwd-174 | 115 | T2 | A | Flaky quarantine doc + tag | `@quarantine` skipped in ship-verify | dev-local | Currents flaky pattern |
| ship-fwd-175 | 116 | T1 | A | Trace-on-failure config | `playwright.config.ts` retain traces | manual | institutional debug |
| ship-fwd-176 | 117 | T2 | A | Evaluate→TLE→export browser path | Single spec RID continuity | playwright | Airia execution trail |
| ship-fwd-177 | 118 | T2 | D | E2E evidence retention runbook | Where traces live; no PII in artifacts | docs | SOC2-style evidence |
| ship-fwd-178 | 119 | T1 | A | Procurement table sort/filter E2E | `/copilot/procurement/` interactions | playwright | UI branch nf-table |
| ship-fwd-179 | 120 | T2 | A | Release gate: critical paths green | Block promote if playwright FAIL | plan-with-no-asf | TestCollab policy hooks |

---

## Wave 13 — Institutional console UI (FQ-121–130)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-180 | 121 | T1 | A | Merge `WorkflowStepper` to main path | Block·Record·Export on all console pages | verify-ui-e2e | Fiddler-grade UX |
| ship-fwd-181 | 122 | T1 | A | `MetricStrip` on cognitive-dashboard | KPI row: evaluates, blocks, exports | verify-ui-e2e | Gateplex metrics |
| ship-fwd-182 | 123 | T1 | A | Shell status bar + www links | Sticky nav + procurement discoverability | verify-ui-e2e | institutional shell |
| ship-fwd-183 | 124 | T2 | A | Workspace data table v2 | Sortable TLE list + empty states | verify-ui-e2e | enterprise tables |
| ship-fwd-184 | 125 | T2 | A | Result `[rid]` receipt hero | Decision badge + copy RID + export CTA | verify-ui-e2e | receipt-first UX |
| ship-fwd-185 | 126 | T1 | A | `nf-pipeline` on static www | Homepage + copilot pipeline strip | verify-gtm | brand parity |
| ship-fwd-186 | 127 | T2 | A | Trust-ledger detail print CSS | Board-meeting print layout | manual | STRATEGIC_LOCK |
| ship-fwd-187 | 128 | T2 | A | Connector health in workspace UI | `last_sync` column visible | dev-local | Agent 365 complement |
| ship-fwd-188 | 129 | T1 | A | Deprecate `governance-console-v1.html` | Redirect to Next console | verify-ui-e2e | route collapse |
| ship-fwd-189 | 130 | T2 | D | Console design tokens doc | Colors, spacing, component map | docs | design system hygiene |

---

## Wave 14 — SSO, RBAC & enterprise shell (FQ-131–140)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-190 | 131 | T2 | D | Entra SSO integration spec | OIDC flow — production gated ASF | spec | enterprise buyers |
| ship-fwd-191 | 132 | T2 | A | Workspace role matrix stub | viewer / operator / admin enums | pytest | Dashwright RBAC |
| ship-fwd-192 | 133 | T1 | D | RBAC buyer FAQ | What roles mean — no overclaim | verify-gtm | Vanta granular RBAC |
| ship-fwd-193 | 134 | T2 | A | Audit log actor field | `actor_id` on evaluate events | pytest | immutable audit |
| ship-fwd-194 | 135 | T2 | A | Session timeout config doc | Dev default vs prod policy | docs | FRFI expectations |
| ship-fwd-195 | 136 | T1 | A | Console login wall stub | Dev bypass banner only | dev-local | honest staging |
| ship-fwd-196 | 137 | T2 | D | SCIM provisioning outline | Post-SSO — not W3 claim | confidentiality | enterprise IT |
| ship-fwd-197 | 138 | T2 | A | API key rotation runbook | Internal ops — metadata keys | docs | procurement FAQ |
| ship-fwd-198 | 139 | T1 | D | Multi-tenant boundary statement | Single-org pilot default | verify-no-asf | PRODUCT_TRUTH |
| ship-fwd-199 | 140 | T2 | A | RBAC pytest suite v1 | Role denies cross-workspace read | pytest | institutional SaaS |

---

## Wave 15 — NIST AI RMF & ISO 42001 conformity (FQ-141–150)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-200 | 141 | T1 | D | NIST AI RMF tier-1 mapping | Map TLE to GOVERN/MAP/MEASURE/MANAGE | spec review | MarketsandMarkets |
| ship-fwd-201 | 142 | T1 | D | ISO 42001 product vs AIMS fence | Noetfield = product evidence not cert | verify-no-asf | Modulos vs Vanta |
| ship-fwd-202 | 143 | T2 | D | ISO 42001 annex export template | Optional PDF appendix for Trust Brief | manual | Gartner frameworks |
| ship-fwd-203 | 144 | T1 | A | Framework picker on procurement | EU / OSFI / NIST toggle copy blocks | verify-gtm | one evidence bundle |
| ship-fwd-204 | 145 | T2 | D | High-risk AI system checklist | EU Annex III buyer self-assess | docs | EU Omnibus 2027 |
| ship-fwd-205 | 146 | T1 | D | NIST GenAI profile crosswalk | Internal map to evaluate policies | spec | US subsidiaries |
| ship-fwd-206 | 147 | T2 | A | `framework_tags` on TLE export | Optional metadata field in JSON | tle-smoke | multi-framework buyers |
| ship-fwd-207 | 148 | T2 | H | Outreach: ISO 42001 programme leads | Agentic — complement Vanta AIMS | Hub | buyer segmentation |
| ship-fwd-208 | 149 | T1 | D | Framework citation integrity guard | verify-gtm blocks unverified stats | verify-gtm | research integrity |
| ship-fwd-209 | 150 | T2 | D | Conformity assessment handoff card | When to route legal vs Noetfield | docs | notified-body path |

---

## Wave 16 — Procurement automation & diligence velocity (FQ-151–160)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-210 | 151 | T1 | A | Questionnaire auto-fill JSON | Machine-readable answers bundle | verify-gtm | Vanta 95% acceptance |
| ship-fwd-211 | 152 | T1 | A | OpenAPI diff in procurement ZIP | Schema changelog since last drop | plan-with-no-asf | technical diligence |
| ship-fwd-212 | 153 | T2 | A | Control catalog deep-link anchors | Each control → pytest name | pytest | copilot-control-catalog |
| ship-fwd-213 | 154 | T1 | D | Evaluator scoring rubric | How procurement grades TLE sample | verify-gtm | buyer enablement |
| ship-fwd-214 | 155 | T2 | A | Sample TLE redaction mode | PII-safe demo export flag | tle-smoke | legal review |
| ship-fwd-215 | 156 | T1 | A | `make procurement-pack` one-shot | ZIP + manifest + checksums | make ship-verify | buyer ZIP |
| ship-fwd-216 | 157 | T2 | D | DPA metadata fields template | Subprocessor + retention bullets | legal draft | Purview metadata |
| ship-fwd-217 | 158 | T2 | A | Pen-test summary placeholder | Scope boundary — shadow pilot | docs | Bank Pilot |
| ship-fwd-218 | 159 | T1 | H | Legal outreach: in-house counsel AB | Agentic — procurement friction | Hub | mid-market legal |
| ship-fwd-219 | 160 | T1 | A | Procurement page verify hardening | All annex links 200 + checksum | verify-gtm | diligence loop |

---

## Wave 17 — Agent observability complement (FQ-161–170)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-220 | 161 | T1 | D | Agent 365 + Noetfield joint diagram | Registry vs receipt — www safe | verify-gtm | KPMG 276K |
| ship-fwd-221 | 162 | T2 | A | Agent sponsor field in evaluate | Maps to Entra agent identity stub | pytest | Microsoft Entra AI |
| ship-fwd-222 | 163 | T1 | D | Fiddler complement battlecard v2 | Observability vs pre-execution receipt | confidentiality | Fiddler control plane |
| ship-fwd-223 | 164 | T2 | A | Fleet summary metric API | `GET /api/v1/agents/summary` mock | pytest | fleet governance gap |
| ship-fwd-224 | 165 | T1 | A | Purview sync status in console | Connector row + last_sync badge | dev-local | Purview Agent 365 |
| ship-fwd-225 | 166 | T2 | D | Defender alert handoff spec | Metadata index only — no SIEM claim | spec | CAF security |
| ship-fwd-226 | 167 | T1 | D | Gateplex latency honest compare | Pre-exec receipt vs ms block | confidentiality | Gateplex EU |
| ship-fwd-227 | 168 | T2 | A | BLOCK reason taxonomy v2 | Standardized reject codes in API | pytest | examiner readability |
| ship-fwd-228 | 169 | T2 | H | M365 admin webinar outreach list | Post-Agent 365 GA wave | agentic | 72%/21% gap |
| ship-fwd-229 | 170 | T1 | A | Copilot governance Agent 365 CTA | `/copilot/governance/` complement block | verify-gtm | complement positioning |

---

## Wave 18 — Design partner proof & W3 economics (FQ-171–180)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-230 | 171 | T1 | H | Design partner LOI template | CAD $2K sandbox SOW outline | agentic | ENFORCEMENT-6MO |
| ship-fwd-231 | 172 | T1 | A | Homepage proof slot v2 | Named placeholder + logo policy | verify-gtm | W3 proof |
| ship-fwd-232 | 173 | T2 | A | Board PDF sample pack v3 | 3 verticals — finance, legal, ops | manual | governance meeting |
| ship-fwd-233 | 174 | T1 | H | Film W2 demo script — console | 3-min Block·Record·Export film | agentic | W1 proof extend |
| ship-fwd-234 | 175 | T1 | A | Economic signal verify v2 | www cites CAD $2K without NO-CC | verify-gtm | GO_FORWARD_NOW |
| ship-fwd-235 | 176 | T2 | D | Pilot success criteria worksheet | Buyer fills KPIs pre-pilot | docs | Forrester TEI |
| ship-fwd-236 | 177 | T2 | H | CIO intro wave — BC credit unions | Agentic E-23 timing | Hub | OSFI runway |
| ship-fwd-237 | 178 | T1 | D | Trust Brief upsell path v2 | $10K diagnostic from pilot | verify-gtm | OFFERINGS |
| ship-fwd-238 | 179 | T2 | A | `make demo-url` staging parity | Staging URL in verify output | plan-with-no-asf | outreach 026 |
| ship-fwd-239 | 180 | T1 | D | Case study skeleton (anonymized) | Structure only — Form PICK body | Form PICK | social proof |

---

## Wave 19 — API platform & developer experience (FQ-181–190)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-240 | 181 | T1 | A | OpenAPI single source convergence | One schema — dev + prod README | plan-with-no-asf | FQ-081 v1 carry |
| ship-fwd-241 | 182 | T1 | A | SDK stub generator doc | curl + Python examples from openapi | verify-gtm | procurement |
| ship-fwd-242 | 183 | T2 | A | Webhook signature verify test | HMAC on BLOCK receipt webhook | pytest | services/governance |
| ship-fwd-243 | 184 | T2 | A | Rate limit headers on evaluate | `X-RateLimit-*` honest local | pytest | enterprise SLA |
| ship-fwd-244 | 185 | T1 | A | API changelog in cursor-reply | Breaking changes surfaced post-ship | plan-with-no-asf | buyer diligence |
| ship-fwd-245 | 186 | T2 | A | Idempotency key on evaluate | `Idempotency-Key` header support | pytest | Fuzentry receipts |
| ship-fwd-246 | 187 | T1 | D | Public API scope boundary | Pre-execution only — no custody | verify-no-asf | PRODUCT_TRUTH |
| ship-fwd-247 | 188 | T2 | A | Health + readiness split endpoints | `/health` vs `/ready` semantics | pytest | k8s pattern |
| ship-fwd-248 | 189 | T2 | D | Partner embed API memo | Stage 2+ — not W3 SKU | confidentiality | unified engine |
| ship-fwd-249 | 190 | T1 | A | Postman collection in procurement ZIP | Importable collection synced | verify-gtm | technical buyers |

---

## Wave 20 — Platform maturity & coherence (FQ-191–200)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-250 | 191 | T1 | A | Forward queue v2 coherence gate | verify-no-asf indexes FQ-101–200 | plan-with-no-asf | audit discipline |
| ship-fwd-251 | 192 | T1 | A | SHIP_DONE_MAP v2 sync | `ship-fwd-16x` patterns in manifest | sync script | registry hygiene |
| ship-fwd-252 | 193 | T2 | A | Load test evaluate p95 gate | p95 &lt;500ms local documented | perf | enterprise SLA |
| ship-fwd-253 | 194 | T1 | D | SSOT_INDEX v2 link | Index points here + v1 | plan-with-no-asf | coherence |
| ship-fwd-254 | 195 | T2 | D | Incident response AI playbook v2 | Agentic ops template refresh | docs | agentic ops |
| ship-fwd-255 | 196 | T1 | A | Intake email audit in ship-verify | `audit_intake_email.py` mandatory | make ship-verify | STRATEGIC_LOCK |
| ship-fwd-256 | 197 | T2 | A | Coherence verify UI + playwright | Single bundle: plan + ui + browser | plan-with-no-asf | institutional E2E |
| ship-fwd-257 | 198 | T1 | D | Twelfth-audit iter 30–39 seed | Next 3 picks from v2 top row | GTM_NEXT | queue hygiene |
| ship-fwd-258 | 199 | T2 | D | Annual license hypothesis v2 | Post-pilot pricing scenarios | Form PICK | GO_FORWARD_NOW |
| ship-fwd-259 | 200 | T1 | D | v1+v2 golden path memo | 10-plan sequenced roadmap for founder | Form PICK | strategic synthesis |

---

## Priority tiers

| Tier | Meaning | Count |
|------|---------|-------|
| **T1** | Revenue, diligence, or console polish inside 90 days | 48 |
| **T2** | Hardening / enablement 90–180 days | 50 |
| **T3** | Stage 2+ / confidential strategy | 2 |

---

## v2 vs v1 — what upgraded

| Dimension | v1 emphasis | v2 upgrade |
|-----------|-------------|------------|
| Buyer UX | Copy + verify gates | **Trust Center**, institutional console, Playwright proof |
| Evidence | TLE + tamper tests | **Retention policy**, requirement→test map, release gates |
| Frameworks | Mapping docs | **ISO 42001 product vs AIMS fence**, framework picker |
| Procurement | ZIP + FAQ | **Auto-fill JSON**, checksum badges, Postman in pack |
| Agents | Complement copy | **Fleet summary API**, sponsor field, Purview sync UI |
| Coherence | FQ manifest gate | **v2 index**, unified verify bundle (plan + ui + playwright) |

---

## Recommended next 3 picks (post–v1 top picks)

After v1 picks (`ship-fwd-060`, `ship-fwd-081`, `ship-fwd-090`) or in parallel where lanes differ:

1. **ship-fwd-160** — Trust Center live posture page (FQ-101)  
2. **ship-fwd-170** — Playwright smoke suite v1 (FQ-111)  
3. **ship-fwd-180** — WorkflowStepper merge to main console path (FQ-121)  

**Fast diligence trio:** ship-fwd-162 + ship-fwd-210 + ship-fwd-219 (procurement velocity)

---

## Proven pattern sources (June 2026)

| Pattern | Source | Noetfield scope |
|---------|--------|-----------------|
| Trust Center / continuous proof | [Vanta Trust Center](https://www.vanta.com/resources/best-compliance-software-for-enterprise) | Control status + verify timestamp — no SOC2 claim |
| Questionnaire deflection | [Vanta vs Drata enterprises](https://www.vanta.com/resources/vanta-vs-drata-for-enterprises) | Security FAQ + procurement auto-fill JSON |
| ISO 42001 buyer path | [Modulos vs Vanta](https://www.modulos.ai/modulos-vs-vanta) | Product evidence vs AIMS audit prep |
| Playwright evidence retention | [TestCollab evidence at scale](https://testcollab.com/blog/playwright-testing-evidence-at-scale) | `make verify-playwright` + 90-day artifacts |
| Console RBAC reference | [Dashwright](https://github.com/CybeDefend/dashwright) | Workspace roles — stub before production SSO |
| Institutional UI | PR #54 `cursor/ui-high-grade-e2e-37f0` | WorkflowStepper, MetricStrip, nf-table |

---

## Law fences (all 100 v2 plans)

- **No** payment rails · custody · NO-CC · cloud deploy hero  
- **No** SourceA disk edits from NF chat  
- **No** TrustField/VIRLUX implementation in Noetfield repo  
- **No** SOC 2 / ISO cert claims on www without founder attest  
- **H** rows = Hub/agentic only — NF-CLOUD maintains copy, not send  
- **Promote** any locked spec to www only after **Form PICK**  

---

## Related

- [NOETFIELD_FORWARD_QUEUE_100_v3.md](./NOETFIELD_FORWARD_QUEUE_100_v3.md) — FQ-201–300 scale (board, CU channel, drift, incidents)  
- [NOETFIELD_FORWARD_QUEUE_100_v1.md](./NOETFIELD_FORWARD_QUEUE_100_v1.md) — FQ-001–100  
- [MARKET_ANALYSIS_2026_LOCKED_v1.md](./MARKET_ANALYSIS_2026_LOCKED_v1.md)  
- [GTM_NEXT.md](../ops/plans/no-asf/GTM_NEXT.md)  
- [SSOT_INDEX.md](../SSOT_INDEX.md)
