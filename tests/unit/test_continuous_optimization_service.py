from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "intelligence/continuous-optimization/index.html"
CSS = ROOT / "assets/noetfield-continuous-optimization-intelligence.css"


class PageStructure(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.fragments: list[str] = []
        self.forms: list[dict[str, str | None]] = []
        self.inputs: list[dict[str, str | None]] = []
        self.current_form: dict[str, str | None] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(str(values["id"]))
        href = values.get("href")
        if href and href.startswith("#"):
            self.fragments.append(href[1:])
        if tag == "form":
            self.current_form = values
            self.forms.append(values)
        elif tag in {"input", "select", "textarea", "button"} and self.current_form is not None:
            self.inputs.append(values)

    def handle_endtag(self, tag: str) -> None:
        if tag == "form":
            self.current_form = None


def test_optimization_page_is_indexable_and_canonical() -> None:
    html = PAGE.read_text(encoding="utf-8")
    assert '<title>Continuous Optimization Intelligence | Noetfield</title>' in html
    assert 'href="https://www.noetfield.com/intelligence/continuous-optimization/"' in html
    description = html.split('<meta name="description" content="', 1)[1].split('"', 1)[0]
    assert 50 <= len(description) <= 160
    assert 'name="robots" content="index,follow"' in html
    assert "application/ld+json" in html


def test_commercial_offer_is_explicit_and_truthful() -> None:
    html = PAGE.read_text(encoding="utf-8")
    for phrase in (
        "Diagnostic Sprint",
        "$2,500–$5,000",
        "From $8,000",
        "$3,000",
        "CAD",
        "paid-upfront terms apply",
        "no charge is taken by this form",
        "not an online checkout",
    ):
        assert phrase.lower() in html.lower()
    assert "no payment has been taken" in html.lower()
    assert "No automatic production changes are included by default" in html


def test_conversion_form_uses_the_established_intake_contract() -> None:
    html = PAGE.read_text(encoding="utf-8")
    parser = PageStructure()
    parser.feed(html)
    assert len(parser.forms) == 1
    form = parser.forms[0]
    assert form.get("id") == "coiIntakeForm"
    assert form.get("data-nf-intake-form") is not None
    assert form.get("data-intake-vector") == "intelligence-diagnostic"
    assert form.get("data-intake-sku") == "intelligence-diagnostic"
    for field in ("email", "org", "name", "engagement", "target_context", "notes", "topic"):
        assert any(item.get("name") == field for item in parser.inputs), field
    for field in ("email", "org", "name", "engagement", "target_context", "notes"):
        assert any(item.get("name") == field and "required" in item for item in parser.inputs), field
    assert "operations@noetfield.com" in html
    assert "within one business day" in html


def test_all_page_fragment_links_resolve_and_ids_are_unique() -> None:
    html = PAGE.read_text(encoding="utf-8")
    parser = PageStructure()
    parser.feed(html)
    assert len(parser.ids) == len(set(parser.ids)), "duplicate element IDs"
    missing = sorted(set(parser.fragments) - set(parser.ids))
    assert not missing, f"unresolved in-page links: {missing}"


def test_public_allowlist_sitemap_and_responsive_styles_are_complete() -> None:
    manifest = json.loads((ROOT / "governance/www-public-artifact-v1.json").read_text(encoding="utf-8"))
    assert "intelligence/continuous-optimization/index.html" in manifest["static_files"]
    assert "assets/noetfield-continuous-optimization-intelligence.css" in manifest["static_files"]
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://www.noetfield.com/intelligence/continuous-optimization/" in sitemap
    assert "<priority>0.7</priority>" in sitemap[sitemap.index("/intelligence/continuous-optimization/") : sitemap.index("/intelligence/continuous-optimization/") + 250]
    css = CSS.read_text(encoding="utf-8")
    assert "@media (max-width:1050px)" in css
    assert "@media (max-width:700px)" in css
    assert "prefers-reduced-motion:reduce" in css
