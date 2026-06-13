# SKILL-010 — Agentic event gate

**When:** Session end (mandatory), after any verify script on ship branches, or when a gate **fails** (scope, conflict, enforcement).

**Authority:** R-012 · [AGENTIC_ENFORCEMENT_MAP_LOCKED_v1.md](../../docs/ops/AGENTIC_ENFORCEMENT_MAP_LOCKED_v1.md)

---

## Steps

1. Read [.cursor/events/EVENT_SCHEMA.yaml](../events/EVENT_SCHEMA.yaml) for allowed `event_types`.
2. Choose session ID: `YYYY-MM-DD-<slug>` (e.g. `2026-06-13-ui-v4-ship`).
3. Append one row to [.cursor/events/REGISTRY.md](../events/REGISTRY.md):

| Field | Value |
|-------|-------|
| Date | ISO date |
| Session ID | slug above |
| Type | from schema |
| Agent | `NF-CLOUD-AGENT` |
| Summary | one line — script + exit code, or shipped scope |

4. On **verify_run** events, include script name and exit code in Summary (e.g. `verify-agent-scope.sh exit 0`).
5. On **session_end**, confirm `scope_confirmed: noetfield_only` in Summary or linked SKILL-003 report.

## Minimum events per ship session

| Event | Required |
|-------|----------|
| `session_start` | Recommended at session open |
| `verify_run` | After `verify-agent-scope.sh` and `verify-agent-enforcement.sh` |
| `session_end` | Before push / PR |

## On gate fail

- File `scope_gate_fail`, `rule_conflict`, or `verify_run` with non-zero exit **before** fixing (if time permits).
- If boundary crossed → **SKILL-004** incident, not only an event.

## Never

- Log contents of `ops/private/` or `docs/internal/`
- Use events to relax R-007/R-008 — events are audit trail only
