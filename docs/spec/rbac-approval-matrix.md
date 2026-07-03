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

# RBAC + Approval Matrix (v1 — markdown policy)

Enforced in code incrementally; Copilot pilot uses config + workflow HITL first.

| Action | Role | Approval |
|--------|------|----------|
| `governance.evaluate` | compliance_analyst | none (shadow) |
| QuickScan signoff | compliance_owner | single_human |
| Readiness pack approve | compliance_owner + exec_sponsor | dual_human |
| Policy pack bind | policy_admin | dual_human |
| Agent publish / ledger write | governance_admin | dual_human + `verification_status=verified` |
| Audit export (full) | compliance_owner | single_human |
| Payment / transfer (any) | — | **denied (Lane C)** |

## Severity → HITL

| risk_score | decision | HITL |
|------------|----------|------|
| &lt; 40 | allow | optional |
| 40–69 | review | single_human |
| ≥ 70 | deny | dual_human to override |

## Tenant isolation

All roles scoped by `tenant_id` / `X-Tenant-ID`. Pilot slug: `copilot-pilot-01`.
