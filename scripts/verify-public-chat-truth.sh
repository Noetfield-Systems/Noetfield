#!/usr/bin/env bash
# Fail closed when public chat truth drifts back to stale infrastructure copy.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
ok() { printf 'OK   verify-public-chat-truth: %s\n' "$*"; }
bad() { printf 'FAIL verify-public-chat-truth: %s\n' "$*" >&2; fail=1; }

CHAT_TRUTH_FILES=(
  "PRODUCT_BRIEF.md"
  "data/chatbot/knowledge/faq.md"
  "data/chatbot/knowledge/positioning.md"
  "data/chatbot/knowledge/pricing-matrix.md"
)

FORBIDDEN_PATTERN='Noetfield provides governance execution infrastructure|Noetfield is governance execution infrastructure|records a defensible compliance log|record a compliance log, and return allow or deny|returns a clear allow or deny decision|support compliance and risk management in AI adoption'

for file in "${CHAT_TRUTH_FILES[@]}"; do
  if [[ ! -f "$file" ]]; then
    bad "missing $file"
    continue
  fi
  if grep -Eiq "$FORBIDDEN_PATTERN" "$file"; then
    bad "stale positioning in $file"
    grep -Ein "$FORBIDDEN_PATTERN" "$file" >&2 || true
  fi
done

PYTHONPATH=".:packages/types:packages/config:packages/sdk:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance:services/factories:services/trust-brief:services/legal-review:services/aml-trace" python3 - <<'PY'
from noetfield_governance.chatbot_knowledge import knowledge_manifest_violations

violations = knowledge_manifest_violations()
if violations:
    for violation in violations:
        print(f"FAIL verify-public-chat-truth: {violation}")
    raise SystemExit(2)
print("OK   verify-public-chat-truth: chatbot manifest allowlist")
PY

combined="$(mktemp)"
trap 'rm -f "$combined"' EXIT
for file in "${CHAT_TRUTH_FILES[@]}"; do
  [[ -f "$file" ]] && printf '\n--- %s ---\n' "$file" >> "$combined" && cat "$file" >> "$combined"
done

for required in \
  "audit trail a regulated Copilot rollout will be asked for later" \
  "Copilot Governance Pack" \
  "board PDF" \
  "procurement ZIP" \
  "metadata-only M365"; do
  if grep -qF "$required" "$combined"; then
    ok "required phrase present: $required"
  else
    bad "missing required phrase: $required"
  fi
done

node - <<'NODE'
const handler = require('./api/public/chat/index.js');
const req = { method: 'POST', body: { message: 'Executive overview', session_id: 'verify-public-chat-truth' } };
const res = {
  statusCode: 200,
  headers: {},
  setHeader(k, v) { this.headers[k] = v; },
  status(code) { this.statusCode = code; return this; },
  json(payload) {
    const reply = String(payload && payload.reply || '');
    const stale = /governance execution infrastructure|record a compliance log|allow or deny decisions|support compliance and risk management in AI adoption/i.test(reply);
    const required = [
      'audit trail a regulated Copilot rollout will be asked for later',
      'Copilot Governance Pack',
      'board PDF',
      'procurement ZIP',
      'metadata-only M365',
    ];
    const missing = required.filter((phrase) => !reply.includes(phrase));
    if (this.statusCode !== 200 || stale || missing.length) {
      console.error(JSON.stringify({ statusCode: this.statusCode, stale, missing, reply }, null, 2));
      process.exit(2);
    }
    return this;
  },
  end() { return this; },
};
Promise.resolve(handler(req, res)).catch((err) => {
  console.error(err);
  process.exit(1);
});
NODE
ok "executive overview handler"

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

ok "PASS"
