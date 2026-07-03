#!/usr/bin/env python3
"""Insert Advisor/Architect checklist stubs into markdown files missing required keys.

Non-destructive: creates a timestamped backup of each edited file (*.bak.TIMESTAMP).
Run from repo root: python3 scripts/insert_advisor_checklist_stubs.py
"""
from pathlib import Path
import time
import sys

ROOT = Path(__file__).resolve().parent.parent
CHECK_KEYS = ['protects:', 'sina_workload:', 'permission_loop:', 'sandbox_autonomy:', 'target_to_blocker:']

STUB = (
    "<!-- ADVISOR_ARCHITECT_CHECKLIST_STUB (auto-inserted) -->\n"
    "Advisor / Architect Minimal Checklist (AUTO-STUB)\n"
    "-----------------------------------------------\n\n"
    "- protects: Which founder goal does this protect? (pick one)\n"
    "- sina_workload: reduces / increases + short rationale\n"
    "- permission_loop: yes / no + explanation\n"
    "- sandbox_autonomy: yes / no + where/how (sandbox lane path)\n"
    "- target_to_blocker: yes / no + mitigation\n"
    "- canon_version: (string)\n"
    "- sandbox_evidence: link(s) to sandbox receipt(s)\n\n"
)

def should_insert(text: str) -> bool:
    low = text.lower()
    return not all(k in low for k in CHECK_KEYS)

def insert_stub(p: Path) -> bool:
    txt = p.read_text(encoding='utf-8')
    if not should_insert(txt):
        return False
    ts = int(time.time())
    bak = p.with_suffix(p.suffix + f'.bak.{ts}')
    bak.write_text(txt, encoding='utf-8')
    new = STUB + txt
    p.write_text(new, encoding='utf-8')
    return True

def find_targets():
    paths = []
    docs = ROOT / 'docs'
    if docs.exists():
        paths += list(docs.rglob('*.md'))
    templates = ROOT / '.agent-policy' / 'dispatch-templates'
    if templates.exists():
        paths += list(templates.rglob('*.md'))
    return paths

def main():
    targets = find_targets()
    edited = []
    for p in targets:
        try:
            if insert_stub(p):
                edited.append(str(p))
        except Exception as e:
            print(f"ERROR editing {p}: {e}")
    print(f"Inserted stubs into {len(edited)} files.")
    for e in edited[:50]:
        print(" -", e)
    if len(edited) > 50:
        print(f"...and {len(edited)-50} more")

if __name__ == '__main__':
    main()
