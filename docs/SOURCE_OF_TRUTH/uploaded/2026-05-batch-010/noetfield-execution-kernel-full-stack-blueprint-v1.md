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

# Noetfield Execution Kernel — Full Stack Blueprint v1.0

Document key: `noetfield-execution-kernel-full-stack-blueprint-v1`

Postgres-centered deterministic kernel: immutable events, LLM advisory-only,
policy-governed execution, full replay.

## Stack (initial draft)

PostgreSQL (truth), pgvector (semantic advisory), Timescale (extension-only optimization),
Redis (ephemeral), S3 (archive), LangGraph (runtime).

## Pipeline

Input → LLM proposal → schema gate → policy → risk (advisory) → LangGraph → PG commit → snapshot → S3.

**Superseded by** `noetfield-stack-blueprint-v1-refined-final` for canonical architecture SOT.
