#!/usr/bin/env bash
# verify-www-ui-grade.sh — fail-closed UI/UX grade vs golden homepage baseline.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== verify-www-ui-grade ==="

if [[ ! -f docs/www/NF_UI_UX_GRADE_LAW_LOCKED_v1.md ]]; then
  echo "FAIL verify-www-ui-grade: missing docs/www/NF_UI_UX_GRADE_LAW_LOCKED_v1.md" >&2
  exit 1
fi
if [[ ! -f .cursor/rules/nf-ui-ux-grade-law.mdc ]]; then
  echo "FAIL verify-www-ui-grade: missing .cursor/rules/nf-ui-ux-grade-law.mdc" >&2
  exit 1
fi
if ! grep -q 'alwaysApply: true' .cursor/rules/nf-ui-ux-grade-law.mdc; then
  echo "FAIL verify-www-ui-grade: nf-ui-ux-grade-law.mdc must alwaysApply" >&2
  exit 1
fi

python3 scripts/nf_www_ui_grade_v1.py

# Optional pixel fixtures — only when explicitly requested and PNGs exist.
if [[ "${NF_WWW_VISUAL:-}" == "1" ]]; then
  FIXDIR="tests/www/visual/home-golden"
  if [[ -f "$FIXDIR/home-first-viewport.png" ]] && command -v npx >/dev/null 2>&1; then
    if [[ -f scripts/compare-www-home-golden.mjs ]]; then
      node scripts/compare-www-home-golden.mjs || exit 1
    else
      echo "OK   NF_WWW_VISUAL=1 but compare script not present — structural grade only"
    fi
  else
    echo "OK   NF_WWW_VISUAL=1 — PNG fixtures not captured yet; structural grade stands"
  fi
fi

echo "verify-www-ui-grade shell PASS"
