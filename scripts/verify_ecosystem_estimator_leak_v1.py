#!/usr/bin/env python3
"""Verify the ecosystem-mode fix — no more singular querySelector(".tb-estimator-fields")."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "assets" / "noetfield-intake-ecosystem-mode.js"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if 'document.querySelector(".tb-estimator-fields")' in text:
        print("FAIL: singular querySelector(\".tb-estimator-fields\") still present", file=sys.stderr)
        return 1
    if 'document.querySelectorAll(".tb-estimator-fields")' not in text:
        print("FAIL: expected querySelectorAll(\".tb-estimator-fields\") not found", file=sys.stderr)
        return 1
    print("OK: ecosystem-mode hides every .tb-estimator-fields match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
