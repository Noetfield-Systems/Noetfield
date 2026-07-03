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

# Noetfield RFC Standard v1.0

Document key: `noetfield-rfc-standard-v1-github-ci`

Machine-verifiable governance: each RFC is a 4-file unit (`vision.md`, `engineering.md`,
`traceability.json`, `metadata.yaml`) under `rfc/RFC-NNNN-slug/`.

## CI gates

- Schema validation (`tools/validator.py`)
- Traceability completeness (`tools/trace-checker.py`)
- Replay safety (`tools/replay-simulator.py`)

## Hard rules

All vision fields mapped; no orphan engineering sections; metadata matches schema;
engineering deterministic; replay-safe or explicitly marked unsafe.

## Lifecycle

Draft → In Review → CI Passed → Approved → Active → Deprecated.
