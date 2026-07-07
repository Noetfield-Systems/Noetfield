#!/usr/bin/env bash
# Deploy governance-console API + Next workspace to Railway; wire www proxy config.
# Law: NEVER railway up gov-sandbox-* from repo root without --path-as-root (API)
#      or environment edit dockerfilePath (web). Root railway.toml = platform-api only.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROJECT_ID="${NF_RAILWAY_PROJECT_ID:-94ade24c-9b24-4d8d-a443-9ddc5bf6ef54}"
ENV_NAME="${NF_RAILWAY_ENV:-production}"
API_SERVICE="${NF_GOV_API_SERVICE:-gov-sandbox-api}"
WEB_SERVICE="${NF_GOV_WEB_SERVICE:-gov-sandbox-web}"
PROXY_CFG="${NF_GOV_PROXY_CFG:-${ROOT}/data/nf-www-gov-proxy-v1.json}"
USE_CUSTOM_DOMAINS="${NF_GOV_USE_CUSTOM_DOMAINS:-1}"
API_CUSTOM_DOMAIN="${NF_GOV_API_DOMAIN:-sandbox-api.noetfield.com}"
WEB_CUSTOM_DOMAIN="${NF_GOV_WEB_DOMAIN:-sandbox.noetfield.com}"
DATA_MOUNT="${NF_GOV_DATA_MOUNT:-/data}"
DATABASE_URL="${NF_GOV_DATABASE_URL:-sqlite:////data/gov_sandbox.db}"
RAILWAY_CALLER="${RAILWAY_CALLER:-scripts/deploy-gov-sandbox-railway}"
SESSION="${RAILWAY_AGENT_SESSION:-gov-sandbox-$(date +%s)}"
GIT_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"

log() { printf '[deploy-gov-sandbox-railway] %s\n' "$*"; }

on_fail() {
  local code=$?
  log "FAIL deploy exit=${code}"
  python3 scripts/nf_post_deploy_verify.py --deploy-failed "gov-sandbox railway (${ENV_NAME})" --surface www 2>/dev/null || true
  exit "$code"
}
trap on_fail ERR

railway_cmd() {
  env RAILWAY_CALLER="$RAILWAY_CALLER" RAILWAY_AGENT_SESSION="$SESSION" railway "$@"
}

link_service() {
  local name="$1"
  railway_cmd link -p "$PROJECT_ID" -e "$ENV_NAME" -s "$name" >/dev/null 2>&1 || true
}

railway_service_url() {
  local name="$1"
  link_service "$name"
  railway_cmd domain list --service "$name" --json 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    items = d if isinstance(d, list) else d.get('domains', d.get('result', []))
    for x in items or []:
        dom = x.get('domain') if isinstance(x, dict) else x
        if dom:
            dom = str(dom).replace('https://', '').rstrip('/')
            print('https://' + dom)
            break
except Exception:
    pass
" 2>/dev/null
}

wait_for_railway_url() {
  local name="$1"
  local url=""
  local attempt
  for attempt in $(seq 1 18); do
    url="$(railway_service_url "$name" || true)"
    if [[ -n "$url" ]]; then
      echo "$url"
      return 0
    fi
    log "waiting for ${name} domain (${attempt}/18)…"
    sleep 10
  done
  return 1
}

ensure_railway_domain() {
  local name="$1"
  local custom="${2:-}"
  link_service "$name"
  local existing
  existing="$(railway_service_url "$name" || true)"
  if [[ -n "$existing" ]]; then
    log "domain exists: ${name} → ${existing}"
    return 0
  fi
  log "creating Railway domain for ${name}…"
  railway_cmd domain -s "$name" >/dev/null 2>&1 || log "WARN: could not create default domain for ${name}"
  sleep 5
  if [[ -n "$custom" && "$USE_CUSTOM_DOMAINS" == "1" ]]; then
    log "attaching custom domain ${custom} → ${name}…"
    railway_cmd domain "$custom" -s "$name" >/dev/null 2>&1 || log "WARN: custom domain ${custom} not attached (DNS may be pending)"
  fi
}

ensure_data_volume() {
  link_service "$API_SERVICE"
  if railway_cmd volume list -s "$API_SERVICE" 2>/dev/null | grep -q "${DATA_MOUNT}"; then
    log "volume mounted at ${DATA_MOUNT}"
    return 0
  fi
  log "provisioning volume mount ${DATA_MOUNT} on ${API_SERVICE}…"
  railway_cmd volume add -m "$DATA_MOUNT" -s "$API_SERVICE" >/dev/null 2>&1 || \
    log "WARN: volume add failed — using ephemeral sqlite until volume provisioned"
}

wait_for_deployment_success() {
  local name="$1"
  local attempt status
  link_service "$name"
  for attempt in $(seq 1 30); do
    status="$(railway_cmd service status -s "$name" 2>/dev/null | grep -E '^Status:' | awk '{print $2}' || true)"
    case "$status" in
      SUCCESS)
        log "${name} deployment SUCCESS"
        return 0
        ;;
      FAILED|CRASHED)
        log "FAIL ${name} deployment ${status}"
        return 1
        ;;
      *)
        log "waiting for ${name} deploy (${attempt}/30) status=${status:-unknown}…"
        sleep 10
        ;;
    esac
  done
  log "WARN: ${name} deployment did not reach SUCCESS in time"
  return 1
}

proxy_cfg_origin() {
  local key="$1"
  python3 -c "
import json
from pathlib import Path
p = Path('${PROXY_CFG}')
if not p.is_file():
    raise SystemExit(0)
d = json.loads(p.read_text(encoding='utf-8'))
print((d.get('${key}') or '').rstrip('/'))
" 2>/dev/null || true
}

prefer_url() {
  local custom="$1"
  local railway_url="$2"
  if [[ "$USE_CUSTOM_DOMAINS" == "1" && -n "$custom" ]]; then
    if curl -sf --connect-timeout 8 "https://${custom}/" >/dev/null 2>&1 || \
       curl -sf --connect-timeout 8 "https://${custom}/health" >/dev/null 2>&1 || \
       curl -sfL --connect-timeout 8 "https://${custom}/workspace" >/dev/null 2>&1; then
      echo "https://${custom}"
      return 0
    fi
    log "WARN: custom https://${custom} not reachable yet — using ${railway_url}"
  fi
  echo "$railway_url"
}

log "project=${PROJECT_ID} env=${ENV_NAME}"
bash scripts/check-gov-railway-manifest.sh

link_service "$API_SERVICE"

log "pin Railway build config (gov-console images, not platform-api)…"
railway_cmd environment edit -p "$PROJECT_ID" -e "$ENV_NAME" \
  --service-config "$API_SERVICE" build.builder DOCKERFILE \
  --service-config "$API_SERVICE" build.dockerfilePath "governance-console/backend/Dockerfile" \
  --service-config "$API_SERVICE" build.watchPatterns '["governance-console/backend/**"]' \
  --service-config "$WEB_SERVICE" build.builder DOCKERFILE \
  --service-config "$WEB_SERVICE" build.dockerfilePath "governance-console/Dockerfile.www" \
  --service-config "$WEB_SERVICE" build.watchPatterns '["governance-console/**","packages/ui-tokens/**"]' \
  -m "gov-sandbox: governance-console dockerfiles" \
  >/dev/null 2>&1 || log "WARN: could not patch Railway build config"

ensure_data_volume

log "set API variables (CORS, SQLite volume path, GIT_SHA)…"
railway_cmd variable set \
  -s "$API_SERVICE" \
  --set "CORS_ORIGINS=https://www.noetfield.com,https://noetfield.com,http://localhost:13080" \
  --set "DATABASE_URL=${DATABASE_URL}" \
  --set "GIT_SHA=${GIT_SHA}" \
  --skip-deploys \
  >/dev/null 2>&1 || log "WARN: could not set API variables"

log "deploy API (${API_SERVICE})…"
ensure_railway_domain "$API_SERVICE" "$API_CUSTOM_DOMAIN"
(
  cd "${ROOT}"
  railway_cmd up "./governance-console/backend" --path-as-root -s "$API_SERVICE" -d -m "gov-sandbox-api: governance-console backend"
)
wait_for_deployment_success "$API_SERVICE"

log "deploy Web (${WEB_SERVICE})…"
ensure_railway_domain "$WEB_SERVICE" "$WEB_CUSTOM_DOMAIN"
(
  cd "${ROOT}"
  railway_cmd up -s "$WEB_SERVICE" -d -m "gov-sandbox-web: Next workspace /workspace"
)
wait_for_deployment_success "$WEB_SERVICE"

log "resolve Railway service URLs…"
API_RAILWAY="$(wait_for_railway_url "$API_SERVICE" || true)"
WEB_RAILWAY="$(wait_for_railway_url "$WEB_SERVICE" || true)"

if [[ -z "$API_RAILWAY" ]]; then
  API_RAILWAY="$(proxy_cfg_origin gov_api_origin)"
  [[ -n "$API_RAILWAY" ]] && log "WARN: using cached gov_api_origin from ${PROXY_CFG}"
fi
if [[ -z "$WEB_RAILWAY" ]]; then
  WEB_RAILWAY="$(proxy_cfg_origin gov_web_origin)"
  [[ -n "$WEB_RAILWAY" ]] && log "WARN: using cached gov_web_origin from ${PROXY_CFG}"
fi

if [[ -z "$API_RAILWAY" || -z "$WEB_RAILWAY" ]]; then
  log "FAIL: could not resolve Railway service URLs"
  exit 2
fi

API_URL="$(prefer_url "$API_CUSTOM_DOMAIN" "$API_RAILWAY")"
WEB_URL="$(prefer_url "$WEB_CUSTOM_DOMAIN" "$WEB_RAILWAY")"

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
    "notes": f"gov-sandbox deploy env=${ENV_NAME} sha=${GIT_SHA[:12] if GIT_SHA else 'unknown'}",
}
path = Path("${PROXY_CFG}")
path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
print(f"wrote {path}")
PY

if [[ "${PROXY_CFG}" == "${ROOT}/data/nf-www-gov-proxy-v1.json" ]]; then
  python3 scripts/generate-cf-redirects.py
  python3 scripts/generate-www-deny-middleware.py
fi

log "smoke API…"
curl -sf "${API_URL}/health" | head -c 300
echo
log "smoke WEB workspace…"
curl -sfL "${WEB_URL}/workspace" | grep -qE '_next|Trust Ledger Workspace' || {
  log "FAIL workspace shell missing on Railway URL"
  exit 3
}
log "OK workspace shell on Railway"

export NF_EXPECT_SHA="${GIT_SHA}"
bash scripts/verify-gov-sandbox-railway.sh || exit 4
bash scripts/assert-gov-railway-config.sh || exit 5

trap - ERR
log "done — run: bash scripts/deploy-gov-sandbox-e2e.sh to promote www proxy"
