# L0 Repo Graph Report — Noetfield

Generated (last indexed): `2026-07-13T10:49:17Z` · template `v1.1.0`
Total files: 33374 · Total size: 271.9MB · Edges detected: 106621

**Read this file first.** Do not spawn broad repo-reading agents ("understand the repo", "map subsystem X", "audit Y") until you have read this report and, if you need more detail, queried the index with `python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>`. This report + a query response should answer routing questions ("which files touch X", "how big is subsystem Y") without opening every file in the subsystem.

## Subsystem map (sorted by size, descending)

| subsystem | files | size | largest files |
|---|---:|---:|---|
| governance-console/ | 452 | 91.0MB | `governance-console/frontend/.next/cache/webpack/server-production/2.pack`, `governance-console/frontend/.next/cache/webpack/client-production/0.pack`, `governance-console/frontend/.next/cache/webpack/server-production/0.pack`, `governance-console/frontend/.next/cache/webpack/server-production/index.pack`, `governance-console/frontend/.next/cache/webpack/server-production/index.pack.old`, `governance-console/frontend/.next/cache/webpack/client-production/1.pack` |
| .claude/ | 26383 | 85.4MB | `.claude/worktrees/ai-receptionist-landing-7b6e62/docs/ops/plans/registry.json`, `.claude/worktrees/cursor-never-miss-call-landing-v1/docs/ops/plans/registry.json`, `.claude/worktrees/noetfield-partner-onboarding-audit-446d8b/docs/ops/plans/registry.json`, `.claude/worktrees/sandbox+noetfield-field-audit-redesign-v1/docs/ops/plans/registry.json`, `.claude/worktrees/ai-receptionist-landing-7b6e62/os/plan-library/noetfield-competitor-1000/REGISTRY.json`, `.claude/worktrees/cursor-never-miss-call-landing-v1/os/plan-library/noetfield-competitor-1000/REGISTRY.json` |
| apps/ | 187 | 73.8MB | `apps/web/.next/cache/webpack/server-production/2.pack`, `apps/web/.next/cache/webpack/client-production/0.pack`, `apps/web/.next/cache/webpack/client-production/3.pack`, `apps/web/.next/cache/webpack/server-production/0.pack`, `apps/web/.next/cache/webpack/server-production/index.pack`, `apps/web/.next/cache/webpack/server-production/index.pack.old` |
| os/ | 3031 | 6.6MB | `os/plan-library/noetfield-competitor-1000/REGISTRY.json`, `os/plan-library/noetfield-1000/REGISTRY.json`, `os/plans/REGISTRY.json`, `os/plan.json`, `os/SHIP_NOW.md`, `os/plan-library/SOURCEA_SUGGESTION_MCP_CHAIN_LOCKED_v1.md` |
| docs/ | 1097 | 6.1MB | `docs/ops/plans/registry.json`, `docs/ops/plans/catalog-500.json`, `docs/ops/plans/tier1-smart.json`, `docs/ops/plans/TIER1_SMART_PROMPTS.md`, `docs/ops/plans/TIER1_SMART_PROMPTS.md.bak.1783081948`, `docs/ops/plans/BRIDGE_NF_PLAN_TO_NF_FUTURE.json` |
| reports/ | 171 | 2.1MB | `reports/www-audit/snapshots/live/crawl_index.json`, `reports/www-audit/snapshots/disk/home.html`, `reports/www-audit/snapshots/live/home.html`, `reports/www-audit/snapshots/disk/trust_brief_intake.html`, `reports/www-audit/snapshots/live/trust_brief_intake.html`, `reports/www-audit/snapshots/live/trust_brief_intake_interest_enterprise_amp_vector_ai_value_governance_os.html` |
| scripts/ | 282 | 1.6MB | `scripts/rebuild-www-v6.py`, `scripts/market_success_1000_data.py`, `scripts/generate-tier1-smart-pack.py`, `scripts/generate-noetfield-1000-prompts.py`, `scripts/generate-prompt-catalog-500.py`, `scripts/generate_batch_006_sot.py` |
| .agents/ | 322 | 1.4MB | `.agents/skills/wrangler/SKILL.md`, `.agents/skills/cloudflare/references/flagship/patterns.md`, `.agents/skills/cloudflare/references/r2-sql/SKILL.md.backup`, `.agents/skills/cloudflare/references/flagship/api.md`, `.agents/skills/cloudflare/SKILL.md`, `.agents/skills/cloudflare/references/realtimekit/api.md` |
| services/ | 118 | 616.7KB | `services/governance/noetfield_governance/api.py`, `services/governance/noetfield_governance/trust_ledger.py`, `services/governance/noetfield_governance/analytics_store.py`, `services/graph/noetfield_graph/mutation.py`, `services/governance/noetfield_governance/chatbot_knowledge.py`, `services/factories/noetfield_factories/nodes.py` |
| assets/ | 65 | 459.2KB | `assets/noetfield-www.css`, `assets/noetfield-live-proof.js`, `assets/noetfield-enterprise.css`, `assets/noetfield-shell.js`, `assets/pages/institutional-2026.css`, `assets/noetfield-shell.css` |
| Noetfield-All-Documents/ | 245 | 382.7KB | `Noetfield-All-Documents/registry/source_document_inventory.json`, `Noetfield-All-Documents/registry/active_rule_candidates.json`, `Noetfield-All-Documents/registry/source_of_truth_registry.json`, `Noetfield-All-Documents/MANIFEST.md`, `Noetfield-All-Documents/uploaded/2026-05-batch-020/noetfield-sot-master-document-v1.md`, `Noetfield-All-Documents/uploaded/2026-05-batch-020/noetfield-unified-cognitive-governance-system-v1.md` |
| L2-knowledge/ | 462 | 248.3KB | `L2-knowledge/strategy/full/2026-05-batch-020/noetfield-sot-master-document-v1.md`, `L2-knowledge/strategy/noetfield/2026-05-batch-020/noetfield-sot-master-document-v1.md`, `L2-knowledge/strategy/full/2026-05-batch-020/noetfield-unified-cognitive-governance-system-v1.md`, `L2-knowledge/strategy/noetfield/2026-05-batch-020/noetfield-unified-cognitive-governance-system-v1.md`, `L2-knowledge/strategy/full/2026-05-batch-001/wp-03-npl-formal-grammar-2026-05-npl-1.md`, `L2-knowledge/strategy/noetfield/2026-05-batch-001/wp-03-npl-formal-grammar-2026-05-npl-1.md` |
| trust-ledger/ | 14 | 246.0KB | `trust-ledger/sample-report/ledger-entry.2.pdf`, `trust-ledger/sample-report/board-memo.pdf`, `trust-ledger/sample-report/ledger-entry.pdf`, `trust-ledger/index.html`, `trust-ledger/sample-report/index.html`, `trust-ledger/verify/index.html` |
| tests/ | 71 | 236.7KB | `tests/unit/test_source_of_truth_registry.py`, `tests/unit/test_public_chat.py`, `tests/unit/test_public_gtm_alignment.py`, `tests/unit/test_chat_scenarios.py`, `tests/unit/test_trust_ledger_v1.py`, `tests/unit/test_factory_copilot.py` |
| functions/ | 20 | 159.9KB | `functions/api/intake.js`, `functions/api/intake/health.js`, `functions/api/demo/evaluate.js`, `functions/api/demo/ssot-change.js`, `functions/api/public/chat.js`, `functions/api/gate/ai-factory-design.js` |
| governance/ | 20 | 98.9KB | `governance/index.html`, `governance/www-pages-routes.json`, `governance/AUTOMATION_SURFACES_LOCKED.json`, `governance/NODE_CATALOG.json`, `governance/NOETFIELD_LIVE_NERVE_RECEIPT.json`, `governance/FACTORY_CATALOG.json` |
| .cursor/ | 54 | 89.8KB | `.cursor/agent-memory/MEMORY_LOCKED.yaml`, `.cursor/incidents/INCIDENT-2026-07-06-001-www-sandbox-downgrade.md`, `.cursor/AGENT_TRACKING.md`, `.cursor/skills/SKILL-007-auto-conflict-resolution.md`, `.cursor/incidents/INCIDENT-2026-06-06-002-unauthorized-disk-edits.md`, `.cursor/incidents/INCIDENT-2026-06-06-001-trustfield-scope-bleed.md` |
| tools/ | 2 | 84.3KB | `tools/pr-conflict-resolver-report/report.html`, `tools/pr-conflict-resolver-report/open-report.sh` |
| copilot/ | 20 | 83.7KB | `copilot/pilot/index.html`, `copilot/procurement/index.html`, `copilot/demo/index.html`, `copilot/index.html`, `copilot/trial/index.html`, `copilot/sme/index.html` |
| gate/ | 36 | 83.7KB | `gate/partners/pack/co-sell-play.pdf`, `gate/procurement/contracting-notes.pdf`, `gate/intake/index.html`, `gate/procurement/security-privacy-summary.pdf`, `gate/procurement/procurement-pack.pdf`, `gate/diligence/index.html` |
| packages/ | 48 | 78.9KB | `packages/config/noetfield_config/__init__.py`, `packages/sdk/examples/local_governance_scaffold.py`, `packages/sdk/noetfield_sdk/client.py`, `packages/schemas/tle-v1.schema.json`, `packages/schemas/factories/copilot_governance_readiness_v1.yaml`, `packages/types/noetfield_types/domain.py` |
| infrastructure/ | 25 | 61.7KB | `infrastructure/supabase/migrations/0001_noetfield_v3_1_foundation.sql`, `infrastructure/supabase/migrations/0008_observability_tables.sql`, `infrastructure/supabase/migrations/0010_public_analytics_funnel_tables.sql`, `infrastructure/supabase/migrations/0002_phase_3_runtime_activation.sql`, `infrastructure/supabase/migrations/0004_source_of_truth_registry.sql`, `infrastructure/supabase/migrations/0003_phase_3_1_backend_core.sql` |
| data/ | 30 | 54.5KB | `data/chatbot/MANIFEST.json`, `data/nf_orient_routing_v1.json`, `data/www-positioning-verdict-matrix-v1.json`, `data/chatbot/knowledge/faq.md`, `data/chatbot/knowledge/pricing-matrix.md`, `data/nf_cleanup_dimensions_v1.json` |
| api/ | 21 | 53.9KB | `api/_lib/governance-evaluate.js`, `api/public/chat/index.js`, `api/_lib/intake-email.js`, `api/_lib/intake-telegram.js`, `api/intake.js`, `api/_lib/ai-factory-core.js` |
| prompts/ | 2 | 51.5KB | `prompts/loop-suggestions-100.json`, `prompts/loop-pack-10-active.json` |
| trust-brief/ | 2 | 39.6KB | `trust-brief/intake/index.html`, `trust-brief/index.html` |
| enterprise/ | 1 | 35.7KB | `enterprise/index.html` |
| demos/ | 8 | 30.3KB | `demos/copilot-governance/generated/demo_output.json`, `demos/copilot-governance/ssot/generated/demo_output.json`, `demos/copilot-governance/sample_deliverable_shape.json`, `demos/copilot-governance/sample_copilot_signal.json`, `demos/copilot-governance/ssot/pending_evaluations.json`, `demos/copilot-governance/template/manifest.json` |
| .github/ | 23 | 24.2KB | `.github/workflows/phase-3-runtime.yml`, `.github/workflows/nf-partner-onboarding-e2e-audit.yml`, `.github/workflows/platform-deploy.yml`, `.github/workflows/trust-ledger-ci.yml`, `.github/workflows/supabase-heartbeat.yml`, `.github/workflows/nf-kaizen-nightly.yml` |
| investors/ | 2 | 19.3KB | `investors/diligence/index.html`, `investors/index.html` |
| ai-value-governance-os/ | 1 | 18.8KB | `ai-value-governance-os/index.html` |
| infra/ | 5 | 18.7KB | `infra/nf-probe-cron/src/probes.js`, `infra/nf-probe-cron/src/index.js`, `infra/cf-www-proxy/src/worker.js`, `infra/nf-probe-cron/wrangler.toml`, `infra/cf-www-proxy/wrangler.toml` |
| ops/ | 13 | 18.3KB | `ops/templates/msb/OUTREACH_EMAILS.md`, `ops/templates/msb/INTAKE_RESPONSE_TEMPLATES.md`, `ops/templates/msb/MSB_PARTNER_ONE_PAGER.md`, `ops/templates/msb/SHADOW_PACK_SOW_TEMPLATE.md`, `ops/README.md`, `ops/templates/msb/STAGING_PROOF_RUNBOOK.md` |
| start/ | 1 | 17.5KB | `start/index.html` |
| proof/ | 3 | 17.0KB | `proof/noetfield.json`, `proof/noetfield/index.html`, `proof/index.html` |
| work-with-us/ | 1 | 16.5KB | `work-with-us/index.html` |
| pricing/ | 1 | 15.2KB | `pricing/index.html` |
| admin/ | 3 | 13.9KB | `admin/traction/index.html`, `admin/partner-onboarding/index.html`, `admin/partner-onboarding/latest.json` |
| ai-factories/ | 2 | 11.8KB | `ai-factories/index.html`, `ai-factories/spec/index.html` |
| trust/ | 1 | 11.1KB | `trust/index.html` |
| intelligence/ | 2 | 11.0KB | `intelligence/intake/index.html`, `intelligence/index.html` |
| next/ | 1 | 10.4KB | `next/index.html` |
| L0-law/ | 3 | 9.9KB | `L0-law/PUBLIC_WWW_BRAND_E2E_LAW_LOCKED_v1.md`, `L0-law/CURRENT.md`, `L0-law/README.md` |
| msp/ | 1 | 9.1KB | `msp/index.html` |
| federal/ | 1 | 9.1KB | `federal/index.html` |
| runtime/ | 1 | 7.7KB | `runtime/index.html` |
| platform/ | 3 | 7.6KB | `platform/factories/index.html`, `platform/dashboard/index.html`, `platform/index.html` |
| ai-automation/ | 1 | 6.3KB | `ai-automation/index.html` |
| bank-pilot/ | 1 | 6.2KB | `bank-pilot/index.html` |
| status/ | 1 | 6.1KB | `status/index.html` |
| console/ | 1 | 6.0KB | `console/index.html` |
| contact/ | 1 | 5.6KB | `contact/index.html` |
| partners/ | 1 | 5.5KB | `partners/index.html` |
| templates/ | 1 | 5.4KB | `templates/index.html` |
| banner/ | 1 | 5.3KB | `banner/index.html` |
| factory/ | 1 | 4.8KB | `factory/index.html` |
| faq/ | 1 | 4.5KB | `faq/index.html` |
| privacy/ | 1 | 4.3KB | `privacy/index.html` |
| auth/ | 4 | 4.2KB | `auth/sign-in/index.html`, `auth/callback/index.html`, `auth/sign-out/index.html`, `auth/index.html` |
| terms/ | 1 | 4.2KB | `terms/index.html` |
| receipts/ | 3 | 3.7KB | `receipts/l0-repo-graph-verify-20260709T071851Z.json`, `receipts/l0-repo-graph-verify-20260709T081131Z.json`, `receipts/.gitkeep` |
| playbook/ | 10 | 3.6KB | `playbook/ai-policy/index.html`, `playbook/board-trust-brief/index.html`, `playbook/eu-ai-act/index.html`, `playbook/index.html`, `playbook/iso-42001/index.html`, `playbook/ledger-schema/index.html` |
| invest/ | 1 | 3.4KB | `invest/index.html` |
| motors/ | 1 | 2.8KB | `motors/index.html` |
| cookies/ | 1 | 2.8KB | `cookies/index.html` |
| investor-workflows/ | 1 | 2.6KB | `investor-workflows/index.html` |
| about/ | 1 | 2.4KB | `about/index.html` |
| gel/ | 1 | 2.4KB | `gel/index.html` |
| roadmap/ | 1 | 2.2KB | `roadmap/index.html` |
| entry/ | 1 | 2.0KB | `entry/START_HERE_LOCKED_v1.md` |
| .sina-agent/ | 2 | 1.6KB | `.sina-agent/.cursor/rules/workspace-governance.mdc`, `.sina-agent/README.md` |
| .vscode/ | 3 | 1.5KB | `.vscode/settings.json`, `.vscode/tasks.json`, `.vscode/launch.json` |
| .noetfield/ | 1 | 1.5KB | `.noetfield/agent_manifest.yml` |
| config/ | 2 | 1.3KB | `config/gate-ai-factory-design.json`, `config/status-ai-factory.json` |
| L1-operational/ | 1 | 708B | `L1-operational/README.md` |
| portal/ | 2 | 678B | `portal/index.html`, `portal/login/index.html` |
| for-whom/ | 2 | 678B | `for-whom/index.html`, `for-whom/mandate/index.html` |
| .agent-policy/ | 1 | 623B | `.agent-policy/dispatch-templates/ADVISOR_ARCHITECT_CHECKLIST.md` |
| L3-external/ | 1 | 501B | `L3-external/README.md` |
| feedback/ | 1 | 422B | `feedback/index.html` |
| resources/ | 1 | 372B | `resources/index.html` |
| thanks/ | 1 | 339B | `thanks/index.html` |
| app/ | 1 | 339B | `app/index.html` |
| signup/ | 1 | 339B | `signup/index.html` |
| directory/ | 1 | 339B | `directory/index.html` |
| policies/ | 1 | 339B | `policies/index.html` |
| accessibility/ | 1 | 339B | `accessibility/index.html` |
| login/ | 1 | 339B | `login/index.html` |
| ex/ | 1 | 339B | `ex/index.html` |
| kits/ | 1 | 339B | `kits/index.html` |
| (root files) | 54 | 363.8KB | `package-lock.json`, `noetfield-gate-512.png`, `noetfield-og.png`, `PLATFORM_BLUEPRINT.md`, `Makefile`, `favicon.ico` |

## Dependency / reference edges

106621 static repo-relative path references were detected across .py/.sh/.md/.json/.yaml/.yml/.jsonc files (best-effort regex scan, not a real import graph). Full edge list is in `graph_index_v1.json`; query by file or subsystem with the query script rather than reading it directly.

## Ignored directories

`.cache`, `.git`, `.noos_cache`, `.pytest_cache`, `.venv`, `.wrangler`, `__pycache__`, `build`, `dist`, `graph-out`, `node_modules`, `venv`

## Query command

```
python3 scripts/query_repo_graph_v1.py <subsystem-name|keyword|path-fragment>
```

## Rebuild command

```
python3 scripts/build_repo_graph_v1.py
```

Rebuild whenever the file layout changes materially (new subsystem, large doc/data additions). See `docs/L0_REPO_GRAPH_MEMORY_v1.md` for the token budget rule and the broad-read prevention rule.
