# SKILL-012 — UI/UX Library 2026 (mandatory for UI + landing generation)

**When:** Before any UI/www edit, landing generation, style pack choice, or agent/LLM brief that produces visual product surfaces.

**SSOT (mirror):** `data/nf-uiux-library-2026-v1.json`  
**App SSOT:** `NOETFIELD-RUNWAY/sites/company-new/functions/_lib/nf-uiux-library-2026-v1.json`  
**Module:** `uiux-library-2026.ts`  
**Related:** SKILL-009 · `docs/www/NF_UI_UX_GRADE_LAW_LOCKED_v1.md` · `data/www-home-golden-baseline-v1.json`

## Law

1. Load the library before proposing UI.
2. Pick `style_pack` from library enum only — never invent fonts or radius systems.
3. Cheap LLMs return brief JSON only; templates render HTML.
4. Grade fail-closed; revise brief fields — not freeform HTML.
5. Corporate homepage uses frozen golden class, not customer packs.

## Steps

1. Read library JSON (`schema: nf-uiux-library-2026-v1`).
2. Match category aliases → pack.
3. Apply `composition_laws` + `craft`.
4. Corporate www: `bash scripts/verify-www-ui-grade.sh`.

## Pass response (internal)

```
uiux_library: PASS
pack: <id>
surface: app-landing|corporate-www
```
