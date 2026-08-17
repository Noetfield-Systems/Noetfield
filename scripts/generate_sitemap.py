#!/usr/bin/env python3
"""Regenerate sitemap.xml from every public indexable HTML route (NF-WWW-SEO).

SSOT: governance/www-public-artifact-v1.json static HTML files that are
index,follow (not noindex), not private prefixes, and not thin redirect stubs.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.dom import minidom
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "governance" / "www-public-artifact-v1.json"
BASE = "https://www.noetfield.com"

NOINDEX_RE = re.compile(
    r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex',
    re.IGNORECASE,
)

# Never list these even if a page forgets noindex.
EXCLUDE_PREFIXES = (
    "/admin/",
    "/assets/partials/",
    "/auth/",
    "/banner/",
    "/console/",
    "/deterministic-api/signin/",
    "/deterministic-api/workspace/",
    "/enterprise/",
    "/ex/",
    "/gate/",
    "/invest/",
    "/login/",
    "/portal/",
    "/signup/",
)
EXCLUDE_EXACT = {
    "/404.html",
    "/gate/sales/thanks/",
    "/copilot/quickscan/thanks/",
}

PRIORITY = {
    "/": 1.0,
    "/motors/": 0.95,
    "/runways/": 0.95,
    "/workflows/": 0.95,
    "/developers/": 0.95,
    "/system/": 0.95,
    "/assurance/": 0.9,
    "/tools/": 0.9,
    "/proof/": 0.9,
    "/deterministic-api/": 0.9,
    "/applications/": 0.9,
    "/applications/trustfield/": 0.9,
    "/start/": 0.9,
    "/pricing/": 0.85,
    "/contact/": 0.85,
    "/investors/": 0.85,
    "/about/": 0.8,
    "/trust/": 0.8,
    "/trust-brief/": 0.85,
    "/public-interest/": 0.8,
}


def route_for_rel(rel: str) -> str:
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return f"/{rel[:-10]}"
    # Standalone public HTML (privacy/terms companions), not error/thanks docs.
    name = Path(rel).name.lower()
    if name in {"404.html", "success.html"}:
        return ""
    if rel.endswith(".html") and "/" in rel:
        return f"/{rel}"
    return ""


def is_sitemap_route(route: str, text: str) -> bool:
    if not route:
        return False
    # Directory routes end with /; standalone pages end with .html
    if not (route.endswith("/") or route.endswith(".html")):
        return False
    if route in EXCLUDE_EXACT:
        return False
    if any(route.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
        return False
    if route.endswith("/thanks/") or route.endswith("/thanks"):
        return False
    if NOINDEX_RE.search(text):
        return False
    if "http-equiv" in text.lower() and "refresh" in text.lower() and len(text) < 1200:
        return False
    return True


def path_for_route(route: str) -> Path:
    if route == "/":
        return ROOT / "index.html"
    if route.endswith(".html"):
        return ROOT / route.lstrip("/")
    return ROOT / route.lstrip("/") / "index.html"


def changefreq(url: str) -> str:
    if url in ("/", "/motors/", "/tools/", "/developers/", "/system/", "/deterministic-api/"):
        return "weekly"
    return "monthly"


def priority(url: str) -> str:
    if url.startswith("/tools/") and url != "/tools/":
        return "0.85"
    if url.startswith("/proof/") and url != "/proof/":
        return "0.75"
    return f"{PRIORITY.get(url, 0.7):.1f}"


def load_committed_lastmods() -> dict[str, str]:
    path = ROOT / "sitemap.xml"
    if not path.exists():
        return {}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return {}
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    out: dict[str, str] = {}
    for url_el in root.findall("sm:url", ns) or root.findall("url"):
        loc_el = url_el.find("sm:loc", ns)
        if loc_el is None:
            loc_el = url_el.find("loc")
        mod_el = url_el.find("sm:lastmod", ns)
        if mod_el is None:
            mod_el = url_el.find("lastmod")
        if loc_el is None or mod_el is None or not loc_el.text or not mod_el.text:
            continue
        loc = loc_el.text.removeprefix(BASE)
        if not loc.startswith("/"):
            loc = "/" + loc
        if not loc.endswith("/"):
            loc = loc + "/"
        out[loc] = mod_el.text.strip()[:10]
    return out


def lastmod_for(index_path: Path, route: str, preserved: dict[str, str]) -> str:
    rel = index_path.relative_to(ROOT).as_posix()
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()[:10]
    except (OSError, subprocess.TimeoutExpired):
        pass
    if route in preserved:
        return preserved[route]
    mtime = index_path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).date().isoformat()


def collect_routes() -> dict[str, Path]:
    allow = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    files = allow.get("static_files", [])
    found: dict[str, Path] = {}
    for rel in files:
        if not isinstance(rel, str) or not rel.endswith(".html"):
            continue
        route = route_for_rel(rel)
        path = ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not is_sitemap_route(route, text):
            continue
        found[route] = path
    return found


def main() -> int:
    preserved_lastmods = load_committed_lastmods()
    routes = collect_routes()
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for loc_path in sorted(routes, key=lambda u: (u != "/", u)):
        url_el = SubElement(urlset, "url")
        SubElement(url_el, "loc").text = BASE + loc_path
        SubElement(url_el, "lastmod").text = lastmod_for(
            routes[loc_path], loc_path, preserved_lastmods
        )
        SubElement(url_el, "changefreq").text = changefreq(loc_path)
        SubElement(url_el, "priority").text = priority(loc_path)

    raw = tostring(urlset, encoding="utf-8")
    pretty = minidom.parseString(raw).toprettyxml(indent="  ", encoding="utf-8")
    out = ROOT / "sitemap.xml"
    out.write_bytes(pretty)
    print(f"wrote {len(routes)} urls to {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
