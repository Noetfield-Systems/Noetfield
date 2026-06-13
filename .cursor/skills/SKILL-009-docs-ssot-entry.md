# SKILL-009 — Docs SSOT entry

**When:** Before creating docs, indexes, or plan files; when docs feel fragmented.

## Steps

1. Read [docs/ops/DOCS_UNIFIED_MAP_LOCKED_v1.md](../../docs/ops/DOCS_UNIFIED_MAP_LOCKED_v1.md) (60s).
2. Use existing entry — do **not** create parallel indexes:
   - Humans → `docs/SSOT_INDEX.md`
   - Agents → `docs/ops/AGENT_READ_LINKS_LOCKED_v1.md` § Cloud ship
   - Ship → `os/SHIP_NOW.md` → `GTM_NEXT.md`
3. New ship work → `GTM_NEXT.md` (`ship-*` IDs), not a new queue file.
4. New strategy → one row in `SSOT_INDEX.md`; link from unified map if cross-silo.
5. Run `./scripts/plan-with-no-asf-verify.sh` if touching ops/ship/verify paths.

## Never

- New `SHIP_NOW` outside `os/`
- New 1000-item registry without bridge JSON
- `docs/reference/` as canonical (use `docs/references/` LOCKED)
