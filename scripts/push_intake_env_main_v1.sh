#!/usr/bin/env bash
# Push Noetfield intake env → main Vercel (the-777-foundation / noetfield) + redeploy.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SCOPE="${NF_VERCEL_SCOPE:-the-777-foundation}"
PROJECT="${NF_VERCEL_PROJECT:-noetfield}"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/noetfield-trial-env-clone-v1.env}"
KEYS="RESEND_API_KEY INTAKE_EMAIL_FROM INTAKE_EMAIL_TO INTAKE_AUTO_ACK_ENABLED"

NPX="/usr/local/bin/npx"
if [[ ! -x "${NPX}" ]]; then NPX="$(command -v npx || echo npx)"; fi
VC=("${NPX}" --yes vercel@latest)

log() { printf '[push-intake-main] %s\n' "$*"; }

log "whoami:"
"${VC[@]}" whoami
log "teams:"
"${VC[@]}" teams ls

[[ -f "${VAULT}" ]] || { log "FAIL: missing ${VAULT}"; exit 1; }

log "link → ${SCOPE}/${PROJECT}"
rm -rf .vercel
"${VC[@]}" link --project "${PROJECT}" --scope "${SCOPE}" --yes

read_val() {
  local key="$1"
  grep -E "^${key}=" "${VAULT}" | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//'
}

for key in ${KEYS}; do
  val="$(read_val "${key}")"
  if [[ -z "${val}" ]]; then
    log "WARN: skip ${key} (empty in vault)"
    continue
  fi
  log "env add ${key} → production"
  "${VC[@]}" env add "${key}" production \
    --scope "${SCOPE}" \
    --force --yes \
    --value "${val}" 2>&1 | tail -2 || log "warn: ${key} may already exist"
done

log "redeploy production"
"${VC[@]}" deploy --prod --scope "${SCOPE}" --yes 2>&1 | tail -15

log "intake health www.noetfield.com:"
curl -sS "https://www.noetfield.com/api/intake/health" | python3 -m json.tool || true

log "DONE — if delivery_mode=resend → safe to delete trial www"
