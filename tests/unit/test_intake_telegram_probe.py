"""Probe vs lead Telegram behavior — node smoke + E2E receipt fields."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from nf_intake_e2e import build_receipt, e2e_intake_body, probe_telegram_ok  # noqa: E402


def test_probe_telegram_ok_with_skipped_probe() -> None:
    assert probe_telegram_ok(
        {
            "telegram_skipped_probe": True,
            "intake_persisted": True,
            "intake_kind": "test",
        }
    )


def test_probe_telegram_ok_false_without_persist() -> None:
    assert not probe_telegram_ok(
        {
            "telegram_skipped_probe": True,
            "intake_persisted": False,
            "intake_kind": "test",
        }
    )


def test_build_receipt_probe_fields() -> None:
    receipt = build_receipt(
        ok=True,
        status="pass",
        request_id="RID-E2E-1",
        intake_url="https://www.noetfield.com/api/intake",
        platform_base="https://platform.noetfield.com",
        reason=None,
        submit={
            "intake_id": "INT-ABC",
            "telegram_skipped_probe": True,
            "intake_persisted": True,
            "intake_kind": "test",
        },
        dedupe={"dedupe_ok": True, "dedupe_intake_id": "INT-ABC", "dedupe_checked": True},
    )
    assert receipt["telegram_skipped_probe"] is True
    assert receipt["intake_persisted"] is True
    assert receipt["dedupe_checked"] is True
    assert receipt["pass_definition"] == "probe_intake_persisted_and_db_dedupe"


def test_e2e_body_form_id() -> None:
    body = e2e_intake_body("RID-E2E-99")
    assert body["metadata"]["form_id"] == "nf_intake_e2e"


def test_node_probe_lead_telegram_smoke() -> None:
    result = subprocess.run(
        ["node", str(ROOT / "scripts" / "test_intake_telegram_probe.cjs")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
