#!/usr/bin/env bash
# verify-uiux-library-2026.sh — library SSOT presence + pack floor
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "=== verify-uiux-library-2026 ==="
LIB="data/nf-uiux-library-2026-v1.json"
[[ -f "$LIB" ]] || { echo "FAIL missing $LIB" >&2; exit 1; }
[[ -f .cursor/skills/SKILL-012-uiux-library-2026.md ]] || { echo "FAIL missing SKILL-012" >&2; exit 1; }
python3 - << PY
import json
from pathlib import Path
lib = json.loads(Path("$LIB").read_text())
assert lib.get("schema") == "nf-uiux-library-2026-v1", lib.get("schema")
packs = lib.get("style_packs") or {}
need = {"advisory","bakery","freight","clinic","saas","legal","default"}
missing = need - set(packs)
assert not missing, f"missing packs {missing}"
assert len(packs) >= 12, f"expected >=12 packs, got {len(packs)}"
assert len(lib.get("categories") or []) >= 10
assert lib.get("craft", {}).get("forbid_all_caps_cta") is True
print(f"OK   {lib['schema']} v{lib.get('version')} packs={len(packs)} categories={len(lib.get('categories') or [])}")
PY
echo "verify-uiux-library-2026 PASS"
