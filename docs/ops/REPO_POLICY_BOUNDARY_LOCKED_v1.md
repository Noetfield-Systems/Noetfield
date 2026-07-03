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
doc_id: repo-policy-boundary-locked-v1
status: LOCKED
---

> **Authored by:** [NF-LOCAL-REPO-AGENT] - 2026-06-28

# Repo Policy Boundary - LOCKED v1

## Purpose

Persist the repo-local cleanup, agent, and boundary policy without redefining this repository from chat memory or outside assumptions.

Machine source:

```text
repo-policy.json
```

Validator:

```bash
python3 scripts/check_repo_policy.py
```

## Authority Used

- `README.md`
- `PROJECT_BOUNDARIES_LOCKED.md`
- `ROUTING_CARD.md`
- `docs/DOC_UNIFIED_INDEX_LOCKED_v1.md`
- `docs/ops/NOETFIELD_OWNERSHIP_SYNC_CHARTER_LOCKED_v1.md`
- `docs/ops/NOETFIELD_LIVE_NERVE_HANDOFF_LOCKED_v1.md`
- `docs/ops/NOETFIELD_CANONICAL_SHIP_REPO_LOCKED_v1.md`
- `docs/ops/AGENT_DOC_TAGGING_LOCKED_v1.md`
- `.cursor/rules/nf-authority-stack.mdc`
- `.cursor/rules/nf-anti-staleness-max.mdc`
- `.cursor/rules/noetfield-agent-doc-tagging.mdc`
- `package.json`, `vercel.json`, `railway.toml`, `.vercelignore`, `Makefile`

## Policy

1. Repo-owned work stays in this repo.
2. Other products, entities, or repos do not become active work here unless repo-local contracts, exports, manifests, APIs, receipts, or locked handoffs say so.
3. Generated, evidence, backlog, and archive outputs use snapshots plus manifests or tracked receipts, not loose dirty files.
4. Cross-repo dependencies use contracts, exports, manifests, APIs, live receipts, or locked handoffs. They must not depend on another repo's private scripts as this repo's execution path.
5. Use one lane per pass.
6. Keep each coherent pass to 20-40 changed files maximum.
7. Use one atomic commit per coherent lane when committing is requested.
8. Use high intelligence for decisions, reviews, and policy interpretation; use deterministic validators, manifests, and receipts for bulk scanning.

## Claims Avoided

- This policy does not claim this repo owns GEL runtime implementation beyond website/platform integration.
- This policy does not claim SourceA, TrustField, VIRLUX, Noetfield OS, or Studio IDE active work belongs in this repo.
- This policy does not claim generated receipts are always commit-ready without manifest/snapshot policy.
