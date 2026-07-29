#!/usr/bin/env python3
"""Audit canonical corporate routes only — 0 P1/P2 gate for grade restore."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from site_audit import audit as audit_mod  # noqa: E402
from site_audit import crawl as crawl_mod  # noqa: E402

CANONICAL = {
    "/",
    "/about/",
    "/contact/",
    "/motors/",
    "/runways/",
    "/proof/",
    "/trust/",
    "/privacy/",
    "/investors/",
}


def main() -> int:
    snap = ROOT / "reports/www-audit/snapshots/disk"
    snap.mkdir(parents=True, exist_ok=True)
    idx = crawl_mod.crawl_disk(ROOT, snap, max_pages=200)
    idx["snapshots_dir"] = str(snap)
    findings = [
        f
        for f in audit_mod.audit_rows(idx)
        if f.get("www_path") in CANONICAL
    ]
    p1 = sum(1 for f in findings if f.get("severity") == "P1")
    p2 = sum(1 for f in findings if f.get("severity") == "P2")
    if p1 or p2:
        for f in findings:
            if f.get("severity") in ("P1", "P2"):
                print(
                    f"FAIL canonical-audit: {f.get('www_path')} {f.get('check')} {f.get('reason')}",
                    file=sys.stderr,
                )
        print(f"FAIL canonical-audit: P1={p1} P2={p2}", file=sys.stderr)
        return 1
    print(f"OK   canonical-audit: {len(CANONICAL)} routes P1=0 P2=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
