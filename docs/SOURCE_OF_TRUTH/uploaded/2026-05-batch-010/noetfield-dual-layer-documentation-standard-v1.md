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

# Noetfield Dual-Layer Documentation Standard v1.0

Document key: `noetfield-dual-layer-documentation-standard-v1`

Industry-grade spec separating Vision (WHY/WHAT/OUTCOME) from Engineering (HOW/TRUTH).

## Canonical structure

Every document: A Vision Layer, B Engineering Layer, C Traceability Map, D Governance Metadata.

## Vision rules

No implementation details, schemas, DB, or APIs. Readable by non-engineers.

## Engineering rules

Fully technical, deterministic, testable. No narrative language.

## Traceability rule

If any Vision element lacks Engineering mapping → document is INVALID.

## Layer priority

Engineering overrides Vision on execution conflicts. Authoritative layer: Engineering only.
