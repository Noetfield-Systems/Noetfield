#!/usr/bin/env bash
# Clone Noetfield trial Vercel (www / project-gc7lm) → local vault + receipt.
# Run while logged into trial CLI OR with trial token.
# Law: docs/VERCEL_PRO_MIGRATION_WEEK_LOCKED_v1.md
#
# Usage:
#   NF_VERCEL_SCOPE=noetfield-systems bash scripts/clone_noetfield_trial_to_local_v1.sh
# Receipt: ~/.sina/noetfield-trial-clone-receipt-v1.json
# Env clone: ~/.sina/noetfield-trial-env-clone-v1.env (600 — never commit)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/www-vercel-canonical.sh
source "$ROOT/scripts/www-vercel-canonical.sh"

SINA="${HOME}/.sina"
ARCHIVE="${CLONE_ARCHIVE:-$HOME/Desktop/SourceA/archive/noetfield-trial-clone-v1}"
ENV_CLONE="${SINA}/noetfield-trial-env-clone-v1.env"
VAULT="${NF_SECRETS_VAULT}"
RECEIPT="${SINA}/noetfield-trial-clone-receipt-v1.json"
TRIAL_URL="${NF_WWW_DEPLOY_URL}"
MAIN_URL="${NF_WWW_CANONICAL_URL}"
NPX="/usr/local/bin/npx"
if [[ ! -x "${NPX}" ]]; then NPX="$(command -v npx || echo npx)"; fi
VC=("${NPX}" --yes vercel@latest)

log() { printf '[clone-noetfield-trial] %s\n' "$*"; }

mkdir -p "${ARCHIVE}" "${SINA}"

health_json() {
  local base="$1"
  curl -sS "${base%/}/api/intake/health" 2>/dev/null || echo '{}'
}

log "=== Noetfield trial clone check ==="
log "Trial scope: ${NF_VERCEL_SCOPE} · project: ${NF_VERCEL_PROJECT}"
log "Trial URL: ${TRIAL_URL}"
log "Main URL:  ${MAIN_URL}"

TRIAL_HEALTH="$(health_json "${TRIAL_URL}")"
MAIN_HEALTH="$(health_json "${MAIN_URL}")"

log "Pulling production env from trial Vercel (names + values → ${ENV_CLONE})…"
PULL_OK=0
if "${VC[@]}" env pull "${ENV_CLONE}" \
  --environment=production \
  --scope="${NF_VERCEL_SCOPE}" \
  --yes 2>/dev/null; then
  chmod 600 "${ENV_CLONE}"
  PULL_OK=1
  log "PASS: env pulled to ${ENV_CLONE}"
else
  log "WARN: vercel env pull failed — syncing from ${VAULT} instead"
  : > "${ENV_CLONE}.tmp"
  chmod 600 "${ENV_CLONE}.tmp"
  for key in ${NF_INTAKE_ENV_KEYS}; do
    line="$(grep -E "^${key}=" "${VAULT}" 2>/dev/null | tail -1 || true)"
    if [[ -n "${line}" ]]; then
      echo "${line}" >> "${ENV_CLONE}.tmp"
    fi
  done
  if [[ -s "${ENV_CLONE}.tmp" ]]; then
    mv "${ENV_CLONE}.tmp" "${ENV_CLONE}"
    PULL_OK=1
    log "PASS: vault copy → ${ENV_CLONE}"
  else
    rm -f "${ENV_CLONE}.tmp"
    log "FAIL: no env in Vercel pull or vault"
  fi
fi

# Sync vault if pull succeeded and vault missing keys
if [[ "${PULL_OK}" == "1" && -f "${ENV_CLONE}" ]]; then
  touch "${VAULT}"
  chmod 600 "${VAULT}" 2>/dev/null || true
  for key in ${NF_INTAKE_ENV_KEYS}; do
    if ! grep -qE "^${key}=" "${VAULT}" 2>/dev/null; then
      line="$(grep -E "^${key}=" "${ENV_CLONE}" | tail -1 || true)"
      if [[ -n "${line}" ]]; then
        echo "${line}" >> "${VAULT}"
        log "vault backfill: ${key}"
      fi
    fi
  done
fi

# Env manifest (names only in archive)
ENV_MANIFEST="${ARCHIVE}/env-keys-manifest.txt"
{
  echo "# Noetfield trial www env — key names only · $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# Full values: ~/.sina/noetfield-trial-env-clone-v1.env (NEVER commit)"
  for key in ${NF_INTAKE_ENV_KEYS}; do
    in_clone=no
    in_vault=no
    [[ -f "${ENV_CLONE}" ]] && grep -qE "^${key}=" "${ENV_CLONE}" && in_clone=yes
    [[ -f "${VAULT}" ]] && grep -qE "^${key}=" "${VAULT}" && in_vault=yes
    echo "${key} clone=${in_clone} vault=${in_vault}"
  done
} > "${ENV_MANIFEST}"

# Intake vectors doc copy
cp -f "${ROOT}/docs/ops/VERCEL_INTAKE_SETUP.md" "${ARCHIVE}/VERCEL_INTAKE_SETUP.md" 2>/dev/null || true
cp -f "${ROOT}/docs/INTAKE_OPS.md" "${ARCHIVE}/INTAKE_OPS.md" 2>/dev/null || true

python3 - <<PY
import json, datetime
from pathlib import Path

def parse_health(s):
    try:
        return json.loads(s)
    except Exception:
        return {}

trial = parse_health('''${TRIAL_HEALTH}''')
main = parse_health('''${MAIN_HEALTH}''')

keys = "${NF_INTAKE_ENV_KEYS}".split()
clone_path = Path("${ENV_CLONE}")
vault_path = Path("${VAULT}")
env_ok = all(
    (clone_path.is_file() and f"{k}=" in clone_path.read_text())
    or (vault_path.is_file() and f"{k}=" in vault_path.read_text())
    for k in keys
)

row = {
    "schema": "noetfield-trial-clone-v1",
    "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "trial_scope": "${NF_VERCEL_SCOPE}",
    "trial_project": "${NF_VERCEL_PROJECT}",
    "trial_url": "${TRIAL_URL}",
    "main_url": "${MAIN_URL}",
    "env_clone_path": str(clone_path),
    "vault_path": str(vault_path),
    "env_keys_complete": env_ok,
    "vercel_env_pull": bool(${PULL_OK}),
    "intake_health": {
        "trial": trial,
        "main": main,
    },
    "trial_intake_green": trial.get("www_email_configured") is True and trial.get("delivery_mode") == "resend",
    "main_intake_green": main.get("www_email_configured") is True,
    "safe_to_delete_trial_www": env_ok and trial.get("www_email_configured") is True,
    "after_delete": "Push env to main noetfield on the-777-foundation · bash scripts/auto-heal-www.sh with NF_VERCEL_SCOPE=the-777-foundation",
    "archive": "${ARCHIVE}",
}
Path("${RECEIPT}").write_text(json.dumps(row, indent=2) + "\\n")
Path("${ARCHIVE}/manifest.json").write_text(json.dumps(row, indent=2) + "\\n")
print(json.dumps(row, indent=2))
PY

log "Receipt: ${RECEIPT}"
if python3 -c "import json; r=json.load(open('${RECEIPT}')); exit(0 if r.get('safe_to_delete_trial_www') else 1)"; then
  log "PASS: local has intake env + trial intake was green — safe to delete trial www AFTER copying env to main"
else
  log "HOLD: fix env clone before deleting trial www"
  exit 1
fi
