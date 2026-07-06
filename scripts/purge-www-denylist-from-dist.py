#!/usr/bin/env python3
"""Remove PUBLIC_OUTPUT_DENYLIST paths from www-pages-dist (static files beat _redirects)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DENYLIST = ROOT / "governance" / "PUBLIC_OUTPUT_DENYLIST.json"
DIST = ROOT / "www-pages-dist"


def main() -> int:
    if not DIST.is_dir():
        print("purge-www-denylist: skip — no www-pages-dist")
        return 0
    data = json.loads(DENYLIST.read_text(encoding="utf-8"))
    removed = 0
    for rel in data.get("exact_paths", []):
        p = DIST / rel.lstrip("/")
        if p.is_file():
            p.unlink()
            removed += 1
        elif p.is_dir():
            shutil.rmtree(p)
            removed += 1
    for prefix in data.get("prefix_paths", []):
        base = DIST / prefix.lstrip("/").rstrip("/")
        if base.is_dir():
            shutil.rmtree(base)
            removed += 1
        elif base.is_file():
            base.unlink()
            removed += 1
    print(f"purge-www-denylist: removed {removed} denylist target(s) from {DIST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
