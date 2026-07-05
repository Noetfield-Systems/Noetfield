#!/usr/bin/env bash
# Post-deploy smoke: health endpoints + optional production base URL.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="${ROOT}:${ROOT}/packages/types:${ROOT}/packages/config:${ROOT}/services/events:${ROOT}/services/ledger:${ROOT}/services/graph:${ROOT}/services/governance:${ROOT}/services/signals:${ROOT}/services/workflow:${ROOT}/services/ai-runtime:${ROOT}/services/inspectors:${ROOT}/services/identity:${ROOT}/services/copilot-governance:${ROOT}/services/factories:${ROOT}/services/trust-brief:${ROOT}/services/legal-review:${ROOT}/services/aml-trace"
export RUNTIME_EVENT_STORE="${RUNTIME_EVENT_STORE:-memory}"
BASE="${PLATFORM_HEALTH_BASE:-http://127.0.0.1:8001}"

echo "== Secret audit =="
python3 "${ROOT}/scripts/audit_no_secrets_in_repo.py"

echo "== Unit tests (chat, telegram, intake) =="
python3 -m pytest "${ROOT}/tests/unit/test_public_chat.py" \
  "${ROOT}/tests/unit/test_openrouter_client.py" \
  "${ROOT}/tests/unit/test_telegram_webhook.py" \
  "${ROOT}/tests/unit/test_public_intake.py" \
  "${ROOT}/tests/unit/test_practical_ecosystem.py" -q

echo "== Health endpoints: ${BASE} =="
if [[ "${BASE}" == "http://127.0.0.1:8001" ]]; then
  uvicorn noetfield_governance.api:app --host 127.0.0.1 --port 8001 --app-dir "${ROOT}/services/governance" &
  UV_PID=$!
  sleep 4
  trap 'kill "${UV_PID}" 2>/dev/null || true' EXIT
fi
PLATFORM_HEALTH_BASE="${BASE}" python3 "${ROOT}/scripts/verify_platform_health.py"

echo "Deploy smoke complete."
