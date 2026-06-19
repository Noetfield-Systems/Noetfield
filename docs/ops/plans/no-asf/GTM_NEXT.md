# GTM_NEXT — Tier A queue (post–1000-pack)

When the NF-PLAN registry is fully synced (`1000/1000 done`), pick the next **≤3** agent tasks from here or `os/plan.json` `next_tasks`.

**Authority:** [NOETFIELD_GTM_60_DAY_LOCKED_v1.md](../../../strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md) · [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](../../../WWW_V16_PACKAGING_PLAN_LOCKED_v1.md)  
**Verify:** `./scripts/plan-with-no-asf-verify.sh`

**Commercial P0:** Outreach/calls = agentic layer (founder Hub). NF-CLOUD-AGENT = validators + www/GTM assets only.

**Packaging P0 (shipped v16):** Self-serve `/start/` · `/pricing/` · agentic strip · sandbox JS · inbox routing doc.

## Registry 1000/1000 semantics

`python3 scripts/sync-prompt-pack-status.py` marks all NF-PLAN rows `done` via `expand_done_by_pattern()` — this is **dedup / pattern propagation**, not “all engineering complete.” Real queue lives here and in `os/plan.json` `next_tasks`.

## ID namespace note

`ship-*-NNN` = GTM Tier A queue (`next_tasks`). `nf-*-NNN` in engineering manifest = product waves — numeric suffix overlap is intentional.

## Next GTM Tier A (NF-CLOUD disk) — iter 20 proposals

Founder pick or bounded `implement`:

1. **ship-www-v18-wave-b-063** · Command Center Shell 2.0 + design token unification  
   Outcome: Product UI matches www tier-1 bar.

1. **ship-stripe-webhook-prod-064** · Configure `STRIPE_WEBHOOK_SECRET` on platform + Stripe dashboard endpoint  
   Outcome: Post-checkout auto-notify operations@.

1. **ship-resend-form-delivery-065** · Founder Vercel env — flip OPS_LIVE form_delivery to live  
   Outcome: `www_email_configured: true` on `/status/`.

## Shipped iter 19 (10-step wave @ main)

| ID | Shipped |
|----|---------|
| ship-sandbox-server-side-057 | Sandbox API + `SANDBOX_PRODUCTION_PERSISTENCE.md` + status health widget |
| ship-agentic-workflow-manifest-058 | `noetfield-agent-manifest.json` on `/start/` |
| ship-procurement-openapi-verify-060 | `verify-procurement-openapi.sh` |
| ship-services-governance-readme-openapi-061 | README + procurement OpenAPI links (already wired) |

## Prior iter 19 proposals (superseded by 10-step ship)

## Agentic only — Hub (not NF-CLOUD implement)

| ID | Owner | Outcome |
|----|-------|---------|
| **ship-design-partner-outreach-026** | Agentic layer | One named CIO contact + demo URL sent; tracker row updated |
| **ship-sandbox-nurture-060** | Agentic layer | Email template for sandbox → design partner upgrade (founder approve) |

Evidence: [DESIGN_PARTNER_PIPELINE_v1.md](../../../copilot/DESIGN_PARTNER_PIPELINE_v1.md) · [AGENTIC_COMMERCIAL_HANDOFF_v1.md](../../AGENTIC_COMMERCIAL_HANDOFF_v1.md) · [COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md](../../COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md)

## Recently shipped (iter 18 — v16 packaging)

| ID | Shipped |
|----|---------|
| ship-v16-packaging-www-057 | `/start/` · `/pricing/` · self-serve rail · agentic block · v16 CSS/JS |
| ship-v16-prompt-pack-058 | WISE/500/inbox/memory/docs aligned to packaging funnel |
| ship-v16-verify-e2e-059 | verify-ui-e2e + verify-static-www v16 needles |

## Recently shipped (iter 18)

| ID | Shipped |
|----|---------|
| ship-procurement-checkpoint-verify-054 | Hardened checkpoint verify guards on procurement |
| ship-services-governance-openapi-bridge-055 | Procurement OpenAPI + services/governance README links |
| ship-merged-window-config-056 | MERGED_WINDOW constant in OPEN_PRS header |

## Recently shipped (iter 17)

| ID | Shipped |
|----|---------|
| ship-blueprint-services-governance-bridge-051 | services/governance README + blueprint §8.3 prod row |
| ship-procurement-control-checkpoint-copy-052 | Procurement eval+enforce control checkpoint copy |
| ship-merged-pr-window-five-053 | Rolling top-5 merged PR window in coherence verify |

## Prior shipped (iter 16 and earlier)

See git history · [SHIP_NOW.md](../../../os/SHIP_NOW.md)
