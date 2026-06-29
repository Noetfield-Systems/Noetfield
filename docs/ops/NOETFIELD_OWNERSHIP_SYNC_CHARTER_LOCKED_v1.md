---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-28"
doc_id: noetfield-ownership-sync-charter-locked-v1
status: LOCKED
---

# Noetfield Ownership Sync Charter - LOCKED v1

## Purpose

Keep Noetfield.com, the Noetfield cloud repo, Noetfield OS, and Studio IDE moving fast without duplicate source-of-truth drift.

## Ownership Ground

| Lane | Owner repo | Owns | Does not own |
|------|------------|------|--------------|
| Public website | `~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/` | `www.noetfield.com`, Vercel project `noetfield`, public copy, public chatbot knowledge, website verification | GEL runtime implementation |
| Platform spine | `~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/` | `platform.noetfield.com`, governance services, public platform docs, intake/chat integration | SourceA internal factory runtime |
| GEL runtime | `~/Projects/noetfeld-os/` | `api.noetfield.com`, FastAPI GEL runtime, `noetfield-gate`, TLE/runtime evidence, NOOS agent vault | Website source or Vercel deploy ownership |
| Studio IDE | `~/Desktop/Noetfield/noetfield-studio-ide/` | Local/desktop Agent IDE on port `3005` | Website truth, GEL runtime truth |
| Foundation patterns | SourceA | Engine patterns, governance receipt patterns, safety law | Default Noetfield.com implementation |

## Live Truth Contract

1. Website truth comes from this repo plus live website verification.
2. GEL runtime truth comes from `~/Projects/noetfeld-os/docs/_NOOS_AGENT/PRODUCT_TRUTH.md` plus `api.noetfield.com` health/readiness.
3. Shared agent status comes from `governance/OPS_LIVE_STATUS_LOCKED.json` and `reports/agent-auto/LIVE-STATUS.md`.
4. Static strategy prose loses to fresh machine receipts and product truth files.
5. If a doc contains both old backlog language and a newer execution receipt, the newer execution receipt wins until the doc is version-refreshed.

## Anti-Duplication Rules

- Do not create a second website source in `noetfeld-os`.
- Do not create a second GEL runtime in the `Noetfield` website repo.
- Do not treat Studio IDE state as product or runtime truth.
- Do not merge SourceA implementation code into Noetfield product repos.
- Do not use legacy `project-gc7lm` or old GEL `:8000` language for live status.

## Agent Grounding Rule

Before editing, every agent states one lane: `website`, `platform-spine`, `gel-runtime`, `studio-ide`, or `foundation-pattern`.

Then read the lane authority:

- `website` / `platform-spine`: `ROUTING_CARD.md`, `reports/agent-auto/LIVE-STATUS.md`, this charter, and the relevant verify target.
- `gel-runtime`: `~/Projects/noetfeld-os/docs/_NOOS_AGENT/PRODUCT_TRUTH.md` and `~/Projects/noetfeld-os/docs/_NOOS_AGENT/NOETFIELD_OS_SSOT_v1_LOCKED.md`.
- `studio-ide`: `~/Desktop/Noetfield/noetfield-studio-ide/AGENTS.md`.
- `foundation-pattern`: SourceA pattern docs only when explicitly required.

## Verification

- Website/public docs: `make verify-static-www`.
- Noetfield tiered ship readiness: `make verify-tier0` through `make verify-tier3` as needed.
- GEL runtime: run the noetfeld-os test/health path after GEL edits.
- Studio IDE: `npm run test` after Studio IDE edits.

## Success Definition

Noetfield.com succeeds when the public website, platform spine, and GEL runtime tell one current story: website sells the evidence, platform coordinates the buyer surface, and Noetfield OS proves the gate and log through `api.noetfield.com`.
