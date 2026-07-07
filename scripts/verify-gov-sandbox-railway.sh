#!/usr/bin/env bash
# Railway gov-sandbox spine — API health + Next workspace shell (direct origins).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROXY_CFG="${ROOT}/data/nf-www-gov-proxy-v1.json"
API_SERVICE="${NF_GOV_API_SERVICE:-gov-sandbox-api}"
WEB_SERVICE="${NF_GOV_WEB_SERVICE:-gov-sandbox-web}"
fail=0

echo "=== verify-gov-sandbox-railway ==="

api_origin=""
web_origin=""
if [[ -f "$PROXY_CFG" ]]; then
  read -r api_origin web_origin <<< "$(python3 -c "
import json
from pathlib import Path
p = Path('$PROXY_CFG')
d = json.loads(p.read_text(encoding='utf-8')) if p.is_file() else {}
print((d.get('gov_api_origin') or '').rstrip('/'), (d.get('gov_web_origin') or '').rstrip('/'))
")"
fi

if [[ -z "$api_origin" || -z "$web_origin" ]]; then
  echo "FAIL missing gov_api_origin or gov_web_origin in ${PROXY_CFG}" >&2
  exit 1
fi

health_body="$(curl -sS --connect-timeout 15 "${api_origin}/health" 2>/dev/null || true)"
if grep -qF 'governance-console-api' <<< "$health_body"; then
  echo "OK   ${api_origin}/health governance-console-api"
else
  echo "FAIL ${api_origin}/health unexpected body: ${health_body:0:120}" >&2
  fail=1
fi

web_html="$(curl -sSL --connect-timeout 15 -H "Accept: text/html" "${web_origin}/workspace" 2>/dev/null || true)"
if grep -qF '_next' <<< "$web_html"; then
  echo "OK   ${web_origin}/workspace has Next.js shell"
else
  echo "FAIL ${web_origin}/workspace missing _next" >&2
  fail=1
fi

if command -v railway >/dev/null 2>&1; then
  for svc in "$API_SERVICE" "$WEB_SERVICE"; do
    status="$(RAILWAY_CALLER="scripts/verify-gov-sandbox-railway" railway service status -s "$svc" 2>/dev/null | grep -E '^Status:' | awk '{print $2}' || true)"
    if [[ "$status" == "SUCCESS" ]]; then
      echo "OK   Railway ${svc} deployment ${status}"
    elif [[ -n "$status" ]]; then
      echo "FAIL Railway ${svc} deployment ${status}" >&2
      fail=1
    else
      echo "NOTE Railway ${svc} status unavailable (not linked?)"
    fi
  done
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-gov-sandbox-railway passed."
  exit 0
fi
echo ""
echo "verify-gov-sandbox-railway failed." >&2
exit 1
