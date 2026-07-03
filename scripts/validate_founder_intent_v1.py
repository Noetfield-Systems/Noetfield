#!/usr/bin/env python3
"""Validate minimal Founder Intent requirements across receipts and advisor/architect outputs.

Checks performed:
- JSON receipts under receipts/ must include `canon_version`.
- Markdown outputs under .agent-policy/dispatch-templates/ and docs/ must include required checklist keys.

Exit code 0 on success, 1 on any violation.
"""
import sys
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent

def check_receipts():
    failures = []
    rec_dir = ROOT / "receipts"
    if not rec_dir.exists():
        return failures
    for p in rec_dir.rglob('*.json'):
        try:
            j = json.loads(p.read_text())
        except Exception as e:
            failures.append(f"BAD_JSON: {p}: {e}")
            continue
        if 'canon_version' not in j:
            failures.append(f"MISSING_CANON: {p}")
    return failures

REQUIRED_KEYS = [
    'protects:',
    'sina_workload:',
    'permission_loop:',
    'sandbox_autonomy:',
    'target_to_blocker:'
]

def check_markdown():
    failures = []
    paths = []
    paths += list((ROOT / '.agent-policy' / 'dispatch-templates').rglob('*.md')) if (ROOT / '.agent-policy').exists() else []
    paths += list((ROOT / 'docs').rglob('*.md')) if (ROOT / 'docs').exists() else []
    for p in paths:
        txt = p.read_text(encoding='utf-8')
        low = txt.lower()
        missing = [k for k in REQUIRED_KEYS if k not in low]
        if missing:
            failures.append(f"MISSING_KEYS: {p} -> {', '.join(missing)}")
    return failures

def main():
    fails = []
    fails += check_receipts()
    fails += check_markdown()
    if fails:
        print("FOUND violations:")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("Founder intent checks passed.")
    sys.exit(0)

if __name__ == '__main__':
    main()
