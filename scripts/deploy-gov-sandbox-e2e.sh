#!/usr/bin/env bash
# Full gov-sandbox ship: Railway → regenerate www proxy → Cloudflare → live verify.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RAILWAY_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --railway-only) RAILWAY_ONLY=1 ;;
  esac
done

EXPECTED_SHA="$(git rev-parse HEAD)"

bash scripts/deploy-gov-sandbox-railway.sh

if [[ "$RAILWAY_ONLY" -eq 1 ]]; then
  echo "deploy-gov-sandbox-e2e: railway-only — skipping www"
  exit 0
fi

python3 scripts/generate-www-deny-middleware.py
python3 scripts/generate-cf-redirects.py
bash scripts/deploy-www-cloudflare.sh
python3 scripts/nf_post_deploy_verify.py --expected-sha "$EXPECTED_SHA" --surface www
bash scripts/verify-www-live-sandbox.sh

echo "deploy-gov-sandbox-e2e: PASS"
