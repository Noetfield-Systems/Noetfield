"""Unit tests for nf_intake_e2e helpers (Telegram + DB PASS v2)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from nf_intake_e2e import (  # noqa: E402
    SCHEMA_VERSION,
    build_receipt,
    e2e_intake_body,
    make_request_id,
    probe_telegram_ok,
)


def test_make_request_id_format() -> None:
    rid = make_request_id()
    assert rid.startswith("RID-E2E-")
    assert re.fullmatch(r"RID-E2E-\d+", rid)


def test_e2e_intake_body_has_request_id() -> None:
    body = e2e_intake_body("RID-E2E-99")
    assert body["request_id"] == "RID-E2E-99"
    assert body["metadata"]["form_id"] == "nf_intake_e2e"
    assert body["metadata"]["intake_kind"] == "test"
    assert "Ignore" not in body["message"]


def test_probe_telegram_ok_skipped_probe() -> None:
    assert probe_telegram_ok(
        {
            "telegram_skipped_probe": True,
            "intake_persisted": True,
            "intake_kind": "test",
        }
    )


def test_build_receipt_pass() -> None:
    receipt = build_receipt(
        ok=True,
        status="pass",
        request_id="RID-E2E-1",
        intake_url="https://www.noetfield.com/api/intake",
        platform_base="https://platform.noetfield.com",
        reason=None,
        submit={
            "intake_id": "INT-ABC",
            "http_status": 200,
            "telegram_skipped_probe": True,
            "intake_persisted": True,
            "intake_kind": "test",
        },
        dedupe={"dedupe_ok": True, "dedupe_intake_id": "INT-ABC"},
    )
    assert receipt["ok"] is True
    assert receipt["status"] == "pass"
    assert receipt["intake_id"] == "INT-ABC"
    assert receipt["telegram_skipped_probe"] is True
    assert receipt["intake_persisted"] is True
    assert receipt["dedupe_checked"] is True
    assert receipt["pass_definition"] == "probe_intake_persisted_and_db_dedupe"
    assert receipt["schema_version"] == SCHEMA_VERSION
    assert receipt["receipt_path"] == "reports/agent-auto/events/nf-intake-e2e-v1.json"
