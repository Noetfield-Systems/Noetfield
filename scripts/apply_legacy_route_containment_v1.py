#!/usr/bin/env python3
"""Mark legacy www routes noindex and remove from sitemap — preserve behavior."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LEGACY_PREFIXES = (
    "copilot/",
    "trust-ledger/",
    "governance/",
    "start/",
    "pricing/",
    "trust-brief/",
    "intelligence/",
    "ai-value-governance-os/",
    "workspace/",
    "enterprise/",
    "bank-pilot/",
    "ai-automation/",
    "federal/",
    "msp/",
    "templates/",
    "next/",
    "gel/",
    "research-packs/",
    "investor-workflows/",
    "ai-factories/",
    "console/",
    "deterministic-api/",
    "faq/",
)

CANONICAL_SITEMAP = {
    "https://www.noetfield.com/",
    "https://www.noetfield.com/about/",
    "https://www.noetfield.com/applications/",
    "https://www.noetfield.com/applications/trustfield/",
    "https://www.noetfield.com/contact/",
    "https://www.noetfield.com/motors/",
    "https://www.noetfield.com/public-interest/",
    "https://www.noetfield.com/proof/",
    "https://www.noetfield.com/privacy/",
    "https://www.noetfield.com/runways/",
    "https://www.noetfield.com/system/",
    "https://www.noetfield.com/trust/",
    "https://www.noetfield.com/investors/",
}

ROBOTS_NOINDEX = '<meta name="robots" content="noindex,nofollow" />'
ROBOTS_INDEX = '<meta name="robots" content="index,follow" />'
BANNER = (
    '<div class="nf-legacy-lane-banner" role="note">'
    "<strong>LEGACY</strong> — retained for existing links; not current corporate positioning. "
    '<a href="/">Return to Noetfield Systems</a> · <a href="/motors/">AI Motors</a> · <a href="/runways/">Runways</a>'
    "</div>"
)


def is_legacy(rel: str) -> bool:
    return any(rel.startswith(p) for p in LEGACY_PREFIXES)


def patch_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    if ROBOTS_INDEX in text:
        text = text.replace(ROBOTS_INDEX, ROBOTS_NOINDEX, 1)
    elif 'name="robots"' not in text:
        text = text.replace("<head>", f"<head>\n {ROBOTS_NOINDEX}", 1)
    if "nf-legacy-lane-banner" not in text and "<body" in text:
        text = re.sub(r"(<body[^>]*>)", r"\1\n " + BANNER, text, count=1)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def patch_sitemap() -> int:
    sm = ROOT / "sitemap.xml"
    if not sm.is_file():
        return 0
    tree = ET.parse(sm)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    removed = 0
    for url in list(root.findall("sm:url", ns)):
        loc = url.find("sm:loc", ns)
        if loc is not None and loc.text not in CANONICAL_SITEMAP:
            root.remove(url)
            removed += 1
    tree.write(sm, encoding="utf-8", xml_declaration=True)
    return removed


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("index.html")):
        rel = str(path.relative_to(ROOT))
        if rel == "index.html" or not is_legacy(rel):
            continue
        if patch_html(path):
            print("patched", rel)
            changed += 1
    removed = patch_sitemap()
    print(f"legacy html patches={changed} sitemap_removed={removed}")


if __name__ == "__main__":
    main()
