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

# Human Gatekeeper UI Wireframe v1

Document key: `noetfield-human-gatekeeper-ui-wireframe-v1`

Single-pane triage and approval for solo founder / steward.

## Screens

1. **Triage Queue** — priority, artifact, drift sparkline, risk(t), Evidence Pack link, quick approve/defer
2. **Artifact Detail** — time slider, structural + semantic diff, drift chart, recommendations
3. **Approval Modal** — approve (HSM sign), reject, request more info → event store
4. **Replay & Export** — simulate/export window → Evidence Pack generation

Keyboard-first; mobile push for critical drift. Founder is default steward assignee.
