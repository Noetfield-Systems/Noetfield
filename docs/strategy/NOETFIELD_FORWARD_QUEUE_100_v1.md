# Noetfield Forward Queue — 100 Plans (v1)

**Status:** Research-derived forward queue · **draft picks** — Form PICK before implement  
**Path:** `docs/strategy/NOETFIELD_FORWARD_QUEUE_100_v1.md`  
**Updated:** 2026-06-12  
**Grounding:** [MARKET_ANALYSIS_2026_LOCKED_v1.md](./MARKET_ANALYSIS_2026_LOCKED_v1.md) · [NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md](../architecture/NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md)  
**ID namespace:** `ship-fwd-060` … `ship-fwd-159` (maps to future GTM iterations post–iter 19)

**Lane key:** **A** = NF-CLOUD disk · **H** = Hub/agentic only · **D** = docs/spec only

---

## Wave 1 — Agent 365 complement positioning (FQ-001–010)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-060 | 001 | T1 | D | Agent 365 complement one-pager | www-safe “registry vs receipt” narrative | verify-gtm | KPMG/Agent 365 GA |
| ship-fwd-061 | 002 | T1 | D | Purview parity checklist page | Map Noetfield controls to Purview capabilities | plan-with-no-asf | Microsoft Purview docs |
| ship-fwd-062 | 003 | T1 | A | Agent registry gap verify script | Assert procurement cites Agent 365 complement | verify-gtm-ops | CAF agent governance |
| ship-fwd-063 | 004 | T2 | D | CISO brief: fleet governance 2026 | PDF outline for design partner outreach | manual | 72%/21% gap |
| ship-fwd-064 | 005 | T1 | A | `/copilot/governance/` Agent 365 section | Buyer page block without competing MS | verify-gtm | Agent 365 GA |
| ship-fwd-065 | 006 | T2 | D | Entra agent identity crosswalk doc | Internal map Entra agent ID → RID | docs lint | Microsoft Entra AI |
| ship-fwd-066 | 007 | T1 | A | Connector manifest Agent 365 stub row | `last_sync` placeholder in connectors API | pytest | CAF registry |
| ship-fwd-067 | 008 | T2 | H | Outreach list: M365 admins post-GA | Hub tracker row template | agentic | Agent 365 GA |
| ship-fwd-068 | 009 | T1 | D | Competitive vs Fiddler positioning | Internal battlecard — receipt export | confidentiality | Fiddler control plane |
| ship-fwd-069 | 010 | T1 | A | Homepage meta refresh Agent 365 era | SEO description governance execution | verify-gtm | Market inversion |

---

## Wave 2 — OSFI E-23 & Canada FRFI (FQ-011–020)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-070 | 011 | T1 | D | OSFI E-23 mapping appendix | Map TLE export to model inventory fields | spec review | OSFI E-23 May 2027 |
| ship-fwd-071 | 012 | T1 | D | Bank Pilot E-23 shadow narrative | `/bank-pilot/` OSFI-aligned copy | verify-gtm | OSFI backgrounder |
| ship-fwd-072 | 013 | T2 | A | Model inventory export stub API | `GET /api/v1/models/inventory` mock | pytest | E-23 inventory |
| ship-fwd-073 | 014 | T1 | D | FRFI buyer deck outline (6 slides) | Trust Brief upsell path | manual | Blakes E-23 |
| ship-fwd-074 | 015 | T2 | D | AI/ML model lifecycle diagram | Architecture doc for enterprise | docs | Crisil E-23 report |
| ship-fwd-075 | 016 | T1 | A | Verify bank-pilot no RPAA claims | Coherence guard on bank-pilot HTML | verify-no-asf | PROJECT_BOUNDARIES |
| ship-fwd-076 | 017 | T2 | H | Outreach: FRFI model risk leads | Agentic list BC/Ontario | Hub | E-23 runway |
| ship-fwd-077 | 018 | T1 | D | TrustField handoff card E-23 | When to route MSB execution | docs | dual-brand matrix |
| ship-fwd-078 | 019 | T2 | A | TLE export OSFI field template | PDF cover sheet model ID + RID | tle-smoke | E-23 Appendix 1 |
| ship-fwd-079 | 020 | T1 | D | Canada channel one-pager update | BC AI + E-23 timing | verify-gtm | canada-partner-gtm |

---

## Wave 3 — EU AI Act evidence & logging (FQ-021–030)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-080 | 021 | T1 | D | EU Art. 12/19 mapping doc | Pre-execution log = TLE spine | spec review | EU Omnibus Dec 2027 |
| ship-fwd-081 | 022 | T1 | A | Tamper FAIL export verify hardening | Export integrity gate in verify | plan-with-no-asf | DeepInspect fail-closed |
| ship-fwd-082 | 023 | T2 | D | 6-month retention policy doc | Ops runbook alignment | docs | Art. 19 retention |
| ship-fwd-083 | 024 | T1 | D | Procurement EU annex paragraph | Optional diligence section | verify-gtm | Gibson Dunn |
| ship-fwd-084 | 025 | T2 | A | Log write fail-closed test | API rejects evaluate if audit write fails | pytest | Art. 12 architecture |
| ship-fwd-085 | 026 | T1 | D | ISO 42001 crosswalk table | Map TLE to ISO controls | spec | Gartner frameworks |
| ship-fwd-086 | 027 | T2 | D | NIST AI RMF tier mapping | GTM appendix for US subsidiaries | docs | MarketsandMarkets |
| ship-fwd-087 | 028 | T1 | A | Behavioral log export endpoint stub | `GET /api/v1/events/replay` narrative link | tle-smoke | Art. 12 query |
| ship-fwd-088 | 029 | T2 | H | Outreach: EU ops Canadian HQs | Agentic AB/ON multinationals | Hub | EU deadline |
| ship-fwd-089 | 030 | T1 | D | Competitive vs Gateplex EU PDF | Internal — compliance export | confidentiality | Gateplex EU |

---

## Wave 4 — Copilot stall & mid-market SME (FQ-031–040)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-090 | 031 | T1 | D | “Past the stall” whitepaper summary | `/copilot/readiness/` cite | verify-gtm | QueryNow |
| ship-fwd-091 | 032 | T1 | A | QuickScan scoring rubric v2 | 5-dimension readiness score | verify-gtm | Nexigen readiness |
| ship-fwd-092 | 033 | T1 | A | Permission debt checklist ol | HTML checklist oversharing | verify-gtm | Stoneridge 65%/25% |
| ship-fwd-093 | 034 | T2 | D | Ring deployment playbook | 20–50 user pilot guide | docs | QueryNow sprints |
| ship-fwd-094 | 035 | T1 | A | Pilot success metrics strip | `/copilot/pilot/` KPI block | verify-gtm | Forrester TEI |
| ship-fwd-095 | 036 | T2 | D | Copilot Product Owner RACI | SME governance lightweight | docs | Perez SMB playbook |
| ship-fwd-096 | 037 | T1 | H | Design partner outreach wave 2 | 10 CIO contacts agentic | Hub | W3 CAD ≥2K |
| ship-fwd-097 | 038 | T1 | A | Demo script “governance meeting” | 5-min board PDF moment | copilot-pilot-e2e | SME blueprint |
| ship-fwd-098 | 039 | T2 | D | Training vs governance ROI note | Match $1 training:$1 license | docs | QueryNow ratio |
| ship-fwd-099 | 040 | T1 | A | `/copilot/quickscan/` step verify | All steps return 200 | verify-gtm | SME journey |

---

## Wave 5 — Pre-execution & receipt spine (FQ-041–050)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-100 | 041 | T1 | A | BLOCK path audit receipt test | REJECT generates signed receipt | pytest | Fuzentry pre-exec |
| ship-fwd-101 | 042 | T1 | A | ALLOW path TLE auto-draft | ALLOW → TLE draft in one hop | tle-smoke | Olympus policy |
| ship-fwd-102 | 043 | T2 | A | Confidence score calibration doc | Threshold guidance in API | docs+pytest | TLE blueprint |
| ship-fwd-103 | 044 | T1 | A | RID continuity cross-service | Same RID evaluate→TLE→export | e2e | Airia execution trail |
| ship-fwd-104 | 045 | T2 | D | Observer mode spec | Evidence-only before enforce | spec | Fuzentry observer |
| ship-fwd-105 | 046 | T1 | A | Export tamper regression test | Drifted PDF fails verify | pytest | SME blueprint |
| ship-fwd-106 | 047 | T2 | A | Multi-approver E-23 scenario | 2-approver path documented | pytest | W78 multi-approve |
| ship-fwd-107 | 048 | T1 | D | Pre-execution glossary www | `/trust-ledger/` terms | verify-gtm | Category education |
| ship-fwd-108 | 049 | T2 | A | Webhook receipt on BLOCK | Telegram/webhook fires on REJECT | pytest | services/governance |
| ship-fwd-109 | 050 | T1 | A | Board pack PDF cover E-23 fields | Model name + risk tier optional | manual | E-23 inventory |

---

## Wave 6 — Procurement & technical diligence (FQ-051–060)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-110 | 051 | T1 | A | OpenAPI status field `openapi` path | `/api/status` documents schema | plan-with-no-asf | iter 20 seed |
| ship-fwd-111 | 052 | T1 | A | Procurement ZIP manifest v2 | File list + checksums in ZIP | verify-gtm | buyer diligence |
| ship-fwd-112 | 053 | T1 | A | Security questionnaire auto-answers | `docs/copilot/SECURITY_FAQ.md` | verify-gtm | procurement |
| ship-fwd-113 | 054 | T2 | A | SOC2-ready control mapping draft | Internal — not claim SOC2 | confidentiality | enterprise buyers |
| ship-fwd-114 | 055 | T1 | A | README www 200 verify governance | services/governance README link | plan-with-no-asf | iter 20 060 |
| ship-fwd-115 | 056 | T2 | D | DPA template outline | Data processing — metadata only | legal draft | Purview metadata |
| ship-fwd-116 | 057 | T1 | A | Control catalog ↔ API parity | Each control maps to test | pytest | copilot-control-catalog |
| ship-fwd-117 | 058 | T2 | D | Pen test scope doc | Shadow pilot boundaries | docs | Bank Pilot |
| ship-fwd-118 | 059 | T1 | A | Trust-brief parity all buyer pages | 4-page loop in verify | verify-no-asf | shipped pattern |
| ship-fwd-119 | 060 | T1 | D | Procurement evaluator guide | How to read TLE samples | verify-gtm | SME provider |

---

## Wave 7 — TLE, evidence & connectors (FQ-061–070)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-120 | 061 | T2 | A | Purview connector sync demo | `last_sync` visible in UI | dev-local | Evidence index |
| ship-fwd-121 | 062 | T2 | A | Entra agent manifest v2 | Agent sponsor field | pytest | Agent 365 |
| ship-fwd-122 | 063 | T1 | A | TLE sample pack refresh | 3 industry samples updated | verify-gtm | positioning |
| ship-fwd-123 | 064 | T2 | A | Evidence hash chain doc | HMAC chain spec public-safe | spec | EU tamper |
| ship-fwd-124 | 065 | T1 | A | Board pack template v2 | Institutional print CSS | manual | STRATEGIC_LOCK |
| ship-fwd-125 | 066 | T2 | A | Connector health dashboard stub | `/workspace/` connector status | ui e2e | SME module map |
| ship-fwd-126 | 067 | T1 | D | Metadata-only evidence FAQ | No content hoarding explainer | verify-gtm | PRODUCT_TRUTH |
| ship-fwd-127 | 068 | T2 | A | TLE export JSON schema publish | `tle-v1.schema.yaml` linked | tle-smoke | diligence |
| ship-fwd-128 | 069 | T2 | A | Evidence index search API | `GET /api/v1/evidence?q=` | pytest | shipped W56 |
| ship-fwd-129 | 070 | T1 | D | Drift blueprints buyer index | Link handbook from copilot | verify-gtm | references |

---

## Wave 8 — Site, GTM & channel (FQ-071–080)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-130 | 071 | T1 | A | Enterprise page E-23 callout | One factual line only | verify-gtm | Canada FRFI |
| ship-fwd-131 | 072 | T1 | A | Homepage social proof strip | Design partner slot placeholder | verify-gtm | W3 proof |
| ship-fwd-132 | 073 | T2 | H | BC AI channel outreach batch | Agentic wave per registry | Hub | channel-outreach |
| ship-fwd-133 | 074 | T1 | D | Partner MSP enablement kit | `/partners/` MSP section | verify-gtm | mid-market |
| ship-fwd-134 | 075 | T2 | A | Staging demo env banner | NF_STAGING_URL wired | staging-smoke | demo film |
| ship-fwd-135 | 076 | T1 | D | GTM 60-day refresh post-research | Update locked GTM fences | spec review | MARKET_ANALYSIS |
| ship-fwd-136 | 077 | T1 | A | Footer Governance API discoverability | API link parity | verify-gtm | public-surface-map |
| ship-fwd-137 | 078 | T2 | D | Trust Brief upsell from pilot | SOW path $10K diagnostic | docs | OFFERINGS |
| ship-fwd-138 | 079 | T1 | H | n8n Apollo/HubSpot glue spec | Founder approve workflow doc | agentic | W3 integration |
| ship-fwd-139 | 080 | T1 | A | `make demo-url` CI artifact | Demo URL in cursor-reply | plan-with-no-asf | outreach 026 |

---

## Wave 9 — Product hardening & verify (FQ-081–090)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-140 | 081 | T1 | A | Dev/prod stack convergence plan | Single OpenAPI source | spec | PLATFORM_BLUEPRINT |
| ship-fwd-141 | 082 | T2 | A | Governance console RBAC test suite | Workspace roles pytest | pytest | console |
| ship-fwd-142 | 083 | T1 | A | Coherence verify forward queue gate | FAIL if FQ T1 done missing manifest | verify-no-asf | audit discipline |
| ship-fwd-143 | 084 | T2 | A | UI e2e flaky dashboard fix doc | NF_DEV_FORCE_DASHBOARD_BUILD | dev-local | ops note |
| ship-fwd-144 | 085 | T1 | A | Intake email audit CI | `audit_intake_email.py` in ship-verify | make ship-verify | STRATEGIC_LOCK |
| ship-fwd-145 | 086 | T2 | A | M365 OAuth stub → design doc | Production OAuth gated ASF | spec | blueprint honest |
| ship-fwd-146 | 087 | T1 | A | Public chat guardrail test | Public chat blocks PII patterns | pytest | SME AI domain |
| ship-fwd-147 | 088 | T2 | D | Incident response AI playbook | `.cursor/incidents` template | docs | agentic ops |
| ship-fwd-148 | 089 | T1 | A | SHIP_DONE_MAP forward queue sync | sync-prompt-pack FQ patterns | sync script | registry |
| ship-fwd-149 | 090 | T2 | A | Load test evaluate endpoint stub | p95 &lt;500ms local | perf | enterprise SLA |

---

## Wave 10 — Strategic & Stage 2 seeds (FQ-091–100)

| ID | FQ | T | L | Plan | Outcome | Verify | Research driver |
|----|----|---|---|------|---------|--------|-----------------|
| ship-fwd-150 | 091 | T3 | D | OEM/embed path memo (Stage 2+) | Internal only — not W3 GTM | confidentiality | unified engine |
| ship-fwd-151 | 092 | T2 | D | TrustField receipt reuse playbook | Same demo, MSB wedge copy | docs | second earner |
| ship-fwd-152 | 093 | T1 | D | Investor one-pager 2026 | Engine powers NF — not SKU | Form PICK | founder line |
| ship-fwd-153 | 094 | T2 | D | Knowledge/RAG evidence-first spec | Phase 3.5 gate | spec | SME design Lane A |
| ship-fwd-154 | 095 | T1 | H | Film W1 demo script final | Founder Hub approve shoot | agentic | W1 proof |
| ship-fwd-155 | 096 | T1 | A | W3 economic signal verify | Procurement cites CAD $2K | verify-gtm | ENFORCEMENT-6MO |
| ship-fwd-156 | 097 | T2 | D | Forrester/IDC citation policy | No unverified stats on www | verify-gtm | research integrity |
| ship-fwd-157 | 098 | T1 | D | SSOT_INDEX forward queue link | Index points here | plan-with-no-asf | coherence |
| ship-fwd-158 | 099 | T2 | A | Eleventh-audit iter 20–29 seed | Next 3 picks from FQ-001–003 | GTM_NEXT | queue hygiene |
| ship-fwd-159 | 100 | T1 | D | Annual license path outline | Post-pilot pricing hypothesis | Form PICK | GO_FORWARD_NOW |

---

## Priority tiers

| Tier | Meaning | Count |
|------|---------|-------|
| **T1** | Revenue or diligence inside 90 days | 52 |
| **T2** | Hardening / enablement 90–180 days | 42 |
| **T3** | Stage 2+ / confidential strategy | 6 |

---

## Recommended next 3 picks (iter 20+)

After current iter 19 (057–059) ships:

1. **ship-fwd-060** — Agent 365 complement one-pager (FQ-001)  
2. **ship-fwd-081** — EU tamper FAIL export hardening (FQ-022)  
3. **ship-fwd-090** — QuickScan scoring rubric v2 (FQ-032)  

---

## Law fences (all 100 plans)

- **No** payment rails · custody · NO-CC · cloud deploy hero  
- **No** SourceA disk edits from NF chat  
- **No** TrustField/VIRLUX implementation in Noetfield repo  
- **H** rows = Hub/agentic only — NF-CLOUD maintains copy, not send  
- **Promote** any locked spec to www only after **Form PICK**  

---

## Related

- [NOETFIELD_FORWARD_QUEUE_100_v2.md](./NOETFIELD_FORWARD_QUEUE_100_v2.md) — FQ-101–200 upgraded (trust center, Playwright, institutional UI)  
- [MARKET_ANALYSIS_2026_LOCKED_v1.md](./MARKET_ANALYSIS_2026_LOCKED_v1.md)  
- [GTM_NEXT.md](../ops/plans/no-asf/GTM_NEXT.md)  
- [SSOT_INDEX.md](../SSOT_INDEX.md)
