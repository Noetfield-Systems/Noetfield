#!/usr/bin/env python3
"""Fail closed on prohibited Motor-authority language in public motors page."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOTORS = ROOT / "motors" / "index.html"

PROHIBITED = [
    r"(?<!does not )(?<!not )Motor\s+verif(?:y|ies|ication)",
    r"the\s+Motor\s+verif",
    r"Motor\s+decides\s+what\s+may\s+continue",
    r"Motor\s+decides\s+promotion",
    r"Motor\s+coordinates\s+models\s+as",
    r"Motor\s+owns\s+policy",
    r"Motor\s+judges\s+its\s+own",
    r"Motor\s+approves",
    r"Motor\s+promotes",
    r"(?<!does not )(?<!not )self-authoriz(?:e|es|ation)",
    r"sovereign\s+intelligence",
    r"Motor\s+creates\s+goals",
    r"Motor\s+reasons",
    r"Motor\s+decides\s+whether\s+authority",
    r"coordinates\s+models,\s+specialized\s+engines,\s+agents,\s+tools,\s+policies",
    r"decides\s+what\s+can\s+continue,\s+stop,\s+escalate,\s+recover\s+or\s+be\s+promoted",
    r"how\s+it\s+verifies,\s+escalates",
    r"turn\s+intent,\s+policy,\s+tools\s+and\s+authority\s+into\s+coordinated\s+execution",
]

REQUIRED = [
    "How a run is allowed",
    "Someone else decides what gets accepted",
    "does not mark its own homework",
    "A separate check judges the result",
    "Models generate. Agents participate. Motors operate.",
]


def main() -> int:
    if not MOTORS.is_file():
        print(f"FAIL verify-motor-boundary: missing {MOTORS}", file=sys.stderr)
        return 1
    text = MOTORS.read_text(encoding="utf-8")
    fail = 0
    for pat in PROHIBITED:
        m = re.search(pat, text, re.I)
        if m:
            print(f"FAIL verify-motor-boundary: prohibited — {pat!r} → {m.group(0)!r}", file=sys.stderr)
            fail = 1
    for needle in REQUIRED:
        if needle not in text:
            print(f"FAIL verify-motor-boundary: missing required — {needle!r}", file=sys.stderr)
            fail = 1
    if fail:
        return 1
    print("OK   verify-motor-boundary: motors/index.html boundary language")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
