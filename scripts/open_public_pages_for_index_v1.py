#!/usr/bin/env python3
"""Open honest public marketing pages for search indexing (NF-WWW-SEO).

Keeps private, auth, legacy-redirect, and thank-you surfaces noindex.
Changes source HTML robots meta only. Social-preview apply/verify must run after.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "governance" / "www-public-artifact-v1.json"

# Always stay out of the public index.
FORCE_NOINDEX_PREFIXES = (
    "/admin/",
    "/auth/",
    "/banner/",
    "/console/",
    "/deterministic-api/signin/",
    "/deterministic-api/workspace/",
    "/enterprise/",
    "/ex/",
    "/invest/",
    "/login/",
    "/portal/",
    "/signup/",
)

FORCE_NOINDEX_EXACT = {
    "/404.html",
    "/gate/sales/thanks/",
    "/copilot/quickscan/thanks/",
}

NOINDEX_META_RE = re.compile(
    r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex[^"\']*["\']\s*/?>',
    re.IGNORECASE,
)
INDEX_META = '<meta name="robots" content="index,follow" />'


def route_for_rel(rel: str) -> str:
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return f"/{rel[:-10]}"
    return f"/{rel}"


def must_stay_noindex(route: str) -> bool:
    if route in FORCE_NOINDEX_EXACT:
        return True
    if route.endswith("/thanks/") or route.endswith("/thanks"):
        return True
    return any(route.startswith(prefix) for prefix in FORCE_NOINDEX_PREFIXES)


def main() -> int:
    import json

    allow = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    files = [
        rel
        for rel in allow.get("static_files", [])
        if isinstance(rel, str) and rel.endswith(".html")
    ]
    opened: list[str] = []
    kept: list[str] = []
    for rel in sorted(files):
        path = ROOT / rel
        if not path.is_file():
            continue
        route = route_for_rel(rel)
        text = path.read_text(encoding="utf-8", errors="replace")
        if not NOINDEX_META_RE.search(text):
            continue
        if must_stay_noindex(route):
            kept.append(route)
            continue
        # Thin redirect stubs stay noindex.
        if "http-equiv" in text.lower() and "refresh" in text.lower() and len(text) < 1200:
            kept.append(route)
            continue
        new_text, n = NOINDEX_META_RE.subn(INDEX_META, text, count=1)
        if n:
            path.write_text(new_text, encoding="utf-8")
            opened.append(route)
    print(f"opened_for_index={len(opened)}")
    for route in opened:
        print(f"  OPEN {route}")
    print(f"kept_noindex={len(kept)}")
    for route in kept:
        print(f"  KEEP {route}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
