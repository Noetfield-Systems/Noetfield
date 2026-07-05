#!/usr/bin/env bash
# SSOT: read Noetfield platform secrets from canonical vault files (not chat memory).
# Order: admin-dashboard → noetfield.env → noetfield-db.env → ~/.sina/secrets.env
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PLATFORM_VAULT_FILES=(
  "${HOME}/.sourcea-secrets/noetfield-admin-dashboard.env"
  "${HOME}/.sourcea-secrets/noetfield.env"
  "${HOME}/.sourcea-secrets/noetfield-db.env"
  "${NF_SECRETS_VAULT:-${HOME}/.sina/secrets.env}"
)

read_platform_vault() {
  local key="$1"
  local file val
  for file in "${PLATFORM_VAULT_FILES[@]}"; do
    [[ -f "$file" ]] || continue
    val="$(grep -E "^${key}=" "$file" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r' | sed -e 's/^"//' -e 's/"$//')"
    if [[ -n "$val" ]]; then
      printf '%s' "$val"
      return 0
    fi
  done
  return 1
}

read_gmail_service_account_json() {
  local inline file
  inline="$(read_platform_vault GMAIL_SERVICE_ACCOUNT_JSON 2>/dev/null || true)"
  if [[ -n "$inline" ]]; then
    printf '%s' "$inline"
    return 0
  fi
  for key in GMAIL_SERVICE_ACCOUNT_JSON_FILE GOOGLE_APPLICATION_CREDENTIALS; do
    file="$(read_platform_vault "$key" 2>/dev/null || true)"
    if [[ -n "$file" && -f "$file" ]]; then
      cat "$file"
      return 0
    fi
  done
  for file in \
    "${HOME}/.sourcea-secrets/noetfield-gmail-service-account.json" \
    "${HOME}/.sourcea-secrets/gmail-service-account.json" \
    "${HOME}/.sina/noetfield-gmail-service-account.json"; do
    if [[ -f "$file" ]]; then
      cat "$file"
      return 0
    fi
  done
  for key in GOOGLE_SERVICE_ACCOUNT_JSON NOETFIELD_GMAIL_SERVICE_ACCOUNT_JSON; do
    inline="$(read_platform_vault "$key" 2>/dev/null || true)"
    if [[ -n "$inline" ]]; then
      printf '%s' "$inline"
      return 0
    fi
  done
  return 1
}

platform_vault_status() {
  python3 - <<'PY' "${PLATFORM_VAULT_FILES[@]}"
import json, os, sys
from pathlib import Path

keys = [
    "ADMIN_DASHBOARD_SECRET",
    "GMAIL_SERVICE_ACCOUNT_JSON",
    "GMAIL_SERVICE_ACCOUNT_JSON_FILE",
    "TELEGRAM_NOETFIELD_OPS_BOT_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_OPS_CHAT_ID",
    "NOETFIELD_SUPABASE_DATABASE_URL",
    "DATABASE_URL",
    "RESEND_API_KEY",
    "OPENROUTER_API_KEY",
]
files = sys.argv[1:]

def parse(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out

merged: dict[str, str] = {}
for f in files:
    merged.update(parse(Path(f)))

gmail_file_candidates = [
    merged.get("GMAIL_SERVICE_ACCOUNT_JSON_FILE", ""),
    merged.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
    str(Path.home() / ".sourcea-secrets/noetfield-gmail-service-account.json"),
    str(Path.home() / ".sourcea-secrets/gmail-service-account.json"),
]
gmail_json = bool(merged.get("GMAIL_SERVICE_ACCOUNT_JSON") or merged.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
if not gmail_json:
    gmail_json = any(Path(p).is_file() for p in gmail_file_candidates if p)

tg = merged.get("TELEGRAM_NOETFIELD_OPS_BOT_TOKEN") or merged.get("TELEGRAM_BOT_TOKEN")
print(
    json.dumps(
        {
            "vault_files": {Path(f).name: Path(f).is_file() for f in files},
            "resolved": {
                "ADMIN_DASHBOARD_SECRET": bool(merged.get("ADMIN_DASHBOARD_SECRET")),
                "GMAIL_SERVICE_ACCOUNT_JSON": gmail_json,
                "TELEGRAM_OPS_BOT_TOKEN": bool(tg),
                "TELEGRAM_OPS_CHAT_ID": bool(merged.get("TELEGRAM_OPS_CHAT_ID")),
                "DATABASE_URL": bool(
                    merged.get("DATABASE_URL") or merged.get("NOETFIELD_SUPABASE_DATABASE_URL")
                ),
            },
        }
    )
)
PY
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-status}" in
    status) platform_vault_status ;;
    get)
      shift
      read_platform_vault "${1:?key required}"
      ;;
    gmail-json) read_gmail_service_account_json ;;
    *)
      echo "usage: $0 [status|get KEY|gmail-json]" >&2
      exit 2
      ;;
  esac
fi
