#!/usr/bin/env bash
# Sync nf-probe-cron EXPECTED_GIT_SHA to repo HEAD (drift probe SSOT).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKER_DIR="$ROOT/infra/nf-probe-cron"
SHA="${1:-$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)}"

if [[ -z "$SHA" ]]; then
  echo "sync-probe-expected-sha: no SHA" >&2
  exit 2
fi

if ! command -v wrangler >/dev/null 2>&1; then
  echo "sync-probe-expected-sha: wrangler not installed" >&2
  exit 1
fi

cd "$WORKER_DIR"
printf '%s' "$SHA" | wrangler secret put EXPECTED_GIT_SHA >/dev/null
echo "[sync-probe-expected-sha] EXPECTED_GIT_SHA=${SHA:0:12}"
