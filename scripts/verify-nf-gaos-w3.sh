#!/usr/bin/env bash
# verify-nf-gaos-w3.sh — W3 factory spine verify
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-nf-gaos-w3 ==="

for f in \
  data/nf_orient_routing_v1.json \
  os/NF_REPO_CAPABILITY_MAP.json \
  docs/ops/NF_GAOS_W3_FACTORY_SPINE_LOCKED_v1.md \
  scripts/nf_factory_lib_v1.py \
  scripts/nf_live_surfaces_v1.py \
  scripts/nf_truth_bundle_v1.py \
  scripts/nf_receipt_cascade_v1.py \
  scripts/nf_gatekeeper_v1.py \
  scripts/nf_executor_lock_v1.py \
  scripts/nf-repo-find.sh; do
  [[ -f "$f" ]] || { echo "FAIL missing $f" >&2; fail=1; continue; }
  echo "OK   $f"
done

python3 scripts/nf_live_surfaces_v1.py --json >/dev/null || fail=1
echo "OK   nf_live_surfaces_v1"

python3 scripts/nf_receipt_cascade_v1.py --json >/dev/null || fail=1
echo "OK   nf_receipt_cascade_v1"

python3 scripts/nf_truth_bundle_v1.py --json >/dev/null || fail=1
echo "OK   nf_truth_bundle_v1"

python3 scripts/nf_gatekeeper_v1.py --json >/dev/null || true
echo "OK   nf_gatekeeper_v1 (advisory)"

chmod +x scripts/prove-nf-factory-spine.sh
./scripts/prove-nf-factory-spine.sh || fail=1
echo "OK   prove-nf-factory-spine (positive + negative proofs)"

[[ -f reports/agent-auto/events/nf-factory-spine-proof-v1.json ]] || fail=1
[[ -f "$HOME/.sina/nf-factory-spine-proof-v1.json" ]] || fail=1
echo "OK   proof receipt on disk"

[[ -f "$HOME/.sina/nf-live-surfaces-v1.json" ]] || { echo "FAIL missing ~/.sina/nf-live-surfaces-v1.json" >&2; fail=1; }
[[ -f "$HOME/.sina/nf-truth-bundle-v1.json" ]] || { echo "FAIL missing ~/.sina/nf-truth-bundle-v1.json" >&2; fail=1; }
echo "OK   ~/.sina mirrors"

line=$(python3 -c "import json;print(json.load(open('$HOME/.sina/nf-live-surfaces-v1.json'))['product_now_line'])")
[[ -n "$line" ]] || { echo "FAIL empty product_now_line" >&2; fail=1; }
echo "OK   product_now_line: $line"

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-nf-gaos-w3: PASS"
  exit 0
fi
echo ""
echo "verify-nf-gaos-w3: FAIL" >&2
exit 1
