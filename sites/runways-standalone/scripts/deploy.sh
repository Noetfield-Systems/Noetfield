#!/usr/bin/env bash
# Deploy standalone Runways product site to Cloudflare Pages (noetfield-runways).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PROJECT="${CF_PAGES_PROJECT:-noetfield-runways}"
BRANCH="${CF_PAGES_BRANCH:-main}"
ACCOUNT="${CLOUDFLARE_ACCOUNT_ID:-0d0b967b77e2e5535455d39ff3dae72c}"
WRANGLER=(npx --yes wrangler@4.103.0)

export CLOUDFLARE_ACCOUNT_ID="$ACCOUNT"

if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  echo "FAIL: CLOUDFLARE_API_TOKEN required" >&2
  exit 2
fi

echo "[runways-standalone] ensure project ${PROJECT}"
"${WRANGLER[@]}" pages project list 2>/dev/null | grep -q "${PROJECT}" || \
  "${WRANGLER[@]}" pages project create "${PROJECT}" --production-branch="${BRANCH}"

if [[ -n "${RUNWAY_RUNTIME_API_SECRET:-}" ]]; then
  echo "[runways-standalone] sync Motor dispatch secrets"
  printf '%s' "$RUNWAY_RUNTIME_API_SECRET" | "${WRANGLER[@]}" pages secret put RUNWAY_RUNTIME_API_SECRET --project-name "$PROJECT"
  printf '%s' "${RUNWAY_RUNTIME_BASE_URL:-https://noetfield-runway-runtime-api-staging.sina-kazemnezhad-ca.workers.dev}" | \
    "${WRANGLER[@]}" pages secret put RUNWAY_RUNTIME_BASE_URL --project-name "$PROJECT"
  printf '%s' "${RUNWAY_RUNTIME_KEY_ID:-staging-proof}" | \
    "${WRANGLER[@]}" pages secret put RUNWAY_RUNTIME_KEY_ID --project-name "$PROJECT"
fi

echo "[runways-standalone] deploy public/ + functions/"
"${WRANGLER[@]}" pages deploy public \
  --project-name "$PROJECT" \
  --branch "$BRANCH" \
  --commit-dirty=true

echo "[runways-standalone] live https://${PROJECT}.pages.dev/"
