#!/usr/bin/env bash
# verify-factory-aml.sh — AML governance trace factory live checks
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

YAML="$ROOT/packages/schemas/factories/aml_governance_trace_v1.yaml"
[[ -f "$YAML" ]] || fail "missing aml_governance_trace_v1.yaml"

python3 -c "
import json, yaml
from pathlib import Path
root = Path('$ROOT')
meta = yaml.safe_load((root / 'packages/schemas/factories/aml_governance_trace_v1.yaml').read_text())['metadata']
assert meta['id'] == 'aml_governance_trace_v1'
assert meta['status'] == 'live'
cat = json.loads((root / 'governance/FACTORY_CATALOG.json').read_text())
entry = next(f for f in cat['factories'] if f['id'] == 'aml_governance_trace_v1')
assert entry['status'] == 'live'
assert entry.get('route')
nodes = yaml.safe_load((root / 'packages/schemas/factories/aml_governance_trace_v1.yaml').read_text())['spec']['nodes']
assert len(nodes) == 8
" || fail "AML governance trace factory spec or catalog invalid"

ok "aml_governance_trace_v1 YAML and catalog live"

grep -q "aml_governance_trace_v1" services/governance/noetfield_governance/api.py || fail "API missing AML factory"
grep -q "AmlGovernanceTraceRuntime" services/governance/noetfield_governance/api.py || fail "API missing AML runtime"
grep -q '"/catalog/platform"' services/governance/noetfield_governance/api.py || fail "API missing /catalog/platform"
[[ -f platform/factories/index.html ]] || fail "missing platform/factories/index.html"

ok "API and platform console present"

PYTHONPATH=packages/types:packages/config:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance:services/factories:services/trust-brief:services/legal-review:services/aml-trace \
  python3 -c "from noetfield_aml_trace import AmlGovernanceTraceRuntime; from noetfield_factories import AmlFactoryRunner" \
  || fail "AML trace packages import failed"

ok "AML trace packages import"

echo ""
echo "verify-factory-aml: all checks passed"
