#!/usr/bin/env bash
# verify-procurement-openapi.sh — ship-procurement-openapi-verify-060
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

OPENAPI="$ROOT/docs/api/openapi.json"
[[ -f "$OPENAPI" ]] || fail "missing docs/api/openapi.json"

python3 -c "
import json
from pathlib import Path
p = Path('$OPENAPI')
data = json.loads(p.read_text())
if not data.get('openapi') and not data.get('swagger'):
    raise SystemExit('invalid openapi root')
paths = data.get('paths') or {}
if len(paths) < 3:
    raise SystemExit('openapi paths too small')
" || fail "openapi.json invalid"

ok "docs/api/openapi.json valid"

grep -q '/openapi.json' services/governance/README.md || fail "services/governance README missing /openapi.json"
grep -q '/openapi.json' copilot/procurement/index.html || fail "procurement missing openapi link"

ok "README and procurement cite /openapi.json"
echo ""
echo "verify-procurement-openapi: passed"
