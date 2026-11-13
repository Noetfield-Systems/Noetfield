"""Regression tests for the strict public brand boundary, not private UI language."""

from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / "scripts" / "verify-public-output-allowlist.py"
SPEC = importlib.util.spec_from_file_location("nf_public_language_check", MODULE)
assert SPEC is not None and SPEC.loader is not None
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


def run(tmp_path: Path, content: str, name: str = "index.html") -> list[str]:
    page = tmp_path / name
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(content, encoding="utf-8")
    return [x["reason"] for x in check.language_boundary_findings(tmp_path, {name})]


def test_public_english_homepage_with_canonical_connect_link_is_permitted(tmp_path: Path) -> None:
    assert run(tmp_path, '<!doctype html><html lang="en"><body><a href="https://www.noetfield.com/connect/">Connect</a></body></html>') == []


def test_persian_public_content_is_blocked(tmp_path: Path) -> None:
    findings = run(tmp_path, '<html lang="fa" dir="rtl"><body>سلام</body></html>')
    assert any("non-English script" in finding for finding in findings)
    assert any("not English" in finding for finding in findings)


def test_public_alternate_language_and_translation_links_are_blocked(tmp_path: Path) -> None:
    findings = run(tmp_path, '<html lang="en"><head><link rel="alternate" hreflang="fa" href="/fa/"></head><body><a href="/connect/?lang=fa">Persian</a><a href="/fr/connect/">French</a></body></html>')
    assert any("alternate language" in finding for finding in findings)
    assert any("language variant" in finding for finding in findings)
    assert any("locale path" in finding for finding in findings)


def test_public_js_translation_link_is_blocked(tmp_path: Path) -> None:
    findings = run(tmp_path, 'const languageSwitch = "/connect/?lang=fa";', "assets/locale.js")
    assert any("language-switch URL" in finding for finding in findings)


def test_registered_persian_satellite_cannot_be_linked_from_main_site(tmp_path: Path) -> None:
    saved = check.NON_ENGLISH_SATELLITE_HOSTS
    try:
        check.NON_ENGLISH_SATELLITE_HOSTS = frozenset({"connect-persian.example"})
        findings = run(tmp_path, '<html lang="en"><a href="https://connect-persian.example/">Persian landing</a></html>')
        assert any("non-English satellite" in finding for finding in findings)
    finally:
        check.NON_ENGLISH_SATELLITE_HOSTS = saved


def test_separate_founder_desk_is_not_subject_to_public_marketing_language_rule(tmp_path: Path) -> None:
    private = tmp_path / "private" / "founder.html"
    private.parent.mkdir()
    private.write_text('<html lang="fa" dir="rtl"><body>میز بنیان‌گذار</body></html>', encoding="utf-8")
    public = tmp_path / "www-pages-dist"
    public.mkdir()
    (public / "index.html").write_text('<html lang="en">Noetfield</html>', encoding="utf-8")
    assert check.language_boundary_findings(public, {"index.html"}) == []
