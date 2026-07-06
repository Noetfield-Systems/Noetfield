#!/usr/bin/env bash
# Deploy governance-console API + Next workspace to Railway; wire www proxy config.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROJECT_ID="${NF_RAILWAY_PROJECT_ID:-94ade24c-9b24-4d8d-a443-9ddc5bf6ef54}"
ENV_NAME="${NF_RAILWAY_ENV:-production}"
API_SERVICE="${NF_GOV_API_SERVICE:-gov-sandbox-api}"
WEB_SERVICE="${NF_GOV_WEB_SERVICE:-gov-sandbox-web}"
PROXY_CFG="${ROOT}/data/nf-www-gov-proxy-v1.json"
RAILWAY_CALLER="${RAILWAY_CALLER:-scripts/deploy-gov-sandbox-railway}"
SESSION="${RAILWAY_AGENT_SESSION:-gov-sandbox-$(date +%s)}"

log() { printf '[deploy-gov-sandbox-railway] %s\n' "$*"; }

railway_cmd() {
  env RAILWAY_CALLER="$RAILWAY_CALLER" RAILWAY_AGENT_SESSION="$SESSION" railway "$@"
}

ensure_service() {
  local name="$1"
  if railway_cmd service list 2>/dev/null | grep -q "${name}"; then
    log "service exists: ${name}"
    return 0
  fi
  log "creating service: ${name}"
  railway_cmd add -s "$name" --json >/dev/null 2>&1 || railway_cmd add -s "$name"
}

service_url() {
  local name="$1"
  railway_cmd service list 2>/dev/null | grep -A3 "$name" | grep -Eo 'https://[^ ]+' | head -1
}

log "project=${PROJECT_ID} env=${ENV_NAME}"

railway_cmd link -p "$PROJECT_ID" -e "$ENV_NAME" >/dev/null 2>&1 || true

ensure_service "$API_SERVICE"
ensure_service "$WEB_SERVICE"

log "set API CORS + SQLite sandbox DB…"
railway_cmd variable set \
  -s "$API_SERVICE" \
  --set "CORS_ORIGINS=https://www.noetfield.com,https://noetfield.com,http://localhost:13080" \
  --set "DATABASE_URL=sqlite:///./gov_sandbox.db" \
  --skip-deploys \
  >/dev/null 2>&1 || log "WARN: could not set API variables"

log "deploy API (${API_SERVICE})…"
(
  cd "${ROOT}/governance-console/backend"
  railway_cmd up -s "$API_SERVICE" -d
)

log "deploy Web (${WEB_SERVICE})…"
(
  cd "${ROOT}"
  if [[ -f railway.toml ]]; then
    cp railway.toml "${ROOT}/.railway.toml.platform.bak"
  fi
  cp governance-console/railway.web.toml railway.toml
  railway_cmd up -s "$WEB_SERVICE" -d .
  if [[ -f "${ROOT}/.railway.toml.platform.bak" ]]; then
    mv "${ROOT}/.railway.toml.platform.bak" railway.toml
  else
    rm -f railway.toml
  fi
)

sleep 15
API_URL="$(service_url "$API_SERVICE")"
WEB_URL="$(service_url "$WEB_SERVICE")"

if [[ -z "$API_URL" || -z "$WEB_URL" ]]; then
  log "FAIL: could not resolve Railway service URLs"
  log "Set data/nf-www-gov-proxy-v1.json manually after checking Railway dashboard"
  exit 2
fi

log "API URL: ${API_URL}"
log "WEB URL: ${WEB_URL}"

python3 - <<PY
import json
from pathlib import Path
cfg = {
    "schema": "nf-www-gov-proxy-v1",
    "enabled": True,
    "gov_web_origin": "${WEB_URL}".rstrip("/"),
    "gov_api_origin": "${API_URL}".rstrip("/"),
}
path = Path("${PROXY_CFG}")
path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
print(f"wrote {path}")
PY

python3 scripts/generate-cf-redirects.py

log "smoke API…"
curl -sf "${API_URL}/health" | head -c 200
echo
log "smoke WEB workspace…"
curl -sf "${WEB_URL}/workspace" | grep -q "Trust Ledger Workspace" && log "OK workspace HTML" || log "WARN: workspace needle missing on Railway URL"

log "done — run: bash scripts/deploy-www-cloudflare.sh to promote www proxy"
