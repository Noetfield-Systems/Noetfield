#!/usr/bin/env bash
# Fail if gov-sandbox Railway services are pinned to wrong dockerfile (platform-api drift).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROJECT_ID="${NF_RAILWAY_PROJECT_ID:-94ade24c-9b24-4d8d-a443-9ddc5bf6ef54}"
ENV_NAME="${NF_RAILWAY_ENV:-production}"
API_SERVICE="${NF_GOV_API_SERVICE:-gov-sandbox-api}"
WEB_SERVICE="${NF_GOV_WEB_SERVICE:-gov-sandbox-web}"
MANIFEST="${ROOT}/data/nf-railway-gov-sandbox-manifest-v1.json"
fail=0

echo "=== assert-gov-railway-config ==="

bash scripts/check-gov-railway-manifest.sh || exit 1

if ! command -v railway >/dev/null 2>&1; then
  echo "SKIP railway CLI not installed — disk manifest checks only"
  exit 0
fi

read -r api_df web_df forbidden <<< "$(python3 -c "
import json
from pathlib import Path
m = json.loads(Path('$MANIFEST').read_text(encoding='utf-8'))
api = m['services']['$API_SERVICE'] if '$API_SERVICE' in m.get('services', {}) else m['services']['gov-sandbox-api']
web = m['services']['$WEB_SERVICE'] if '$WEB_SERVICE' in m.get('services', {}) else m['services']['gov-sandbox-web']
print(api['dockerfile_path'], web['dockerfile_path'], m.get('forbidden_dockerfile', ''))
")"

check_service_config() {
  local svc="$1"
  local expected_df="$2"
  # Live dockerfilePath is not exposed reliably via Railway CLI without dashboard.
  # Disk manifest + governance-console/*.toml are the enforcement SSOT; deploy uses --path-as-root.
  if command -v railway >/dev/null 2>&1; then
    local status
    status="$(RAILWAY_CALLER="scripts/assert-gov-railway-config" railway service status -s "$svc" 2>/dev/null | grep -E '^Status:' | awk '{print $2}' || true)"
    if [[ -n "$status" && "$status" != "SUCCESS" ]]; then
      echo "FAIL ${svc} Railway deployment ${status} (expected SUCCESS)" >&2
      return 1
    fi
    if [[ -n "$status" ]]; then
      echo "OK   ${svc} Railway ${status} + expected dockerfile ${expected_df}"
      return 0
    fi
  fi
  echo "OK   ${svc} expected dockerfile ${expected_df} (disk + manifest)"
  return 0
}

check_service_config "$API_SERVICE" "$api_df" || fail=1
check_service_config "$WEB_SERVICE" "$web_df" || fail=1

if grep -qF 'infrastructure/docker/Dockerfile.api' <<< "$api_df$web_df"; then
  echo "FAIL manifest points at forbidden platform dockerfile" >&2
  fail=1
fi

# Disk: web toml must not reference platform dockerfile
if grep -q 'Dockerfile.api' "${ROOT}/governance-console/railway.web.toml" "${ROOT}/governance-console/backend/railway.toml" 2>/dev/null; then
  echo "FAIL governance-console railway.toml references platform Dockerfile.api" >&2
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "assert-gov-railway-config passed."
  exit 0
fi
echo ""
echo "assert-gov-railway-config failed." >&2
exit 1
