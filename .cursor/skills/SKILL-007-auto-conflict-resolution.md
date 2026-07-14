# SKILL-007 — Auto conflict resolution (all agents)

**When:** Any time two or more rules, skills, cursor rules, or founder laws disagree — **before** first disk edit.

**Authority:** R-010 · NOETFIELD AUTONOMOUS CHANGE-PRESERVATION LAW v1.1

---

## Precedence ladder (highest wins)

| Tier | Source | Examples |
|------|--------|----------|
| **T0** | Founder **current message** explicit order | task instruction; `merge` / `deploy` / `ship` / `PROMOTE` when stated |
| **T1** | **CPL v1.1** + hard rules **R-001–R-011** (as reinterpreted) | execute scoped work; preserve unrelated; Noetfield-only; no AUTO-RUN commercial send |
| **T2** | Open **P0/P1 incidents** | stop wrong scope; anti-stale www; no downgrade |
| **T3** | Portfolio / Brain law | `execution_authority: false` — advise only unless T0 ship order |
| **T4** | Bounded **workflow triggers** | PLAN WITH NO ASF bundle inside task scope |
| **T5** | Ship-first / backlog convenience | `os/plan.json`, QUICK_PICK — do not self-start outside task |

**Golden resolver:** *Routine reversible scoped work proceeds under CPL v1.1. Old ask-first does not block commits/PRs/tests/edits inside the task. Ask only for irreversible/destructive authority, material ambiguity, unauthorized promote, or downgrade risk.*

---

## Auto-resolve algorithm

```
ON session start OR before first disk mutation:
  1. LOAD memory hard_rules + open incidents + CPL v1.1
  2. PARSE user message as task authority for ordinary scoped work
  3. IF action is routine reversible and inside inferred scope:
       PROCEED — do not ASK for permission
  4. IF action is destructive/irreversible OR merge/deploy without authority
       OR would overwrite unrelated / downgrade live:
       STOP with exact blocker verdict + smallest missing decision
  5. IF two rules conflict on routine work:
       Winner = CPL v1.1 (execute + preserve); continue
  6. ON session end: receipt with verdict; no routine permission theater
```

---

## Known conflict pairs (pre-resolved)

| Rule A | Rule B | Winner | Allowed path |
|--------|--------|--------|--------------|
| `noetfield-ship-first` — ship without waiting | CPL v1.1 — preserve / no unapproved promote | **CPL v1.1** | Build/PR ok; promote only if instructed |
| Legacy ask-before-edit | CPL v1.1 autonomous execute | **CPL v1.1** | Scoped execute; ask only on stop conditions |
| `noetfield-no-asf-plans` — implement ≤3 tasks | CPL v1.1 | **CPL v1.1** | Infer scope from task; proceed |
| Bare `IMPLEMENT` (no task name) | CPL v1.1 | **CPL v1.1** | Infer smallest scope or `BLOCKED_MATERIAL_AMBIGUITY` |
| Mandatory SourceA file missing | Any ship order | **R-009** | BLOCK implement; sync or paste first |
| TrustField task | Any other rule | **R-001** | STOP always |
| Cursor AUTO-RUN commercial send | R-011 | **R-011** | Validators + www copy only |
| Stale HEAD deploy vs newer live | Any ship | **R-014 / CPL** | `BLOCKED_STALE_RELEASE` / anti-stale |

---

## T0 triggers (examples)

| Founder says | Bounded bundle |
|--------------|----------------|
| Any concrete task (fix/build/implement/prepare/PR) | Scoped execute per CPL v1.1 |
| `merge` / `deploy` / `ship` / `publish` / `PROMOTE <SURFACE> <SHA>` | Promotion authority for that surface/SHA |
| `PLAN WITH NO ASF iter N implement` | Merge PR + ≤3 QUICK_PICK tasks + verify + PR |
| `WRITE DOWN incident reports` | `.cursor/incidents/` + registry + memory |

**Not promotion authority:** prior session ship, ship-first rule alone, plan.json queue.

---

## Agent output template (real blocker only)

```markdown
**BLOCKED_<VERDICT>**

Smallest missing decision: <one line>

Unrelated/protected work: untouched
```

Do **not** use the old “I will not edit disk until you choose A/B/C” template for routine scoped work.

---

## Integration

| Skill / rule | When |
|--------------|------|
| SKILL-006 | Autonomous scoped execute |
| **SKILL-007** | **This — on rule conflict** |
| **SKILL-011** | **Git/PR file conflicts (R-013)** |
| SKILL-001 | Scope gate inside task |
| `000-noetfield-universal-change-preservation-law-v1.1.mdc` | alwaysApply binding law |
| `noetfield-ask-before-edit.mdc` | pointer to CPL v1.1 |

---

**END**
