#!/usr/bin/env python3
"""Lightweight HTML smoke for bank-grade P0 pages and platform console (no browser)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

P0_PAGES = (
    ROOT / "bank-pilot" / "index.html",
    ROOT / "enterprise" / "index.html",
    ROOT / "trust-brief" / "intake" / "index.html",
)

CONSOLE_HTML = (
    ROOT / "services" / "governance" / "noetfield_governance" / "static" / "governance-console-v1.html"
)

P0_MARKERS = ('name="viewport"', "nfHeader", "noetfield-tokens.css")
INSTITUTIONAL_2026_MARKERS = (
    'name="nf-institutional"',
    "noetfield-institutional-2026.css",
    "noetfield-bank-grade.css",
    "nf-site-2026",
)
BANK_PILOT_MARKERS = ("OSFI E-23", "nf-policy-callout", "noetfield-frfi.css")
ENTERPRISE_MARKERS = ("OSFI E-23", "Governance execution pipeline", "noetfield-frfi.css")
TIER_2026_PAGES = (
    ROOT / "index.html",
    ROOT / "partners" / "index.html",
    ROOT / "trust-center" / "index.html",
    ROOT / "trust-ledger" / "index.html",
    ROOT / "copilot" / "index.html",
)
CONSOLE_MARKERS = (
    "noetfield-tokens.css",
    "noetfield-console.css",
    "pilotKeyInput",
    "noetfield_governance_pilot_api_key",
    "audit-export",
)


def main() -> int:
    errors: list[str] = []
    extra_markers: dict[Path, tuple[str, ...]] = {
        ROOT / "bank-pilot" / "index.html": BANK_PILOT_MARKERS,
        ROOT / "enterprise" / "index.html": ENTERPRISE_MARKERS,
    }
    for path in P0_PAGES:
        if not path.is_file():
            errors.append(f"missing P0 page: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in P0_MARKERS:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing {marker!r}")
        for marker in extra_markers.get(path, ()):
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing {marker!r}")

    for path in TIER_2026_PAGES:
        if not path.is_file():
            errors.append(f"missing tier page: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in INSTITUTIONAL_2026_MARKERS:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing 2026 frame {marker!r}")

    if not CONSOLE_HTML.is_file():
        errors.append("governance-console-v1.html missing")
    else:
        text = CONSOLE_HTML.read_text(encoding="utf-8")
        for marker in CONSOLE_MARKERS:
            if marker not in text:
                errors.append(f"console: missing {marker!r}")

    for e in errors:
        print("ERROR:", e)
    if errors:
        return 1
    print("bank-grade HTML smoke: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
