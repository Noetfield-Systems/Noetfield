#!/usr/bin/env python3
"""Apply June 2026 institutional + bank-grade site frame to GTM tier HTML pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TIER_PAGES = (
    ROOT / "index.html",
    ROOT / "enterprise" / "index.html",
    ROOT / "bank-pilot" / "index.html",
    ROOT / "partners" / "index.html",
    ROOT / "partners" / "msp" / "index.html",
    ROOT / "federal" / "index.html",
    ROOT / "trust-center" / "index.html",
    ROOT / "trust-ledger" / "index.html",
    ROOT / "copilot" / "index.html",
    ROOT / "copilot" / "demo" / "index.html",
    ROOT / "copilot" / "pilot" / "index.html",
    ROOT / "copilot" / "procurement" / "index.html",
    ROOT / "trust-brief" / "index.html",
    ROOT / "console" / "index.html",
)

CSS_2026 = '<link rel="stylesheet" href="/assets/noetfield-institutional-2026.css" />'
GRID_CSS = '<link rel="stylesheet" href="/assets/noetfield-institutional-grid.css" />'
BANK_CSS = '<link rel="stylesheet" href="/assets/noetfield-bank-grade.css" />'
META_MARKER = '<meta name="nf-institutional" content="2026-06" />'
FRFI_CSS = '<link rel="stylesheet" href="/assets/noetfield-frfi.css" />'

GRID_PAGES = {
    "partners", "partners/msp", "federal", "trust-center", "trust-ledger",
    "enterprise", "bank-pilot", "index",
}

FRFI_PAGES = {"bank-pilot", "enterprise", "federal"}
BANK_GRADE_PAGES = {
    "index", "enterprise", "bank-pilot", "trust-center", "trust-ledger",
    "copilot", "copilot/demo", "copilot/pilot", "copilot/procurement",
    "partners", "partners/msp", "federal", "trust-brief", "console",
}


def page_key(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel.name != "index.html":
        return str(rel.parent).replace("\\", "/")
    parent = str(rel.parent).replace("\\", "/")
    return "." if parent == "." else parent


def insert_after_anchor(text: str, anchor: str, insert: str) -> str:
    if insert in text:
        return text
    if anchor in text:
        return text.replace(anchor, anchor + "\n " + insert, 1)
    return text.replace("</head>", f" {insert}\n</head>", 1)


def ensure_stylesheets(text: str, key: str) -> str:
    anchor = '<link rel="stylesheet" href="/assets/noetfield-sales.css" />'
    if "noetfield-institutional-2026.css" not in text:
        text = insert_after_anchor(text, anchor, CSS_2026)
    if key in GRID_PAGES and GRID_CSS not in text:
        text = insert_after_anchor(text, CSS_2026, GRID_CSS)
    if key in BANK_GRADE_PAGES and BANK_CSS not in text:
        anchor2 = GRID_CSS if GRID_CSS in text else CSS_2026
        text = insert_after_anchor(text, anchor2, BANK_CSS)
    if key in FRFI_PAGES and FRFI_CSS not in text:
        text = insert_after_anchor(text, CSS_2026, FRFI_CSS)
    return text


def ensure_meta(text: str) -> str:
    if 'name="nf-institutional"' in text:
        return text
    return text.replace("<head>", "<head>\n " + META_MARKER, 1)


def merge_body_classes(existing: str, *classes: str) -> str:
    found = set(re.findall(r"\b([\w-]+)\b", existing or ""))
    for c in classes:
        found.add(c)
    ordered = []
    for c in ("nf-frfi", "nf-site-2026", "nf-bank-grade"):
        if c in found:
            ordered.append(c)
    for c in sorted(found):
        if c not in ordered:
            ordered.append(c)
    return " ".join(ordered)


def ensure_body_class(text: str, key: str) -> str:
    classes = ["nf-site-2026"]
    if key in FRFI_PAGES:
        classes.insert(0, "nf-frfi")
    if key in BANK_GRADE_PAGES:
        classes.append("nf-bank-grade")

    def repl(match: re.Match[str]) -> str:
        attrs = match.group(1) or ""
        class_match = re.search(r'\bclass="([^"]*)"', attrs)
        if class_match:
            merged = merge_body_classes(class_match.group(1), *classes)
            attrs = re.sub(r'\bclass="[^"]*"', f'class="{merged}"', attrs, count=1)
            attrs = re.sub(r'\bclass="[^"]*"\s+class="[^"]*"', f'class="{merged}"', attrs)
        else:
            attrs = (attrs + f' class="{" ".join(classes)}"').strip()
        return f"<body{attrs}>"

    if re.search(r"<body[^>]*class=", text):
        text = re.sub(r"<body([^>]*)>", repl, text, count=1)
        text = re.sub(
            r'class="([^"]*)"\s+class="([^"]*)"',
            lambda m: f'class="{merge_body_classes(m.group(1), m.group(2))}"',
            text,
            count=1,
        )
    else:
        text = re.sub(
            r"<body([^>]*)>",
            lambda m: f'<body{m.group(1)} class="{" ".join(classes)}">',
            text,
            count=1,
        )
    return text


def ensure_skip_link(text: str) -> str:
    if 'class="skip"' in text or "skip to content" in text.lower():
        return text
    return text.replace(
        '<header id="nfHeader">',
        '<a class="skip" href="#main">Skip to content</a>\n <header id="nfHeader">',
        1,
    )


def strip_inline_hero_actions(text: str) -> str:
    return re.sub(
        r'<div class="nf-cta-actions" style="[^"]*">',
        '<div class="nf-hero-actions">',
        text,
    ).replace(
        '<div class="nf-cta-actions" style="margin-top:1.25rem;display:flex;flex-wrap:wrap;gap:.75rem">',
        '<div class="nf-hero-actions">',
    )


def main() -> int:
    changed = 0
    for path in TIER_PAGES:
        if not path.is_file():
            print("SKIP missing", path.relative_to(ROOT))
            continue
        key = page_key(path)
        original = path.read_text(encoding="utf-8")
        updated = original
        updated = ensure_meta(updated)
        updated = ensure_stylesheets(updated, key)
        updated = ensure_body_class(updated, key)
        updated = ensure_skip_link(updated)
        updated = strip_inline_hero_actions(updated)
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
