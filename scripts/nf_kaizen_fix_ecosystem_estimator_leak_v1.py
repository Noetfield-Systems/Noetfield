#!/usr/bin/env python3
"""Kaizen fix — noetfield-intake-ecosystem-mode.js hides only the FIRST element matching
class .tb-estimator-fields (querySelector), but two elements share that class (a section
label and its content wrapper holding the actual required fields). Switch to
querySelectorAll and hide every match."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "assets" / "noetfield-intake-ecosystem-mode.js"

OLD = (
    '    var trustEstimator = document.querySelector(".tb-estimator-fields");\n'
    '    var pilotScope = document.querySelector(".pilot-scope-fields");\n'
    "    if (trustEstimator) trustEstimator.hidden = true;\n"
    "    if (pilotScope) pilotScope.hidden = true;\n"
)
NEW = (
    '    var trustEstimatorEls = document.querySelectorAll(".tb-estimator-fields");\n'
    '    var pilotScope = document.querySelector(".pilot-scope-fields");\n'
    "    trustEstimatorEls.forEach(function (el) { el.hidden = true; });\n"
    "    if (pilotScope) pilotScope.hidden = true;\n"
)


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if OLD not in text:
        if NEW in text:
            print("nf_kaizen_fix_ecosystem_estimator_leak: no change (already fixed?)")
            return 0
        print("FAIL: expected block not found (file changed shape?)", file=sys.stderr)
        return 1

    TARGET.write_text(text.replace(OLD, NEW), encoding="utf-8")
    print("nf_kaizen_fix_ecosystem_estimator_leak: querySelector -> querySelectorAll")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
