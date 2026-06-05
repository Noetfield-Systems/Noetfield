# Agent doc tagging (LOCKED v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-DOCTAG-001` |
| **Updated** | 2026-06-06 |

---

## Law

**Every document an agent writes** (tracked `.md`, `.mdc`, `.yaml`, reports, incidents, skills, ops locks) **must** include the agent tag header below with **today's date** in `Updated`.

Commits by agents use prefix: `[NF-CLOUD-AGENT]`

---

## Required header (copy into every new/edited agent doc)

```markdown
| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-<AREA>-<NNN>` |
| **Updated** | YYYY-MM-DD |
```

| Placeholder | Rule |
|-------------|------|
| `<AREA>` | Short slug: `AUDIT`, `OPS`, `INCIDENT`, `SKILL`, `MEMORY`, `REPORT` |
| `<NNN>` | 3-digit sequence per area, or date slug `2026-06-06` for one-offs |

---

## Examples

| Doc type | Doc trace example |
|----------|-------------------|
| Incident | `NF-CLOUD-INCIDENT-001` |
| Skill | `NF-CLOUD-SKILL-005` |
| Ops lock | `NF-CLOUD-OPS-012` |
| Session report | `NF-CLOUD-REPORT-2026-06-06` |

---

## Forbidden

- Untagged agent-authored docs in `docs/`, `.cursor/`, `scripts/` (when doc-heavy)
- Wrong tag (`NF-LOCAL-AGENT` in cloud workspace)
- Missing or stale `Updated` date

---

## Skill

[.cursor/skills/SKILL-005-doc-tagging.md](../../.cursor/skills/SKILL-005-doc-tagging.md)

---

**END**
