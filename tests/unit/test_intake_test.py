"""Unit tests for probe/E2E test intake detection."""

from __future__ import annotations

from noetfield_governance.intake_test import ensure_test_metadata, is_test_intake, pipeline_label


def test_is_test_intake_by_form_id() -> None:
    assert is_test_intake(metadata={"form_id": "nf_probe_cron", "topic": "probe"})


def test_is_test_intake_by_request_id() -> None:
    assert is_test_intake(request_id="RID-E2E-123456")


def test_is_test_intake_customer_lead_false() -> None:
    assert not is_test_intake(
        metadata={"form_id": "contact"},
        request_id="RID-2026-0613-ABC",
        contact_email="buyer@example.com",
    )


def test_ensure_test_metadata_tags_pipeline() -> None:
    meta = ensure_test_metadata(
        {"form_id": "nf_intake_e2e", "topic": "e2e"},
        request_id="RID-E2E-1",
        contact_email="e2e@noetfield.com",
    )
    assert meta["intake_kind"] == "test"
    assert meta["pipeline"] == "nf_intake_e2e:deploy_verify"


def test_pipeline_label_probe_cron() -> None:
    assert pipeline_label({"form_id": "nf_probe_cron"}) == "probe_cron:intake_e2e"
