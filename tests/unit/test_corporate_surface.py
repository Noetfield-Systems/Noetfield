"""NF-WEB-001 corporate entry surface contracts."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
PAGES = (ROOT / "index.html", ROOT / "about" / "index.html", ROOT / "investors" / "index.html")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_corporate_pages_share_navigation_footer_and_metadata() -> None:
    for path in PAGES:
        text = read(path)
        assert "/assets/noetfield-corporate-v1.css?v=1" in text, path
        assert '<nav class="nf-corp-nav" aria-label="Primary navigation">' in text, path
        assert 'class="nf-corp-footer"' in text, path
        assert "Evidence before claims." in text, path
        assert 'property="og:title"' in text, path
        assert 'property="og:description"' in text, path
        assert 'property="og:image" content="https://www.noetfield.com/noetfield-og.png"' in text, path
        assert text.count("<h1") == 1, path
        for landmark in ("<header", "<nav", '<main id="main">', "<footer"):
            assert landmark in text, f"{path}: {landmark}"


def test_homepage_explains_company_portfolio_proof_and_asks() -> None:
    text = read(ROOT / "index.html")
    required = (
        "Vancouver · AI-native systems company &amp; product studio",
        "human intent, business policy, institutional knowledge, AI capability and decision authority",
        "act, verify, escalate, recover and produce evidence",
        "The institutional execution problem",
        "Custom AI Motors",
        "Enterprise AI Governance",
        "SourceA",
        "SourceB",
        "Investor Workflows",
        "Evidence &amp; proof",
        "What Noetfield is seeking",
        "Founder &amp; company",
        "Incubator / ecosystem",
        "Operating partner",
        "Pilot / client",
    )
    for phrase in required:
        assert phrase in text
    assert text.count("<section") == 7


def test_homepage_statuses_preserve_claim_boundaries() -> None:
    text = read(ROOT / "index.html")
    for status in ("Available", "Demonstrated · client-zero", "Planned", "Not claimed"):
        assert status in text
    assert "not an external enterprise claim" in text
    assert "independent external validation remains planned" in text
    assert "not a certifier, regulated institution, payment operator or custodian" in text
    assert not re.search(r"trusted by|fortune.?500|\d+[+]? (?:clients|customers|enterprises)", text, re.I)
    assert "$" not in text


def test_public_corporate_pages_have_no_private_workspace_conversion() -> None:
    for path in PAGES:
        assert 'href="/workspace/' not in read(path), path


def test_about_states_founder_company_and_trustfield_boundary() -> None:
    text = read(ROOT / "about" / "index.html")
    assert "Founder &amp; company" in text
    assert "founder-led" in text
    assert "Vancouver, British Columbia" in text
    assert "A separate venture in formation that Noetfield may support" in text
    assert "not presented as a Noetfield product or subsidiary" in text


def test_ecosystem_page_is_informational_and_preserves_invest_security() -> None:
    text = read(ROOT / "investors" / "index.html")
    assert "not a public securities offering or solicitation" in text
    assert "Private materials remain access-controlled" in text
    assert 'href="/invest/"' in text
    assert "Verified parties only · sign-in required" in text
    assert "nothing on this page bypasses authentication" in text.lower()


def test_three_contact_paths_are_present_on_all_corporate_pages() -> None:
    topics = ("incubator-ecosystem", "operating-partner", "pilot-client")
    for path in PAGES:
        text = read(path)
        for topic in topics:
            assert f'/contact/?topic={topic}' in text, f"{path}: {topic}"


def test_sourcea_reference_is_scoped_to_corporate_portfolio_context() -> None:
    home = read(ROOT / "index.html")
    assert "Separate system · case study planned" in home
    assert "SourceA is not presented here as client proof" in home
    for path in (ROOT / "about" / "index.html", ROOT / "investors" / "index.html"):
        text = read(path)
        if "SourceA" in text:
            assert "case studies are not yet published as Noetfield proof" in text
