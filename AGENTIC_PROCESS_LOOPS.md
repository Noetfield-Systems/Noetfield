AGENTIC_PROCESS_LOOPS — Draft
=============================

Status: DRAFT — inert until founder commits to SSOT.
canon_version: DRAFT-0

Purpose
-------
Practical, minimal loops that let machines and agents validate, act, learn, and expand autonomy without routing routine work back to Sina. This patches the process layer first (advisors/architects), before agent laws.

Default Question
----------------
"How does the process solve this without Sina?"

Minimum Founder Triggers
- Reserved for capital/legal commitments, irreversible L5 actions, and phase unlocks. All other proposals must define how the system retires founder triggers (technical debt plan + receipts).

Loops (concise)
---------------

1) Worker Execution Loop
- Purpose: run repeatable tasks safely in disposable lanes.
- Steps: schedule -> provision disposable lane -> run task -> emit receipts -> auto-teardown.
- Success criteria: deterministic outputs + sandbox receipt containing inputs, versions, logs, and artifacts.

2) Machine Validation Loop
- Purpose: automated checks before and after execution (types, contracts, invariants).
- Steps: pre-validate -> dry-run in sandbox -> run -> post-validate -> flag anomalies -> generate remediation proposal.
- Failure mode: create a reproducible failing-receipt and route to self-repair/adversarial critique loop, not to founder.

3) Adversarial Critique Loop
- Purpose: find design/logic weaknesses via red-team style probes.
- Steps: snapshot artifact -> adversarial runner probes -> synthesize counterexamples -> produce prioritized defects + sandbox repros.
- Usage: periodic and pre-merge for high-risk changes.

4) Self-Repair Loop
- Purpose: automated corrective actions for common failures.
- Steps: detect -> classify -> select repair candidate -> sandbox-apply patch -> run validation -> publish repair receipt.
- Guardrail: human-in-the-loop only for repairs that touch irreversible L5 or legal/capital surfaces.

5) Outside Audit / Advisory Loop
- Purpose: bring external expertise for non-routine, high-uncertainty matters.
- Steps: prepare audit bundle (receipts + artifacts) -> external advisor runs in sandbox -> advisory receipt with citations.
- Constraint: external auditors operate on disposable lanes and produce receipts; they do not gain runtime authority.

6) Deep Research Loop (for uncertainty)
- Purpose: pursue investigations that require extended compute or human research.
- Steps: hypothesis -> lightweight experiments -> evidence receipts -> meta-report with recommended actions and confidence bands.

7) Receipt-Based Proof Loop
- Purpose: make evidence the unit of trust and autonomy expansion.
- Steps: mandate standard receipt schema (inputs, versions, actor, canon_version, timestamp, evidence links) -> store indexed receipts -> use receipts as input for automated governance and earned autonomy checks.

8) Earned Autonomy Expansion Loop
- Purpose: expand agent permissions based on historical, verifiable receipts.
- Steps: define metrics & thresholds -> evaluate receipts -> grant sandboxed wider scopes -> monitor -> promote or revoke.
- Requirement: all promotions must include a rollback plan and a retirement plan for any founder triggers introduced.

Process Rules
-------------
- Always answer the Default Question in every proposal and receipt.
- Every proposal must include: (a) sandbox execution plan or repro, (b) receipt(s) demonstrating the behavior, (c) a retirement plan for any founder triggers.
- Minimize founder triggers; if present, proposals must list the exact technical debt and the automated plan + timeframe to retire them.
- Do not escalate normal validation, repair, audit, or uncertainty to Sina. Use the loops above; only escalate when founder-trigger limits are hit.

Metadata & Receipt Requirements
-------------------------------
- `canon_version`: the canon used for reasoning (required).
- `actor`, `timestamp`, `evidence` (sandbox links), `outcome`, `confidence` (optional).
- Index receipts so they can be queried for earned-autonomy evaluations.

Example Minimal Proposal Checklist
---------------------------------
- Default Question answered: YES/NO + short justification
- Sandbox plan: link to disposable lane + command
- Receipt: link(s) to sandbox run evidence
- Founder trigger: NONE or explicit listing + retirement plan
- canon_version: string

Scope & Limits
--------------
- This document hardens the process layer only. It is DRAFT and INERT until founder commits to SSOT. Do not change agent runtime laws here; first validate these loops with advisors/architects.

End of Draft
