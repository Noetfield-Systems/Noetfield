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

---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-28"
doc_id: noetfield-e2e-smart-upgrade-321-tasks-v1
status: DRAFT
---

# Noetfield E2E Smart Upgrade Plan - 321 Tasks v1

## Basis

Live E2E and static verification passed on 2026-06-28 after the AI Factory Layer went live. This plan turns the audit into a structured upgrade backlog. It is not a done list.

## Verify Baseline

- `make verify-www-e2e` passed.
- `make verify-static-www` passed.
- Focused live route smoke returned `200` for AI Factory pages, OpenAPI, config JSON, status, pricing, status, and intake routes.
- Immediate upgrade already identified: E2E coverage should include AI Factory pages, config, OpenAPI, Gate API, and Status API.

## Lane 1 - E2E Contract Coverage

- [ ] E2E-001 Add `/ai-factories/` to live 200 route checks.
- [ ] E2E-002 Add `/ai-factories/spec/` to live 200 route checks.
- [ ] E2E-003 Add `/openapi.json` to live 200 route checks.
- [ ] E2E-004 Add `/config/gate-ai-factory-design.json` to live 200 route checks.
- [ ] E2E-005 Add `/config/status-ai-factory.json` to live 200 route checks.
- [ ] E2E-006 Add `/noetfield-ai-factory-lanes.json` to live 200 route checks.
- [ ] E2E-007 Assert AI Factory homepage contains the primary value proposition.
- [ ] E2E-008 Assert AI Factory homepage contains `AI Factory Design`.
- [ ] E2E-009 Assert AI Factory homepage contains the Gate CTA.
- [ ] E2E-010 Assert AI Factory spec page contains `YAML Factory Spec`.
- [ ] E2E-011 Assert AI Factory spec page contains copyable deployment language.
- [ ] E2E-012 Assert OpenAPI mentions the AI Factory API title.
- [ ] E2E-013 Assert OpenAPI references the Gate endpoint.
- [ ] E2E-014 Assert Gate config JSON contains `AI Factory Design`.
- [ ] E2E-015 Assert Gate config JSON contains `YAML Factory Spec`.
- [ ] E2E-016 Assert Status config JSON contains `ledger_complete`.
- [ ] E2E-017 Add POST smoke for `/api/gate/ai-factory-design`.
- [ ] E2E-018 Assert Gate smoke returns HTTP 202 or another explicit accepted success.
- [ ] E2E-019 Assert Gate smoke returns a policy decision in `ALLOW`, `BLOCK`, or `ESCALATE`.
- [ ] E2E-020 Add GET smoke for `/api/status/ai-factory`.
- [ ] E2E-021 Assert Status smoke returns the requested `request_id`.
- [ ] E2E-022 Assert Status smoke returns `request_type: AI Factory`.
- [ ] E2E-023 Add regression check that `/api/config` is not required by the public AI Factory page.
- [ ] E2E-024 Add regression check that serverless function count stays at or below 12 on Hobby.
- [ ] E2E-025 Add production E2E output line naming the deployed git SHA when available.
- [ ] E2E-026 Add Cloudflare proxy header check for `x-noetfield-proxy`.
- [ ] E2E-027 ~~Add Vercel cache sanity check for fresh AI Factory deploys.~~ WON'T DO — Vercel retired 2026-07-09.
- [ ] E2E-028 Add fallback check for `/api/health` when `/health` is rewritten.
- [ ] E2E-029 Add JSON parse checks for every public JSON route.
- [ ] E2E-030 Add HTTP content-type checks for HTML and JSON routes.
- [ ] E2E-031 Add E2E failure summary grouping by route, copy, API, and leak.
- [ ] E2E-032 Add E2E docs pointer to `L0-law/PUBLIC_WWW_BRAND_E2E_LAW_LOCKED_v1.md`.

## Lane 2 - AI Factory Product Surface

- [ ] E2E-033 Clarify the AI Factory hero promise in one sentence.
- [ ] E2E-034 Add a short “who this is for” buyer block.
- [ ] E2E-035 Add a short “who this is not for” scope block.
- [ ] E2E-036 Add visible ALLOW/BLOCK/ESCALATE explanation.
- [ ] E2E-037 Add request ID explanation near the factory form.
- [ ] E2E-038 Add Trust Ledger-ready audit explanation.
- [ ] E2E-039 Add stateless runtime explanation.
- [ ] E2E-040 Add example input payload on the spec page.
- [ ] E2E-041 Add example output receipt on the spec page.
- [ ] E2E-042 Add a validation failure example.
- [ ] E2E-043 Add a BLOCK decision example.
- [ ] E2E-044 Add an ESCALATE decision example.
- [ ] E2E-045 Add a “copy YAML” success state.
- [ ] E2E-046 Add a no-JavaScript fallback note.
- [ ] E2E-047 Add “start Gate intake” link consistency check.
- [ ] E2E-048 Add link from `/runtime/` to AI Factory Layer.
- [ ] E2E-049 Add link from `/templates/` to AI Factory Layer.
- [ ] E2E-050 Add link from `/governance/` to AI Factory Layer if buyer-safe.
- [ ] E2E-051 Add footer link to AI Factory only if the navigation remains clean.
- [ ] E2E-052 Add one buyer-safe diagram in HTML, not as internal ops jargon.
- [ ] E2E-053 Add FAQ entry explaining factory versus chatbot.
- [ ] E2E-054 Add FAQ entry explaining factory versus automation agency.
- [ ] E2E-055 Add FAQ entry explaining factory versus GRC platform.
- [ ] E2E-056 Add public copy guard against “agent ops” language.
- [ ] E2E-057 Add public copy guard against “SourceA” language on AI Factory pages.
- [ ] E2E-058 Add public copy guard against “internal receipt” language.
- [ ] E2E-059 Add canonical metadata to the spec page.
- [ ] E2E-060 Add OpenGraph metadata to the AI Factory page.
- [ ] E2E-061 Add structured data only if it stays buyer-safe.
- [ ] E2E-062 Add print stylesheet coverage for the spec page.
- [ ] E2E-063 Add procurement-safe PDF export path as a future task.
- [ ] E2E-064 Add AI Factory route to sitemap generation.

## Lane 3 - Public Route UX

- [ ] E2E-065 Review homepage route priority after AI Factory launch.
- [ ] E2E-066 Confirm AI Factory does not dilute primary pilot CTA.
- [ ] E2E-067 Confirm AI Factory does not conflict with Diagnostic Sprint.
- [ ] E2E-068 Add route map for `/start/`, `/pricing/`, `/runtime/`, and `/ai-factories/`.
- [ ] E2E-069 Add clear buyer path from AI Factory to intake.
- [ ] E2E-070 Add clear developer path from AI Factory to OpenAPI.
- [ ] E2E-071 Add clear governance path from AI Factory to Trust Ledger sample.
- [ ] E2E-072 Confirm all header links stay under 8 primary items.
- [ ] E2E-073 Confirm mobile header renders AI Factory link if included.
- [ ] E2E-074 Confirm footer does not become too dense.
- [ ] E2E-075 Confirm `/next/` mentions AI Factory only if operationally true.
- [ ] E2E-076 Confirm `/status/` can surface AI Factory availability later.
- [ ] E2E-077 Add route health summary for public status.
- [ ] E2E-078 Add route ownership comments to verify scripts.
- [ ] E2E-079 Add stale route scan for old project aliases.
- [ ] E2E-080 Add stale copy scan for retired `design partner` wording.
- [ ] E2E-081 Add stale copy scan for old platform DNS claims.
- [ ] E2E-082 Add stale copy scan for old `api.noetfield.com` future claims.
- [ ] E2E-083 Add buyer journey smoke from homepage to intake.
- [ ] E2E-084 Add buyer journey smoke from AI Factory to intake.
- [ ] E2E-085 Add buyer journey smoke from pricing to intake.
- [ ] E2E-086 Add buyer journey smoke from trust page to sample report.
- [ ] E2E-087 Add route canonical URL checks.
- [ ] E2E-088 Add robots meta checks for public pages.
- [ ] E2E-089 Add noindex checks for embed-only pages.
- [ ] E2E-090 Add 404 checks for internal docs added after each deploy.
- [ ] E2E-091 Add allowed public docs whitelist.
- [ ] E2E-092 Add forbidden public docs denylist.
- [ ] E2E-093 Add regression check for `/platform/*` leakage.
- [ ] E2E-094 Add regression check for `/reports/*` leakage.
- [ ] E2E-095 Add regression check for `/os/*` leakage.
- [ ] E2E-096 Add regression check for `.cursor` leakage.

## Lane 4 - Intake And Conversion

- [ ] E2E-097 Add AI Factory interest code to intake URLs.
- [ ] E2E-098 Add AI Factory option to intake form if buyer-safe.
- [ ] E2E-099 Add hidden source route field for AI Factory form submissions.
- [ ] E2E-100 Add intake telemetry event for AI Factory page view.
- [ ] E2E-101 Add intake telemetry event for Gate CTA click.
- [ ] E2E-102 Add intake telemetry event for YAML copy.
- [ ] E2E-103 Add intake telemetry event for API smoke failures.
- [ ] E2E-104 Add conversion metric from AI Factory to pilot application.
- [ ] E2E-105 Add conversion metric from OpenAPI view to intake.
- [ ] E2E-106 Add conversion metric from spec page to intake.
- [ ] E2E-107 Add email routing label for AI Factory inquiries.
- [ ] E2E-108 Add CRM-safe subject line for AI Factory inquiries.
- [ ] E2E-109 Add autoresponder copy for AI Factory inquiries.
- [ ] E2E-110 Add buyer qualification question for existing AI workflows.
- [ ] E2E-111 Add buyer qualification question for compliance owner.
- [ ] E2E-112 Add buyer qualification question for deployment deadline.
- [ ] E2E-113 Add buyer qualification question for evidence requirement.
- [ ] E2E-114 Add buyer qualification question for Microsoft stack.
- [ ] E2E-115 Add anti-ICP rejection copy for full chatbot builds.
- [ ] E2E-116 Add anti-ICP routing copy for requests outside governance scope.
- [ ] E2E-117 Add route-specific thank-you state.
- [ ] E2E-118 Add operations@ delivery proof to verify output.
- [ ] E2E-119 Add platform intake fallback proof to verify output.
- [ ] E2E-120 Add Resend configured regression check.
- [ ] E2E-121 Add Postgres intake storage regression check.
- [ ] E2E-122 Add intake spam-throttle note in docs.
- [ ] E2E-123 Add intake JSON schema for AI Factory interest.
- [ ] E2E-124 Add dashboard-ready intake fields.
- [ ] E2E-125 Add weekly report metric for AI Factory leads.
- [ ] E2E-126 Add failed lead submit alert plan.
- [ ] E2E-127 Add dead-letter path for intake delivery failures.
- [ ] E2E-128 Add proof row in `/status/` once metrics exist.

## Lane 5 - Chat And Knowledge

- [ ] E2E-129 Add AI Factory facts to chatbot knowledge.
- [ ] E2E-130 Add AI Factory route to pinned chatbot knowledge.
- [ ] E2E-131 Add chatbot FAQ for “What is an AI Factory?”
- [ ] E2E-132 Add chatbot FAQ for “How does Gate decide?”
- [ ] E2E-133 Add chatbot FAQ for “Does this store data?”
- [ ] E2E-134 Add chatbot FAQ for “How do I start?”
- [ ] E2E-135 Add chatbot scope routing for requests outside governance context.
- [ ] E2E-136 Add chatbot refusal for bypass/governance evasion requests.
- [ ] E2E-137 Add chatbot answer test for AI Factory.
- [ ] E2E-138 Add chatbot answer test for Trust Ledger-ready audit.
- [ ] E2E-139 Add chatbot answer test for pricing/next step.
- [ ] E2E-140 Add chatbot answer test for OpenAPI route.
- [ ] E2E-141 Add chatbot answer test for spec route.
- [ ] E2E-142 Add chatbot telemetry label for AI Factory questions.
- [ ] E2E-143 Add chatbot source citation to AI Factory page.
- [ ] E2E-144 Add chatbot source citation to OpenAPI.
- [ ] E2E-145 Add chatbot source citation to config JSON.
- [ ] E2E-146 Add public-chat health check for knowledge bundle version.
- [ ] E2E-147 Add knowledge bundle size regression threshold.
- [ ] E2E-148 Add stale knowledge scan for old Noetfield OS Phase 1 claims.
- [ ] E2E-149 Add stale knowledge scan for old `api.noetfield.com` claims.
- [ ] E2E-150 Add stale knowledge scan for old Vercel project claims. STILL RELEVANT post-retirement — scan should flag any remaining "Vercel is canonical" claims across the repo.
- [ ] E2E-151 Add answer-quality eval for buyer-safe language.
- [ ] E2E-152 Add answer-quality eval for no internal ops terms.
- [ ] E2E-153 Add answer-quality eval for CTA consistency.
- [ ] E2E-154 Add answer-quality eval for scope honesty.
- [ ] E2E-155 Add answer-quality eval for no competitor comparison framing.
- [ ] E2E-156 Add chatbot fallback when platform proxy is unavailable.
- [ ] E2E-157 Add chatbot mode regression for `platform-proxy`.
- [ ] E2E-158 Add chatbot mode regression for `www-local`.
- [ ] E2E-159 Add visible user-facing error for chat outages.
- [ ] E2E-160 Add weekly chatbot telemetry review task.

## Lane 6 - Platform And GEL Sync

- [ ] E2E-161 Add dedicated platform health smoke to E2E closeout.
- [ ] E2E-162 Add dedicated GEL health smoke to E2E closeout.
- [ ] E2E-163 Add `api.noetfield.com/health` curl check.
- [ ] E2E-164 Add `api.noetfield.com/readiness` curl check.
- [ ] E2E-165 Add `platform.noetfield.com/health` curl check.
- [ ] E2E-166 Add `platform.noetfield.com/api/status` curl check.
- [ ] E2E-167 Add Noetfield OS `PRODUCT_TRUTH.md` sync check.
- [ ] E2E-168 Add Noetfield ownership charter sync check.
- [ ] E2E-169 Add stale `noetfeld-os` spelling confusion guard.
- [ ] E2E-170 Add GEL route ownership note to OpenAPI.
- [ ] E2E-171 Add AI Factory route ownership note to OpenAPI.
- [ ] E2E-172 Add platform route ownership note to docs index.
- [ ] E2E-173 Add adapter boundary test for `use_gel_adapter`.
- [ ] E2E-174 Add adapter timeout behavior test.
- [ ] E2E-175 Add adapter error mapping test.
- [ ] E2E-176 Add adapter no-secret logging test.
- [ ] E2E-177 Add platform public ecosystem check.
- [ ] E2E-178 Add platform chat proxy check.
- [ ] E2E-179 Add platform intake proxy check.
- [ ] E2E-180 Add platform telemetry write check.
- [ ] E2E-181 Add GEL sample decision smoke.
- [ ] E2E-182 Add GEL idempotency smoke.
- [ ] E2E-183 Add GEL policy version smoke.
- [ ] E2E-184 Add GEL TLE export smoke.
- [ ] E2E-185 Add GEL board PDF stub smoke.
- [ ] E2E-186 Add Noetfield OS PyPI status check.
- [ ] E2E-187 Add Noetfield OS npm SDK status check.
- [ ] E2E-188 Add cross-repo stale truth ledger link.
- [ ] E2E-189 Add cross-repo route source map.
- [ ] E2E-190 Add cross-repo “do not duplicate website” guard.
- [ ] E2E-191 Add cross-repo “do not duplicate GEL runtime” guard.
- [ ] E2E-192 Add platform/GEL smoke summary to `/status/` when public-safe.

## Lane 7 - Deployment And CI

- [ ] E2E-193 ~~Add Vercel function count check to `verify-static-www`.~~ WON'T DO — Vercel retired 2026-07-09; use a Cloudflare Pages Functions count check instead.
- [ ] E2E-194 ~~Add Vercel function count check to CI.~~ WON'T DO — Vercel retired 2026-07-09; use a Cloudflare Pages Functions count check instead.
- [ ] E2E-195 Add Node runtime pin check.
- [ ] E2E-196 ~~Add `npx vercel build --prod` to deploy readiness when Vercel settings exist.~~ WON'T DO — Vercel retired 2026-07-09.
- [ ] E2E-197 ~~Add warning if Vercel output target is preview during prod deploy.~~ WON'T DO — Vercel retired 2026-07-09; use a Cloudflare Pages preview-vs-production warning instead.
- [ ] E2E-198 Add CI check that PYTHONPATH matches Makefile service paths.
- [ ] E2E-199 Add CI check for missing service roots.
- [ ] E2E-200 Add CI check for serverless function additions.
- [ ] E2E-201 Add CI check for `.vercelignore` public allowlist. STILL RELEVANT — `.vercelignore` remains load-bearing for the Cloudflare Pages build (`scripts/build-www-pages-dist.sh` rsyncs with `--exclude-from=.vercelignore`).
- [ ] E2E-202 Add CI check for public JSON config allowlist.
- [ ] E2E-203 Add CI check for accidental docs publishing.
- [ ] E2E-204 ~~Add CI check for generated `.vercel` files not committed.~~ WON'T DO — Vercel retired 2026-07-09; no more `.vercel/` directory is ever generated.
- [ ] E2E-205 Add CI check for package-lock engine drift.
- [ ] E2E-206 Add CI check for GitHub Actions path filters.
- [ ] E2E-207 ~~Add CI check for Vercel deployment status after push.~~ WON'T DO — Vercel retired 2026-07-09; use a Cloudflare Pages deployment status check instead.
- [ ] E2E-208 Add retry-safe live route polling after deploy.
- [ ] E2E-209 ~~Add failure parser for `vercel inspect --logs`.~~ WON'T DO — Vercel retired 2026-07-09; use `wrangler pages deployment tail` instead.
- [ ] E2E-210 Add failure parser for GitHub commit statuses.
- [ ] E2E-211 Add failure parser for GitHub check annotations.
- [ ] E2E-212 Add no-secret output scrubber for deploy logs.
- [ ] E2E-213 Add deploy rollback runbook.
- [ ] E2E-214 Add Hobby plan cap runbook.
- [ ] E2E-215 Add Pro plan upgrade decision note.
- [ ] E2E-216 Add function consolidation strategy.
- [ ] E2E-217 Add static-first route policy.
- [ ] E2E-218 Add API route budget policy.
- [ ] E2E-219 Add public config static policy.
- [ ] E2E-220 Add deploy preview smoke for PRs.
- [ ] E2E-221 Add production smoke for merges.
- [ ] E2E-222 Add cache purge note for Cloudflare. (Vercel retired 2026-07-09 — Cloudflare only.)
- [ ] E2E-223 Add deploy SHA stamp to status output.
- [ ] E2E-224 Add deploy closeout template.

## Lane 8 - Security And Privacy

- [ ] E2E-225 Add secret pattern audit to www E2E closeout.
- [ ] E2E-226 Add public HTML scan for API keys.
- [ ] E2E-227 Add public JSON scan for secrets.
- [ ] E2E-228 Add public JS scan for secrets.
- [ ] E2E-229 Add route-level CORS audit.
- [ ] E2E-230 Add POST payload size cap for AI Factory Gate.
- [ ] E2E-231 Add method allowlist tests for AI Factory APIs.
- [ ] E2E-232 Add malformed JSON test for AI Factory Gate.
- [ ] E2E-233 Add missing field test for AI Factory Gate.
- [ ] E2E-234 Add prompt-injection phrase test for AI Factory Gate.
- [ ] E2E-235 Add bypass phrase test for AI Factory Gate.
- [ ] E2E-236 Add prohibited phrase test for AI Factory Gate.
- [ ] E2E-237 Add no-storage claim verification note.
- [ ] E2E-238 Add privacy copy for stateless preview.
- [ ] E2E-239 Add audit hash stability test.
- [ ] E2E-240 Add final output hash presence test.
- [ ] E2E-241 Add request ID entropy test.
- [ ] E2E-242 Add no-cookie requirement check for AI Factory pages.
- [ ] E2E-243 Add security headers smoke.
- [ ] E2E-244 Add HSTS header smoke.
- [ ] E2E-245 Add content security policy plan.
- [ ] E2E-246 Add clickjacking header plan.
- [ ] E2E-247 Add robots/noindex review for API docs.
- [ ] E2E-248 Add safe error message check.
- [ ] E2E-249 Add internal stack trace leak check.
- [ ] E2E-250 Add 404 body leak check.
- [ ] E2E-251 Add public route path traversal check.
- [ ] E2E-252 Add JSON schema validation for public config.
- [ ] E2E-253 Add OpenAPI schema validation.
- [ ] E2E-254 Add Trust Ledger wording compliance check.
- [ ] E2E-255 Add non-custodial wording compliance check.
- [ ] E2E-256 Add “no payment product” wording compliance check.

## Lane 9 - Performance And Accessibility

- [ ] E2E-257 Add HTML size budget for AI Factory page.
- [ ] E2E-258 Add CSS size budget for AI Factory CSS.
- [ ] E2E-259 Add JS size budget for AI Factory JS.
- [ ] E2E-260 Add image asset budget check.
- [ ] E2E-261 Add font loading review.
- [ ] E2E-262 Add no render-blocking extras check.
- [ ] E2E-263 Add preconnect sanity check.
- [ ] E2E-264 Add mobile viewport check.
- [ ] E2E-265 Add heading order check.
- [ ] E2E-266 Add one `h1` per page check.
- [ ] E2E-267 Add skip link check.
- [ ] E2E-268 Add form label check.
- [ ] E2E-269 Add button accessible name check.
- [ ] E2E-270 Add color contrast review task.
- [ ] E2E-271 Add keyboard-only form operation check.
- [ ] E2E-272 Add copy button keyboard check.
- [ ] E2E-273 Add reduced motion check.
- [ ] E2E-274 Add print view check for spec page.
- [ ] E2E-275 Add empty-state check for receipt panel.
- [ ] E2E-276 Add failed-submit accessible alert.
- [ ] E2E-277 Add success receipt accessible region.
- [ ] E2E-278 Add ARIA audit for dynamic receipt.
- [ ] E2E-279 Add structured list semantics check.
- [ ] E2E-280 Add link text uniqueness check.
- [ ] E2E-281 Add no “click here” copy check.
- [ ] E2E-282 Add long-line code block wrap check.
- [ ] E2E-283 Add JSON route compression check.
- [ ] E2E-284 Add cache header review.
- [ ] E2E-285 Add Cloudflare cache age review.
- [ ] E2E-286 ~~Add Vercel cache status review.~~ WON'T DO — Vercel retired 2026-07-09; use a Cloudflare Pages cache status review instead.
- [ ] E2E-287 Add latency tracking for critical routes.
- [ ] E2E-288 Add p95 response budget for live smoke.

## Lane 10 - Ops, Analytics, And Revenue Learning

- [ ] E2E-289 Add AI Factory page view analytics event.
- [ ] E2E-290 Add AI Factory form input analytics event.
- [ ] E2E-291 Add AI Factory form submit analytics event.
- [ ] E2E-292 Add AI Factory gate accepted analytics event.
- [ ] E2E-293 Add AI Factory gate blocked analytics event.
- [ ] E2E-294 Add AI Factory gate escalated analytics event.
- [ ] E2E-295 Add YAML copied analytics event.
- [ ] E2E-296 Add spec page view analytics event.
- [ ] E2E-297 Add OpenAPI view analytics event.
- [ ] E2E-298 Add config JSON request metric if feasible.
- [ ] E2E-299 Add live E2E telemetry row for AI Factory.
- [ ] E2E-300 Add weekly AI Factory funnel report.
- [ ] E2E-301 Add monthly route quality report.
- [ ] E2E-302 Add AI Factory lead quality rubric.
- [ ] E2E-303 Add AI Factory demo script.
- [ ] E2E-304 Add AI Factory procurement one-pager.
- [ ] E2E-305 Add AI Factory Trust Brief attachment path.
- [ ] E2E-306 Add AI Factory pricing hypothesis.
- [ ] E2E-307 Add AI Factory pilot packaging.
- [ ] E2E-308 Add AI Factory implementation checklist.
- [ ] E2E-309 Add AI Factory partner lane.
- [ ] E2E-310 Add AI Factory managed ops lane.
- [ ] E2E-311 Add AI Factory no-code/low-code lane.
- [ ] E2E-312 Add AI Factory regulated workflow lane.
- [ ] E2E-313 Add AI Factory Microsoft/Copilot lane.
- [ ] E2E-314 Add AI Factory evidence-pack lane.
- [ ] E2E-315 Add AI Factory status page tile.
- [ ] E2E-316 Add AI Factory incident response row.
- [ ] E2E-317 Add AI Factory release note template.
- [ ] E2E-318 Add AI Factory customer proof template.
- [ ] E2E-319 Add AI Factory roadmap handoff to noetfeld-os where runtime-owned.
- [ ] E2E-320 Add AI Factory website ownership handoff where www-owned.
- [ ] E2E-321 Add final 321-task review gate: pick next 3 tasks only, verify, then update this plan.

## Execution Rule

Do not execute all 321 tasks in one pass. Pick at most three related tasks, implement, verify, and update this plan with evidence.
