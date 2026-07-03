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
doc_id: noetfield-canonical-ship-repo-locked-v1
doc_revision: 1
last_edited_at: "2026-06-07"
provenance: local-only
committed: true
---

> **Authored by:** `[NF-LOCAL-REPO-AGENT]` — ASF lock 2026-06-07

# Noetfield canonical ship repo (LOCKED v1)

**Status:** LOCKED — resolves pick-script vs runbook path drift for `noetfield_local`  
**Agent:** `noetfield_local` · workspace `Noetfield-All-Documents`  
**Supersedes:** ad-hoc answers citing `~/Desktop/Noetfield` as primary for this workspace

---

## Locked Q&A

**Q:** Which folder should the agent treat as the canonical ship repo for this turn?  
(Pick script works in `Noetfield-All-Documents/Noetfield`; runbook says `~/Desktop/Noetfield`.)

**A (LOCKED):** **`Noetfield-All-Documents/Noetfield`** — the **current workspace subfolder**.

| Field | Value |
|-------|-------|
| **Relative (workspace)** | `Noetfield-All-Documents/Noetfield` |
| **Absolute** | `/Users/sinakazemnezhad/Desktop/Noetfield-All-Documents/Noetfield` |
| **Pick script CWD** | Run `pick` / `plan-no-asf-run` from this subfolder |
| **REGISTRY / plan.json** | `Noetfield/os/plan.json` · `Noetfield/os/plan-library/noetfield-1000/` |

---

## Two-repo law (unchanged lanes)

| Lane | Agent id | Canonical ship repo | Forbidden |
|------|----------|---------------------|-----------|
| **Local loop (this workspace)** | `noetfield_local` | `Noetfield-All-Documents/Noetfield` | `~/Desktop/Noetfield` |
| **Cloud GitHub ship** | `noetfield_cloud` | `~/Desktop/Noetfield` | `Noetfield-All-Documents` |

**Runbook paths** that say `~/Desktop/Noetfield` apply to **`noetfield_cloud`** only — not `noetfield_local` turns.

---

## Agent checklist (every turn)

1. Confirm Cursor workspace root is `Noetfield-All-Documents`.
2. Treat **`Noetfield/`** subfolder as canonical ship repo for pick, verify, and code edits.
3. Do **not** switch primary work to `~/Desktop/Noetfield` from this chat.
4. Cloud merge/deploy: hand off to `noetfield_cloud` agent — not inline from local.

---

## Cross-refs

- `~/Desktop/Noetfield-All-Documents/NOETFIELD_TWO_REPOS.md`
- `~/.sina/agent-workspaces/noetfield_local/GOVERNANCE_LOCKED.md` § Canonical ship repo
- `Noetfield/docs/ops/NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md`
