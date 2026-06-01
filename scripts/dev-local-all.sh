#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

PUBLIC_PORT="${NF_DEV_PUBLIC_PORT:-13080}"
URLS_FILE="${ROOT}/.local-dev-urls.txt"
PROXY_PID_FILE="${ROOT}/.dev-proxy.pid"
PROXY_LOG="${ROOT}/.dev-proxy.log"

chmod +x "${ROOT}/scripts/ensure-platform-console.sh" \
  "${ROOT}/scripts/dev-cognitive-dashboard.sh" \
  "${ROOT}/scripts/dev-unified-proxy.py" 2>/dev/null || true

kill_port() {
  local p="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -tiTCP:"$p" -sTCP:LISTEN 2>/dev/null | xargs -r kill -9 2>/dev/null || true
  fi
}

echo "=== Noetfield local dev (ONE port: ${PUBLIC_PORT}) ==="

# Internal backends (not forwarded separately)
export PLATFORM_CONSOLE_PORT="${NF_DEV_PLATFORM_PORT}"
export COGNITIVE_DASHBOARD_PORT="${NF_DEV_WEB_PORT}"
export COGNITIVE_DASHBOARD_API_PORT="${NF_DEV_GOV_API_PORT}"

"${ROOT}/scripts/ensure-platform-console.sh"

WEB_URL="http://127.0.0.1:${COGNITIVE_DASHBOARD_PORT}/cognitive-dashboard"
if ! curl -sf -o /dev/null --connect-timeout 2 "$WEB_URL" 2>/dev/null; then
  nohup env COGNITIVE_DASHBOARD_PORT="$COGNITIVE_DASHBOARD_PORT" \
    COGNITIVE_DASHBOARD_API_PORT="$COGNITIVE_DASHBOARD_API_PORT" \
    bash "${ROOT}/scripts/dev-cognitive-dashboard.sh" >>"${ROOT}/.cognitive-dashboard.log" 2>&1 &
  echo $! >"${ROOT}/.cognitive-dashboard.pid"
  for _ in $(seq 1 60); do
    curl -sf -o /dev/null --connect-timeout 2 "$WEB_URL" 2>/dev/null && break
    sleep 1
  done
fi

# Unified public proxy on 13080 only
kill_port "$PUBLIC_PORT"
[[ -f "$PROXY_PID_FILE" ]] && kill "$(cat "$PROXY_PID_FILE")" 2>/dev/null || true
nohup python3 "${ROOT}/scripts/dev-unified-proxy.py" >>"$PROXY_LOG" 2>&1 &
echo $! >"$PROXY_PID_FILE"
sleep 1

check() {
  local path="$1"
  local label="$2"
  curl -sf -o /dev/null --connect-timeout 3 "http://127.0.0.1:${PUBLIC_PORT}${path}" \
    && echo "OK  ${label}  http://localhost:${PUBLIC_PORT}${path}" \
    || echo "FAIL ${label}  http://localhost:${PUBLIC_PORT}${path}" >&2
}

for _ in $(seq 1 30); do
  if curl -sf -o /dev/null --connect-timeout 2 "http://127.0.0.1:${PUBLIC_PORT}/" 2>/dev/null; then
    break
  fi
  sleep 1
done

cat >"$URLS_FILE" <<EOF
# >>> OPEN THIS IN YOUR BROWSER (forward port ${PUBLIC_PORT} in Cursor Ports) <<<
WEBSITE=http://localhost:${PUBLIC_PORT}/
CONSOLE=http://localhost:${PUBLIC_PORT}/console
DASHBOARD=http://localhost:${PUBLIC_PORT}/cognitive-dashboard
EOF

echo ""
cat "$URLS_FILE"
echo ""
check "/" "website"
check "/console" "platform console"
check "/cognitive-dashboard" "cognitive dashboard"
echo ""
echo "If the browser is blank: Cursor → Ports → forward port ${PUBLIC_PORT} → click globe icon."
