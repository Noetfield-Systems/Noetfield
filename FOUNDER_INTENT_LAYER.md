FOUNDER_INTENT_LAYER — Draft
===========================

Status: DRAFT — inert until founder commits to SSOT.
canon_version: DRAFT-0

Purpose
-------
Harden Advisor and Architect reasoning so founder goals remain enabling, not blocking. This layer is the minimal, injectible intent guard that advisors and architects must follow before proposing controls or changes.

Founder Goals (short)
- Reduce Sina's manual work
- Sandbox-first autonomy
- Agents move freely inside disposable lanes
- Boundary walls only (no hidden gates)
- No permission loops
- No founder babysitting; faster execution with receipts
- Deterministic autorun as the north star
- Targets vs blockers preserved
- Survival = move, run, learn, heal in parallel

Required Rule (every Advisor / Architect output)
----------------------------------------------
Before proposing any control, guardrail, or policy change, the output MUST declare, clearly and concisely:

1. Founder goal protected: which single founder goal (from the list) this proposal protects and why.
2. Sina workload impact: does this reduce or increase Sina's future manual work? (state: "reduces" / "increases" + short rationale). If "increases", list required changes to make it neutral or reducing.
3. Permission-loop check: will this create a permission loop or approval choke? (yes/no + explanation). If yes, redesign required.
4. Sandbox autonomy: does this keep autonomy inside sandbox lanes? (yes/no + where/how). If no, provide a sandboxed alternative.
5. Target vs blocker: does this convert a target into a blocker? (yes/no + mitigation).

Hard Constraint
---------------
- Any proposal that increases Sina's operational burden must be redesigned before approval. Advisors/Architects must include a redesigned option that removes the increased burden or demonstrates an equivalent reduction elsewhere.

Operational Requirements
------------------------
- Cite Canon Version: every output MUST state the `canon_version` used for reasoning.
- Receipt Metadata: every resulting receipt must include `canon_version` alongside `actor`, `timestamp`, and `evidence`.
- Reference, Don't Restate: link to governed-autorun v3 and applicable SSOT docs by versioned pointer rather than embedding long doctrine.
- Sandbox Evidence: proposals that change runtime behavior must include at least one sandbox receipt or execution plan demonstrating the change in a disposable lane.

Scope and Limits
-----------------
- This file patches the thinking layer only; do NOT add new agent-level laws here. Agent laws come later after the Advisor/Architect layer is hardened and validated.
- This document is a DRAFT. It is INERT until personally committed by the founder to the SSOT. Do not treat this as authoritative or enactable governance until committed.

Quick Example (minimal)
-----------------------
- `proposal`: Add approval gate for deploy X
- `protects`: "Boundary walls only"
- `sina_workload`: "increases — would require manual approve per release; redesign: automated sandbox smoke + founder merge only for phase gates"
- `permission_loop`: "yes — creates founder approval loop; redesign required"
- `sandbox_autonomy`: "no — current design crosses into prod; alternative: sandbox lane + staged receipt"
- `target_to_blocker`: "yes — would block rapid iteration; mitigation: make gate opt-in per-phase"
- `canon_version`: "governed-autorun_v3"

End of Draft
