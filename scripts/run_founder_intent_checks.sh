#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Running Founder Intent checks..."
python3 "$ROOT/scripts/validate_founder_intent_v1.py"
echo "Done."
