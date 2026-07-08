#!/usr/bin/env bash
# Verify Noetfield Voyage AI live wire receipt (SourceA anti-drift pattern).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 scripts/nf_voyage_ai_live_wire_v1.py --json
