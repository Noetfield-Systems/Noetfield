#!/usr/bin/env python3
"""Audit public HTML for GTM lock + corporate homepage law.

SSOT: docs/www/WWW_IMPLEMENTATION_STATUS_v1.md
- `/` (index.html) is the corporate entry surface for company, portfolio and proof.
- Tier institutional pages keep shell + pilot CTA requirements.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Institutional shell pages (not the direction gate).
TIER_PAGES = (
    ROOT / "governance" / "index.html",
    ROOT / "enterprise" / "index.html",
    ROOT / "trust-brief" / "index.html",
    ROOT / "copilot" / "index.html",
    ROOT / "console" / "index.html",
)

REQUIRED_TIER = (
    "nfHeader",
    "viewport",
    "noetfield-shell.css",
)

REQUIRED_TIER_BY_PAGE = {
    "governance/index.html": ("Apply for pilot", "governance"),
}

# Corporate homepage requirements (advisor P1 one-company narrative).
CORPORATE_HOME_REQUIRED = (
    "nf-corp",
    "noetfield-corporate-v1.css",
    'name="viewport"',
    "/motors/",
    "/runways/",
    "/investors/",
    "/proof/",
    "AI systems that can act—and show why the action was allowed.",
    "Inspect current proof",
    "TrustField",
    "A receipt is not certification.",
)

REQUIRED_SHELL_PARTIALS = (
    ROOT / "assets" / "partials" / "header.html",
    ROOT / "assets" / "partials" / "footer.html",
    ROOT / "assets" / "partials" / "offerings-strip.html",
)

FORBIDDEN_HOME = (
    "Cross-Border Payments",
    "Payment Intent",
    "Submit Payment",
    "FX Calculator",
)


def iter_html() -> list[Path]:
    return sorted(ROOT.rglob("*.html"))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_SHELL_PARTIALS:
        if not path.is_file():
            errors.append(f"missing shell partial: {path.relative_to(ROOT)}")

    home = ROOT / "index.html"
    if not home.is_file():
        errors.append("missing tier page: index.html")
    else:
        ht = home.read_text(encoding="utf-8", errors="replace")
        for req in CORPORATE_HOME_REQUIRED:
            if req not in ht:
                errors.append(f"index.html: missing corporate marker {req!r}")
        for phrase in FORBIDDEN_HOME:
            if phrase in ht:
                errors.append(f"index.html contains forbidden: {phrase}")
        for bad in ("Golden Edge", "GCIP", "pre-execution", "audit ledger"):
            if bad in ht:
                errors.append(f"index.html contains internal term: {bad}")
        if "nf-gate__directions" in ht:
            errors.append("index.html: stale recovery direction-gate structure")

    for path in TIER_PAGES:
        if not path.is_file():
            errors.append(f"missing tier page: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = str(path.relative_to(ROOT))
        # Allow enterprise (or others) to migrate to nf-gate without failing CI mid-transition.
        if 'class="nf-gate' in text or "nf-gate nf-gate" in text or "nf-gate--" in text:
            if "viewport" not in text and 'name="viewport"' not in text:
                errors.append(f"{rel}: missing 'viewport'")
            continue
        for req in REQUIRED_TIER:
            if req not in text:
                errors.append(f"{rel}: missing {req!r}")
        for req in REQUIRED_TIER_BY_PAGE.get(rel, ("Apply for pilot",)):
            if req not in text:
                errors.append(f"{rel}: missing {req!r}")

    no_shell = []
    no_viewport = []
    for path in iter_html():
        rel = path.relative_to(ROOT)
        if "node_modules" in rel.parts:
            continue
        if rel.parts[:2] == ("assets", "partials"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if 'name="viewport"' not in text and "name='viewport'" not in text:
            no_viewport.append(str(rel))
        if (
            "nfHeader" not in text
            and "nf-gate" not in text
            and rel.parts[0] not in ("app", "portal", "ex", "auth", "login", "signup")
        ):
            # allow minimal redirect stubs
            if "http-equiv" in text and "refresh" in text.lower():
                continue
            if len(text) < 800:
                continue
            no_shell.append(str(rel))

    if no_viewport:
        warnings.append(f"{len(no_viewport)} pages without viewport meta (sample: {no_viewport[:5]})")

    if len(no_shell) > 40:
        warnings.append(f"{len(no_shell)} large pages without shell (legacy); tier pages must pass above")

    for w in warnings:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)

    if errors:
        return 1
    print("public site health: OK (corporate entry + institutional tier pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
