#!/usr/bin/env bash
# Fail if QUICK_PICK top-5 are all already done in registry (stale picks).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUICK="${ROOT}/docs/ops/plans/no-asf/QUICK_PICK.md"
REGISTRY="${ROOT}/docs/ops/plans/registry.json"

echo "=== verify-quick-pick-fresh ==="

if [[ ! -f "$QUICK" || ! -f "$REGISTRY" ]]; then
  echo "FAIL missing QUICK_PICK or registry.json" >&2
  exit 1
fi

ids="$(python3 - <<'PY'
import re
from pathlib import Path
text = Path("docs/ops/plans/no-asf/QUICK_PICK.md").read_text(encoding="utf-8")
section = text.split("## Next 25")[1].split("## Recently")[0] if "## Next 25" in text else text
found = re.findall(r"\*\*(NF-PLAN-\d{4})\*\*", section)
print("\n".join(found[:5]))
PY
)"

done_count=0
total=0
while IFS= read -r pid; do
  [[ -z "$pid" ]] && continue
  total=$((total + 1))
  status="$(python3 -c "
import json, sys
r = json.load(open('docs/ops/plans/registry.json'))
p = next((x for x in r['plans'] if x['id'] == sys.argv[1]), None)
print(p.get('status','MISSING') if p else 'MISSING')
" "$pid")"
  echo "  $pid → $status"
  if [[ "$status" == "done" ]]; then
    done_count=$((done_count + 1))
  fi
done <<< "$ids"

if [[ "$total" -ge 5 && "$done_count" -eq "$total" ]]; then
  echo "FAIL top-5 QUICK_PICK entries are all done — run sync-prompt-pack-status.py" >&2
  exit 1
fi

echo ""
echo "verify-quick-pick-fresh passed ($done_count/$total top-5 done)."
