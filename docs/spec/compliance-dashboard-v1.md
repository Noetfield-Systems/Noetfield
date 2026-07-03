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

# Compliance Dashboard v1 — Wireframe Spec

**Scope:** Design-only heatmap for Copilot Governance Pack. No React requirement in v1; governance console pages may link here.

## Layout

```
+------------------------------------------------------------------+
|  Copilot Governance — Compliance Overview          [tenant slug] |
+------------------------------------------------------------------+
|  [Allow] [Review] [Deny]   KPI tiles (last 7d evaluate counts)   |
+------------------------------------------------------------------+
|  Control heatmap (rows=controls, cols=severity x status)          |
|  COP-DLP-001    [====] high / open                                 |
|  COP-SCOPE-002  [==  ] medium / mitigating                         |
|  ...                                                               |
+------------------------------------------------------------------+
|  Open workflows (QuickScan / Readiness) | SLA breach count         |
+------------------------------------------------------------------+
|  Recent RIDs (table) → link to /audit/{rid}                        |
+------------------------------------------------------------------+
```

## Data sources (read API v1)

- `GET /audit` — tenant-scoped events
- Policy pack binding (future): `policy_id` + `version` on evaluate metadata
- Workflow service: `workflow_type` in `copilot_quickscan`, `copilot_readiness`

## Heatmap rules

- **Green:** control test passed in last 30d with evidence attached
- **Amber:** evaluate `review` mapped to control via `evaluate_reason_map`
- **Red:** `deny` or missing evidence for HITL control

## Non-goals

- Payment or ledger KPIs (Lane C deferred)
- Real-time M365 sync (connector design only)
