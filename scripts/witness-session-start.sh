#!/usr/bin/env bash
# witness-session-start.sh — cloud-safe session witness (no Mac SourceA required)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== witness-session-start ==="
echo ""

OPS="$ROOT/governance/OPS_LIVE_STATUS_LOCKED.json"
if [[ -f "$OPS" ]]; then
  echo "OK   OPS_LIVE_STATUS_LOCKED.json present"
  python3 -c "
import json
from pathlib import Path
ops = json.loads(Path('$OPS').read_text())
for k, v in ops.get('layers', {}).items():
    print(f'  · {k}: {v.get(\"status\", \"?\")}')"
else
  echo "FAIL missing OPS_LIVE_STATUS — BLOCK build until founder writes ops truth" >&2
  exit 1
fi

echo ""
if [[ -f .cursor/agent-memory/MEMORY_LOCKED.yaml ]]; then
  ver=$(grep '^version:' .cursor/agent-memory/MEMORY_LOCKED.yaml | head -1)
  echo "OK   MEMORY_LOCKED $ver"
else
  echo "FAIL missing MEMORY_LOCKED.yaml" >&2
  exit 1
fi

if [[ -f ops/private/sourceA/founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md ]]; then
  echo "OK   SourceA SEMI_NOTICE mirrored"
else
  echo "WARN SourceA SEMI_NOTICE not on disk — use OPS_LIVE + in-repo locks only (INCIDENT-003)"
fi

echo ""
echo "Open PR branches (local):"
git branch -a 2>/dev/null | grep -E 'cursor/' | head -8 || true

echo ""
echo "Production probes (best effort):"
if command -v curl >/dev/null 2>&1; then
  curl -sS --max-time 5 https://www.noetfield.com/api/intake/health 2>/dev/null | head -c 200 || echo "  (intake health unreachable)"
  echo ""
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 https://www.noetfield.com/gate/sales/ 2>/dev/null || echo "000")
  echo "  gate/sales HTTP $code"
fi

echo ""
echo "Witness complete — read OPS_LIVE before building. Run: make verify-ops-live"
