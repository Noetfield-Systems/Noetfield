# Institutional bank-grade UI — 100-plan (VC / FRFI)

**Status:** Strategic execution roadmap — Form PICK before www promote claims  
**Path:** `docs/strategy/INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md`  
**Updated:** 2026-06-03  
**Grounding:** [MARKET_ANALYSIS_2026_LOCKED_v1.md](./MARKET_ANALYSIS_2026_LOCKED_v1.md) · [INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md](./INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md) · buyer moments: board PDF · procurement ZIP · E-23 committee · MSP client board

**Lane key:** **A** = NF-CLOUD disk · **D** = docs/spec · **H** = Hub only (R-011)

**Success model:** Every item must move a **buyer-visible proof point** — not infra for its own sake.

---

## Executive pick order

1. **Waves 1–3** — Shell, proof bars, FRFI fences (what committees see first)  
2. **Waves 4–6** — Trust center, demo funnel, procurement export path  
3. **Waves 7–9** — Channel + federal + console parity  
4. **Wave 10** — Verify, a11y, print — lock bank-grade regression gates  

**Bottleneck:** GTM validation 2/10 until a **board PDF** is used in a real governance meeting.

---

## Wave 1 — Design system & shell (001–010)

| ID | T | L | Plan | Outcome | Verify | Pattern |
|----|---|---|------|---------|--------|---------|
| bank-ui-001 | T1 | A | Bank-grade CSS layer on all tier pages | `noetfield-bank-grade.css` loaded on 14 GTM routes | smoke_bank_grade | board-pdf-moment |
| bank-ui-002 | T1 | A | Fix merged body classes (`nf-frfi nf-site-2026`) | No duplicate `class=` on bank-pilot / enterprise | smoke_bank_grade | frfi-fence |
| bank-ui-003 | T1 | A | Status strip with live posture pill | Shadow-mode pill + trust center link on all 2026 pages | verify-ui-e2e | trust-center-grid |
| bank-ui-004 | T1 | A | Nav glass + hairline border polish | Elevated nav on `.nf-site-2026` | manual | institutional-shell |
| bank-ui-005 | T2 | A | Skip link on every tier + funnel page | a11y baseline on 14 routes | smoke_bank_grade | a11y-baseline |
| bank-ui-006 | T1 | D | DESIGN_SYSTEM.md bank-grade stack doc | Tokens → shell → bank-grade load order locked | verify-gtm | design-system |
| bank-ui-007 | T2 | A | `apply_institutional_2026_frame.py` v2 | Auto-frame copilot funnel + partners/msp + federal | pytest | frame-automation |
| bank-ui-008 | T2 | A | Canonical + theme-color on funnel pages | demo / pilot / procurement SEO parity | verify-gtm | seo-parity |
| bank-ui-009 | T2 | D | Typography scale audit doc | IBM Plex hierarchy for board PDFs + print | docs | typography-lock |
| bank-ui-010 | T1 | A | Proof diligence bar component | `.nf-proof-bar` on `/`, enterprise, bank-pilot, demo | verify-ui-e2e | board-pdf-moment |

---

## Wave 2 — Homepage & enterprise (011–020)

| ID | T | L | Plan | Outcome | Verify | Pattern |
|----|---|---|------|---------|--------|---------|
| bank-ui-011 | T1 | A | Homepage diligence path strip | 3-step board → pilot → procurement on `/` | verify-gtm | buyer-hero |
| bank-ui-012 | T1 | A | Enterprise E-23 proof bar | FRFI proof points above metrics | smoke_bank_grade | frfi-fence |
| bank-ui-013 | T1 | A | Enterprise E-23 table zebra polish | Audit-readable `.nf-table` on enterprise | manual | e23-mapping |
| bank-ui-014 | T2 | A | Homepage offerings price hierarchy | Trust Brief $10K visual anchor | verify-gtm | buyer-hero |
| bank-ui-015 | T1 | D | Enterprise buyer one-pager PDF outline | CCO/CRO committee leave-behind spec | spec review | enterprise-deck |
| bank-ui-016 | T2 | A | CTA band shadow elevation | Footer CTA matches bank-grade close | manual | cta-band |
| bank-ui-017 | T1 | A | Homepage metrics OK state emphasis | TLE receipt metric highlighted | verify-gtm | receipt-export-wedge |
| bank-ui-018 | T2 | A | Enterprise Bank Pilot dual CTA | Intake + overview paths visible | verify-gtm | frfi-fence |
| bank-ui-019 | T1 | D | VC diligence FAQ block spec | 12 questions → doc anchors | verify-gtm | trust-center-grid |
| bank-ui-020 | T2 | A | Homepage social proof placeholder slot | Form PICK-gated proof strip (no logos) | verify-no-asf | honest-posture |

---

## Wave 3 — Bank Pilot & FRFI (021–030)

| ID | T | L | Plan | Outcome | Verify | Pattern |
|----|---|---|------|---------|--------|---------|
| bank-ui-021 | T1 | A | Bank Pilot proof bar | Shadow / E-23 / export / RPAA fence scan | smoke_bank_grade | frfi-fence |
| bank-ui-022 | T1 | A | RPAA policy callout elevation | `.nf-policy-callout-fence` bank-grade shadow | verify-gtm | regulatory-fence |
| bank-ui-023 | T1 | D | E-23 committee script v1 | 5-min OSFI readout talking points | verify-gtm | e23-mapping |
| bank-ui-024 | T2 | A | Bank Pilot shadow mode badge | Persistent shadow badge in hero | verify-gtm | shadow-only |
| bank-ui-025 | T1 | A | Bank Pilot intake CTA prominence | Primary gate intake above fold | verify-gtm | frfi-fence |
| bank-ui-026 | T2 | D | FRFI diligence appendix outline | Model inventory + vendor AI sections | docs | e23-mapping |
| bank-ui-027 | T1 | A | `nf-frfi` hero width on bank pages | Serif headline max-width for committees | manual | frfi-typography |
| bank-ui-028 | T2 | A | Bank Pilot pipeline active step | Block·Record·Export visual parity | verify-ui-e2e | pipeline-parity |
| bank-ui-029 | T1 | D | Shadow vs enforce sign-off copy | Board sign-off language locked | verify-no-asf | shadow-first |
| bank-ui-030 | T2 | A | Bank Pilot → trust center link path | Cross-link diligence surfaces | verify-gtm | trust-center-grid |

---

## Wave 4 — Trust center & diligence UI (031–040)

| ID | T | L | Plan | Outcome | Verify | Pattern |
|----|---|---|------|---------|--------|---------|
| bank-ui-031 | T1 | A | Trust center framework grid polish | 3-column `.nf-framework-grid` bank-grade | verify-ui-e2e | trust-center-grid |
| bank-ui-032 | T1 | A | Control checkpoint table upgrade | Status badges + honest posture rows | verify-gtm | trust-center-grid |
| bank-ui-033 | T1 | A | Trust center proof bar | Metadata-only · oriented-not-certified scan | verify-gtm | honest-posture |
| bank-ui-034 | T2 | A | `last_verified_at` display stub | Verify timestamp on trust center | plan-with-no-asf | continuous-proof |
| bank-ui-035 | T1 | D | Security FAQ index (20 questions) | Questionnaire deflection doc + anchors | verify-gtm | diligence-shortcut |
| bank-ui-036 | T2 | A | Subprocessor table page | Metadata-only vendor table live-safe | verify-gtm | enterprise-procurement |
| bank-ui-037 | T1 | D | SOC2 claim fence copy audit | No certification claims on www | verify-no-asf | honest-posture |
| bank-ui-038 | T2 | A | Trust center federal section rows | NIST + OMB orientation rows | verify-gtm | federal-framework-map |
| bank-ui-039 | T1 | A | Procurement ZIP link in status strip | One-click diligence from every tier page | verify-ui-e2e | procurement-zip |
| bank-ui-040 | T2 | A | Trust center print CSS | Board-meeting print layout | manual | print-grade |

---

## Wave 5 — Copilot funnel & demo (041–050)

| ID | T | L | Plan | Outcome | Verify | Pattern |
|----|---|---|------|---------|--------|---------|
| bank-ui-041 | T1 | A | 2026 frame on demo / pilot / procurement | All funnel pages `nf-site-2026` + bank-grade | verify-ui-e2e | board-pdf-moment |
| bank-ui-042 | T1 | A | Demo page proof bar + highlight URL block | Committee-scan demo entry | verify-gtm | board-pdf-moment |
| bank-ui-043 | T1 | A | Demo script numbered pipeline UI | 7-step script as visual checklist | verify-gtm | demo-path |
| bank-ui-044 | T2 | A | `make demo-url` CTA on demo hero | Live URL injection when staging set | dev-local | demo-url |
| bank-ui-045 | T1 | A | Pilot page design-partner pricing band | CAD $2K+ sandbox hero | verify-gtm | design-partner |
| bank-ui-046 | T2 | A | Readiness page institutional frame | QuickScan funnel bank-grade shell | verify-gtm | proof-demo |
| bank-ui-047 | T1 | A | Copilot complement strip polish | Registry-vs-receipt on `/copilot/` | verify-gtm | registry-vs-receipt |
| bank-ui-048 | T2 | D | Demo rehearsal checklist UI sync | Checklist mirrors live demo page steps | docs | demo-path |
| bank-ui-049 | T1 | A | Buyer debrief CTA post-demo | Link debrief template from demo footer | verify-gtm | buyer-debrief |
| bank-ui-050 | T2 | A | Playwright demo funnel E2E | demo → evaluate → workspace path green | playwright | ci-buyer-regression |

---

## Wave 6 — Trust Ledger & procurement (051–060)

| ID | T | L | Plan | Outcome | Verify | Pattern |
|----|---|---|------|---------|--------|---------|
| bank-ui-051 | T1 | A | Trust Ledger capabilities list polish | Receipt wedge bullets bank-grade spacing | verify-gtm | receipt-export-wedge |
| bank-ui-052 | T1 | A | Procurement page full institutional frame | Canonical, skip, 2026, bank-grade | verify-ui-e2e | procurement-zip |
| bank-ui-053 | T1 | A | Procurement framework table upgrade | NIST / ISO orientation rows | verify-gtm | procurement-zip |
| bank-ui-054 | T2 | A | ZIP checksum badge on procurement | SHA-256 manifest visible | verify-gtm | tamper-verify |
| bank-ui-055 | T1 | A | TLE sample report bank-grade frame | Sample downloads committee-ready | verify-gtm | receipt-export-wedge |
| bank-ui-056 | T2 | A | Trust Ledger workspace CTA hierarchy | Primary workspace + sample secondary | verify-gtm | receipt-export-wedge |
| bank-ui-057 | T1 | D | Board pack PDF cover spec v2 | E-23 fields on PDF cover block | spec | board-pdf-moment |
| bank-ui-058 | T2 | A | Confidence score hero on result page | Receipt-first evaluate result UX | verify-ui-e2e | confidence-score |
| bank-ui-059 | T1 | A | Tamper FAIL export verify surfaced | Integrity check called out on trust-ledger | verify-gtm | tamper-verify |
| bank-ui-060 | T2 | D | Procurement README orientation v2 | Legal reviewer 1-pager in ZIP | verify-gtm | procurement-zip |

---

## Wave 7 — Partners & MSP channel (061–070)

| ID | T | L | Plan | Outcome | Verify | Pattern |
|----|---|---|------|---------|--------|---------|
| bank-ui-061 | T1 | A | MSP two-tier grid polish | `.nf-msp-tier` featured card emphasis | verify-gtm | msp-two-tier |
| bank-ui-062 | T1 | A | Partners proof metrics row | 90-day SOW · white-label · shadow | verify-gtm | msp-channel-sow |
| bank-ui-063 | T2 | A | Partner intake CTA on partners hub | Primary partner briefing path | verify-gtm | msp-channel-sow |
| bank-ui-064 | T1 | D | 90-day pilot SOW template v2 | MSP attach PDF outline | docs | msp-two-tier |
| bank-ui-065 | T2 | A | White-label board PDF header spec | Optional MSP header on export | spec | msp-two-tier |
| bank-ui-066 | T1 | A | Partners page bank-grade frame | Full CSS stack on `/partners/` | verify-ui-e2e | msp-channel-sow |
| bank-ui-067 | T2 | A | MSP activation dashboard spec card | Partner demo URL + activation UI | verify-gtm | msp-two-tier |
| bank-ui-068 | T1 | D | Partner procurement annex outline | ZIP annex for end-client diligence | verify-gtm | procurement-zip |
| bank-ui-069 | T2 | A | GDAP scope callout on MSP page | Metadata-only connector fence visible | verify-no-asf | metadata-only |
| bank-ui-070 | T2 | H | MSP partner briefing outreach list | Hub tracker — complement not compete | agentic | msp-channel-sow |

---

## Wave 8 — Federal lane (071–080)

| ID | T | L | Plan | Outcome | Verify | Pattern |
|----|---|---|------|---------|--------|---------|
| bank-ui-071 | T1 | A | Federal framework grid bank-grade | AIA · ADM · NIST cards elevated | verify-ui-e2e | federal-framework-map |
| bank-ui-072 | T1 | A | F lane lock callout polish | No clearance / RPAA claims fence | verify-gtm | federal-fence |
| bank-ui-073 | T1 | A | Federal mapping table zebra | Audit-readable status badges | verify-gtm | federal-framework-map |
| bank-ui-074 | T2 | D | AIA impact evidence field spec | TLE export risk tier fields | spec | federal-framework-map |
| bank-ui-075 | T1 | A | Federal intake CTA band | Trust Brief federal vector primary | verify-gtm | federal-lane |
| bank-ui-076 | T2 | A | Federal trust center cross-link | NIST rows link to trust center | verify-gtm | trust-center-grid |
| bank-ui-077 | T1 | D | GovCon questionnaire auto-fill JSON | Machine-readable federal diligence | verify-gtm | questionnaire-deflection |
| bank-ui-078 | T2 | A | OMB orientation row live-safe | Honest planned vs operational badges | verify-gtm | honest-posture |
| bank-ui-079 | T1 | D | Dual-jurisdiction vendor brief | AIA + NIST crosswalk 1-pager | docs | federal-framework-map |
| bank-ui-080 | T2 | A | Federal page print CSS | Committee leave-behind layout | manual | print-grade |

---

## Wave 9 — Console parity & workspace (081–090)

| ID | T | L | Plan | Outcome | Verify | Pattern |
|----|---|---|------|---------|--------|---------|
| bank-ui-081 | T1 | A | Shell.tsx status strip parity | Console matches www status strip | verify-ui-e2e | console-parity |
| bank-ui-082 | T1 | A | WorkflowStepper on all console routes | Block·Record·Export visible | verify-ui-e2e | console-polish |
| bank-ui-083 | T1 | A | MetricStrip on cognitive-dashboard | KPI row: evaluates, blocks, exports | verify-ui-e2e | console-metrics |
| bank-ui-084 | T2 | A | Workspace TLE table v2 | Sortable list + empty states | verify-ui-e2e | receipt-export-wedge |
| bank-ui-085 | T1 | A | Result `[rid]` receipt hero | Decision badge + copy RID + export CTA | verify-ui-e2e | confidence-score |
| bank-ui-086 | T2 | A | Connector `last_sync` column | Evidence freshness visible | dev-local | metadata-index |
| bank-ui-087 | T1 | A | Evaluate → TLE → export browser E2E | Single spec RID continuity | playwright | proof-export |
| bank-ui-088 | T2 | A | Trust ledger detail print CSS | Board PDF print layout in console | manual | board-pdf-moment |
| bank-ui-089 | T1 | A | Console `/console/` static bridge page | Static page links to live console | verify-gtm | console-parity |
| bank-ui-090 | T2 | D | Console design tokens doc | Tailwind ↔ CSS token map | docs | design-system |

---

## Wave 10 — Verify, a11y, GTM proof (091–100)

| ID | T | L | Plan | Outcome | Verify | Pattern |
|----|---|---|------|---------|--------|---------|
| bank-ui-091 | T1 | A | `smoke_bank_grade_html.py` bank-grade markers | P0 pages require bank-grade.css | plan-with-no-asf | regression-gate |
| bank-ui-092 | T1 | A | `verify-ui-e2e` funnel routes | demo + procurement in e2e suite | verify-ui-e2e | regression-gate |
| bank-ui-093 | T1 | A | Playwright 5-route smoke suite | www + console critical paths | playwright | ci-buyer-regression |
| bank-ui-094 | T2 | A | `noetfield-print.css` on tier pages | Board-meeting print on enterprise + bank-pilot | manual | print-grade |
| bank-ui-095 | T1 | D | a11y focus ring audit | Focus-visible on all interactive elements | manual | a11y-baseline |
| bank-ui-096 | T2 | A | Sitemap tier URL expansion | trust-center, federal, bank-pilot in sitemap | verify-gtm | seo-parity |
| bank-ui-097 | T1 | A | Governance meeting demo film v1 | Recorded 5-min board moment artifact | manual | board-pdf-moment |
| bank-ui-098 | T1 | D | Customer #1 proof log template | Meeting date + RID + export hash fields | docs | customer-1-proof |
| bank-ui-099 | T1 | A | `plan-with-no-asf-verify` bank-grade gate | Full bundle green after UI wave | plan-with-no-asf | regression-gate |
| bank-ui-100 | T1 | D | Bank-grade sign-off checklist | Founder Form PICK before promote claims | spec review | form-pick |

---

## Suggested first 3 picks (PLAN WITH NO ASF)

1. **bank-ui-010** — Proof bar on tier pages (extends shipped wave 1)  
2. **bank-ui-041** — Copilot funnel 2026 frame (extends shipped apply script)  
3. **bank-ui-050** — Playwright demo funnel E2E (locks board PDF path)

---

## Related

- [INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md](./INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md)
- [DESIGN_SYSTEM.md](../DESIGN_SYSTEM.md)
- [POSITIONING_CLIENT_SYNTHESIS_v1.md](../diligence/POSITIONING_CLIENT_SYNTHESIS_v1.md)
- [scripts/apply_institutional_2026_frame.py](../../scripts/apply_institutional_2026_frame.py)
