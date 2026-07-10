#!/usr/bin/env python3
"""Verify the partner-apply.js fix — exactly one legitimate `fields.role` should remain,
the one inside buildMessage(fields); the two inside successCopy must be gone."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "assets" / "noetfield-partner-apply.js"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    count = text.count("fields.role")
    if count != 1:
        print(
            f"FAIL: expected exactly 1 remaining 'fields.role' (buildMessage's own param), found {count}",
            file=sys.stderr,
        )
        return 1
    print("OK: fields.role appears exactly once (buildMessage scope only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
