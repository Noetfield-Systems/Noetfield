#!/usr/bin/env bash
# verify-ops-live.sh — OPS witness SSOT anti-drift (R-013)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

OPS="$ROOT/governance/OPS_LIVE_STATUS_LOCKED.json"
MEMORY="$ROOT/.cursor/agent-memory/MEMORY_LOCKED.yaml"

[[ -f "$OPS" ]] || fail "missing governance/OPS_LIVE_STATUS_LOCKED.json"
[[ -f "$MEMORY" ]] || fail "missing MEMORY_LOCKED.yaml"

python3 -c "
import json
from pathlib import Path
root = Path('$ROOT')
ops = json.loads((root / 'governance/OPS_LIVE_STATUS_LOCKED.json').read_text())
layers = ops.get('layers', {})
ws = layers.get('google_workspace_inbox', {})
if ws.get('status') != 'live':
    raise SystemExit('google_workspace_inbox must be live')
stripe = layers.get('stripe_commercial_licensing', {})
if stripe.get('status') != 'live':
    raise SystemExit('stripe_commercial_licensing must be live')
form = layers.get('form_delivery_resend', {})
if form.get('status') not in ('deferred_post_factory', 'live', 'pending'):
    raise SystemExit('form_delivery_resend status invalid')
sales = (root / 'gate/sales/index.html').read_text()
if 'noetfield-stripe-catalog.json' not in sales:
    raise SystemExit('gate/sales must load stripe catalog (not redirect stub)')
if 'http-equiv=\"refresh\"' in sales and '/enterprise/' in sales:
    raise SystemExit('gate/sales must not redirect to enterprise when stripe live')
status = (root / 'status/index.html').read_text()
if 'Google Workspace' not in status:
    raise SystemExit('status must distinguish Google Workspace inbox active')
nextp = (root / 'next/index.html').read_text()
if 'Google Workspace' not in nextp:
    raise SystemExit('next ops lane must mention Google Workspace inbox active')
" || fail "OPS_LIVE validation failed"

ok "OPS_LIVE_STATUS_LOCKED.json layers valid"

grep -q 'R-013' "$MEMORY" || fail "MEMORY_LOCKED.yaml missing R-013 witness rule"
grep -q 'OPS_LIVE_STATUS' "$MEMORY" || fail "MEMORY_LOCKED must reference OPS_LIVE_STATUS"
grep -q 'M-005' "$MEMORY" || fail "MEMORY_LOCKED missing M-005 staleness pattern"

ok "MEMORY_LOCKED R-013 + M-005 present"

[[ -f docs/ops/OPS_WITNESS_AUDIT_LOCKED_v1.md ]] || fail "missing OPS_WITNESS_AUDIT doc"
grep -q 'OPS_LIVE_STATUS' docs/ops/AGENT_READ_LINKS_LOCKED_v1.md || fail "AGENT_READ_LINKS must list OPS_LIVE"

ok "witness docs wired"
echo ""
echo "verify-ops-live: all checks passed"
