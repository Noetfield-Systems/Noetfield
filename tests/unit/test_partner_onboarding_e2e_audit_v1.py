"""Partner onboarding audit contract tests."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from nf_partner_onboarding_e2e_audit_v1 import (  # noqa: E402
    build_receipt,
    check_investor_evidence_contract,
    make_finding,
)


def test_current_investor_evidence_contract_passes() -> None:
    html = (ROOT / "investors" / "index.html").read_text(encoding="utf-8")
    assert check_investor_evidence_contract(html) == []


def test_retired_investor_form_fails_current_contract() -> None:
    html = (ROOT / "investors" / "index.html").read_text(encoding="utf-8")
    findings = check_investor_evidence_contract(html + '<form id="nfInvestorForm"></form>')
    assert [finding["check_id"] for finding in findings] == ["investor_legacy_form_exposed"]
    assert findings[0]["severity"] == "critical"


def test_missing_investor_journey_elements_are_reported() -> None:
    findings = check_investor_evidence_contract("<html></html>")
    assert {finding["check_id"] for finding in findings} == {
        "investor_evidence_link_missing",
        "investor_contact_path_missing",
        "investor_disclosure_missing",
    }


def test_receipt_uses_current_investor_journey_label() -> None:
    finding = make_finding(
        check_id="investor_access_control_bypass",
        severity="critical",
        summary="Restricted materials exposed",
        detail="test",
    )
    receipt = build_receipt([finding], browser_ran=True, score=75)
    investor_check = next(
        check
        for check in receipt["checks"]
        if check["label"] == "Investor evidence and restricted-access journey is intact"
    )
    assert investor_check["state"] == "fail"
    assert receipt["status"] == "fail"


def test_obsolete_investor_form_check_is_removed() -> None:
    source = (ROOT / "scripts" / "nf_partner_onboarding_e2e_audit_v1.py").read_text(
        encoding="utf-8"
    )
    assert "_check_investor_form_regression" not in source
    assert 'check_id="investor_form_regression"' not in source
