#!/usr/bin/env bash
# Poll platform /api/public/chat/health until git_sha matches expected (deploy gate).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPECTED_SHA=""
PLATFORM_BASE="${PLATFORM_BASE:-https://platform.noetfield.com}"
TIMEOUT_SEC="${TIMEOUT_SEC:-360}"
INTERVAL_SEC="${INTERVAL_SEC:-10}"

usage() {
  cat <<'EOF'
Usage: wait-for-platform-sha.sh [--expected-sha SHA] [--platform-base URL]

Blocks until live platform git_sha matches expected (prefix-safe).
Exits 1 on timeout.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --expected-sha)
      EXPECTED_SHA="${2:-}"
      shift 2
      ;;
    --platform-base)
      PLATFORM_BASE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "wait-for-platform-sha: unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$EXPECTED_SHA" ]]; then
  EXPECTED_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
fi
if [[ -z "$EXPECTED_SHA" ]]; then
  echo "wait-for-platform-sha: no expected SHA" >&2
  exit 2
fi

health_url="${PLATFORM_BASE%/}/api/public/chat/health"
deadline=$(( $(date +%s) + TIMEOUT_SEC ))
attempt=0

while [[ $(date +%s) -lt $deadline ]]; do
  attempt=$((attempt + 1))
  live="$(curl -sS "$health_url" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('git_sha',''))" 2>/dev/null || true)"
  echo "[wait-for-platform-sha] attempt=${attempt} live=${live:0:12} expected=${EXPECTED_SHA:0:12}"
  if [[ -n "$live" && ( "$live" == "$EXPECTED_SHA" || "${live:0:12}" == "${EXPECTED_SHA:0:12}" ) ]]; then
    echo "[wait-for-platform-sha] PASS"
    exit 0
  fi
  sleep "$INTERVAL_SEC"
done

echo "[wait-for-platform-sha] TIMEOUT after ${TIMEOUT_SEC}s (live=${live:-none})" >&2
exit 1
