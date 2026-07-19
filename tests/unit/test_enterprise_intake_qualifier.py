"""Unit tests for deterministic enterprise intake qualification."""

from __future__ import annotations

import asyncio

from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app
from noetfield_governance.enterprise_intake_motor import (
    MOTOR_EVENT_TYPE,
    build_enterprise_intake_motor_payload,
    emit_enterprise_intake_motor_event,
)
from noetfield_governance.enterprise_intake_qualifier import (
    QUALIFICATION_SCHEMA,
    is_enterprise_intake,
    qualify_enterprise_intake,
)
from noetfield_governance.intake_store import IntakeRecord


def test_is_enterprise_intake_vectors() -> None:
    assert is_enterprise_intake(vector="ai-value-governance-os", sku="general")
    assert is_enterprise_intake(
        vector="trust-brief-intake",
        sku="trust_brief",
        metadata={"interest": "enterprise"},
    )
    assert not is_enterprise_intake(vector="work-with-us", sku="general")
    assert not is_enterprise_intake(vector="copilot-governance", sku="copilot")


def test_qualify_high_fit_regulated_enterprise() -> None:
    result = qualify_enterprise_intake(
        organization="Acme Financial Services",
        contact_email="ciso@acme-bank.example",
        message=(
            "We are rolling out Microsoft 365 Copilot under board scrutiny and need "
            "governance evidence aligned with EU AI Act and NIST AI RMF before production."
        ),
        vector="ai-value-governance-os",
        sku="trust_brief",
        request_id="RID-ENT-HIGH-001",
        metadata={"interest": "enterprise", "buyer_role": "ciso"},
    )
    payload = result.to_qualification_json()
    assert payload["schema"] == QUALIFICATION_SCHEMA
    assert result.tier == "A"
    assert result.fit_score >= 72
    assert result.urgency == "immediate"
    assert result.next_step == "schedule_briefing"
    assert result.owner_sla_hours == 24
    assert "vector:ai-value-governance-os" in result.reasons
    assert not result.blockers


def test_qualify_defer_payment_rails_blocker() -> None:
    result = qualify_enterprise_intake(
        organization="Shadow Payments LLC",
        contact_email="ops@shadow.example",
        message="Need payment rails and custody integration with your AI stack.",
        vector="ai-value-governance-os",
        sku="trust_brief",
        metadata={"interest": "enterprise"},
    )
    assert result.tier == "defer"
    assert "payment_rails" in result.blockers
    assert result.next_step == "polite_decline"


def test_qualify_consumer_email_nurture_tier() -> None:
    result = qualify_enterprise_intake(
        organization="Solo Founder",
        contact_email="founder@gmail.com",
        message="Interested in AI Value OS.",
        vector="ai-value-governance-os",
        sku="general",
        metadata={"interest": "enterprise"},
    )
    assert result.tier in {"B", "C", "defer"}
    assert "consumer_email_domain" in result.blockers


def test_qualify_is_deterministic() -> None:
    kwargs = {
        "organization": "Northwind Insurance",
        "contact_email": "grc@northwind.example",
        "message": "Copilot governance pilot for regulated insurance workflows.",
        "vector": "ai-value-governance-os",
        "sku": "trust_brief",
        "request_id": "RID-ENT-DET-1",
        "metadata": {"interest": "enterprise"},
    }
    first = qualify_enterprise_intake(**kwargs).to_qualification_json()
    second = qualify_enterprise_intake(**kwargs).to_qualification_json()
    assert first == second


def test_motor_payload_builder() -> None:
    record = IntakeRecord(
        intake_id="INT-TESTMOTOR01",
        created_at="2026-07-18T00:00:00+00:00",
        request_id="RID-MOTOR-1",
        organization="Acme",
        contact_name=None,
        contact_email="lead@acme.example",
        sku="trust_brief",
        vector="ai-value-governance-os",
        source="web",
        message="Enterprise briefing request.",
        metadata={},
        qualification_json={"schema": QUALIFICATION_SCHEMA, "tier": "A", "fit_score": 80},
    )
    payload = build_enterprise_intake_motor_payload(
        record=record,
        qualification_json=record.qualification_json or {},
    )
    assert payload["event"] == MOTOR_EVENT_TYPE
    assert payload["schema"] == QUALIFICATION_SCHEMA
    assert payload["idempotency_key"] == "noetfield-intake:RID-MOTOR-1"
    assert payload["data"]["intake_id"] == "INT-TESTMOTOR01"


def test_motor_emit_outbox_when_gateway_unset() -> None:
    record = IntakeRecord(
        intake_id="INT-TESTMOTOR02",
        created_at="2026-07-18T00:00:00+00:00",
        request_id="RID-MOTOR-2",
        organization="Acme",
        contact_name=None,
        contact_email="lead@acme.example",
        sku="trust_brief",
        vector="ai-value-governance-os",
        source="web",
        message="Enterprise briefing request.",
        metadata={},
        qualification_json={"schema": QUALIFICATION_SCHEMA, "tier": "B", "fit_score": 55},
    )
    receipt = emit_enterprise_intake_motor_event(
        record=record,
        qualification_json=record.qualification_json or {},
        motor_gateway_url=None,
    )
    assert receipt.mode == "outbox"
    assert receipt.delivered is False
    assert receipt.detail == "motor_gateway_url_unset"


def test_intake_api_persists_qualification_json_for_enterprise_vector() -> None:
    async def run() -> None:
        from noetfield_governance import intake_repository

        await intake_repository.init_intake_repository()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/intake",
                json={
                    "organization": "Contoso Bank",
                    "contact_email": "grc@contoso.example",
                    "message": (
                        "Board-level Copilot governance rollout with compliance evidence "
                        "for regulated financial services."
                    ),
                    "request_id": "RID-ENT-API-001",
                    "vector": "ai-value-governance-os",
                    "sku": "trust_brief",
                    "metadata": {"interest": "enterprise"},
                    "source": "web",
                },
            )
        assert response.status_code == 200
        stored = await intake_repository.get_by_request_id("RID-ENT-API-001")
        assert stored is not None
        assert stored.qualification_json is not None
        assert stored.qualification_json["schema"] == QUALIFICATION_SCHEMA
        assert "tier" in stored.qualification_json
        assert "fit_score" in stored.qualification_json

    asyncio.run(run())


def test_intake_api_skips_qualification_for_non_enterprise_vector() -> None:
    async def run() -> None:
        from noetfield_governance import intake_repository

        await intake_repository.init_intake_repository()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/intake",
                json={
                    "organization": "Partner Co",
                    "contact_email": "partner@example.com",
                    "message": "Connector application.",
                    "request_id": "RID-PARTNER-001",
                    "vector": "work-with-us",
                    "sku": "general",
                    "source": "web",
                },
            )
        assert response.status_code == 200
        stored = await intake_repository.get_by_request_id("RID-PARTNER-001")
        assert stored is not None
        assert stored.qualification_json is None

    asyncio.run(run())
