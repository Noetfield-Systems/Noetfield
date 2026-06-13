# UI tier-1 — 10 next big upgrades (LOCKED v1)

| Field | Value |
|-------|--------|
| Agent tag | `NF-CLOUD-AGENT` |
| Updated | 2026-06-13 |
| Status | Strategic target list — **UI is P0** |
| Parent | [INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md](./INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md) (100 items) |
| Packaging | [PACKAGING_TIER_SANDBOX_LOCKED_v1.md](./PACKAGING_TIER_SANDBOX_LOCKED_v1.md) |

**Purpose:** Condense the 100-plan into **10 shippable upgrades** that move Noetfield www + console UI from credible institutional v4 to **world-class tier-1** — the bar set by top identity/compliance SaaS (self-serve trial, async product demo, published tiers, in-product trust center, browser CI).

**Bottleneck unchanged:** Customer #1 board PDF in a real governance meeting. UI upgrades **accelerate trial → proof**, they do not replace proof.

---

## Current UI baseline (audit 2026-06-13)

| Strength | Gap |
|----------|-----|
| Institutional v4 homepage (trust-hero + TLE receipt card) | **Two-speed UI** — quickscan, FAQ, gate/intake, sample-report off v4 stack |
| Bank-grade CSS on 15 GTM routes | Verification is **grep/curl**, not browser layout |
| Packaging tiers shipped (Starter · Sandbox · Production) | Trial is **copy-first** — no in-product meter or onboarding |
| Console parity (WorkflowStepper, MetricStrip, confidence hero) | Copilot hub has **4 hero buttons** (v4 discipline is ≤2) |
| `verify-ui-visual-e2e` gates homepage v4 | Visual gate covers **5 routes only**, not full funnel |

**Doc ladder:** `INSTITUTIONAL_SITE_PLAN (10)` → `INSTITUTIONAL_BANK_GRADE_100` → **this file** → `MARKET_SUCCESS_1000`

---

## The 10 upgrades (priority order)

### 1. Unified Design System v5 — one visual language everywhere

**Tier-1 bar:** Single token source; www and console feel like one product, not two repos stitched together.

| Today | Target |
|-------|--------|
| 14 layered CSS files; Tailwind duplicates tokens in `governance-console/frontend/` | Shared token package: colors, type scale, spacing, elevation, focus rings |
| `DESIGN_SYSTEM.md` stops at v3 | v5 load order: tokens → shell → 2026 → bank-grade → v4 → print |

**Deliverables**

- `docs/DESIGN_SYSTEM.md` v5 rewrite (bank-ui-006)
- `assets/noetfield-tokens.css` — export CSS variables consumed by console `tailwind.config.ts` (bank-ui-090)
- `scripts/verify-design-system-parity.sh` — token hex parity www ↔ console

**Verify:** `make verify-gtm` · token parity script in `plan-with-no-asf-verify`

**Maps to:** bank-ui-006, bank-ui-009, bank-ui-090

---

### 2. Full-stack frame unification — kill the two-speed site

**Tier-1 bar:** Every buyer touchpoint uses the same institutional shell; no funnel feels “older” or off-brand.

| Off-stack today | Must frame |
|-----------------|------------|
| `copilot/quickscan/**` (9 pages) | v4 + bank-grade + 2026 meta |
| `gate/intake/index.html` | Trial vector is visually first-class |
| `faq/index.html`, `trust-ledger/sample-report/` | Same proof bar + pipeline strip |

**Deliverables**

- `scripts/apply_institutional_2026_frame.py` v2 — extend `TIER_PAGES` to quickscan, gate, FAQ, sample-report (bank-ui-007, bank-ui-046)
- `scripts/verify-ui-frame-parity.sh` — all public HTML has `nf-site-2026` + `noetfield-bank-grade.css`
- Hero CTA discipline on `/copilot/` — **≤2 primary buttons**, rest in links row (matches homepage v4 gate)

**Verify:** `verify-ui-visual-e2e.sh` extended to 14+ routes · `smoke_bank_grade_html.py`

**Maps to:** bank-ui-007, bank-ui-046, bank-ui-055, bank-ui-008

---

### 3. Productized trial UX — signup to sandbox without a sales call

**Tier-1 bar:** Starter tier is **in-product**, not email-only. Buyer sees trial state, limits, and next step inside the console.

| Today | Target |
|-------|--------|
| `/copilot/trial/` + intake email | Guided onboarding wizard in console |
| Copy: 14-day · 50 checks | **Live meter** in `Shell.tsx` — days left, evaluates used |
| No tier badge | Starter / Sandbox / Production pill on every console route |

**Deliverables**

- `governance-console/frontend/components/TrialBanner.tsx` — tier + usage counter
- `governance-console/frontend/components/OnboardingStepper.tsx` — 5-step async demo checklist synced with `/copilot/demo/`
- `gate/intake/index.html` — trial signup form UI (routes to provision, not wall of text)
- Ship: `ship-trial-intake-automation-063`, `ship-trial-console-meter-066` (new)

**Verify:** `verify-packaging-tier.sh` + new `verify-trial-console-ui.sh` (banner + meter strings)

**Maps to:** PACKAGING PKG-01–03 · GTM_NEXT iter 21

---

### 4. Playwright buyer journey CI — browser truth, not grep truth

**Tier-1 bar:** Layout regressions (hero button count, broken export CTAs, mobile nav) fail CI before merge.

| Today | Target |
|-------|--------|
| `verify-ui-e2e.sh` = curl + string match | Playwright runs real Chromium |
| No `playwright.config.ts` | `make verify-playwright` in ship bundle |

**Deliverables**

- `governance-console/playwright.config.ts`
- `e2e/buyer-journey.spec.ts` — `/copilot/demo/` → `/evaluate` → POST → `/result/{rid}` → `/workspace` → export links visible
- `e2e/packaging-trial.spec.ts` — `/copilot/trial/` → console paths · tier table visible
- Optional: screenshot diff on homepage trust-hero (1 golden file)

**Verify:** `bank-ui-050`, `bank-ui-093`–`099`, `ship-fwd-170`–`176`

**Maps to:** BANK_GRADE_CHECKLIST Pillar 5 (Playwright open item)

---

### 5. Trust center as a live product surface — not a static brochure

**Tier-1 bar:** Diligence reviewers get freshness, subprocessors, and questionnaire deflection without emailing ops.

| Today | Target |
|-------|--------|
| Static framework grid | `last_verified_at` pill per control row |
| No subprocessor page | Metadata-only subprocessor table (live-safe) |
| FAQ scattered | Security FAQ index (20 Q) with anchor deep-links |

**Deliverables**

- `trust-center/index.html` — control badges v2, freshness strip (bank-ui-032–034)
- `trust-center/subprocessors/index.html` (new) — bank-ui-036
- `docs/ops/SECURITY_FAQ_INDEX_v1.md` wired to trust center anchors (bank-ui-035)
- Status strip on all tier pages → procurement ZIP one-click (bank-ui-039)

**Verify:** `verify-gtm-ops-docs.sh` · trust-center string gates

**Maps to:** bank-ui-031–040 · Wave 4 of 100-plan

---

### 6. Procurement-grade interactive diligence UI

**Tier-1 bar:** Legal and vendor risk teams can sort, filter, and verify integrity without opening a ZIP blind.

| Today | Target |
|-------|--------|
| Procurement page is strong copy | Interactive framework table (sortable rows) |
| ZIP mentioned | **SHA-256 checksum badge** visible pre-download |
| OpenAPI link | Self-serve API explorer block on `/copilot/trial/` (ship-openapi-self-serve-doc-065)

**Deliverables**

- `copilot/procurement/index.html` — full v4 frame + framework table v2 (bank-ui-052–053)
- Checksum manifest UI component `.nf-checksum-badge` (bank-ui-054)
- Client-side table sort on procurement controls (ship-fwd-178 pattern)

**Verify:** `procurement-pack-e2e.sh` · `verify-packaging-tier.sh`

**Maps to:** bank-ui-052–054, ship-openapi-self-serve-doc-065

---

### 7. Governance console enterprise shell — workspace as the product

**Tier-1 bar:** Console is where buyers **live** during pilot — sortable ledger, empty states, receipt-first result, no legacy HTML split.

| Today | Target |
|-------|--------|
| Workspace table not sortable | Column sort + filter on TLE list |
| Inline empty divs | Shared `EmptyState` everywhere |
| Dual console (`governance-console-v1.html` + Next) | Retire v1 HTML; single console story |

**Deliverables**

- `workspace/page.tsx` — sortable table v2, `EmptyState` (bank-ui-084, ship-fwd-183)
- `result/[rid]/page.tsx` — receipt hero polish, confidence + RID copy UX (bank-ui-058, bank-ui-085)
- Deprecate `governance-console-v1.html` from smoke path (bank-ui-089, ship-fwd-188)
- `auditor-export` dedicated view — JSON + bundle download UX (mr-0121)

**Verify:** `verify-ui-e2e.sh` (chunks) · `copilot-pilot-e2e.sh`

**Maps to:** bank-ui-081–089 · Wave 9 of 100-plan

---

### 8. Async demo guided stepper — product demo, not a markdown script

**Tier-1 bar:** Demo is a **guided async experience** — progress tracked, deep-linked to console, resumable.

| Today | Target |
|-------|--------|
| Demo page = numbered `<ol>` | Visual 7-step stepper with completion state |
| Rehearsal checklist is separate doc | Checklist UI mirrors live demo page 1:1 |
| Staging URL hidden unless injected | `make demo-url` CTA block always visible when env set |

**Deliverables**

- `copilot/demo/index.html` — `.nf-demo-stepper` component (bank-ui-043)
- Sync with `docs/ops/DEMO_REHEARSAL_CHECKLIST_v1.md` (bank-ui-048)
- Console `OnboardingStepper` shares step IDs with www demo (upgrade #3)
- Live demo URL hero block (bank-ui-044)

**Verify:** `verify-copilot-demo-links.sh` · stepper DOM in `verify-ui-visual-e2e.sh`

**Maps to:** bank-ui-042–049 · packaging async demo narrative

---

### 9. Visual regression + responsive gates — institutional on every device

**Tier-1 bar:** Board members open the site on iPad in a committee room; nothing breaks, nothing overlaps.

| Today | Target |
|-------|--------|
| `verify-ui-visual-e2e` = homepage only | v4 structure on all tier + funnel routes |
| Device lab checklist open in BANK_GRADE_CHECKLIST | Automated viewport smoke at 320 / 768 / 1280 |
| Skip links partial | Skip link + focus ring on every public route (bank-ui-005) |

**Deliverables**

- Extend `verify-ui-visual-e2e.sh` — trust-hero OR proof-bar rules per route archetype
- `scripts/verify-responsive-smoke.sh` — Playwright viewports or puppeteer heights
- `assets/noetfield-print.css` wired on enterprise, bank-pilot, trust-center (bank-ui-040, bank-ui-080)
- a11y: `axe-core` pass on P0 routes in Playwright

**Verify:** BANK_GRADE_CHECKLIST Pillar 1 device lab · `plan-with-no-asf-verify`

**Maps to:** bank-ui-005, bank-ui-040, bank-ui-080, bank-ui-095–099

---

### 10. Agentic production tier UI — show autonomous execution, not “AI assist”

**Tier-1 bar:** Production-tier buyers see **agents executing** investigate → triage → draft → low-risk act — with audit trail visible in UI.

| Today | Target |
|-------|--------|
| Agentic copy on www only | Production mode badge + workflow run panel in console |
| No agent run history | Timeline: agent action → human gate → TLE recorded |
| Same console for all tiers | Production tier unlocks autonomous workflow UI (shadow stays manual) |

**Deliverables**

- `governance-console/frontend/components/AgentWorkflowPanel.tsx` — run status, last action, escalation
- `governance-console/frontend/components/ProductionModeBadge.tsx` — tier indicator in Shell
- `enterprise/index.html` + `/copilot/trial/` — link to live workflow panel in console
- Architecture: [AGENTIC_AUTONOMOUS_WORKFLOWS_LOCKED_v1.md](../architecture/AGENTIC_AUTONOMOUS_WORKFLOWS_LOCKED_v1.md)

**Verify:** production tier strings + panel mount in `verify-ui-e2e.sh` (console HTML)

**Maps to:** ship-agentic-autonomous-copy-062 (extend) · new `ship-agentic-console-panel-067`

---

## Pick order for agents (PLAN WITH NO ASF)

When founder says **tier-1 UI sprint**, pick **≤3** per iter in this order:

| Iter focus | Pick from upgrades |
|------------|-------------------|
| **Sprint A** | #2 Frame unification + #3 Trial UX |
| **Sprint B** | #4 Playwright CI + #8 Async demo stepper |
| **Sprint C** | #5 Trust center + #6 Procurement interactive |
| **Sprint D** | #7 Console shell + #1 Design system v5 |
| **Sprint E** | #9 Responsive/visual + #10 Agentic production UI |

**Never pick three infra-only tasks** — each iter must move a **buyer-visible** surface.

---

## Success metrics (tier-1 definition)

| Metric | Tier-1 target |
|--------|---------------|
| Frame parity | 100% public HTML on v4/bank-grade stack |
| Browser CI | Playwright buyer journey green on every PR |
| Trial UX | In-console meter + onboarding stepper live |
| Trust center | Freshness + subprocessor + FAQ index shipped |
| Console | Single Next console; v1 HTML retired |
| Visual gate | Extended visual e2e on ≥14 routes |
| Responsive | 320/768/1280 smoke pass on P0 pages |
| CTA discipline | ≤2 primary hero buttons on all tier pages |
| Packaging | Starter → Sandbox → Production visible in product, not copy-only |
| Agentic UI | Production workflow panel in console |

---

## Verify bundle (after upgrades ship)

```bash
./scripts/verify-ui-visual-e2e.sh      # extended routes
./scripts/verify-packaging-tier.sh      # packaging copy
./scripts/verify-ui-e2e.sh              # content + console chunks
make verify-playwright                    # browser journey (new)
./scripts/plan-with-no-asf-verify.sh      # full bundle
```

---

## Related

| Doc | Role |
|-----|------|
| [INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md](./INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md) | Full 100-item backlog |
| [INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md](./INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md) | Original 10-step site plan |
| [BANK_GRADE_CHECKLIST.md](../BANK_GRADE_CHECKLIST.md) | Pillar gates |
| [PACKAGING_TIER_SANDBOX_LOCKED_v1.md](./PACKAGING_TIER_SANDBOX_LOCKED_v1.md) | Trial/sandbox tiers |
| [PAGE_AUTHORITY_MAP.md](../site/PAGE_AUTHORITY_MAP.md) | URL ownership |
