#!/usr/bin/env bash
# Validate gov-sandbox Railway manifest vs disk (dockerfiles, toml, scripts).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MANIFEST="${ROOT}/data/nf-railway-gov-sandbox-manifest-v1.json"
fail=0

echo "=== check-gov-railway-manifest ==="

if [[ ! -f "$MANIFEST" ]]; then
  echo "FAIL missing ${MANIFEST}" >&2
  exit 1
fi

python3 - <<'PY' || fail=1
import json
import sys
from pathlib import Path

root = Path(".")
manifest = json.loads((root / "data/nf-railway-gov-sandbox-manifest-v1.json").read_text(encoding="utf-8"))
fail = False

for name, svc in manifest.get("services", {}).items():
    df = root / svc["dockerfile_path"]
    toml = root / svc["railway_toml"]
    if not df.is_file():
        print(f"FAIL {name} missing dockerfile {df}", file=sys.stderr)
        fail = True
    else:
        print(f"OK   {name} dockerfile {svc['dockerfile_path']}")
    if not toml.is_file():
        print(f"FAIL {name} missing railway.toml {toml}", file=sys.stderr)
        fail = True
    else:
        print(f"OK   {name} railway.toml {svc['railway_toml']}")

for script in manifest.get("verify_scripts", []):
    p = root / script
    if not p.is_file():
        print(f"FAIL missing script {script}", file=sys.stderr)
        fail = True
    else:
        print(f"OK   script {script}")

forbidden = manifest.get("forbidden_dockerfile", "")
if forbidden and (root / forbidden).is_file():
    print(f"OK   forbidden dockerfile exists on disk (must not be used for gov-sandbox): {forbidden}")

sys.exit(1 if fail else 0)
PY

if [[ "$fail" -ne 0 ]]; then
  echo ""
  echo "check-gov-railway-manifest failed." >&2
  exit 1
fi
echo ""
echo "check-gov-railway-manifest passed."
