#!/usr/bin/env bash
# Deploy Cloudflare www proxy worker (Phase 3 — noetfield-www-proxy).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
PROXY_DIR="$ROOT/infra/cf-www-proxy"

read_vault() {
  local key="$1"
  [[ -f "$VAULT" ]] || return 1
  grep -E "^${key}=" "$VAULT" | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//'
}

export CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-$(read_vault CF_NOETFIELD_API_TOKEN || read_vault CF_API_TOKEN || true)}"

log() { printf '[deploy-cf-www-proxy] %s\n' "$*"; }

log "deploying noetfield-www-proxy from $PROXY_DIR"
cd "$PROXY_DIR"

# Zone-scoped API tokens often lack Workers deploy permission — prefer wrangler OAuth.
if [[ "${CF_WWW_PROXY_FORCE_TOKEN:-0}" == "1" && -n "$CLOUDFLARE_API_TOKEN" ]]; then
  wrangler deploy
else
  unset CLOUDFLARE_API_TOKEN CF_API_TOKEN
  wrangler deploy
fi

log "checking worker route (www may still be direct Vercel DNS — see docs/ops/CF_WWW_PROXY_LOCKED_v1.md)"
curl -sS -I https://www.noetfield.com/ | grep -iE '^(server|x-noetfield|cf-ray):' || true
log "done"
