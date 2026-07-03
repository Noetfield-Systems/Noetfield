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

# Noetfield v3 MVP — Final Production Spec

Document key: `noetfield-v3-mvp-production-spec-final`

**Active v3 product SOT.** Linear pipeline: Intent → Orchestrator → rule router → sequential execution
→ single governance PASS/FAIL → append-only ledger. Explicitly excludes DAG compiler, scoring router,
microservices for MVP ship. Buildable in 48h; FastAPI single service.
