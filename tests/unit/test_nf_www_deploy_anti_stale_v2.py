"""R-014 anti-stale deployment contracts."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "nf_www_deploy_anti_stale_v2.py"
SPEC = importlib.util.spec_from_file_location("nf_www_deploy_anti_stale_v2", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SHA = "e3b51d4b7d352655f9d956211ee5048518f2238f"


def _contract() -> dict[str, object]:
    return {
        "schema": "noetfield-www-protected-surfaces-v2",
        "surfaces": {
            "homepage": {
                "dist_path": "index.html",
                "route": "/",
                "required_text": ["Governed AI systems that can act and show their work."],
                "required_links": ["/investors/", "/investor-workflows/"],
                "forbidden_text": ["Invest in Noetfield"],
                "forbidden_link_prefixes": ["/invest/", "/workspace/"],
            }
        },
    }


def _good_html() -> str:
    return """
    <html><body>
      <h1>Governed AI systems that can act and show their work.</h1>
      <a href="/investors/">Ecosystem</a>
      <a href="/investor-workflows/">Investor Workflows</a>
    </body></html>
    """


def test_ecosystem_and_investor_workflows_are_not_invest_company_leaks() -> None:
    result = MODULE.evaluate_html(_good_html(), _contract()["surfaces"]["homepage"])
    assert result["ok"] is True


def test_invest_company_cta_is_fail_closed() -> None:
    html = _good_html() + '<a href="/invest/">Invest in Noetfield</a>'
    result = MODULE.evaluate_html(html, _contract()["surfaces"]["homepage"])
    assert result["ok"] is False
    assert result["present_forbidden_text"] == ["Invest in Noetfield"]
    assert result["present_forbidden_links"] == ["/invest/"]


def test_exact_authorized_sha_is_required(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(_good_html(), encoding="utf-8")
    result = MODULE.run_gate(
        dist=tmp_path,
        contract=_contract(),
        expected_sha=SHA,
        authorized_sha="0" * 40,
        live_base=None,
        actual_sha=SHA,
    )
    assert result["ok"] is False
    assert result["verdict"] == "BLOCKED_UNAPPROVED_PROMOTION"


def test_live_ahead_candidate_regression_is_blocked(tmp_path: Path) -> None:
    stale = _good_html().replace(
        "Governed AI systems that can act and show their work.",
        "An older homepage",
    )
    (tmp_path / "index.html").write_text(stale, encoding="utf-8")
    result = MODULE.run_gate(
        dist=tmp_path,
        contract=_contract(),
        expected_sha=SHA,
        authorized_sha=SHA,
        live_base="https://www.noetfield.com",
        actual_sha=SHA,
        fetcher=lambda _url: _good_html(),
    )
    assert result["ok"] is False
    assert result["verdict"] == "BLOCKED_PROTECTED_SURFACE_REGRESSION"
    assert result["surfaces"]["homepage"]["live_regressions"]


def test_deploy_and_workflow_wiring_remain_non_skippable() -> None:
    deploy = (ROOT / "scripts" / "deploy-www-cloudflare.sh").read_text(encoding="utf-8")
    production = (ROOT / ".github/workflows/noetfield-www-production.yml").read_text(
        encoding="utf-8"
    )
    ci = (ROOT / ".github/workflows/noetfield-www-ci.yml").read_text(encoding="utf-8")

    gate_call = deploy.index("scripts/nf_www_deploy_anti_stale_v2.py")
    assert gate_call < deploy.index("ensure_project", gate_call)
    assert gate_call < deploy.index("pages deploy", gate_call)
    assert "NF_AUTHORIZED_PROMOTE_SHA: ${{ github.sha }}" in production
    assert '"anti_stale_guard"' in production
    assert '"anti_stale_guard"' in deploy
    assert "scripts/nf_www_deploy_anti_stale_v2.py" in production
    assert "scripts/nf_www_deploy_anti_stale_v2.py" in ci
    assert "--offline" in ci
