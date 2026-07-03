FOUNDER_CANON — Draft
=====================

Status: DRAFT — inert until founder commits to SSOT.
canon_version: DRAFT-0

Purpose
-------
Short, injectible founder guidance to harden goals before architecture or agent reasoning. This is a slim, referential artifact; it does not replace governed doctrine or SSOT.

Core Principles
---------------
- Goal Is Not Authority: goals communicate intent and priorities — they do not grant runtime or policy authority. Authority remains defined and scoped in the SSOT and governed-autorun artifacts.
- Sandbox-First: default to experimental, non-production sandboxes for design and evaluation. Agents and advisors should prefer safe failure, reproducible receipts, and rollbackable experiments over blocking production changes.
- Founder Role: the founder is a merge / L5 / phase authority — responsible for final merges, phase approvals, and strategic direction. The founder is NOT a runtime babysitter; day-to-day runtime operations, incidents, and on-call are handled by designated runtime teams and automated governance.

Operational Requirements for Agents, Architects & Advisors
---------------------------------------------------------
- Cite Canon Version: every architect/advisor/agent output MUST explicitly state the `canon_version` it reasoned against.
- Receipt Metadata: every receipt produced by an agent or system MUST include `canon_version` (string) alongside other standard receipt fields (timestamp, actor, outcome, evidence links).
- Reference, Don't Restate: avoid restating full doctrine. When reasoning, link or pointer to the governed-autorun v3 and the applicable SSOT doc versions (use versioned pointers). Prefer concise citations over embedding policy text.
- Sandbox Evidence: outputs that propose changes must include at least one sandbox execution plan or repro receipt demonstrating the proposal in a non-production environment.

Canonical Pointers (by version)
-------------------------------
- governed-autorun v3 — primary operational governance pointer (use versioned pointer in outputs).
- SSOT / Master documents — cite the specific SSOT doc and version relevant to the decision.

Rules for Use
-------------
- This file is a DRAFT. It remains INERT until the founder personally commits it to the SSOT. Do not treat this draft as authoritative or executable governance.
- Do not sign, commit to SSOT, place tokens, or generate execution artifacts from this draft without explicit founder action.

Quick Metadata Example
----------------------
Required fields on receipts/outputs:
- `canon_version`: "governed-autorun_v3"  # the canon the reasoning used
- `actor`: "agent-name or human"
- `timestamp`: "ISO-8601"
- `evidence`: [list of sandbox receipts or repro links]

End of Draft
