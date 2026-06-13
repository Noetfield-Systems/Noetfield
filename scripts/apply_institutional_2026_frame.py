#!/usr/bin/env python3
"""Apply June 2026 institutional site frame to GTM tier HTML pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TIER_PAGES = (
    ROOT / "index.html",
    ROOT / "enterprise" / "index.html",
    ROOT / "bank-pilot" / "index.html",
    ROOT / "partners" / "index.html",
    ROOT / "trust-center" / "index.html",
    ROOT / "trust-ledger" / "index.html",
    ROOT / "copilot" / "index.html",
    ROOT / "trust-brief" / "index.html",
    ROOT / "console" / "index.html",
)

CSS_LINK = '<link rel="stylesheet" href="/assets/noetfield-institutional-2026.css" />'
META_MARKER = '<meta name="nf-institutional" content="2026-06" />'
FRFI_CSS = '<link rel="stylesheet" href="/assets/noetfield-frfi.css" />'


def ensure_stylesheet(text: str) -> str:
    if "noetfield-institutional-2026.css" in text:
        return text
    anchor = '<link rel="stylesheet" href="/assets/noetfield-sales.css" />'
    if anchor in text:
        return text.replace(anchor, anchor + "\n " + CSS_LINK, 1)
    return text.replace("</head>", f" {CSS_LINK}\n</head>", 1)


def ensure_meta(text: str) -> str:
    if 'name="nf-institutional"' in text:
        return text
    return text.replace("<head>", "<head>\n " + META_MARKER, 1)


def ensure_body_class(text: str) -> str:
    if "nf-site-2026" in text:
        return text
    text = re.sub(r"<body([^>]*)>", r'<body\1 class="nf-site-2026">', text, count=1)
    if 'class="nf-site-2026"' not in text:
        text = text.replace("<body>", '<body class="nf-site-2026">', 1)
    return text


def strip_inline_hero_actions(text: str) -> str:
    return re.sub(
        r'<div class="nf-cta-actions" style="[^"]*">',
        '<div class="nf-hero-actions">',
        text,
    ).replace(
        '<div class="nf-cta-actions" style="margin-top:1.25rem;display:flex;flex-wrap:wrap;gap:.75rem">',
        '<div class="nf-hero-actions">',
    )


def ensure_frfi_on_bank_enterprise(text: str, path: Path) -> str:
    if path.name != "index.html":
        return text
    if path.parent.name not in ("bank-pilot", "enterprise"):
        return text
    if "noetfield-frfi.css" in text:
        return text
    if CSS_LINK in text:
        return text.replace(CSS_LINK, CSS_LINK + "\n " + FRFI_CSS, 1)
    return text


def main() -> int:
    changed = 0
    for path in TIER_PAGES:
        if not path.is_file():
            print("SKIP missing", path.relative_to(ROOT))
            continue
        original = path.read_text(encoding="utf-8")
        updated = original
        updated = ensure_stylesheet(updated)
        updated = ensure_meta(updated)
        updated = ensure_body_class(updated)
        updated = strip_inline_hero_actions(updated)
        updated = ensure_frfi_on_bank_enterprise(updated, path)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print("OK  ", path.relative_to(ROOT))
            changed += 1
        else:
            print("    ", path.relative_to(ROOT), "(already framed)")
    print(f"apply_institutional_2026_frame: {changed} updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
