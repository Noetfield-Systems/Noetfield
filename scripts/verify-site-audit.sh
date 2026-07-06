#!/usr/bin/env bash
# verify-site-audit.sh — Noetfield site-audit machine v2 (disk gate, P0 fail-closed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== verify-site-audit (disk / P0) ==="
python3 scripts/nf_site_audit_v1.py --mode disk --fail-on P0
echo "verify-site-audit PASS"
