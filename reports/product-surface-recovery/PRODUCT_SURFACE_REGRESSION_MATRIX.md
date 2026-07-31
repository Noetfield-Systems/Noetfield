# PRODUCT_SURFACE_REGRESSION_MATRIX

Release: NOETFIELD_PRODUCT_SURFACE_RECOVERY_V1
Baseline (pre-regression): 53328256184f136a0fccde7312220e581bf059c2 (2026-07-29, PR #200)
Reduction began: f08ef6c24cc34bf164f891723fc9eaa0a3fbbe24 (NOETFIELD_DOMAIN_CANONICAL_V2)
Current main at audit: 679f81291c06bbc1ac3022b8eb1a48a50e776d07
Recovery branch: recovery/noetfield-product-surface-v1

## Headline findings

1. No route files were deleted by the canonicalization; the damage was
   content collapse plus orphaning. The homepage lost 73% of its content
   (44,556 B to 12,239 B) and Runways lost 77% (28,468 B to 6,516 B).
2. Rich product routes (deterministic-api, copilot, start, research-packs,
   faq) survived byte-intact but were delisted: dropped from the sitemap
   (deterministic-api, faq), removed from all navigation, and
   deterministic-api was marked noindex.
3. The live app at app.noetfield.com (public goal-intake flow, headline
   "Give Noetfield a goal.") was not linked from anywhere on www.
4. The sitemap was never regenerated for canonical v2: /system/,
   /applications/, /applications/trustfield/, /public-interest/ are live
   but absent from sitemap.xml (P8 item).

## Matrix

| Route / surface | Pre-canonical | Current main | Capability | Backend dependency | Decision | Maturity | Destination |
| --- | --- | --- | --- | --- | --- | --- | --- |
| / | 44.5 KB product homepage: hero, comparison, architecture, interactive walkthrough, dark receipt, runways, commissioning, readiness, ecosystem | 12.2 KB editorial shell | Product proposition | static | RESTORED: product-first homepage per P2 with app hero, walkthrough, product map, truthful copy | live | / |
| app.noetfield.com | linked as "Deploy" | not linked at all | Agentic workspace: projects, goals, Front Person, tasks, artifacts, previews, revisions, receipts | NOETFIELD-RUNWAY repo: sites/company-new + apps/project-runtime-control-plane (staging worker noetfield-runway-runtime-api-staging) | RESTORED: nav item, CTA, hero screenshot, app section | live (client-zero commissioning) | https://app.noetfield.com/ |
| Signed-in workspace IA | n/a (app repo) | n/a | project list, task state, documents, preview, revision, deployment, receipts | NOETFIELD-RUNWAY repo | AUDITED, NOT EDITED: app runtime is not owned by the www repo; public explanation shipped with honest maturity labels; signed-in redesign is a separate NOETFIELD-RUNWAY release | client-zero | app repo |
| /runways/ | 28.5 KB catalogue: 3 featured + 12 catalogue paths + engagement | 6.5 KB, three paragraphs | Workflow catalogue | static + decision-brief dispatch API | RESTORED: full catalogue with LIVE / INTERNAL·DEMONSTRATED / DEVELOPER PREVIEW / PLANNED labels, wedge first | live | /runways/ |
| /runways/decision-brief/ | live demo with form | unchanged | Public sample run | api/runway/jobs.js (HMAC dispatch, budget-capped) | KEPT | live public sample | /runways/decision-brief/ |
| /deterministic-api/ | 16 KB developer page | intact but noindex + delisted | Developer/API surface | api.noetfield.com (tenant-gated; public POST /v1/chat/completions returns 404 unauthenticated) + platform workspace | RESTORED: re-indexed, in nav, reference section added (request/response/receipt shapes marked SHAPE ONLY, error and safe-stop behavior, limitations) | developer preview | /deterministic-api/ |
| /motors/ | 23.6 KB technical page | intact, reachable via System page only | AI Motors architecture | static | RESTORED to nav | live | /motors/ |
| /applications/trustfield/ | n/a (added later) | canonical product page | TrustField product boundary | trustfield.ca | KEPT, in nav | live, synthetic public demo | /applications/trustfield/ |
| /proof/ | evidence register | intact | Receipts and evidence | static + proof JSON | KEPT, in nav | live | /proof/ |
| /system/ | n/a | canonical v2 overview | Product/system overview | static | KEPT as nav "Product" | live | /system/ |
| /applications/ | n/a | canonical v2 inventory | Application inventory | static | KEPT, linked from product map + footer | live | /applications/ |
| /public-interest/ | n/a | canonical program page | SFF program | static | MOVED per P1: Company submenu + footer + direct route; removed from primary nav | live | /public-interest/ |
| /investors/, /investors/diligence/ | live | live | Ecosystem + diligence workflow | static | KEPT; diligence recorded as internal-demonstrated in catalogue | live / internal | unchanged |
| /contact/ + /gate/intake/ | live intake | live | Contact + gated intake | intake email lane | KEPT; commission-workflow topic restored to the select | live | unchanged |
| /research-packs/ | live lane | live, orphaned | Research pack runs | static | RELINKED from homepage examples; catalogue entry | developer preview | /research-packs/ |
| /start/, /copilot/, /faq/, /work-with-us/, /partners/ | live | live, orphaned/demoted | Legacy lanes | static | DEFERRED to P8 (migrate / 301 / archive+noindex after preview approval); recorded in manifest as legacy-pending-p8 | legacy | P8 decision |
| Pricing / access path | /start/ sandbox + workspace billing | demoted | Access entry | platform workspace | RESTORED as homepage Access section: app entry, developer workspace, pilot contact; no public pricing claims | live | /#engage |

## Deliberately excluded stale claims (not restored)

- "Parent-company self-audit" case study (superseded, retired surface)
- SourceB references anywhere public (gate-enforced absent)
- "LIVE ARCHITECTURE" chip and unscoped operating-loop claims
- Cost/retry/quality claims ("exact per-run cost", "complete retry count",
  "all outputs verified") — remain gate-forbidden
- "three product lines", "validation vertical developed and operated",
  separate-venture TrustField framing (ownership stays canonical)
- Invented mockup copy markers ($48k transfer, 18/24 nodes, Governed
  Exchange, Audit Factory, HIPAA policy pack) — remain gate-forbidden;
  FINTRAC unbanned because it is now the real TrustField wedge

## API status audit (P5)

- api.noetfield.com resolves (Railway CNAME); POST /v1/chat/completions
  returns 404 unauthenticated — endpoint activation is per workspace
  tenant during commissioning, matching the page's stated scope.
- Page now documents: status badge, auth model (workspace keys after
  sign-in), base URL + endpoint, sample request/response/receipt marked
  SHAPE ONLY, provider-routing boundary, fail-closed error behavior,
  limitations, workspace access CTA.
- No universal compatibility or production-readiness claims added.

## App backend-binding audit (P0.6 / P3)

- app.noetfield.com is served from the NOETFIELD-RUNWAY repository
  (sites/company-new; runtime control plane in
  apps/project-runtime-control-plane; staging API worker
  noetfield-runway-runtime-api-staging on workers.dev).
- The www repo holds no app runtime code. All www references to app
  capabilities are labeled live / client-zero / commissioning and describe
  only the publicly observable flow plus the workspace IA (left project
  navigation, central working thread, right execution/evidence panel).
- No simulated runtime output is presented anywhere on www.

## Preservation gate (P7)

- governance/product-surface-manifest-v1.json: 28 active capability
  records with route, surface, maturity, state, backend binding, evidence
  link, founder-approved visibility, and a content needle.
- scripts/verify-product-surface-manifest.py enforces: every active
  capability's surface exists and still contains its needle; the primary
  nav keeps all eight labels; removals require founder approval, a
  replacement route, and a recorded reason. Wired into make
  verify-static-www, which production CI runs on every release.
