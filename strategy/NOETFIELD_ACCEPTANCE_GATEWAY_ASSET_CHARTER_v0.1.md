# NOETFIELD_ACCEPTANCE_GATEWAY_ASSET_CHARTER_v0.1

Status: CANONICAL CHARTER · v0.1 · scoping only.
Explicitly authorized in this pass: definition. Explicitly NOT authorized:
implementation, code, adapters, deployment, public copy, outreach use.
Versioning: immutable once merged; changes require v0.2+.

## Purpose

The Acceptance Gateway is the extraction and productization of primitives
already present in Noetfield into a standalone, provider-neutral strategic
asset: the component that decides whether the exact result of an agentic
execution is acceptable, and preserves the evidence of that decision.

It is an extraction, not an invention. The source pipeline exists in
Noetfield today:

authorized event
→ authority/policy/budget/context envelope
→ bounded executor
→ exact candidate binding
→ separate verifier
→ bounded repair, escalation, or safe stop
→ external human promotion
→ machine-readable receipt

## Inputs

| Input | Meaning |
|---|---|
| authorized_event | The scoped, authorized trigger; never an open prompt |
| authority_envelope | Who may act, delegated limits, escalation paths |
| policy_ref | The resolved policy version applicable to this run |
| budget_and_scope | Spend/time budget and context scope fencing |
| candidate_ref | Reference to the exact candidate artifact or effect |
| candidate_digest | Cryptographic digest binding the exact candidate |
| executor_identity | Identity of the producing worker/executor |
| acceptance_contract | The criteria the candidate must satisfy |
| evidence_bundle | The evidence submitted for evaluation |
| verifier_identity | Identity of the evaluating verifier |

## Decisions

`ACCEPT` · `REPAIR` · `ESCALATE` · `STOP` · `NOT_EVALUABLE`

`NOT_EVALUABLE` is a first-class decision: when required evidence or contract
elements are missing or malformed, the Gateway fails closed with that
decision rather than guessing.

## Outputs

| Output | Meaning |
|---|---|
| decision | One of the five decisions above |
| reason_codes | Machine-readable reasons for the decision |
| criterion_results | Per-criterion pass/fail against the acceptance_contract |
| repair_allowance | Remaining bounded-repair budget, if any |
| promotion_eligibility | Whether the result may be offered for promotion |
| verdict_digest | Digest binding the verdict to the exact candidate |
| evidence_digest | Digest of the evaluated evidence bundle |
| signed_receipt | The machine-readable, signed record of all of the above |

## Non-negotiable invariants

1. The verifier is distinct from the producing worker.
2. The candidate is immutable during verification.
3. The verdict is bound to the exact candidate/effect (digest-bound).
4. Missing required evidence fails closed (`NOT_EVALUABLE`).
5. The Gateway has no promotion authority.
6. Promotion remains outside both executor and verifier.
7. Repair is bounded and recorded.
8. Provider and model neutrality.
9. Failed and indeterminate attempts remain inspectable.
10. A receipt is not certification.

## Relationship to existing Noetfield systems

The classification of each requirement against what exists today is
maintained in `strategy/noetfield-existing-asset-inventory-v1.json`
(PROVEN_EXISTING / PARTIAL_EXISTING / DESIGNED_NOT_PROVEN / MISSING), with
evidence pointers. The public first-party demonstration of the source
pipeline is https://www.noetfield.com/proof/governed-replacement/.

## Out of scope for v0.1

Implementation and API surface design; SDK; vendor adapters (IBM, NVIDIA,
MCP/A2A); signing key management design; benchmark suite; pricing;
packaging; naming beyond "Acceptance Gateway" as a working title.

## Next gate

Deep Research output determines buyer priority, acquisition whitespace,
proof thresholds, and first integration order. Charter v0.2 (API and
conformance surface) and any implementation start require explicit founder
authorization.
