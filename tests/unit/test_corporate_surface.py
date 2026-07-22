"""NF-WEB-001 corporate entry surface contracts."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = (ROOT / "index.html", ROOT / "about" / "index.html", ROOT / "investors" / "index.html")
BRIDGE_PAGES = (
    ROOT / "proof" / "index.html",
    ROOT / "investor-workflows" / "index.html",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_corporate_pages_share_navigation_footer_and_metadata() -> None:
    expected_css_versions = {
        ROOT / "index.html": "v=2",
        ROOT / "about" / "index.html": "v=1",
        ROOT / "investors" / "index.html": "v=1",
    }
    expected_images = {
        ROOT / "index.html": "noetfield-corporate-v2.png",
        ROOT / "about" / "index.html": "noetfield-corporate-v2.png",
        ROOT / "investors" / "index.html": "noetfield-investors-v2.png",
    }
    for path in PAGES:
        text = read(path)
        css_version = expected_css_versions[path]
        assert f"/assets/noetfield-corporate-v1.css?{css_version}" in text, path
        assert '<nav class="nf-corp-nav" aria-label="Primary navigation">' in text, path
        assert 'class="nf-corp-footer"' in text, path
        assert "Evidence before claims." in text, path
        assert 'property="og:title"' in text, path
        assert 'property="og:description"' in text, path
        expected = f"https://www.noetfield.com/assets/social/{expected_images[path]}"
        assert f'property="og:image" content="{expected}"' in text, path
        assert 'property="og:image:width" content="1200"' in text, path
        assert 'property="og:image:height" content="630"' in text, path
        assert f'name="twitter:image" content="{expected}"' in text, path
        assert text.count("<h1") == 1, path
        for landmark in ("<header", "<nav", '<main id="main">', "<footer"):
            assert landmark in text, f"{path}: {landmark}"


def test_homepage_explains_company_portfolio_proof_and_asks() -> None:
    text = read(ROOT / "index.html")
    required = (
        "Vancouver · AI-native systems company &amp; product studio",
        "human intent, business policy, institutional knowledge, AI capability "
        "and decision authority",
        "act, verify, escalate, recover and produce evidence",
        "The institutional execution problem",
        "Noetfield builds AI Motors: governed execution systems",
        "Models generate. Agents participate. Motors operate.",
        "Governs, executes, verifies, escalates, recovers and records the operational system.",
        "For clarification: like a Tesla-class car",
        "Custom AI Motors",
        "Enterprise AI Governance",
        "SourceA",
        "SourceB",
        "TrustField",
        "trustfield.ca",
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
    assert text.count("<section") == 8


def test_homepage_statuses_preserve_claim_boundaries() -> None:
    text = read(ROOT / "index.html")
    for status in (
        "Available",
        "Demonstrated · client-zero",
        "Live product surface · case study planned",
        "Live commercial service · case study planned",
        "Not claimed",
    ):
        assert status in text
    assert "not an external enterprise claim" in text
    assert "independent external validation remains planned" in text
    assert "not a certifier, regulated institution, payment operator or custodian" in text
    assert not re.search(
        r"trusted by|fortune.?500|\d+[+]? (?:clients|customers|enterprises)", text, re.I
    )
    assert "$" not in text


def test_public_corporate_pages_have_no_private_workspace_conversion() -> None:
    for path in PAGES:
        assert 'href="/workspace/' not in read(path), path


def test_about_states_founder_company_and_trustfield_boundary() -> None:
    text = read(ROOT / "about" / "index.html")
    assert "Founder &amp; company" in text
    assert "founder-led" in text
    assert "Vancouver, British Columbia" in text
    assert "TrustField" in text
    assert "A Noetfield Systems Inc. product" in text
    assert 'href="https://trustfield.ca/"' in text
    assert "not presented as a Noetfield product or subsidiary" not in text


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
            assert f"/contact/?topic={topic}" in text, f"{path}: {topic}"


def test_sourcea_and_sourceb_statuses_are_truthfully_scoped() -> None:
    for path in PAGES:
        text = read(path)
        assert "Live product surface · case study planned" in text, path
        assert "Noetfield’s professional governed-execution product and infrastructure" in text, (
            path
        )
        assert "No external-client proof is claimed yet" in text, path
        assert "Live commercial service · case study planned" in text, path
        assert "SourceB.ca is a live multilingual service with an operating lead path" in text, path
        assert "No customers, revenue, installations or external traction are claimed" in text, path
        assert "a formal public Noetfield case study remains planned" in text, path

    home = read(ROOT / "index.html")
    assert "Separate system · case study planned" not in home
    assert ">Planned</span></div>\n      <h3>SourceB</h3>" not in home


def test_trustfield_is_listed_as_live_noetfield_product() -> None:
    home = read(ROOT / "index.html")
    assert "<h3>TrustField</h3>" in home
    assert 'href="https://trustfield.ca/"' in home
    assert "Live product surface · case study planned" in home
    assert "A Noetfield Systems Inc. product" in home
    assert "A separate venture in formation" not in home

    about = read(ROOT / "about" / "index.html")
    assert "TrustField" in about
    assert 'href="https://trustfield.ca/"' in about
    assert "not presented as a Noetfield product" not in about

    investors = read(ROOT / "investors" / "index.html")
    assert ">TrustField<" in investors or "TrustField</strong>" in investors
    assert "trustfield.ca" in investors.lower() or "TrustField.ca" in investors


def test_public_bridge_pages_have_coherent_navigation_and_footer() -> None:
    for path in BRIDGE_PAGES:
        text = read(path)
        assert 'class="nf-vc-site-nav"' in text, path
        assert 'class="nf-gate__foot nf-vc-footer"' in text, path
        for href in ("/about/", "/proof/", "/motors/", "/investors/", "/contact/"):
            assert href in text, f"{path}: {href}"


def test_motors_page_uses_the_corporate_navigation_and_footer() -> None:
    text = read(ROOT / "motors" / "index.html")
    assert '<nav class="nf-corp-nav" aria-label="Primary navigation">' in text
    assert 'class="nf-corp-footer"' in text
    assert '<a href="/motors/" aria-current="page">AI Motors</a>' in text
    assert 'href="/runways/"' in text
    for href in ("/about/", "/proof/", "/motors/", "/investors/"):
        assert href in text


def test_runways_page_is_honest_product_surface() -> None:
    text = read(ROOT / "runways" / "index.html")
    assert '<nav class="nf-corp-nav" aria-label="Primary navigation">' in text
    assert 'class="nf-corp-footer"' in text
    assert '<a href="/runways/" aria-current="page">Runways</a>' in text
    assert "From goal to verified output." in text
    assert "Agents participate. Runways finish the work." in text
    assert "The models may be probabilistic. The runway is controlled." in text
    assert "Paid customer delivery is not claimed." in text
    assert "Demonstrated on staging Runway" in text
    assert "Evidence before claims." in text
    assert "Trading Performance" in text
    assert "Video Qualify" in text
    assert "Commissioning Specialist" in text
    assert "Software Repair" in text
    assert text.count("<h1") == 1
    assert 'href="/assets/noetfield-runways-v1.css?v=1"' in text
    for forbidden in (
        "Ruflo",
        "CrewAI",
        "LangGraph",
        "TrustField",
        "99.9%",
        "hundreds of public agents",
    ):
        assert forbidden not in text, forbidden
    assert 'href="/contact/?topic=enterprise-governance"' in text
    assert 'href="/contact/?topic=pilot-client"' in text
    assert 'id="rw-dispatch-btn"' in text
    assert 'fetch("/api/runway/jobs"' in text
    assert "POST /v1/jobs" in text


def test_homepage_footer_links_to_runways() -> None:
    text = read(ROOT / "index.html")
    assert 'href="/runways/"' in text
    assert "Governed AI systems that can act and show their work." in text


def test_corporate_nav_includes_deploy_tab_to_live_builder() -> None:
    """Deploy tab opens the always-synced Company New builder on app.noetfield.com."""
    for path in (*PAGES, ROOT / "motors" / "index.html"):
        text = read(path)
        assert 'href="https://app.noetfield.com/"' in text, path
        assert ">Deploy</a>" in text, path
    home = read(ROOT / "index.html")
    assert (
        '<nav aria-label="Systems">' in home
        and 'href="https://app.noetfield.com/">Deploy</a>' in home
    )


def test_every_public_contact_topic_has_a_select_option() -> None:
    contact = read(ROOT / "contact" / "index.html")
    configured = set(re.findall(r'<option value="([^"#]+)"', contact))
    artifact = json.loads(read(ROOT / "governance" / "www-public-artifact-v1.json"))
    referenced: set[str] = set()
    for rel in artifact["static_files"]:
        if not rel.endswith(".html"):
            continue
        referenced.update(
            topic.split("#", 1)[0]
            for topic in re.findall(r'href="/contact/\?topic=([^"&]+)', read(ROOT / rel))
        )
    assert referenced <= configured, f"missing contact topics: {sorted(referenced - configured)}"
    assert "YOUR_FORMSPREE_ID" not in contact
