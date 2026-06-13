#!/usr/bin/env bash
# Packaging tier copy gates — async demo, trial, published tiers, agentic autonomous.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"
cd "$ROOT"
fail=0

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"

check_page() {
  local url="$1"
  local label="$2"
  shift 2
  local html
  html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "$url" 2>/dev/null || true)"
  local missing=0
  for needle in "$@"; do
    if ! echo "$html" | grep -qF "$needle"; then
      echo "FAIL $label — missing: $needle" >&2
      missing=1
    fi
  done
  if [[ "$missing" -eq 0 ]]; then
    echo "OK   $label"
  else
    fail=1
  fi
}

echo "=== verify-packaging-tier ==="

for f in \
  docs/strategy/PACKAGING_TIER_SANDBOX_LOCKED_v1.md \
  docs/architecture/AGENTIC_AUTONOMOUS_WORKFLOWS_LOCKED_v1.md \
  copilot/trial/index.html; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done

check_page "${BASE}/" "homepage packaging" \
  "14-day trial" \
  "Full async demo" \
  "Starter" \
  "Agentic autonomous"

check_page "${BASE}/copilot/" "copilot hub packaging" \
  "Published tiers" \
  "14-day trial" \
  "dev sandbox"

check_page "${BASE}/copilot/trial/" "trial page" \
  "14-day trial" \
  "50 evaluate checks" \
  "full async demo" \
  "Agentic autonomous"

check_page "${BASE}/copilot/demo/" "async demo page" \
  "Full async demo" \
  "without a sales call"

check_page "${BASE}/enterprise/" "enterprise packaging" \
  "Starter" \
  "Sandbox" \
  "Production"

if grep -q '14-day trial' OFFERINGS_LOCKED.md 2>/dev/null; then
  echo "OK   OFFERINGS_LOCKED packaging modes"
else
  echo "FAIL OFFERINGS_LOCKED missing packaging modes" >&2
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-packaging-tier passed."
  exit 0
fi
echo ""
echo "Fix packaging tier copy. See docs/strategy/PACKAGING_TIER_SANDBOX_LOCKED_v1.md" >&2
exit 1
