"""Public HTML must not contain prohibited financial product language."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_IN_HOME = (
    "Cross-Border Payments",
    "Payment Intent",
    "FX Calculator",
    "Active Corridors",
    "Submit Payment",
)

ALLOWED_PUBLIC = (
    ROOT / "index.html",
    ROOT / "platform" / "index.html",
    ROOT / "platform" / "dashboard" / "index.html",
)


def test_homepage_has_no_prohibited_payment_language() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    for phrase in FORBIDDEN_IN_HOME:
        assert phrase not in text, f"index.html still contains: {phrase}"


def test_homepage_states_governance_positioning() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8").lower()
    assert "pre-execution" in text
    assert "governance" in text


def test_platform_dashboard_has_no_treasury_corridor_ui() -> None:
    text = (ROOT / "platform" / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "Treasury Routing" not in text
    assert "In-Flight Settlements" not in text
    assert "Active Corridors" not in text


def test_north_star_exists() -> None:
    assert (ROOT / "NORTH_STAR.md").is_file()
    assert (ROOT / "OFFERINGS.md").is_file()
