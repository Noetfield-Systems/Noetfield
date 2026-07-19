#!/usr/bin/env bash
# Anti-downgrade gate — interactive buyer surfaces must not shrink or lose live-demo hooks
# when agents ship other www upgrades (audit, copy, asset pins, CI).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASELINE="${ROOT}/data/www-interactive-baseline-v1.json"
fail=0

echo "=== verify-www-interactive-fidelity (no interactive downgrade) ==="

if [[ ! -f "$BASELINE" ]]; then
  echo "FAIL missing baseline: data/www-interactive-baseline-v1.json" >&2
  exit 1
fi

python3 - <<'PY'
import json
import sys
from pathlib import Path

root = Path(".")
baseline = json.loads((root / "data/www-interactive-baseline-v1.json").read_text())
errors: list[str] = []

for surf in baseline.get("surfaces", []):
    rel = surf["path"]
    path = root / rel
    sid = surf.get("id", rel)
    if not path.is_file():
        errors.append(f"{sid}: missing file {rel}")
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    size = path.stat().st_size
    min_bytes = int(surf.get("min_bytes", 0))
    if size < min_bytes:
        errors.append(f"{sid}: size {size} < baseline min_bytes {min_bytes} — likely interactive downgrade")
    for marker in surf.get("required_markers", []):
        if marker not in text:
            errors.append(f"{sid}: missing required marker {marker!r}")

demo = root / "copilot/demo/index.html"
if demo.is_file():
    dt = demo.read_text(encoding="utf-8", errors="replace")
    has_mock = "nf-workspace-mock" in dt
    has_ssot = "nfSsotDemo" in dt and "nf26-demoStepper" in dt
    has_trace = "noetfield-agent-trace-demo.js" in dt
    if has_mock and not (has_ssot and has_trace):
        errors.append(
            "copilot-demo: nf-workspace-mock present without full interactive demo (ssot + agent trace) — mock-only regression"
        )

index = root / "index.html"
if index.is_file():
    it = index.read_text(encoding="utf-8", errors="replace")
    if "nf-corp" not in it:
        errors.append("homepage: missing nf-corp corporate shell")
    if "nfLiveProofForm" in it:
        errors.append("homepage: unexpected live-proof playground on corporate homepage")

if errors:
    for e in errors:
        print(f"FAIL {e}", file=sys.stderr)
    print(
        "Fix: restore interactive sections from scripts/templates/copilot-demo-nf26.html "
        "or prior commit; never drop nf26-* hooks for validator/copy passes alone.",
        file=sys.stderr,
    )
    sys.exit(1)

print("OK   all interactive baseline surfaces present")
print(f"OK   SSOT note: {baseline.get('live_sandbox_ssot', {}).get('note', '')}")
PY

echo "verify-www-interactive-fidelity PASS"
