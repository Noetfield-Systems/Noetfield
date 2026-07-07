#!/usr/bin/env bash
# Deploy gov-sandbox to Railway staging environment (isolated from production).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export NF_RAILWAY_ENV="${NF_RAILWAY_ENV:-staging}"
export NF_GOV_API_SERVICE="${NF_GOV_API_SERVICE:-gov-sandbox-api-staging}"
export NF_GOV_WEB_SERVICE="${NF_GOV_WEB_SERVICE:-gov-sandbox-web-staging}"
export NF_GOV_PROXY_CFG="${NF_GOV_PROXY_CFG:-${ROOT}/data/nf-www-gov-proxy-staging-v1.json}"
export NF_GOV_USE_CUSTOM_DOMAINS="${NF_GOV_USE_CUSTOM_DOMAINS:-0}"

log() { printf '[deploy-gov-sandbox-staging] %s\n' "$*"; }

log "env=${NF_RAILWAY_ENV} api=${NF_GOV_API_SERVICE} web=${NF_GOV_WEB_SERVICE}"
log "proxy cfg=${NF_GOV_PROXY_CFG}"

bash scripts/deploy-gov-sandbox-railway.sh

log "staging deploy complete — proxy written to ${NF_GOV_PROXY_CFG}"
log "optional: NOETFIELD_E2E_BASE=<pages-preview> bash scripts/verify-www-live-sandbox.sh"
