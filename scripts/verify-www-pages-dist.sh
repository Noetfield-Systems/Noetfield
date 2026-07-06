#!/usr/bin/env bash
# Pre-deploy gate — www-pages-dist must not contain PUBLIC_OUTPUT_DENYLIST paths.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DIST="${ROOT}/www-pages-dist"
fail=0

echo "=== verify-www-pages-dist ==="

if [[ ! -d "$DIST" ]]; then
  echo "FAIL missing www-pages-dist — run: bash scripts/build-www-pages-dist.sh" >&2
  exit 1
fi

python3 - <<'PY'
import json
import sys
from pathlib import Path

root = Path("www-pages-dist")
deny = json.loads(Path("governance/PUBLIC_OUTPUT_DENYLIST.json").read_text())
errors = []
for rel in deny.get("exact_paths", []):
    p = root / rel.lstrip("/")
    if p.exists():
        errors.append(f"exact leak: {rel}")
for prefix in deny.get("prefix_paths", []):
    p = root / prefix.lstrip("/").rstrip("/")
    if p.exists():
        errors.append(f"prefix leak: {prefix}")
if errors:
    for e in errors:
        print(f"FAIL {e}", file=sys.stderr)
    sys.exit(1)
print("OK   denylist paths absent from www-pages-dist")
PY

for needle in _redirects "Open workspace" "nf26-demoStepper"; do
  case "$needle" in
    _redirects)
      if [[ -f "${DIST}/_redirects" ]] && grep -q 'noetfield.com' "${DIST}/_redirects"; then
        echo "OK   apex redirect in _redirects"
      else
        echo "FAIL _redirects missing apex redirect" >&2
        fail=1
      fi
      ;;
    *)
      if grep -rqF "$needle" "${DIST}/copilot/demo/" 2>/dev/null; then
        echo "OK   copilot/demo contains: $needle"
      else
        echo "FAIL copilot/demo missing: $needle" >&2
        fail=1
      fi
      ;;
  esac
done

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-www-pages-dist PASS"
  exit 0
fi
echo ""
echo "verify-www-pages-dist failed." >&2
exit 1
