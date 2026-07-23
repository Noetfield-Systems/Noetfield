"""Investor governance diligence lane — public www and collateral alignment."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CHECKLIST = ROOT / "docs" / "diligence" / "INVESTOR_GOVERNANCE_CHECKLIST_MAP_v1.md"
DILIGENCE_PAGE = ROOT / "gate" / "diligence" / "index.html"
HOME = ROOT / "index.html"


def test_header_has_institutional_canada_nav() -> None:
    text = (ROOT / "assets" / "partials" / "header.html").read_text(encoding="utf-8")
    assert "instTopbar" in text
    assert "navGroup" in text
    assert "Canada" in text
    assert "Vancouver" in text


def test_homepage_has_no_gcip_bleed() -> None:
    text = HOME.read_text(encoding="utf-8")
    assert "GCIP" not in text
    assert "(internal)" not in text


def test_homepage_has_modern_shell_and_spine() -> None:
    text = HOME.read_text(encoding="utf-8")
    # NF-WEB-001 corporate entry — one company narrative (advisor P1).
    required = (
        "<title>Noetfield Systems Inc. — AI Motors &amp; Governed Execution</title>",
        '<link rel="canonical" href="https://www.noetfield.com/" />',
        '<body class="nf-corp">',
        '<main id="main">',
        "AI systems that can act—and show why the action was allowed.",
        'id="ai-motors"',
        'id="current-proof"',
        'id="runways"',
        "TrustField",
        'href="/motors/"',
        'href="/about/"',
        'href="/proof/"',
        'href="/investors/"',
        "/assets/noetfield-corporate-v1.css?v=2",
    )
    for contract in required:
        assert contract in text
    for superseded in (
        'nf-gate__directions',
        'id="nfHeader"',
        "nf26-hero",
        "nfInvestorForm",
        'id="capabilities"',
        "SourceA",
        "SourceB",
        "Investor Workflows",
    ):
        assert superseded not in text


def test_checklist_map_references_all_four_groups() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    for n in range(1, 5):
        assert f"Group {n}" in text


def test_diligence_page_lists_three_skus_only() -> None:
    text = DILIGENCE_PAGE.read_text(encoding="utf-8").lower()
    assert "trust brief" in text
    assert "copilot readiness" in text
    assert "bank pilot" in text
    assert "fourth sku" not in text


def test_diligence_page_has_buy_side_wedge_copy() -> None:
    text = DILIGENCE_PAGE.read_text(encoding="utf-8")
    assert "decision-evidence" in text
    assert "investor-diligence" in text


def test_intake_pages_include_investor_diligence_vector() -> None:
    for rel in ("gate/intake/index.html", "trust-brief/intake/index.html"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "investor-diligence" in text
        assert "internal tracking" not in text.lower()


def test_investors_capital_raise_lane_stays_noindex() -> None:
    text = (ROOT / "gate" / "partners" / "investors" / "index.html").read_text(
        encoding="utf-8"
    )
    assert "noindex" in text
