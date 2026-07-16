#!/usr/bin/env bash
# Deploy Cloudflare www proxy worker (Phase 3 — noetfield-www-proxy).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
PROXY_DIR="$ROOT/infra/cf-www-proxy"
ORIGIN="${CF_WWW_ORIGIN:-}"
RELEASE_SHA="${NF_WWW_RELEASE_SHA:-}"
WRANGLER_VERSION="${CF_WRANGLER_VERSION:-4.103.0}"
WRANGLER=(npx --yes "wrangler@${WRANGLER_VERSION}")

read_vault() {
  local key="$1"
  [[ -f "$VAULT" ]] || return 1
  grep -E "^${key}=" "$VAULT" | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//'
}

export CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-$(read_vault CF_NOETFIELD_API_TOKEN || read_vault CF_API_TOKEN || true)}"

log() { printf '[deploy-cf-www-proxy] %s\n' "$*"; }

if [[ ! "$RELEASE_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  log "FAIL: NF_WWW_RELEASE_SHA must be the exact full lowercase git SHA"
  exit 2
fi
if [[ ! "$ORIGIN" =~ ^https://[a-z0-9-]+\.noetfield-www\.pages\.dev/?$ ]] || \
   [[ "$ORIGIN" =~ ^https://(main|production|www)\.noetfield-www\.pages\.dev/?$ ]]; then
  log "FAIL: CF_WWW_ORIGIN must be an immutable noetfield-www Pages deployment URL"
  exit 2
fi

log "deploying noetfield-www-proxy release=${RELEASE_SHA:0:12} origin=${ORIGIN}"
cd "$PROXY_DIR"

DEPLOY_ARGS=(
  deploy
  --message "NF-WEB release ${RELEASE_SHA}"
  --var "ORIGIN:${ORIGIN}"
  --var "RELEASE_SHA:${RELEASE_SHA}"
  --var "APEX_HOST:noetfield.com"
  --var "CANONICAL_HOST:www.noetfield.com"
  --var "STATUS_HOST:status.noetfield.com"
)

# Zone-scoped API tokens often lack Workers deploy permission — prefer wrangler OAuth.
if [[ "${CF_WWW_PROXY_FORCE_TOKEN:-0}" == "1" && -n "$CLOUDFLARE_API_TOKEN" ]]; then
  "${WRANGLER[@]}" "${DEPLOY_ARGS[@]}"
else
  unset CLOUDFLARE_API_TOKEN CF_API_TOKEN
  "${WRANGLER[@]}" "${DEPLOY_ARGS[@]}"
fi

log "waiting for the exact canonical Worker release pin"
for attempt in $(seq 1 12); do
  headers="$(curl -sS -D - -o /dev/null \
    "https://www.noetfield.com/api/health?nf_release=${RELEASE_SHA}&nf_cachebust=${attempt}" \
    2>/dev/null || true)"
  observed_release="$(printf '%s\n' "$headers" | awk -F': *' \
    'tolower($1)=="x-noetfield-release" {gsub("\\r", "", $2); print tolower($2)}' | tail -1)"
  observed_proxy="$(printf '%s\n' "$headers" | awk -F': *' \
    'tolower($1)=="x-noetfield-proxy" {gsub("\\r", "", $2); print tolower($2)}' | tail -1)"
  if [[ "$observed_release" == "$RELEASE_SHA" && "$observed_proxy" == "cf-www-proxy" ]]; then
    log "canonical Worker release pin confirmed (${attempt})"
    log "done"
    exit 0
  fi
  log "canonical pin pending release=${observed_release:-missing} proxy=${observed_proxy:-missing} (${attempt}/12)"
  sleep 5
done

log "FAIL: canonical Worker did not expose the exact release pin"
exit 3
