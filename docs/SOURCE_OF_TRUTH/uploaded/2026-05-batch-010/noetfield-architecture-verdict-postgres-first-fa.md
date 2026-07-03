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

# Architecture Verdict — Postgres-First (Persian)

Document key: `noetfield-architecture-verdict-postgres-first-fa`

Reference analysis (FA): Postgres-first + pgvector inside PG aligns with Stripe/Temporal-style
single source of truth. Timescale must remain extension-only, not split truth path.
