# SKILL-005 — Doc tagging (mandatory)

**When:** Creating or materially editing any agent-authored document in this repo.

## Header (required top block)

```markdown
| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-<AREA>-<NNN>` |
| **Updated** | YYYY-MM-DD |
```

Use **today's UTC or local date** for `Updated` on every edit.

## Doc trace

- New file: pick `<AREA>` + next `<NNN>` or use `YYYY-MM-DD` suffix for reports
- Edit existing: bump `Updated` date; bump trace version if structural change

## Commits

```
[NF-CLOUD-AGENT] <message>
```

## Reference

[docs/ops/AGENT_DOC_TAGGING_LOCKED_v1.md](../../docs/ops/AGENT_DOC_TAGGING_LOCKED_v1.md)
