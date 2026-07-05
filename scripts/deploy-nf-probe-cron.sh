#!/usr/bin/env bash
# Deploy nf-probe-cron worker — 15-min uptime/greeting/drift/intake probes → Supabase + Telegram.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
SOURCEA_SECRETS="${HOME}/.sourcea-secrets/noetfield.env"
WORKER_DIR="$ROOT/infra/nf-probe-cron"

read_vault() {
  local key="$1"
  [[ -f "$VAULT" ]] || return 1
  grep -E "^${key}=" "$VAULT" | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//'
}

load_secrets() {
  if [[ -f "$SOURCEA_SECRETS" ]]; then
    # shellcheck disable=SC1090
    set -a && source "$SOURCEA_SECRETS" && set +a
  fi
}

log() { printf '[deploy-nf-probe-cron] %s\n' "$*"; }

sync_secret() {
  local key="$1"
  local val="$2"
  [[ -n "$val" ]] || { log "WARN: ${key} missing — skip"; return 0; }
  log "secret ${key}"
  cd "$WORKER_DIR"
  printf '%s' "$val" | wrangler secret put "$key" >/dev/null
}

GIT_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
LIVE_PLATFORM_SHA="$(curl -sS "${PLATFORM_BASE:-https://platform.noetfield.com}/api/public/chat/health" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('git_sha',''))" 2>/dev/null || true)"
EXPECTED_SHA="${LIVE_PLATFORM_SHA:-$GIT_SHA}"

load_secrets

SUPABASE_URL="$(read_vault NOETFIELD_SUPABASE_URL || read_vault SUPABASE_URL || true)"
SUPABASE_URL="${NOETFIELD_SUPABASE_URL:-${SUPABASE_URL:-}}"
SUPABASE_SERVICE="$(read_vault NOETFIELD_SUPABASE_SERVICE_ROLE_KEY || read_vault SUPABASE_SERVICE_ROLE_KEY || true)"
SUPABASE_SERVICE="${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-${SUPABASE_SERVICE_ROLE_KEY:-${SUPABASE_SERVICE:-}}}"
TELEGRAM_TOKEN="$(read_vault TELEGRAM_NOETFIELD_OPS_BOT_TOKEN || true)"
TELEGRAM_CHAT="$(read_vault TELEGRAM_OPS_CHAT_ID || true)"
[[ -n "$TELEGRAM_CHAT" ]] || TELEGRAM_CHAT="8635650894"

log "deploy nf-probe-cron from ${WORKER_DIR}"
cd "$WORKER_DIR"

if [[ "${NF_PROBE_CRON_FORCE_TOKEN:-0}" == "1" ]]; then
  :
else
  unset CLOUDFLARE_API_TOKEN CF_API_TOKEN
fi

wrangler deploy

sync_secret "SUPABASE_URL" "$SUPABASE_URL"
sync_secret "SUPABASE_SERVICE_ROLE_KEY" "$SUPABASE_SERVICE"
sync_secret "TELEGRAM_NOETFIELD_OPS_BOT_TOKEN" "$TELEGRAM_TOKEN"
sync_secret "TELEGRAM_OPS_CHAT_ID" "$TELEGRAM_CHAT"
sync_secret "EXPECTED_GIT_SHA" "$EXPECTED_SHA"

log "PASS — nf-probe-cron deployed (cron */15 * * * *)"
log "manual smoke: wrangler tail nf-probe-cron — or POST /run on workers.dev URL after deploy"
