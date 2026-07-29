"""NF-WEB-001 corporate entry surface contracts."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = (ROOT / "index.html", ROOT / "about" / "index.html", ROOT / "investors" / "index.html")
BRIDGE_PAGES = (
    ROOT / "proof" / "index.html",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_corporate_pages_share_navigation_footer_and_metadata() -> None:
    expected_css_versions = {
        ROOT / "index.html": "v=4",
        ROOT / "about" / "index.html": "v=4",
        ROOT / "investors" / "index.html": "v=4",
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
        if path == ROOT / "index.html":
            assert "/assets/noetfield-home-v2.css?v=4" in text, path
            assert 'class="nf-corp nf-home"' in text, path
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
    """Canonical v2 homepage: governed execution + client-zero commissioning."""
    text = read(ROOT / "index.html")
    required = (
        "GOVERNED AI EXECUTION",
        "CLIENT-ZERO",
        "AI systems should not decide when their own work is safe to ship.",
        "client-zero commissioning",
        "See what is live",
        "Inspect the evidence",
        "Capable AI is not the same as accountable execution.",
        "Governed replacement",
        "Claims-boundary correction",
        "TrustField",
        "separate venture",
        "not a Noetfield Systems Inc. product",
        "nf-status-rail",
        "nf-corp-section",
        "nf-corp-hero",
        "/system/",
        "/applications/",
        "/public-interest/",
        "/assets/noetfield-home-v2.css",
        'class="nf-corp nf-home"',
    )
    for phrase in required:
        assert phrase in text, phrase
    assert "SourceB" not in text
    assert "Invest in Noetfield" not in text
    assert text.count("<section") >= 7


def test_homepage_statuses_preserve_claim_boundaries() -> None:
    text = read(ROOT / "index.html")
    assert "does not prove external adoption" in text
    assert "separate venture" in text.lower()
    assert "not a noetfield systems inc. product" in text.lower()
    assert not re.search(r"trusted by", text, re.I)
    assert not re.search(r"\d+[+]? (?:clients|customers|enterprises)", text, re.I)


def test_public_corporate_pages_have_no_private_workspace_conversion() -> None:
    for path in PAGES:
        assert 'href="/workspace/' not in read(path), path


def test_about_states_founder_company_and_trustfield_boundary() -> None:
    text = read(ROOT / "about" / "index.html")
    assert "Sina Kazemnezhad" in text
    assert "sole operating lead" in text.lower()
    assert "Vancouver" in text
    assert "TrustField" in text
    assert "separate venture" in text.lower()
    assert "not a Noetfield Systems Inc. product" in text
    assert "SourceB" not in text


def test_ecosystem_page_is_informational_and_preserves_invest_security() -> None:
    text = read(ROOT / "investors" / "index.html")
    assert "Company thesis" in text or "thesis" in text.lower()
    assert "external customers" in text.lower() or "not established" in text.lower()
    assert 'href="/contact/?topic=program-funding"' in text


def test_three_contact_paths_are_present_on_all_corporate_pages() -> None:
    """Legacy topic aliases remain in contact form; corporate pages link to Contact."""
    for path in PAGES:
        text = read(path)
        assert 'href="/contact/' in text, path
        assert "commission-workflow" in text or "/contact/" in text, path


def test_sourcea_and_sourceb_statuses_are_truthfully_scoped() -> None:
    home = read(ROOT / "index.html")
    assert "SourceA" in home
    assert "SourceB" not in home
    about = read(ROOT / "about" / "index.html")
    assert "SourceA" in about
    assert "SourceB" not in about


def test_trustfield_is_listed_as_separate_venture_boundary() -> None:
    home = read(ROOT / "index.html")
    assert "TrustField" in home
    assert 'href="https://trustfield.ca/"' in home
    assert "separate venture" in home.lower()
    assert "validation vertical developed and operated" not in home.lower()

    about = read(ROOT / "about" / "index.html")
    assert "TrustField" in about
    assert "separate venture" in about.lower()

    investors = read(ROOT / "investors" / "index.html")
    assert "TrustField" in investors
    assert "separate venture" in investors.lower()


def test_public_bridge_pages_have_coherent_navigation_and_footer() -> None:
    for path in BRIDGE_PAGES:
        text = read(path)
        assert 'class="nf-corp-nav"' in text or 'class="nf-corp-header"' in text, path
        assert 'class="nf-corp-footer"' in text, path
        for href in ("/system/", "/applications/", "/proof/", "/public-interest/", "/about/"):
            assert href in text, f"{path}: {href}"
    proof = read(ROOT / "proof" / "index.html")
    assert 'class="nf-corp-nav"' in proof
    assert 'class="nf-corp-footer"' in proof


def test_motors_page_uses_the_corporate_navigation_and_footer() -> None:
    text = read(ROOT / "motors" / "index.html")
    assert '<nav class="nf-corp-nav" aria-label="Primary navigation">' in text
    assert 'class="nf-corp-footer"' in text
    assert 'href="/system/"' in text
    assert 'href="/motors/"' in text or "Motors" in text
    for href in ("/system/", "/applications/", "/proof/", "/about/"):
        assert href in text


def test_corporate_primary_nav_is_advisor_consistent() -> None:
    """Shared corporate headers: System · Applications · Evidence · Program · Company · Contact · Open client-zero alpha."""
    order_markers = (
        'href="/system/"',
        'href="/applications/"',
        'href="/proof/"',
        'href="/public-interest/"',
        'href="/about/"',
        'href="/contact/"',
        'href="https://app.noetfield.com/"',
    )
    for path in (
        ROOT / "index.html",
        ROOT / "motors" / "index.html",
        ROOT / "about" / "index.html",
        ROOT / "investors" / "index.html",
        ROOT / "runways" / "index.html",
        ROOT / "system" / "index.html",
    ):
        text = read(path)
        nav_match = re.search(
            r'<nav class="nf-corp-nav" aria-label="Primary navigation">(.*?)</nav>',
            text,
            flags=re.DOTALL,
        )
        assert nav_match, path
        nav = nav_match.group(1)
        positions = [nav.index(item) for item in order_markers]
        assert positions == sorted(positions), path
        assert "Open client-zero alpha" in nav, path
        assert 'href="/#capabilities"' not in nav, path
        assert 'href="/deterministic-api/"' not in nav, path
        assert ">Ecosystem</a>" not in nav, path
        assert ">Capabilities</a>" not in nav, path


def test_runways_page_is_honest_product_surface() -> None:
    text = read(ROOT / "runways" / "index.html")
    assert '<nav class="nf-corp-nav" aria-label="Primary navigation">' in text
    assert 'class="nf-corp-footer"' in text
    assert "Governed qualification paths" in text
    assert "Three public runways" in text or "Public runways" in text
    assert "Governed Software Change" in text
    assert "Decision Brief" in text
    assert "Institutional Workflow Commissioning" in text
    assert "Trading Performance" not in text
    assert "Video Qualify" not in text
    assert text.count("<h1") == 1
    assert 'href="/assets/noetfield-runways-v1.css?v=4"' in text
    assert 'href="/enterprise/"' not in text
    assert 'href="/investor-workflows/"' not in text
    assert "accepted outcome or documented safe stop" in text.lower() or "safe stop" in text.lower()


def test_runways_primary_nav_matches_homepage() -> None:
    text = read(ROOT / "runways" / "index.html")
    nav_match = re.search(
        r'<nav class="nf-corp-nav" aria-label="Primary navigation">(.*?)</nav>',
        text,
        flags=re.DOTALL,
    )
    assert nav_match
    nav = nav_match.group(1)
    order_markers = (
        'href="/system/"',
        'href="/applications/"',
        'href="/proof/"',
        'href="/public-interest/"',
        'href="/about/"',
        'href="/contact/"',
        'href="https://app.noetfield.com/"',
    )
    positions = [nav.index(item) for item in order_markers]
    assert positions == sorted(positions)


def test_legacy_identity_pages_are_demoted() -> None:
    legacy = (
        "enterprise",
        "pricing",
        "intelligence",
        "research-packs",
        "investor-workflows",
        "gel",
        "next",
        "deterministic-api",
        "faq",
    )
    for slug in legacy:
        text = read(ROOT / slug / "index.html")
        assert '<meta name="robots" content="noindex,nofollow" />' in text, slug
        assert "nf-legacy-lane-banner" in text or slug == "deterministic-api", slug
        assert 'href="/system/"' in text or 'href="/motors/"' in text, slug
        assert "index,follow" not in text or "noindex,nofollow" in text, slug


def test_deterministic_api_product_remains_reachable_but_not_in_corp_nav() -> None:
    text = read(ROOT / "deterministic-api" / "index.html")
    assert '<meta name="robots" content="noindex,nofollow" />' in text
    home = read(ROOT / "index.html")
    assert 'href="/deterministic-api/"' not in home


def test_homepage_footer_links_to_trust_and_investors() -> None:
    text = read(ROOT / "index.html")
    assert 'href="/trust/"' in text
    assert 'href="/privacy/"' in text
    assert 'href="/investors/">Investors / Ecosystem</a>' in text
    assert "Governed AI execution infrastructure" in text
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
        assert 'href="/investors/"' in footer, rel
        assert 'href="/trust/"' in footer, rel


def test_corporate_nav_and_footer_link_to_live_app() -> None:
    """Every corporate route keeps one visible client-zero alpha path in header."""
    for path in (*PAGES, ROOT / "motors" / "index.html", ROOT / "runways" / "index.html"):
        text = read(path)
        nav_match = re.search(
            r'<nav class="nf-corp-nav" aria-label="Primary navigation">(.*?)</nav>',
            text,
            flags=re.DOTALL,
        )
        assert nav_match, path
        nav = nav_match.group(1)
        assert nav.count('href="https://app.noetfield.com/"') >= 1, path
        assert 'href="/#capabilities"' not in nav, path


def test_alpha_cta_is_not_hidden_by_mobile_navigation_rules() -> None:
    css = read(ROOT / "assets" / "noetfield-corporate-v1.css")
    assert ".nf-corp-nav__alpha {" in css
    assert not re.search(
        r"\.nf-corp-nav__alpha\s*\{[^}]*display\s*:\s*none",
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
