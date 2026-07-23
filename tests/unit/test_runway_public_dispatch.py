"""Public www → Motor dispatch allowlist contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "api" / "_lib" / "runway-public-dispatch.js"


def _load_via_node_require_shape() -> dict:
    """Read allowlist constants without executing Node — mirror the JS freeze set."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'recipe_id: "vendor-decision-brief"' in text
    assert 'caller_site: "noetfield.com"' in text
    assert "MOTOR_DISPATCH_UNCONFIGURED" in text
    assert "RECIPE_NOT_ALLOWLISTED" in text
    assert "/v1/jobs" in text
    return {"ok": True}


def test_public_dispatch_module_locks_allowlist_and_hmac_path() -> None:
    assert SCRIPT.is_file()
    assert (ROOT / "api" / "runway" / "jobs.js").is_file()
    assert (ROOT / "api" / "runway" / "job-status.js").is_file()
    assert (ROOT / "api" / "_lib" / "runway-hmac.js").is_file()
    text = SCRIPT.read_text(encoding="utf-8")
    assert "PUBLIC_BUDGET_USD = 1" in text or "budget_usd: PUBLIC_BUDGET_USD" in text
    assert "/v1/intake" in text
    _load_via_node_require_shape()


def test_runways_page_exposes_dual_cta_paths() -> None:
    text = (ROOT / "runways" / "index.html").read_text(encoding="utf-8")
    assert 'href="/contact/?topic=governed-motor"' in text
    assert 'id="rw-dispatch-btn"' in text
    assert "/api/runway/jobs" in text
    assert 'href="/runways/decision-brief/"' in text
    assert "Three public runways" in text
    assert 'href="/contact/?topic=enterprise-governance"' not in text


def test_decision_brief_buyer_page_exists() -> None:
    page = ROOT / "runways" / "decision-brief" / "index.html"
    assert page.is_file()
    text = page.read_text(encoding="utf-8")
    assert 'recipe_id: "vendor-decision-brief"' in text
    assert "/api/runway/jobs" in text
    assert "/contact/?topic=decision-brief-pilot" in text
    assert 'id="db-form"' in text
    for forbidden in (
        "HMAC",
        "POST /v1/jobs",
        "allowlisted",
        "staging Motor",
        "Ready for a paid",
        "managed brief",
    ):
        assert forbidden not in text, forbidden
