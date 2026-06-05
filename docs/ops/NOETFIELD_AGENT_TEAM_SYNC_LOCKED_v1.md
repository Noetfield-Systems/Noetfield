---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
agent_role: local-repo-chat-mac
doc_id: agent-team-sync-locked-v1
doc_revision: 2
last_edited_at: "2026-06-06"
provenance: local-only
committed: true
---

> **Authored by:** `[NF-LOCAL-REPO-AGENT]` — local repo chat (Mac). **Cloud agent:** sign your edits `[NF-CLOUD-AGENT]`; do not overwrite this file without UKE + `doc_revision` bump.

# Noetfield agent team sync (LOCKED v1)

**Status:** LOCKED — committed so **cloud Cursor agent** can read without Mac Desktop  
**Tagging:** [NOETFIELD_AGENT_TAGGING_LOCKED.md](../../../ops/private/agent-reference/NOETFIELD_AGENT_TAGGING_LOCKED.md) (private) — every doc must carry `agent_tag`  
**Locked:** 2026-06-05  
**Full private corpus:** `ops/private/agent-reference/` (gitignored — on workspace disk when founder/cloud share same folder)  
**Do not** put secrets, `ops/private/` raw essays, or tunnel URLs in this file.

---

## One team, two runtimes

| Runtime | Role |
|---------|------|
| **Local (Mac)** | verify-gtm · ingest · sync-sourceA · update private LOCKED_PLANS · update this manifest revision |
| **Cloud (VM)** | verify-gtm · implement · update private plans if `ops/private/` on workspace · set `founder_ingest_required` |

**Self-heal:** `plan.json` + `make verify-gtm` beat chat memory. Reconcile on every session start.

---

## In charge (summary)

| Tier | Docs |
|------|------|
| L0 | `PRODUCT_TRUTH.md`, `NORTH_STAR.md`, `OFFERINGS_LOCKED.md`, `PROJECT_BOUNDARIES_LOCKED.md` |
| L1 | `NOETFIELD_GTM_60_DAY_LOCKED_v1.md`, `NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md` |
| L2 | `GOVERNANCE_SOURCES_BOOK_v1.md`, `GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md`, `GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md` (four 2026 blueprints) |
| L3 | `os/plan.json`, `os/SHIP_NOW.md`, `NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md` |
| L4 private | `ops/private/agent-reference/` — scope, UKE, drift map, LOCKED_PLANS, `blueprints/` annexes |
| Cloud blueprints | `docs/ops/NOETFIELD_DRIFT_BLUEPRINTS_CLOUD_READ_ORDER_LOCKED_v1.md` |

**Noetfield only.** TrustField / VIRLUX = separate companies — never implement in this repo.

---

## Shipped waves (locked summary)

| Wave | Highlights |
|------|------------|
| 028–033 | M365 ingest, PDF v2, RBAC chain, signature_block, staging-smoke, alembic |
| 034–036 | Procurement ZIP, demo page, `make demo-url` |
| 037–039 | Buyer pack, workspace UX, `make verify-gtm` |
| 040–042 | Design partner SOW, copilot hub, homepage CTA |

**`next_tasks`:** empty — repopulate only via founder "PLAN WITH NO ASF".

**Verify:** `make verify-gtm` or `make ship-verify` (alias — same `scripts/verify-gtm.sh`)

---

## Private locked plans index (full text on workspace disk)

| Plan ID | Purpose |
|---------|---------|
| `no-asf-operating-model` | NO ASF ship loop |
| `waves-028-042-shipped` | Shipped wave summary |
| `wave-template-no-asf` | Copy for next sprint |
| `uke-locked` | Unifying knowledge engine rules |
| `agent-team-self-heal` | Local/cloud correction protocol |

Path: `ops/private/agent-reference/LOCKED_PLANS/`  
Registry: `ops/private/agent-reference/LOCKED_PLANS_REGISTRY.yaml`  
Live state: `ops/private/agent-reference/AGENT_TEAM_STATE.yaml`

---

## Cloud without `ops/private/`

1. Use **this file** + `os/plan.json` + public LOCKED docs  
2. Write `reports/cursor-reply-latest.txt` — founder ingests on Mac  
3. Set in handoff: `founder_ingest_required: true`  
4. Do not claim Mac paths (`~/Desktop/SourceA`, SinaPromptOS) were executed

---

## Sync manifest revision

```yaml
revision: 2
updated_at: "2026-06-06"
reconciliation_revision: 3
last_wave_mac: "040-042"
branch: cursor/bank-grade-fullstack-37f0
mac_head: d399a1b
verify_baseline: make verify-gtm  # alias make ship-verify
cloud_ahead: NF-PLAN-011x + QUICK_PICK claimed — verify after merge PR #25
private_plans: ops/private/agent-reference/plans/LOCKED_PLANS_INTERNAL.yaml
repo_truth_log: ops/private/agent-reference/REPO_TRUTH_CORRECTIONS.md
```

**Local agent:** bump `revision` when LOCKED_PLANS or waves change, then commit this file.

---

## Reputation

When unsure what goes online → say less. No sister-company names. No unverified stats. See private `NOETFIELD_REPUTATION_AND_DISCLOSURE_GUARD.md` on workspace disk.

---

*Agents: read this in cloud; read full `agent-reference/` on Mac/shared workspace.*
