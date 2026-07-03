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

# SoT Engine Repository v1.0

Document key: `sot-engine-repo-v1`

## Stack

FastAPI (`app/`), `sot_miner/` (pattern detection, extractor, validator, scheduler), Supabase (`execution_logs`, `sot_rules`), Telegram integration.

## Core loop

Log execution → detect frequency ≥3 → extract rules → validate → policy inject.

## Registry

Implementation scaffold; superseded as normative architecture by `sot-engine-auto-running-architecture-v1`.
