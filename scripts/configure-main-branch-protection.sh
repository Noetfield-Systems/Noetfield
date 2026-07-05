#!/usr/bin/env bash
# Require validate / validate on main before merge.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-Noetfield-Systems/Noetfield}"
CHECK_CONTEXT="${NF_REQUIRED_CHECK_CONTEXT:-validate / validate}"

log() { printf '[configure-main-branch-protection] %s\n' "$*"; }

body="$(python3 -c "
import json
print(json.dumps({
  'required_status_checks': {
    'strict': True,
    'checks': [{'context': '${CHECK_CONTEXT}'}],
  },
  'enforce_admins': False,
  'required_pull_request_reviews': None,
  'restrictions': None,
  'allow_force_pushes': False,
  'allow_deletions': False,
}))
")"

log "setting required check on main: ${CHECK_CONTEXT}"
gh api "repos/${REPO}/branches/main/protection" -X PUT --input - <<<"$body"
log "PASS — main requires ${CHECK_CONTEXT}"
