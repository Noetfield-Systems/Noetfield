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


def test_homepage_explains_company_narrative_proof_and_asks() -> None:
    text = read(ROOT / "index.html")
    required = (
        "Vancouver, Canada · Governed execution systems",
        "AI systems that can act—and show why the action was allowed.",
        "Noetfield builds AI Motors: governed execution runtimes that coordinate",
        "Probabilistic workers. Deterministic controls. Explicit authority. Inspectable receipts.",
        "AI capability is abundant. Governed execution is not.",
        "Engines provide capability. Agents perform bounded work. Runways define how results qualify. Motors govern execution.",
        "P05-class client-zero commissioning is the present focus.",
        "does not invent SHAs, witness runs, or PASS_P05 claims",
        "Governed Software Change",
        "Decision Brief",
        "Institutional Workflow Commissioning",
        "TrustField",
        "trustfield.ca",
        "A receipt is not certification.",
        "Inspect current proof",
        "Discuss one workflow",
        "Incubator / ecosystem",
        "Operating partner",
        "Pilot / client",
    )
    for phrase in required:
        assert phrase in text
    assert "Tesla" not in text
    assert "Tesla-class" not in text
    assert "SourceA" not in text
    assert "SourceB" not in text
    assert "Investor Workflows" not in text
    assert "Custom AI Motors" not in text
    assert "not a single product" not in text.lower()
    assert "PASS_P05" not in text or "does not invent SHAs, witness runs, or PASS_P05 claims" in text
    assert "governed execution systems that coordinate" not in text
    assert "records the operational system" not in text
    assert text.count("<section") == 8


def test_homepage_statuses_preserve_claim_boundaries() -> None:
    text = read(ROOT / "index.html")
    for status in (
        "Client-zero · P05",
        "Runway",
        "Commissioning",
    ):
        assert status in text
    assert "A receipt is not certification." in text
    assert "not a certifier, regulated institution, payment operator, or custodian" in text
    assert "does not invent SHAs, witness runs, or PASS_P05 claims" in text
    assert not re.search(
        r"trusted by|fortune.?500|\d+[+]? (?:clients|customers|enterprises)", text, re.I
    )
    assert "$" not in text
    assert re.search(r"\b[0-9a-f]{7,40}\b", text, re.I) is None


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
    # Portfolio honesty remains on About / Investors; homepage is one company narrative.
    for path in (ROOT / "about" / "index.html", ROOT / "investors" / "index.html"):
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
    assert "SourceA" not in home
    assert "SourceB" not in home
    assert "Investor Workflows" not in home


def test_trustfield_is_listed_as_live_noetfield_product() -> None:
    home = read(ROOT / "index.html")
    assert "TrustField" in home
    assert 'href="https://trustfield.ca/"' in home
    assert "compliance workflow setup and operations" in home
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


def test_corporate_primary_nav_is_advisor_consistent() -> None:
    """Shared corporate headers keep the company IA plus its live app entry."""
    expected = (
        'href="/motors/"',
        'href="/runways/"',
        'href="/proof/"',
        'href="/about/"',
        'href="https://app.noetfield.com/">Deploy</a>',
        'href="/contact/?topic=pilot-client">Contact</a>',
    )
    for path in (
        ROOT / "index.html",
        ROOT / "motors" / "index.html",
        ROOT / "about" / "index.html",
        ROOT / "investors" / "index.html",
        ROOT / "runways" / "index.html",
    ):
        text = read(path)
        nav_match = re.search(
            r'<nav class="nf-corp-nav" aria-label="Primary navigation">(.*?)</nav>',
            text,
            flags=re.DOTALL,
        )
        assert nav_match, path
        nav = nav_match.group(1)
        positions = [nav.index(item) for item in expected]
        assert positions == sorted(positions), path
        assert 'href="/#capabilities"' not in nav, path
        assert 'href="/deterministic-api/"' not in nav, path
        assert ">Ecosystem</a>" not in nav, path
        assert ">Capabilities</a>" not in nav, path


def test_runways_page_is_honest_product_surface() -> None:
    text = read(ROOT / "runways" / "index.html")
    assert '<nav class="nf-corp-nav" aria-label="Primary navigation">' in text
    assert 'class="nf-corp-footer"' in text
    assert '<a href="/runways/" aria-current="page">Runways</a>' in text
    assert "From goal to accepted output—or a documented safe stop." in text
    assert "Bounded workers perform scoped work. Runways define how the result qualifies." in text
    assert "The models may be probabilistic. The runway is controlled." in text
    assert "Evidence before claims." in text
    assert "Three public runways" in text
    assert "Governed Software Change" in text
    assert "Institutional Workflow Commissioning" in text
    assert "Additional / planned / internal paths" in text
    assert "Trading Performance" in text
    assert "Video Qualify" in text
    assert "Commissioning Specialist" in text
    assert "Software Repair" in text
    assert text.count("<h1") == 1
    assert 'href="/assets/noetfield-runways-v1.css?v=3"' in text
    assert "agentic" not in text.lower()
    for forbidden in (
        "Ruflo",
        "CrewAI",
        "LangGraph",
        "TrustField",
        "99.9%",
        "hundreds of public agents",
        "HMAC",
        "POST /v1/jobs",
        "allowlisted",
        "staging Motor",
    ):
        assert forbidden not in text, forbidden
    assert 'href="/contact/?topic=governed-motor"' in text
    assert 'href="/contact/?topic=pilot-client"' in text
    assert 'href="/runways/decision-brief/"' in text
    assert 'id="rw-dispatch-btn"' in text
    assert 'fetch("/api/runway/jobs"' in text
    assert 'href="/enterprise/"' not in text
    assert 'href="/research-packs/"' not in text
    assert 'href="/investor-workflows/"' not in text


def test_runways_primary_nav_matches_homepage() -> None:
    text = read(ROOT / "runways" / "index.html")
    nav_match = re.search(
        r'<nav class="nf-corp-nav" aria-label="Primary navigation">(.*?)</nav>',
        text,
        flags=re.DOTALL,
    )
    assert nav_match
    nav = nav_match.group(1)
    expected = (
        'href="/motors/"',
        'href="/runways/"',
        'href="/proof/"',
        'href="/about/"',
        'href="https://app.noetfield.com/">Deploy</a>',
        'href="/contact/?topic=pilot-client">Contact</a>',
    )
    positions = [nav.index(item) for item in expected]
    assert positions == sorted(positions)


def test_legacy_identity_pages_are_demoted() -> None:
    legacy = (
        "enterprise",
        "pricing",
        "intelligence",
        "deterministic-api",
        "research-packs",
        "investor-workflows",
        "gel",
        "next",
    )
    for slug in legacy:
        text = read(ROOT / slug / "index.html")
        assert '<meta name="robots" content="noindex,nofollow" />' in text, slug
        assert "nf-legacy-lane-banner" in text, slug
        assert 'href="/motors/"' in text, slug
        assert 'href="/runways/"' in text, slug
        assert "index,follow" not in text or "noindex,nofollow" in text, slug


def test_homepage_footer_links_to_runways_and_trust() -> None:
    text = read(ROOT / "index.html")
    assert 'href="/runways/"' in text
    assert 'href="/trust/"' in text
    assert 'href="/privacy/"' in text
    assert 'href="/investors/">Investors</a>' in text
    assert "AI systems that can act—and show why the action was allowed." in text
    assert 'href="/deterministic-api/"' not in text
    assert 'href="/enterprise/"' not in text
    assert 'href="/investor-workflows/"' not in text


def test_corporate_footers_do_not_promote_legacy_systems() -> None:
    for rel in ("about/index.html", "investors/index.html", "motors/index.html", "runways/index.html"):
        text = read(ROOT / rel)
        footer_match = re.search(
            r'<footer class="nf-corp-footer">(.*?)</footer>',
            text,
            flags=re.DOTALL,
        )
        assert footer_match, rel
        footer = footer_match.group(1)
        assert 'href="/enterprise/"' not in footer, rel
        assert 'href="/investor-workflows/"' not in footer, rel
        assert 'href="/deterministic-api/"' not in footer, rel
        assert 'href="/research-packs/"' not in footer, rel
        assert 'href="/motors/"' in footer, rel
        assert 'href="/runways/"' in footer, rel


def test_corporate_nav_and_footer_link_to_live_app() -> None:
    """Every corporate route keeps one visible Deploy path in header and footer."""
    for path in (*PAGES, ROOT / "motors" / "index.html", ROOT / "runways" / "index.html"):
        text = read(path)
        nav_match = re.search(
            r'<nav class="nf-corp-nav" aria-label="Primary navigation">(.*?)</nav>',
            text,
            flags=re.DOTALL,
        )
        assert nav_match, path
        nav = nav_match.group(1)
        assert nav.count('href="https://app.noetfield.com/">Deploy</a>') == 1, path
        footer_match = re.search(
            r'<footer class="nf-corp-footer">(.*?)</footer>',
            text,
            flags=re.DOTALL,
        )
        assert footer_match, path
        assert 'href="https://app.noetfield.com/">Deploy</a>' in footer_match.group(1), path
        assert 'href="/#capabilities"' not in nav, path


def test_deploy_tab_is_not_hidden_by_mobile_navigation_rules() -> None:
    css = read(ROOT / "assets" / "noetfield-corporate-v1.css")
    assert ".nf-corp-nav__deploy {" in css
    assert "white-space: nowrap;" in css
    assert not re.search(
        r"\.nf-corp-nav__deploy\s*\{[^}]*display\s*:\s*none",
        css,
        flags=re.DOTALL,
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
