# L0 Repo Graph Report — sina-governance-ssot

Generated (last indexed): `2026-07-09T07:18:53Z`
Total files: 6998 · Total size: 186.9MB · Edges detected: 21196

**Read this file first.** Do not spawn broad repo-reading agents ("understand the repo", "map subsystem X", "audit Y") until you have read this report and, if you need more detail, queried the index with `python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>`. This report + a query response should answer routing questions ("which files touch X", "how big is subsystem Y") without opening every file in the subsystem.

## Subsystem map (sorted by size, descending)

| subsystem | files | size | largest files |
|---|---:|---:|---|
| governance-console/ | 454 | 91.0MB | `governance-console/frontend/.next/cache/webpack/server-production/2.pack`, `governance-console/frontend/.next/cache/webpack/client-production/0.pack`, `governance-console/frontend/.next/cache/webpack/server-production/0.pack`, `governance-console/frontend/.next/cache/webpack/server-production/index.pack`, `governance-console/frontend/.next/cache/webpack/server-production/index.pack.old`, `governance-console/frontend/.next/cache/webpack/client-production/1.pack` |
| apps/ | 188 | 73.8MB | `apps/web/.next/cache/webpack/server-production/2.pack`, `apps/web/.next/cache/webpack/client-production/0.pack`, `apps/web/.next/cache/webpack/client-production/3.pack`, `apps/web/.next/cache/webpack/server-production/0.pack`, `apps/web/.next/cache/webpack/server-production/index.pack`, `apps/web/.next/cache/webpack/server-production/index.pack.old` |
| os/ | 3031 | 6.6MB | `os/plan-library/noetfield-competitor-1000/REGISTRY.json`, `os/plan-library/noetfield-1000/REGISTRY.json`, `os/plans/REGISTRY.json`, `os/plan.json`, `os/SHIP_NOW.md`, `os/plan-library/SOURCEA_SUGGESTION_MCP_CHAIN_LOCKED_v1.md` |
| docs/ | 1097 | 6.1MB | `docs/ops/plans/registry.json`, `docs/ops/plans/catalog-500.json`, `docs/ops/plans/tier1-smart.json`, `docs/ops/plans/TIER1_SMART_PROMPTS.md`, `docs/ops/plans/TIER1_SMART_PROMPTS.md.bak.1783081948`, `docs/ops/plans/BRIDGE_NF_PLAN_TO_NF_FUTURE.json` |
| reports/ | 200 | 2.7MB | `reports/www-audit/receipts/audit_20260707T235714Z.json`, `reports/www-audit/snapshots/live/crawl_index.json`, `reports/www-audit/snapshots/disk/home.html`, `reports/www-audit/snapshots/live/home.html`, `reports/www-audit/snapshots/disk/trust_brief_intake.html`, `reports/www-audit/snapshots/live/trust_brief_intake.html` |
| scripts/ | 278 | 1.5MB | `scripts/rebuild-www-v6.py`, `scripts/market_success_1000_data.py`, `scripts/generate-tier1-smart-pack.py`, `scripts/generate-noetfield-1000-prompts.py`, `scripts/generate-prompt-catalog-500.py`, `scripts/generate_batch_006_sot.py` |
| .agents/ | 322 | 1.4MB | `.agents/skills/wrangler/SKILL.md`, `.agents/skills/cloudflare/references/flagship/patterns.md`, `.agents/skills/cloudflare/references/r2-sql/SKILL.md.backup`, `.agents/skills/cloudflare/references/flagship/api.md`, `.agents/skills/cloudflare/SKILL.md`, `.agents/skills/cloudflare/references/realtimekit/api.md` |
| services/ | 118 | 611.3KB | `services/governance/noetfield_governance/api.py`, `services/governance/noetfield_governance/trust_ledger.py`, `services/governance/noetfield_governance/analytics_store.py`, `services/graph/noetfield_graph/mutation.py`, `services/governance/noetfield_governance/chatbot_knowledge.py`, `services/factories/noetfield_factories/nodes.py` |
| assets/ | 62 | 443.6KB | `assets/noetfield-www.css`, `assets/noetfield-live-proof.js`, `assets/noetfield-enterprise.css`, `assets/noetfield-shell.js`, `assets/pages/institutional-2026.css`, `assets/noetfield-shell.css` |
| Noetfield-All-Documents/ | 245 | 382.7KB | `Noetfield-All-Documents/registry/source_document_inventory.json`, `Noetfield-All-Documents/registry/active_rule_candidates.json`, `Noetfield-All-Documents/registry/source_of_truth_registry.json`, `Noetfield-All-Documents/MANIFEST.md`, `Noetfield-All-Documents/uploaded/2026-05-batch-020/noetfield-sot-master-document-v1.md`, `Noetfield-All-Documents/uploaded/2026-05-batch-020/noetfield-unified-cognitive-governance-system-v1.md` |
| L2-knowledge/ | 462 | 248.3KB | `L2-knowledge/strategy/full/2026-05-batch-020/noetfield-sot-master-document-v1.md`, `L2-knowledge/strategy/noetfield/2026-05-batch-020/noetfield-sot-master-document-v1.md`, `L2-knowledge/strategy/full/2026-05-batch-020/noetfield-unified-cognitive-governance-system-v1.md`, `L2-knowledge/strategy/noetfield/2026-05-batch-020/noetfield-unified-cognitive-governance-system-v1.md`, `L2-knowledge/strategy/full/2026-05-batch-001/wp-03-npl-formal-grammar-2026-05-npl-1.md`, `L2-knowledge/strategy/noetfield/2026-05-batch-001/wp-03-npl-formal-grammar-2026-05-npl-1.md` |
| trust-ledger/ | 14 | 246.0KB | `trust-ledger/sample-report/ledger-entry.2.pdf`, `trust-ledger/sample-report/board-memo.pdf`, `trust-ledger/sample-report/ledger-entry.pdf`, `trust-ledger/index.html`, `trust-ledger/sample-report/index.html`, `trust-ledger/verify/index.html` |
| tests/ | 71 | 236.6KB | `tests/unit/test_source_of_truth_registry.py`, `tests/unit/test_public_chat.py`, `tests/unit/test_public_gtm_alignment.py`, `tests/unit/test_chat_scenarios.py`, `tests/unit/test_trust_ledger_v1.py`, `tests/unit/test_factory_copilot.py` |
| functions/ | 16 | 142.6KB | `functions/api/intake.js`, `functions/api/intake/health.js`, `functions/api/demo/evaluate.js`, `functions/api/demo/ssot-change.js`, `functions/api/public/chat.js`, `functions/api/gate/ai-factory-design.js` |
| .cursor/ | 53 | 88.4KB | `.cursor/agent-memory/MEMORY_LOCKED.yaml`, `.cursor/incidents/INCIDENT-2026-07-06-001-www-sandbox-downgrade.md`, `.cursor/AGENT_TRACKING.md`, `.cursor/skills/SKILL-007-auto-conflict-resolution.md`, `.cursor/incidents/INCIDENT-2026-06-06-002-unauthorized-disk-edits.md`, `.cursor/incidents/INCIDENT-2026-06-06-001-trustfield-scope-bleed.md` |
| governance/ | 19 | 88.4KB | `governance/index.html`, `governance/NODE_CATALOG.json`, `governance/AUTOMATION_SURFACES_LOCKED.json`, `governance/NOETFIELD_LIVE_NERVE_RECEIPT.json`, `governance/FACTORY_CATALOG.json`, `governance/PUBLIC_OUTPUT_DENYLIST.json` |
| tools/ | 2 | 84.3KB | `tools/pr-conflict-resolver-report/report.html`, `tools/pr-conflict-resolver-report/open-report.sh` |
| copilot/ | 20 | 83.7KB | `copilot/pilot/index.html`, `copilot/procurement/index.html`, `copilot/demo/index.html`, `copilot/index.html`, `copilot/trial/index.html`, `copilot/sme/index.html` |
| gate/ | 36 | 83.3KB | `gate/partners/pack/co-sell-play.pdf`, `gate/procurement/contracting-notes.pdf`, `gate/intake/index.html`, `gate/procurement/security-privacy-summary.pdf`, `gate/procurement/procurement-pack.pdf`, `gate/diligence/index.html` |
| packages/ | 48 | 78.9KB | `packages/config/noetfield_config/__init__.py`, `packages/sdk/examples/local_governance_scaffold.py`, `packages/sdk/noetfield_sdk/client.py`, `packages/schemas/tle-v1.schema.json`, `packages/schemas/factories/copilot_governance_readiness_v1.yaml`, `packages/types/noetfield_types/domain.py` |
| infrastructure/ | 24 | 60.4KB | `infrastructure/supabase/migrations/0001_noetfield_v3_1_foundation.sql`, `infrastructure/supabase/migrations/0008_observability_tables.sql`, `infrastructure/supabase/migrations/0010_public_analytics_funnel_tables.sql`, `infrastructure/supabase/migrations/0002_phase_3_runtime_activation.sql`, `infrastructure/supabase/migrations/0004_source_of_truth_registry.sql`, `infrastructure/supabase/migrations/0003_phase_3_1_backend_core.sql` |
| data/ | 31 | 54.9KB | `data/chatbot/MANIFEST.json`, `data/nf_orient_routing_v1.json`, `data/www-positioning-verdict-matrix-v1.json`, `data/chatbot/knowledge/faq.md`, `data/chatbot/knowledge/pricing-matrix.md`, `data/nf_cleanup_dimensions_v1.json` |
| prompts/ | 2 | 50.6KB | `prompts/loop-suggestions-100.json`, `prompts/loop-pack-10-active.json` |
| api/ | 18 | 50.5KB | `api/_lib/governance-evaluate.js`, `api/public/chat/index.js`, `api/_lib/intake-email.js`, `api/_lib/intake-telegram.js`, `api/intake.js`, `api/_lib/ai-factory-core.js` |
| trust-brief/ | 2 | 39.6KB | `trust-brief/intake/index.html`, `trust-brief/index.html` |
| investors/ | 2 | 33.8KB | `investors/index.html`, `investors/diligence/index.html` |
| demos/ | 8 | 30.3KB | `demos/copilot-governance/generated/demo_output.json`, `demos/copilot-governance/ssot/generated/demo_output.json`, `demos/copilot-governance/sample_deliverable_shape.json`, `demos/copilot-governance/sample_copilot_signal.json`, `demos/copilot-governance/ssot/pending_evaluations.json`, `demos/copilot-governance/template/manifest.json` |
| .github/ | 22 | 21.7KB | `.github/workflows/phase-3-runtime.yml`, `.github/workflows/platform-deploy.yml`, `.github/workflows/trust-ledger-ci.yml`, `.github/workflows/supabase-heartbeat.yml`, `.github/workflows/nf-kaizen-nightly.yml`, `.github/workflows/nf-probe-sync-expected-sha.yml` |
| ai-value-governance-os/ | 1 | 18.8KB | `ai-value-governance-os/index.html` |
| infra/ | 5 | 18.7KB | `infra/nf-probe-cron/src/probes.js`, `infra/nf-probe-cron/src/index.js`, `infra/cf-www-proxy/src/worker.js`, `infra/nf-probe-cron/wrangler.toml`, `infra/cf-www-proxy/wrangler.toml` |
| ops/ | 13 | 18.3KB | `ops/templates/msb/OUTREACH_EMAILS.md`, `ops/templates/msb/INTAKE_RESPONSE_TEMPLATES.md`, `ops/templates/msb/MSB_PARTNER_ONE_PAGER.md`, `ops/templates/msb/SHADOW_PACK_SOW_TEMPLATE.md`, `ops/README.md`, `ops/templates/msb/STAGING_PROOF_RUNBOOK.md` |
| start/ | 1 | 17.5KB | `start/index.html` |
| work-with-us/ | 1 | 15.6KB | `work-with-us/index.html` |
| pricing/ | 1 | 15.1KB | `pricing/index.html` |
| structure/ | 1 | 14.1KB | `structure/index.html` |
| ai-factories/ | 2 | 11.8KB | `ai-factories/index.html`, `ai-factories/spec/index.html` |
| trust/ | 1 | 11.1KB | `trust/index.html` |
| intelligence/ | 2 | 11.0KB | `intelligence/intake/index.html`, `intelligence/index.html` |
| next/ | 1 | 10.3KB | `next/index.html` |
| federal/ | 1 | 9.1KB | `federal/index.html` |
| msp/ | 1 | 9.0KB | `msp/index.html` |
| auth/ | 5 | 8.9KB | `auth/sign-in/index.html`, `auth/sign-up/index.html`, `auth/callback/index.html`, `auth/sign-out/index.html`, `auth/index.html` |
| L0-law/ | 3 | 7.9KB | `L0-law/PUBLIC_WWW_BRAND_E2E_LAW_LOCKED_v1.md`, `L0-law/CURRENT.md`, `L0-law/README.md` |
| enterprise/ | 1 | 7.7KB | `enterprise/index.html` |
| runtime/ | 1 | 7.7KB | `runtime/index.html` |
| platform/ | 3 | 7.6KB | `platform/factories/index.html`, `platform/dashboard/index.html`, `platform/index.html` |
| ai-automation/ | 1 | 6.3KB | `ai-automation/index.html` |
| admin/ | 1 | 6.2KB | `admin/traction/index.html` |
| bank-pilot/ | 1 | 6.2KB | `bank-pilot/index.html` |
| status/ | 1 | 6.1KB | `status/index.html` |
| console/ | 1 | 6.0KB | `console/index.html` |
| contact/ | 1 | 5.6KB | `contact/index.html` |
| partners/ | 1 | 5.4KB | `partners/index.html` |
| templates/ | 1 | 5.4KB | `templates/index.html` |
| banner/ | 1 | 5.3KB | `banner/index.html` |
| factory/ | 1 | 4.8KB | `factory/index.html` |
| faq/ | 1 | 4.5KB | `faq/index.html` |
| about/ | 1 | 4.4KB | `about/index.html` |
| privacy/ | 1 | 4.3KB | `privacy/index.html` |
| terms/ | 1 | 4.2KB | `terms/index.html` |
| playbook/ | 10 | 3.6KB | `playbook/ai-policy/index.html`, `playbook/board-trust-brief/index.html`, `playbook/eu-ai-act/index.html`, `playbook/index.html`, `playbook/iso-42001/index.html`, `playbook/ledger-schema/index.html` |
| cookies/ | 1 | 2.8KB | `cookies/index.html` |
| gel/ | 1 | 2.4KB | `gel/index.html` |
| entry/ | 1 | 2.0KB | `entry/START_HERE_LOCKED_v1.md` |
| .vscode/ | 3 | 1.5KB | `.vscode/settings.json`, `.vscode/tasks.json`, `.vscode/launch.json` |
| .noetfield/ | 1 | 1.5KB | `.noetfield/agent_manifest.yml` |
| .sina-agent/ | 2 | 1.5KB | `.sina-agent/.cursor/rules/workspace-governance.mdc`, `.sina-agent/README.md` |
| config/ | 2 | 1.3KB | `config/gate-ai-factory-design.json`, `config/status-ai-factory.json` |
| L1-operational/ | 1 | 708B | `L1-operational/README.md` |
| for-whom/ | 2 | 678B | `for-whom/index.html`, `for-whom/mandate/index.html` |
| portal/ | 2 | 678B | `portal/index.html`, `portal/login/index.html` |
| .agent-policy/ | 1 | 623B | `.agent-policy/dispatch-templates/ADVISOR_ARCHITECT_CHECKLIST.md` |
| L3-external/ | 1 | 501B | `L3-external/README.md` |
| feedback/ | 1 | 422B | `feedback/index.html` |
| resources/ | 1 | 372B | `resources/index.html` |
| thanks/ | 1 | 339B | `thanks/index.html` |
| login/ | 1 | 339B | `login/index.html` |
| accessibility/ | 1 | 339B | `accessibility/index.html` |
| policies/ | 1 | 339B | `policies/index.html` |
| signup/ | 1 | 339B | `signup/index.html` |
| directory/ | 1 | 339B | `directory/index.html` |
| app/ | 1 | 339B | `app/index.html` |
| kits/ | 1 | 339B | `kits/index.html` |
| ex/ | 1 | 339B | `ex/index.html` |
| receipts/ | 1 | 0B | `receipts/.gitkeep` |
| (root files) | 55 | 406.3KB | `package-lock.json`, `noetfield-gate-512.png`, `noetfield-og.png`, `index.html`, `PLATFORM_BLUEPRINT.md`, `Makefile` |

## Dependency / reference edges

21196 static repo-relative path references were detected across .py/.sh/.md/.json/.yaml/.yml/.jsonc files (best-effort regex scan, not a real import graph — this is a governance/docs-heavy repo, not a single-language codebase). Full edge list is in `graph_index_v1.json`; query by file or subsystem with the query script rather than reading it directly.

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

Rebuild whenever the file layout changes materially (new subsystem, large doc/data additions) — this report drifts from truth otherwise. See `docs/L0_REPO_GRAPH_MEMORY_v1.md` for the token budget rule and the broad-read prevention rule.
