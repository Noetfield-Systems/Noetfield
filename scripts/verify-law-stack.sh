#!/usr/bin/env bash
# verify-law-stack.sh — anti-fragmentation / anti-staleness / anti-drift for law stack
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

MANIFEST="$ROOT/governance/LAW_STACK.json"
[[ -f "$MANIFEST" ]] || fail "missing governance/LAW_STACK.json"

python3 -c "
import json, sys
from pathlib import Path
root = Path('$ROOT')
m = json.loads((root / 'governance/LAW_STACK.json').read_text())
for key in ('manifest_version', 'active_l0', 'active_gtm', 'entry_points', 'verify_commands'):
    if key not in m:
        sys.exit(f'manifest missing key: {key}')
for rel in m['entry_points'].values():
    if not (root / rel).is_file():
        sys.exit(f'entry point missing: {rel}')
" || fail "LAW_STACK.json invalid or entry points missing"

ok "LAW_STACK.json valid"

[[ -f docs/LAWS/CURRENT_STACK_v2026.md ]] || fail "missing docs/LAWS/CURRENT_STACK_v2026.md"
[[ -f docs/LAWS/README.md ]] || fail "missing docs/LAWS/README.md"
[[ -f docs/LAWS/ROUTING.md ]] || fail "missing docs/LAWS/ROUTING.md"
[[ -f docs/LAWS/PIPELINES.md ]] || fail "missing docs/LAWS/PIPELINES.md"
[[ -f L0-law/CURRENT.md ]] || fail "missing L0-law/CURRENT.md"
[[ -f docs/SOURCE_OF_TRUTH/archive/SUPERSESSION_INDEX.md ]] || fail "missing supersession index"

ok "law hub files present"

# Active L0 must be registered
python3 -c "
import json, sys
from pathlib import Path
root = Path('$ROOT')
m = json.loads((root / 'governance/LAW_STACK.json').read_text())
active = m['active_l0']['doc_id']
reg = json.loads((root / 'docs/SOURCE_OF_TRUTH/registry/source_of_truth_registry.json').read_text())
l0 = next((d for d in reg['decisions'] if d['domain'] == 'noetfield_constitution_l0'), None)
if not l0 or l0.get('active_document_key') != active:
    sys.exit(f'active L0 mismatch in source_of_truth_registry.json: {l0}')
inv = json.loads((root / 'docs/SOURCE_OF_TRUTH/registry/source_document_inventory.json').read_text())
doc = next((d for d in inv['documents'] if d['document_key'] == active), None)
if not doc:
    sys.exit(f'active L0 {active} not in source_document_inventory.json')
if doc.get('classification') != 'active_source_of_truth':
    sys.exit(f'active L0 classification is {doc.get(\"classification\")}')
" || fail "active L0 not registered as active"

ok "active L0 registered"

# CURRENT.md must reference active doc id
grep -q "noetfield-constitution-gcip-v4" L0-law/CURRENT.md || fail "L0-law/CURRENT.md stale"
grep -q "noetfield-constitution-gcip-v4" docs/LAWS/CURRENT_STACK_v2026.md || fail "CURRENT_STACK stale"

ok "visible current stack references GCIP v4"

# Duplicate files must be listed in supersession index
python3 -c "
from pathlib import Path
root = Path('$ROOT')
uploaded = root / 'docs/SOURCE_OF_TRUTH/uploaded'
dups = sorted(uploaded.glob('*-duplicate.md'))
index = (root / 'docs/SOURCE_OF_TRUTH/archive/SUPERSESSION_INDEX.md').read_text()
missing = [p.name for p in dups if p.name not in index]
if missing:
    raise SystemExit('duplicates not indexed: ' + ', '.join(missing))
" || fail "duplicate files not in SUPERSESSION_INDEX"

ok "duplicate uploads indexed in archive"

# Derived mirror should match registry rule count (anti-drift)
python3 -c "
import json
from pathlib import Path
root = Path('$ROOT')
canon = json.loads((root / 'docs/SOURCE_OF_TRUTH/registry/active_rule_candidates.json').read_text())
mirror = root / 'Noetfield-All-Documents/registry/active_rule_candidates.json'
if mirror.is_file():
    m = json.loads(mirror.read_text())
    if len(m.get('rules', [])) != len(canon.get('rules', [])):
        raise SystemExit(f'mirror rule drift: canon={len(canon.get(\"rules\",[]))} mirror={len(m.get(\"rules\",[]))} — run make sync-derived-docs')
" || fail "derived registry drift (run make sync-derived-docs)"

ok "derived registry rule count aligned"

# NORTH_STAR should point to law hub
grep -q "docs/LAWS" NORTH_STAR.md || fail "NORTH_STAR.md missing docs/LAWS link"

ok "NORTH_STAR links law hub"

echo ""
echo "verify-law-stack: all checks passed"
