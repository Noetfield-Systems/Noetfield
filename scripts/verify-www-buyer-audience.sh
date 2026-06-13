#!/usr/bin/env bash
# Buyer-audience copy gate — www must speak to ICP (CISO, procurement, legal), not founders/agents.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-www-buyer-audience ==="

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
  partners/index.html
  partners/msp/index.html
  federal/index.html
  trust-brief/index.html
  gate/intake/index.html
  faq/index.html
  console/index.html
  ai-automation/index.html
)

FORBIDDEN=(
  'plan-with-no-asf'
  'AGENT_SELF_AUDIT'
  'NF-CLOUD'
  'founder sign-off'
  'founder attest'
  'Founder / solutions'
  'this repo'
  'TrustField execution'
  'docs/ops/'
  'docs/strategy/PACKAGING'
  'docs/strategy/channel-outreach'
  'docs/architecture/AGENTIC'
  'Ship verify'
  'ship verification'
  'internal release gate'
  'Buyer surface coherence'
  'outreach copy'
  'outreach guide'
  'STAGING_DEMO'
  'Internal runbook'
  'SME design partner (W3)'
  'until founder sign-off'
  'Revenue grows from'
  'local dev:'
  'PRODUCT_TRUTH'
  'Execution checklist — next 30 days'
  'Operating Model'
  'repo-native'
  'agent self-audit'
)

for rel in "${PAGES[@]}"; do
  if [[ ! -f "$rel" ]]; then
    echo "SKIP missing $rel"
    continue
  fi
  text="$(cat "$rel")"
  label="${rel%/index.html}"
  label="${label:-homepage}"
  page_fail=0
  for phrase in "${FORBIDDEN[@]}"; do
    if grep -qF "$phrase" <<< "$text"; then
      echo "FAIL $label — internal phrase: $phrase" >&2
      page_fail=1
      fail=1
    fi
  done
  if [[ "$page_fail" -eq 0 ]]; then
    echo "OK   $label buyer-audience clean"
  fi
done

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-www-buyer-audience passed."
  exit 0
fi
echo ""
echo "Remove founder/agent/internal copy from www. Buyers only." >&2
exit 1
