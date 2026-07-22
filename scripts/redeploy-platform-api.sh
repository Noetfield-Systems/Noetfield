#!/usr/bin/env bash
# Canonical platform-api redeploy — set GIT_SHA, build, wait for live match, verify, sync probe.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=scripts/read_platform_vault.sh
source "${ROOT}/scripts/read_platform_vault.sh"

API_SERVICE="${RAILWAY_API_SERVICE:-platform-api}"
PLATFORM_DOMAIN="${NF_PLATFORM_LIVE_DOMAIN:-platform.noetfield.com}"
PLATFORM_BASE="https://${PLATFORM_DOMAIN}"

log() { printf '[redeploy-platform-api] %s\n' "$*"; }

railway_cmd() {
  RAILWAY_CALLER="skill:use-railway" RAILWAY_AGENT_SESSION="${RAILWAY_AGENT_SESSION:-redeploy-platform-api-$$}" \
    railway "$@"
}

GIT_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
if [[ -z "$GIT_SHA" ]]; then
  log "FAIL: not a git repo"
  exit 1
fi

command -v railway >/dev/null || { log "FAIL: railway CLI missing"; exit 1; }
railway_cmd whoami >/dev/null

# Fail closed: do not redeploy auth-required without env keys OR admin secret (DB bootstrap).
ensure_pilot_keys_before_redeploy() {
  local auth_required pilot_keys remote_auth remote_keys admin_secret
  auth_required="${GOVERNANCE_PILOT_AUTH_REQUIRED:-}"
  pilot_keys="${GOVERNANCE_PILOT_API_KEYS:-}"
  admin_secret="${ADMIN_DASHBOARD_SECRET:-}"
  if [[ -z "$pilot_keys" ]]; then
    pilot_keys="$(read_platform_vault GOVERNANCE_PILOT_API_KEYS 2>/dev/null || true)"
  fi
  if [[ -z "$pilot_keys" ]]; then
    local bearer tenant
    bearer="$(read_platform_vault CONSOLE_BEARER 2>/dev/null || true)"
    tenant="${GOVERNANCE_PILOT_TENANT_ID:-00000000-0000-4000-8000-000000000001}"
    if [[ -n "$bearer" ]]; then
      if [[ "$bearer" == *:* ]]; then
        pilot_keys="$bearer"
      else
        pilot_keys="${tenant}:${bearer}"
      fi
    fi
  fi
  if [[ -z "$admin_secret" ]]; then
    admin_secret="$(read_platform_vault ADMIN_DASHBOARD_SECRET 2>/dev/null || true)"
  fi
  remote_auth="$(railway_cmd variable list --service "$API_SERVICE" --json 2>/dev/null | python3 -c '
import json,sys
try:
  d=json.load(sys.stdin)
  print(str((d or {}).get("GOVERNANCE_PILOT_AUTH_REQUIRED") or "").strip())
except Exception:
  print("")
' 2>/dev/null || true)"
  remote_keys="$(railway_cmd variable list --service "$API_SERVICE" --json 2>/dev/null | python3 -c '
import json,sys
try:
  d=json.load(sys.stdin)
  print(str((d or {}).get("GOVERNANCE_PILOT_API_KEYS") or "").strip())
except Exception:
  print("")
' 2>/dev/null || true)"
  if [[ -z "$auth_required" ]]; then
    auth_required="$remote_auth"
  fi
  if [[ "$auth_required" == "true" || "$auth_required" == "1" ]]; then
    if [[ -n "$pilot_keys" ]]; then
      log "Syncing GOVERNANCE_PILOT_API_KEYS before redeploy (last4=${pilot_keys: -4})"
      railway_cmd variable set --service "$API_SERVICE" --skip-deploys \
        "GOVERNANCE_PILOT_API_KEYS=${pilot_keys}"
    elif [[ -n "$remote_keys" ]]; then
      log "Remote GOVERNANCE_PILOT_API_KEYS already present (last4=${remote_keys: -4})"
    elif [[ -n "$admin_secret" ]]; then
      log "WARN: no env/remote pilot keys — redeploy allowed via ADMIN_DASHBOARD_SECRET (DB bootstrap)"
    else
      log "FAIL: GOVERNANCE_PILOT_AUTH_REQUIRED=true but no GOVERNANCE_PILOT_API_KEYS and no ADMIN_DASHBOARD_SECRET"
      log "  → Set keys or ADMIN_DASHBOARD_SECRET in ~/.noetfield-platform-secrets then retry"
      exit 4
    fi
  fi
}

ensure_pilot_keys_before_redeploy

log "greeting SSOT coupling check…"
python3 "$ROOT/scripts/sync_chat_greeting_asset.py"
python3 "$ROOT/scripts/verify_chat_greeting_coupling.py"

log "set GIT_SHA=${GIT_SHA:0:12} on ${API_SERVICE} (skip intermediate deploy)…"
railway_cmd variable set --service "$API_SERVICE" --skip-deploys "GIT_SHA=${GIT_SHA}"

log "deploy ${API_SERVICE}…"
railway_cmd up --service "$API_SERVICE" -d -y

log "wait for live git_sha…"
PLATFORM_BASE="$PLATFORM_BASE" "$ROOT/scripts/wait-for-platform-sha.sh" --expected-sha "$GIT_SHA" --platform-base "$PLATFORM_BASE"

log "post-deploy verify (platform + www intake path)…"
python3 "$ROOT/scripts/nf_post_deploy_verify.py" --expected-sha "$GIT_SHA" --surface both \
  --platform-base "$PLATFORM_BASE" --www-base "${NF_WWW_LIVE_BASE:-https://www.noetfield.com}"

log "sync probe EXPECTED_GIT_SHA…"
"$ROOT/scripts/sync-probe-expected-sha.sh" "$GIT_SHA"

log "PASS — platform-api live at ${GIT_SHA:0:12}"
