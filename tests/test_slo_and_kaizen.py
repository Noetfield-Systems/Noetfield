#!/usr/bin/env python3
"""Tests for SLO Scorer v1, Kaizen receipts, and heartbeat schemas.

Tests:
- SLO scoring logic (latency, success_rate)
- Kaizen receipt v2 schema and emission
- Cycle receipt schema
- Cleanliness report schema
- Health probe schema
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from slo_scorer_v1 import (
    KaizenReceiptV2,
    SLOScore,
    create_kaizen_receipt,
    emit_cycle_receipt,
    score_workflow,
)


class TestSLOScoring(unittest.TestCase):
    """Test SLO scoring logic."""

    def test_score_workflow_all_pass(self):
        """Test scoring when all SLOs pass."""
        targets = {
            "latency_target_minutes": 60,
            "success_rate_target": 90,
        }
        run_data = {
            "conclusion": "success",
            "durationMinutes": 30,
        }
        score = score_workflow("www-ci", "noetfield-www-ci.yml", run_data, targets)
        self.assertEqual(score.overall_status, "pass")
        self.assertEqual(score.score_percent, 100.0)
        self.assertTrue(score.pass_fail["latency"])
        self.assertTrue(score.pass_fail["success"])

    def test_score_workflow_latency_miss(self):
        """Test scoring when latency SLO misses."""
        targets = {
            "latency_target_minutes": 30,
            "success_rate_target": 90,
        }
        run_data = {
            "conclusion": "success",
            "durationMinutes": 90,
        }
        score = score_workflow("www-ci", "noetfield-www-ci.yml", run_data, targets)
        self.assertEqual(score.overall_status, "miss")
        self.assertFalse(score.pass_fail["latency"])
        self.assertTrue(score.pass_fail["success"])
        self.assertEqual(score.score_percent, 50.0)

    def test_score_workflow_failure(self):
        """Test scoring when workflow fails."""
        targets = {
            "latency_target_minutes": 60,
            "success_rate_target": 90,
        }
        run_data = {
            "conclusion": "failure",
            "durationMinutes": 30,
        }
        score = score_workflow("www-ci", "noetfield-www-ci.yml", run_data, targets)
        self.assertEqual(score.overall_status, "miss")
        self.assertFalse(score.pass_fail["success"])
        self.assertEqual(score.score_percent, 50.0)

    def test_score_workflow_no_data(self):
        """Test scoring with no run data."""
        targets = {
            "latency_target_minutes": 60,
            "success_rate_target": 90,
        }
        score = score_workflow("www-ci", "noetfield-www-ci.yml", None, targets)
        self.assertEqual(score.overall_status, "unknown")
        self.assertIn("No recent run data", score.evidence)


class TestKaizenReceipt(unittest.TestCase):
    """Test Kaizen receipt v2 schema and emission."""

    def test_kaizen_receipt_schema(self):
        """Test Kaizen receipt v2 structure."""
        receipt = KaizenReceiptV2(
            receipt_id="kaizen-www-ci-1234567890",
            timestamp="2026-07-03T06:00:00+00:00",
            workflow_id="www-ci",
            slo_miss_type="latency",
            slo_target={"latency_target_minutes": 60},
            observed_value={"duration_minutes": 120},
            diff_summary="Workflow exceeded latency SLO",
            expected_effect="Reduce latency to <60 minutes",
            roi_estimate="ROI: ~50% SLO recovery",
            rollback_command="git revert --no-edit abc123",
            evidence=["latency=120m (target=60m): false"],
        )
        data = receipt.to_dict()
        self.assertEqual(data["schema_version"], "improvement-receipt-v2")
        self.assertEqual(data["workflow_id"], "www-ci")
        self.assertEqual(data["slo_miss_type"], "latency")
        self.assertIn("diff_summary", data)
        self.assertIn("rollback_command", data)

    def test_kaizen_receipt_json(self):
        """Test Kaizen receipt JSON serialization."""
        receipt = KaizenReceiptV2(
            receipt_id="kaizen-www-ci-1234567890",
            timestamp="2026-07-03T06:00:00+00:00",
            workflow_id="www-ci",
        )
        json_str = receipt.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["schema_version"], "improvement-receipt-v2")
        self.assertEqual(parsed["workflow_id"], "www-ci")

    def test_create_kaizen_receipt_on_miss(self):
        """Test creating Kaizen receipt when SLO misses."""
        score = SLOScore(
            workflow_id="www-ci",
            workflow_name="noetfield-www-ci.yml",
            timestamp="2026-07-03T06:00:00+00:00",
            slo_targets={"latency_target_minutes": 60},
            observed_values={"duration_minutes": 120},
            pass_fail={"latency": False},
            overall_status="miss",
            score_percent=0.0,
        )
        receipt = create_kaizen_receipt(score)
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.workflow_id, "www-ci")
        self.assertEqual(receipt.slo_miss_type, "latency")
        self.assertIn("latency", receipt.diff_summary.lower())

    def test_create_kaizen_receipt_on_pass(self):
        """Test that no Kaizen receipt is created when SLO passes."""
        score = SLOScore(
            workflow_id="www-ci",
            workflow_name="noetfield-www-ci.yml",
            timestamp="2026-07-03T06:00:00+00:00",
            slo_targets={"latency_target_minutes": 60},
            observed_values={"duration_minutes": 30},
            pass_fail={"latency": True},
            overall_status="pass",
            score_percent=100.0,
        )
        receipt = create_kaizen_receipt(score)
        self.assertIsNone(receipt)


class TestCycleReceiptSchema(unittest.TestCase):
    """Test cycle receipt schema."""

    def test_cycle_receipt_emit(self):
        """Test emitting cycle receipt to JSONL log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            governance_dir = tmppath / "governance"
            governance_dir.mkdir()
            cycle_log = governance_dir / "NOETFIELD_CYCLE_RECEIPTS_v1.jsonl"

            score = SLOScore(
                workflow_id="www-ci",
                workflow_name="noetfield-www-ci.yml",
                timestamp="2026-07-03T06:00:00+00:00",
                slo_targets={"latency_target_minutes": 60},
                observed_values={"duration_minutes": 30},
                pass_fail={"latency": True},
                overall_status="pass",
                score_percent=100.0,
            )

            # Monkey-patch the log path
            with patch("slo_scorer_v1.CYCLE_RECEIPTS_LOG", cycle_log):
                emit_cycle_receipt(score)

            # Verify log was written
            self.assertTrue(cycle_log.exists())
            lines = cycle_log.read_text().strip().split("\n")
            self.assertEqual(len(lines), 1)
            entry = json.loads(lines[0])
            self.assertEqual(entry["workflow_id"], "www-ci")
            self.assertEqual(entry["cycle"]["status"], "pass")


class TestHealthProbeSchema(unittest.TestCase):
    """Test health probe v1 schema."""

    def test_health_probe_schema(self):
        """Verify health probe JSON schema structure."""
        probe_output = {
            "schema": "noetfield-health-v1",
            "timestamp": "2026-07-03T06:00:00+00:00",
            "service": "noetfield",
            "version": "0.1.0",
            "status": "ok",
            "policy": {
                "check_pass": True,
                "check_message": "policy check passed",
                "policy_hash": "17cb5a33...",
            },
            "surfaces": {
                "probes": [
                    {
                        "name": "www-home",
                        "url": "https://www.noetfield.com/",
                        "status_code": 200,
                        "body_size": 5000,
                        "reachable": True,
                        "error": None,
                    }
                ],
                "reachable_count": 1,
                "total_probes": 1,
            },
            "workflows": {
                "checks": [
                    {
                        "workflow": "noetfield-www-ci.yml",
                        "exists": True,
                        "last_run_status": "ok",
                        "error": None,
                    }
                ],
                "all_exist": True,
            },
        }
        # Validate required fields
        self.assertEqual(probe_output["schema"], "noetfield-health-v1")
        self.assertIn("status", probe_output)
        self.assertIn("policy", probe_output)
        self.assertIn("surfaces", probe_output)
        self.assertIn("workflows", probe_output)


class TestCleanlinessReportSchema(unittest.TestCase):
    """Test repo cleanliness report v1 schema."""

    def test_cleanliness_report_schema(self):
        """Verify cleanliness report JSON schema structure."""
        report = {
            "schema": "repo-cleanliness-v1",
            "repo": "/path/to/repo",
            "dirty_count": 3,
            "triage_threshold": 30,
            "status": "OK",
            "files": {
                "untracked": ["file1.txt", "file2.txt"],
                "modified": ["file3.txt"],
                "staged": [],
            },
            "counts": {
                "untracked": 2,
                "modified": 1,
                "staged": 0,
            },
            "recommendation": "OK: 3 files is within threshold.",
        }
        # Validate required fields
        self.assertEqual(report["schema"], "repo-cleanliness-v1")
        self.assertIn("dirty_count", report)
        self.assertIn("triage_threshold", report)
        self.assertIn("status", report)
        self.assertIn("recommendation", report)


class TestWorkflowHealthRegistry(unittest.TestCase):
    """Test workflow health registry schema."""

    def test_registry_schema(self):
        """Verify WORKFLOW_HEALTH_RECEIPTS_LOCKED.json schema."""
        registry = {
            "schema_version": "workflow-health-registry-v1",
            "timestamp": "2026-07-03T06:00:00+00:00",
            "slo_targets": {
                "www-ci": {
                    "filename": "noetfield-www-ci.yml",
                    "slo_targets": {
                        "latency_target_minutes": 60,
                        "success_rate_target": 99,
                    },
                },
                "platform-deploy": {
                    "filename": "platform-deploy.yml",
                    "slo_targets": {
                        "latency_target_minutes": 10,
                        "success_rate_target": 95,
                    },
                },
            },
            "kaizen_escalation_policy": {
                "throttle_miss_count": 2,
                "throttle_window_days": 7,
                "escalate_priority": "high",
            },
        }
        # Validate required fields
        self.assertEqual(registry["schema_version"], "workflow-health-registry-v1")
        self.assertIn("slo_targets", registry)
        self.assertIn("kaizen_escalation_policy", registry)


if __name__ == "__main__":
    unittest.main()
