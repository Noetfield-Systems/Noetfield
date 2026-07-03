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

# Evidence Pack JSON Schema v1

Document key: `noetfield-evidence-pack-json-schema-v1`

Portable, signed, auditor-verifiable package reconstructing governance state for a scope/time window.

## Required fields

`pack_id`, `scope`, `timestamp`, `manifest_sha256`, `snapshots[]`, `events_url`, `lineage_graph`,
`drift_summary`, `decision_logs`, `signatures[]`

## Transport

`pack.json` + `data.tar.gz` + `manifest.sha256` + `manifest.sig` (detached HSM signature).

## Verification

`verify.sh` rehashes files and validates detached signature with public key.

## Signatures

Minimum: snapshot_agent, audit_agent, steward. Aligns with Copilot Governance / Trust Ledger wedge.
