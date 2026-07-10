#!/usr/bin/env python3
"""Kaizen fix — noetfield-partner-apply.js: successCopy references an undeclared `fields`
variable (the submit handler's local var is `role`, not `fields`). Only touches the
successCopy block; buildMessage(fields)'s own `fields.role`/`fields.org`/... stay intact."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "assets" / "noetfield-partner-apply.js"
START_MARKER = "successCopy: {"
END_MARKER = "errorCopy: {"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    try:
        start = text.index(START_MARKER)
        end = text.index(END_MARKER, start)
    except ValueError:
        print(f"FAIL: markers not found in {TARGET}", file=sys.stderr)
        return 1

    region = text[start:end]
    fixed_region = region.replace("fields.role", "role")
    if fixed_region == region:
        print("nf_kaizen_fix_partner_apply_reference_error: no change (already fixed?)")
        return 0

    TARGET.write_text(text[:start] + fixed_region + text[end:], encoding="utf-8")
    print("nf_kaizen_fix_partner_apply_reference_error: patched successCopy block")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
