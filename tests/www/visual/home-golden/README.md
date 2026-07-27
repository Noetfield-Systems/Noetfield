# Homepage golden visual fixtures

**Authority:** `docs/www/NF_UI_UX_GRADE_LAW_LOCKED_v1.md`  
**Class:** PR #186 Claude content × Codex corporate restyle

## What lives here

- `manifest.json` — fixture contract + CSS probes  
- `home-first-viewport.png` / `home-mobile.png` — optional Playwright baselines (not required for structural grade PASS)

## Refresh screenshots

```bash
NF_WWW_VISUAL=1 bash scripts/capture-www-home-golden.sh
```

Structural grade (`scripts/verify-www-ui-grade.sh`) always runs. Pixel diff runs only when PNGs exist and `NF_WWW_VISUAL=1`.

## Authored by

[NF-LOCAL-REPO-AGENT] — 2026-07-27
