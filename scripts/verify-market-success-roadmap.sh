#!/usr/bin/env bash
# Verify MARKET_SUCCESS_1000_ROADMAP_v1.md structure and client-safe copy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

ROADMAP="docs/strategy/MARKET_SUCCESS_1000_ROADMAP_v1.md"
GEN="scripts/generate_market_success_1000_roadmap.py"
DATA="scripts/market_success_1000_steps_data.py"

echo "=== verify-market-success-roadmap ==="

for f in "$ROADMAP" "$GEN" "$DATA"; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done

if [[ -f "$ROADMAP" ]]; then
  step_count="$(grep -cE '^\| mr-[0-9]{4} \|' "$ROADMAP" || true)"
  if [[ "$step_count" -eq 1000 ]]; then
    echo "OK   roadmap has 1000 step rows"
  else
    echo "FAIL roadmap step count $step_count (expected 1000)" >&2
    fail=1
  fi

  phase_count="$(grep -cE '^## Phase [0-9]+ —' "$ROADMAP" || true)"
  if [[ "$phase_count" -eq 10 ]]; then
    echo "OK   roadmap has 10 phases"
  else
    echo "FAIL roadmap phase count $phase_count (expected 10)" >&2
    fail=1
  fi

  if grep -q 'mr-0001' "$ROADMAP" && grep -q 'mr-1000' "$ROADMAP"; then
    echo "OK   roadmap spans mr-0001–mr-1000"
  else
    echo "FAIL roadmap missing mr-0001 or mr-1000" >&2
    fail=1
  fi

  for sm in SM-01 SM-02 SM-03 SM-04 SM-05 SM-06 SM-07 SM-08 SM-09 SM-10; do
    if grep -q "$sm" "$ROADMAP"; then
      echo "OK   archetype $sm present"
    else
      echo "FAIL archetype $sm missing" >&2
      fail=1
    fi
  done

  vendor_re='Vanta|Drata|OneTrust|Credo AI|IBM watsonx|ServiceNow|RegScale|Complyance|MetricStream|Modulos|Microsoft Purview|Microsoft 365|\bM365\b|competitor'
  if grep -qiE "$vendor_re" "$ROADMAP" "$DATA" 2>/dev/null; then
    echo "FAIL vendor/competitor name in roadmap or data" >&2
    grep -niE "$vendor_re" "$ROADMAP" "$DATA" 2>/dev/null | head -5 >&2 || true
    fail=1
  else
    echo "OK   no vendor names in roadmap sources"
  fi

  if grep -q 'Golden insights' "$ROADMAP" && grep -q 'Customer #1' "$ROADMAP"; then
    echo "OK   golden insights + Customer #1 gate documented"
  else
    echo "FAIL roadmap missing golden insights or Customer #1" >&2
    fail=1
  fi
fi

if [[ -f "$GEN" ]] && [[ -f "$DATA" ]]; then
  tmp="$(mktemp)"
  cp "$ROADMAP" "$tmp"
  if python3 "$GEN" >/dev/null 2>&1; then
    if diff -q "$tmp" "$ROADMAP" >/dev/null 2>&1; then
      echo "OK   generator output matches committed roadmap"
    else
      echo "FAIL roadmap out of sync with generator — run: python3 $GEN" >&2
      fail=1
    fi
  else
    echo "FAIL generator script failed" >&2
    fail=1
  fi
  rm -f "$tmp"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-market-success-roadmap passed."
  exit 0
fi
exit 1
