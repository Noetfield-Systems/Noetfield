#!/usr/bin/env python3
"""Noetfield SLO Scorer v1 — score workflows against SLO targets and emit Kaizen receipts.

Reads:
- governance/WORKFLOW_HEALTH_RECEIPTS_LOCKED.json (SLO targets)
- GitHub Actions API (workflow run results)
- git history (latency, churn)

Emits:
- SLO score for each workflow
- Kaizen receipt v2 on SLO miss (with diff_summary, expected_effect, ROI, rollback_command)
- governance/NOETFIELD_CYCLE_RECEIPTS_v1.jsonl (append-only log)

Repo-local only: no cross-repo writes, no alternate coordination doctrine.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_DIR = ROOT / "governance"
WORKFLOWS_DIR = ROOT / ".github" / "workflows"

# Registry files
WORKFLOW_HEALTH_REGISTRY = GOVERNANCE_DIR / "WORKFLOW_HEALTH_RECEIPTS_LOCKED.json"
CYCLE_RECEIPTS_LOG = GOVERNANCE_DIR / "NOETFIELD_CYCLE_RECEIPTS_v1.jsonl"
KAIZEN_RECEIPTS_DIR = GOVERNANCE_DIR / "kaizen_receipts"


def utc_now() -> str:
    """Current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_workflow_registry() -> dict[str, Any]:
    """Load SLO targets from WORKFLOW_HEALTH_RECEIPTS_LOCKED.json."""
    if not WORKFLOW_HEALTH_REGISTRY.is_file():
        return {"slo_targets": {}}
    return json.loads(WORKFLOW_HEALTH_REGISTRY.read_text())


def get_workflow_run_data(workflow_name: str) -> dict[str, Any] | None:
    """Fetch latest run for workflow from GitHub API."""
    try:
        result = subprocess.run(
            [
                "gh",
                "run",
                "list",
                "--workflow",
                workflow_name,
                "--limit",
                "1",
                "--json",
                "name,conclusion,startedAt,durationMinutes",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        runs = json.loads(result.stdout) if result.stdout else []
        return runs[0] if runs else None
    except Exception as e:
        print(f"Error fetching workflow data for {workflow_name}: {e}", file=sys.stderr)
        return None


@dataclass
class SLOScore:
    """Score for a single workflow against SLO targets."""

    workflow_id: str
    workflow_name: str
    timestamp: str
    slo_targets: dict[str, Any]
    observed_values: dict[str, Any]
    pass_fail: dict[str, bool] = field(default_factory=dict)
    overall_status: str = "unknown"  # pass, miss, degraded
    score_percent: float = 0.0
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def score_workflow(
    workflow_id: str, workflow_name: str, run_data: dict[str, Any] | None,
    targets: dict[str, Any]
) -> SLOScore:
    """Score a workflow run against SLO targets.
    
    Args:
        workflow_id: Machine-friendly workflow identifier (e.g., 'www-ci')
        workflow_name: Human name (e.g., 'noetfield-www-ci.yml')
        run_data: Latest run data from GitHub API
        targets: SLO targets from registry (success_rate_target, latency_target_minutes, etc.)
    
    Returns:
        SLOScore with pass/fail decisions and evidence.
    """
    score = SLOScore(
        workflow_id=workflow_id,
        workflow_name=workflow_name,
        timestamp=utc_now(),
        slo_targets=targets,
        observed_values={},
    )

    if not run_data:
        score.overall_status = "unknown"
        score.evidence = f"No recent run data for {workflow_name}"
        return score

    # Extract observed values
    conclusion = run_data.get("conclusion", "unknown")
    duration_minutes = run_data.get("durationMinutes", 0)
    
    score.observed_values = {
        "latest_conclusion": conclusion,
        "duration_minutes": duration_minutes,
    }

    # Check latency SLO
    latency_target = targets.get("latency_target_minutes", 120)
    latency_pass = duration_minutes <= latency_target
    score.pass_fail["latency"] = latency_pass

    # Check success SLO
    success_target = targets.get("success_rate_target", 90)
    success_pass = conclusion in ["success", "completed"]
    score.pass_fail["success"] = success_pass

    # Overall status
    all_pass = all(score.pass_fail.values())
    score.overall_status = "pass" if all_pass else "miss"
    score.score_percent = (
        sum(score.pass_fail.values()) / len(score.pass_fail) * 100
        if score.pass_fail
        else 0.0
    )

    score.evidence = (
        f"latency={duration_minutes}m (target={latency_target}m): {latency_pass}, "
        f"success={conclusion}: {success_pass}"
    )

    return score


@dataclass
class KaizenReceiptV2:
    """Kaizen improvement receipt for SLO miss or drift."""

    receipt_id: str
    timestamp: str
    schema_version: str = "improvement-receipt-v2"
    workflow_id: str = ""
    slo_miss_type: str = ""  # latency, success_rate, freshness, etc.
    slo_target: dict[str, Any] = field(default_factory=dict)
    observed_value: dict[str, Any] = field(default_factory=dict)
    diff_summary: str = ""
    expected_effect: str = ""
    roi_estimate: str = ""
    rollback_command: str = ""
    evidence: list[str] = field(default_factory=list)
    assignee: str = ""
    priority: str = "medium"  # low, medium, high, critical

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def create_kaizen_receipt(score: SLOScore, score_history: list[SLOScore] | None = None) -> KaizenReceiptV2 | None:
    """Create Kaizen receipt v2 for SLO miss.
    
    Args:
        score: Current SLO score
        score_history: Recent history for drift detection
    
    Returns:
        KaizenReceiptV2 if SLO miss, None otherwise.
    """
    if score.overall_status == "pass":
        return None

    receipt_id = f"kaizen-{score.workflow_id}-{int(datetime.now(timezone.utc).timestamp())}"

    # Determine miss type
    miss_types = [k for k, v in score.pass_fail.items() if not v]
    miss_type = miss_types[0] if miss_types else "unknown"

    # Build diff summary
    diff_summary = (
        f"Workflow {score.workflow_name} missed {miss_type} SLO. "
        f"Target: {score.slo_targets.get(miss_type + '_target', 'N/A')}, "
        f"Observed: {score.observed_values.get(f'{miss_type}_minutes', score.observed_values.get('latest_conclusion', 'N/A'))}"
    )

    # Expected effect (placeholder — customize per workflow)
    expected_effect = (
        f"Fix {miss_type} issue in {score.workflow_name} to improve reliability. "
        f"Target SLO: {score.slo_targets.get(miss_type + '_target', 'N/A')}."
    )

    # ROI estimate
    roi_estimate = f"ROI: ~{int(score.score_percent)}% SLO pass rate recovery"

    # Rollback command
    rollback_command = f"git revert --no-edit <commit-sha>"

    receipt = KaizenReceiptV2(
        receipt_id=receipt_id,
        timestamp=utc_now(),
        workflow_id=score.workflow_id,
        slo_miss_type=miss_type,
        slo_target=score.slo_targets,
        observed_value=score.observed_values,
        diff_summary=diff_summary,
        expected_effect=expected_effect,
        roi_estimate=roi_estimate,
        rollback_command=rollback_command,
        evidence=[score.evidence],
        priority="high" if score.score_percent < 50 else "medium",
    )

    return receipt


def emit_cycle_receipt(score: SLOScore, kaizen: KaizenReceiptV2 | None = None) -> None:
    """Emit cycle receipt to append-only log.
    
    Cycle receipt schema:
    {
      "workflow_id": str,
      "timestamp": str,
      "cycle": {"status": "pass|miss", "slo_targets": {...}, "observed": {...}},
      "kaizen_receipt_id": str or null
    }
    """
    cycle_receipt = {
        "workflow_id": score.workflow_id,
        "timestamp": score.timestamp,
        "cycle": {
            "status": score.overall_status,
            "slo_targets": score.slo_targets,
            "observed": score.observed_values,
            "score_percent": score.score_percent,
        },
        "kaizen_receipt_id": kaizen.receipt_id if kaizen else None,
    }

    # Append to log (create if missing)
    CYCLE_RECEIPTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(CYCLE_RECEIPTS_LOG, "a") as f:
        f.write(json.dumps(cycle_receipt) + "\n")


def write_kaizen_receipt(receipt: KaizenReceiptV2) -> None:
    """Write Kaizen receipt v2 to file."""
    KAIZEN_RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    receipt_file = KAIZEN_RECEIPTS_DIR / f"{receipt.receipt_id}.json"
    receipt_file.write_text(receipt.to_json())


def main() -> int:
    """Main entry point: score all Tier-1 workflows."""
    registry = load_workflow_registry()
    targets = registry.get("slo_targets", {})

    if not targets:
        print("No SLO targets found in registry", file=sys.stderr)
        return 1

    results = {
        "timestamp": utc_now(),
        "schema": "workflow-slo-scores-v1",
        "scores": [],
        "kaizen_receipts_filed": 0,
    }

    for workflow_id, workflow_config in targets.items():
        workflow_name = workflow_config.get("filename", f"{workflow_id}.yml")
        slo_targets = workflow_config.get("slo_targets", {})

        # Fetch latest run
        run_data = get_workflow_run_data(workflow_name)

        # Score workflow
        score = score_workflow(workflow_id, workflow_name, run_data, slo_targets)

        # Emit cycle receipt
        emit_cycle_receipt(score)

        # Auto-file Kaizen receipt on miss
        kaizen = None
        if score.overall_status == "miss":
            kaizen = create_kaizen_receipt(score)
            if kaizen:
                write_kaizen_receipt(kaizen)
                results["kaizen_receipts_filed"] += 1
                print(f"Filed Kaizen receipt: {kaizen.receipt_id}")

        results["scores"].append(score.to_dict())

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
