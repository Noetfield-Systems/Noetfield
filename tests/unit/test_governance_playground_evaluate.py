"""Regression tests for the public Governance Playground evaluator."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_playground_evaluator_scores_allow_review_and_deny() -> None:
    script = r"""
const { evaluateIntent } = require("./api/_lib/governance-evaluate");
const cases = [
  evaluateIntent({
    actor: "sandbox-operator",
    action: "auto_record_evaluate",
    context: "Pre-approved sandbox evaluate with evidence ready.",
    metadata: { risk_tier: "low", evidence_ready: true }
  }),
  evaluateIntent({
    actor: "procurement",
    action: "vendor_ai_intake",
    context: "Vendor AI SaaS onboarding with unverified GPAI model evidence.",
    metadata: { risk_tier: "medium", gpai_vendor_status: "unverified", evidence_ready: false }
  }),
  evaluateIntent({
    actor: "security-team",
    action: "copilot_rollout",
    context: "Production M365 Copilot rollout with overshared SharePoint and sensitive board files.",
    metadata: { policy_version: "3.2", risk_tier: "critical", broad_sharing: true, sensitive_data: true, evidence_ready: false }
  })
];
console.log(JSON.stringify(cases));
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    cases = json.loads(result.stdout)

    assert [case["decision"] for case in cases] == ["allow", "review", "deny"]
    for case in cases:
        assert 0 <= case["confidence_score"] <= 1
        assert isinstance(case["risk_score"], int)
        assert case["risk_level"] in {"Low", "Medium", "High"}
        assert case["reason"]
        assert case["conditions"]

