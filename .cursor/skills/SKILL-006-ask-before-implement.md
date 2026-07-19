# SKILL-006 — Autonomous scoped execute (CPL v1.1)

**When:** Every session — before disk mutation and at session end.

**Authority:** NOETFIELD AUTONOMOUS CHANGE-PRESERVATION LAW v1.1 · MEMORY_LOCKED R-007 · R-008 (reinterpreted)

**On rule conflict:** Run [SKILL-007-auto-conflict-resolution.md](./SKILL-007-auto-conflict-resolution.md) first.

---

## Default mode

**Execute autonomously within the task’s reasonable scope. Preserve unrelated work.**

Do not ask for routine permission. Do not stop merely to report preflight.

## Before disk edit

1. Infer smallest reasonable authorized scope from the task.
2. Prefer isolated branch/worktree; leave unrelated dirty files untouched.
3. Preflight automatically (baseline, ancestry, allow/protect paths, deploy authority).
4. Proceed with scoped edits, tests, commits, and PRs as needed.
5. Verify preservation before closing (scope subset; protected surfaces intact; no stale restore).

## Ask founder only for

| Trigger | Meaning |
|---------|---------|
| Destroy/overwrite unrelated work | Stop — `BLOCKED_SCOPE_BREACH` / preservation risk |
| Material ambiguity | Stop — `BLOCKED_MATERIAL_AMBIGUITY` + smallest missing decision |
| Destructive / irreversible action | Stop — `BLOCKED_DESTRUCTIVE_AUTHORITY` |
| Merge/deploy without instruction or standing authority | Stop — do not promote |
| Unknown production baseline + downgrade risk | Stop — `BLOCKED_BASELINE_CONFLICT` / `BLOCKED_STALE_RELEASE` |

## Session end

1. Receipt: baseline, scope, changed paths, preservation checks, verdict.
2. Open blockers only if a real stop condition applies.
3. Do **not** ask “May I…?” for routine next steps already implied by the task.

## Fail response (real blocker only)

```
BLOCKED_<VERDICT>
Smallest missing decision: <one line>
Protected/unrelated work left untouched.
```

---

**END**
