#!/usr/bin/env bash
# Frame parity — all GTM + funnel HTML on institutional 2026 + bank-grade + v4 stack.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-ui-frame-parity ==="

PAGES=(
  index.html
  enterprise/index.html
  bank-pilot/index.html
  trust-center/index.html
  trust-ledger/index.html
  trust-ledger/sample-report/index.html
  copilot/index.html
  copilot/demo/index.html
  copilot/pilot/index.html
  copilot/trial/index.html
  copilot/procurement/index.html
  gate/intake/index.html
  faq/index.html
  partners/index.html
  federal/index.html
)

for rel in "${PAGES[@]}"; do
  f="$rel"
  if [[ ! -f "$f" ]]; then
    echo "FAIL missing $f" >&2
    fail=1
    continue
  fi
  text="$(cat "$f")"
  label="${rel%/index.html}"
  label="${label:-homepage}"
  missing=0
  for needle in 'nf-institutional" content="2026-06' noetfield-institutional-2026.css noetfield-bank-grade.css noetfield-institutional-v4.css nf-site-2026 nf-v4; do
    if ! grep -qF "$needle" <<< "$text"; then
      echo "FAIL $label missing $needle" >&2
      missing=1
    fi
  done
  if [[ "$missing" -eq 0 ]]; then
    echo "OK   $label full v4 frame"
  else
    fail=1
  fi
done

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-ui-frame-parity passed."
  exit 0
fi
exit 1
