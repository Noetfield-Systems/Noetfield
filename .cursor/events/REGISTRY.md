# Agent event registry

Lightweight session and gate audit trail. **Not** a substitute for [incidents](../incidents/REGISTRY.md) — use SKILL-004 for boundary violations.

Schema: [EVENT_SCHEMA.yaml](./EVENT_SCHEMA.yaml) · Skill: [SKILL-010](../skills/SKILL-010-agentic-event-gate.md) · Map: [AGENTIC_ENFORCEMENT_MAP_LOCKED_v1.md](../../docs/ops/AGENTIC_ENFORCEMENT_MAP_LOCKED_v1.md)

## How to file

Add a row to the table below at **session end** or when a gate **fails**. One row per event type per session is enough unless debugging a failed verify.

## Events

| Date | Session ID | Type | Agent | Summary |
|------|------------|------|-------|---------|
| 2026-06-13 | 2026-06-13-agentic-enforcement-v2 | session_end | NF-CLOUD-AGENT | Enforcement v2: map, R-012/R-013, SKILL-010, verify-agent-enforcement, events schema |
| 2026-06-13 | 2026-06-13-agentic-enforcement-v2 | verify_run | NF-CLOUD-AGENT | verify-agent-enforcement.sh — seeded at ship |

## Event types (quick ref)

| Type | When |
|------|------|
| `session_start` | After MEMORY + incidents read |
| `scope_gate_pass` / `scope_gate_fail` | SKILL-001 |
| `rule_conflict` | SKILL-007 |
| `verify_run` | Any verify script (note exit code) |
| `pre_commit` | SKILL-002 complete |
| `session_end` | SKILL-003 |
| `incident_filed` | SKILL-004 |
