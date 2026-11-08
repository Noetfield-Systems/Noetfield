"""Public intake API and LLM fallback."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from noetfield_governance import api as governance_api
from noetfield_governance.analytics_store import InMemoryAnalyticsStore
from noetfield_governance.api import app
from noetfield_governance.chat_errors import ChatAPIError
from noetfield_governance.public_chat import answer_public_question


def test_intake_health() -> None:
    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/intake/health")
        assert response.status_code == 200
        body = response.json()
        assert body["enabled"] is True
        assert "ops_email_configured" in body
        assert "resend_webhook_configured" in body
        assert "auto_ack_enabled" in body

    asyncio.run(run())


def test_intake_submit() -> None:
    async def run() -> None:
        from noetfield_governance import intake_repository

        await intake_repository.init_intake_repository()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/intake",
                json={
                    "organization": "Acme Bank",
                    "contact_email": "lead@acme.example",
                    "message": "Interested in Trust Brief.",
                    "request_id": "RID-TEST123-ABC",
                    "source": "web",
                },
            )
        assert response.status_code == 200
        body = response.json()
        assert body["intake_id"].startswith("INT-")
        assert body["request_id"] == "RID-TEST123-ABC"

    asyncio.run(run())


def test_intake_submit_work_with_us_vector() -> None:
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
                    "vector": "work-with-us",
                    "sku": "general",
                    "metadata": {"program_lane": "connector", "async": True},
                    "source": "web",
                },
            )
        assert response.status_code == 200
        body = response.json()
        assert body["intake_id"].startswith("INT-")
        assert "async" in body["message"].lower()

    asyncio.run(run())




def test_business_os_intake_feed_requires_dedicated_token_and_redacts_customer_data() -> None:
    async def run() -> None:
        from unittest.mock import AsyncMock
        from noetfield_governance import intake_repository

        original_secret = governance_api.settings.business_os_intake_sync_token
        original_list_after = intake_repository.list_after
        governance_api.settings.business_os_intake_sync_token = SecretStr("business-os-feed-test-secret")
        intake_repository.list_after = AsyncMock(return_value=[{
            "intake_id": "INT-ABCDEF123456",
            "created_at": "2026-11-08T10:00:00+00:00",
            "request_id": "RID-TEST123-ABC",
            "organization": "Example Bank",
            "contact_name": "Sensitive Contact",
            "contact_email": "private@example.com",
            "message": "Private customer message that must never be projected",
            "sku": "trust_brief",
            "vector": "ai-value-governance-os",
            "source": "web",
            "metadata": {"private": "metadata"},
            "qualification_json": {
                "tier": "A",
                "fit_score": 88,
                "urgency": "immediate",
                "next_step": "schedule_briefing",
                "owner_sla_hours": 24,
                "reasons": ["private@example.com"],
                "blockers": [],
                "qualifier_version": "enterprise-intake-qualifier-v1",
            },
        }])
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                denied = await client.get("/api/internal/business-os/intake-feed")
                allowed = await client.get(
                    "/api/internal/business-os/intake-feed",
                    headers={"X-Business-OS-Token": "business-os-feed-test-secret"},
                )
            assert denied.status_code == 401
            assert allowed.status_code == 200
            body = allowed.json()
            assert body["page_size"] == 1
            item = body["items"][0]
            assert item["intake_id"] == "INT-ABCDEF123456"
            assert item["qualification"]["tier"] == "A"
            assert item["qualification"]["fit_score"] == 88
            serialized = json.dumps(body)
            for forbidden in (
                "Sensitive Contact", "private@example.com",
                "Private customer message", "Example Bank", "private",
            ):
                assert forbidden not in serialized
            intake_repository.list_after.assert_awaited_once()
        finally:
            governance_api.settings.business_os_intake_sync_token = original_secret
            intake_repository.list_after = original_list_after

    asyncio.run(run())


def test_business_os_intake_feed_skips_synthetic_records() -> None:
    async def run() -> None:
        from unittest.mock import AsyncMock
        from noetfield_governance import intake_repository

        original_secret = governance_api.settings.business_os_intake_sync_token
        original_list_after = intake_repository.list_after
        governance_api.settings.business_os_intake_sync_token = SecretStr("business-os-feed-test-secret")
        intake_repository.list_after = AsyncMock(return_value=[{
            "intake_id": "INT-TEST00000001",
            "created_at": "2026-11-08T10:00:00+00:00",
            "request_id": "RID-E2E-123456",
            "organization": "Noetfield",
            "contact_name": None,
            "contact_email": "e2e@noetfield.com",
            "message": "Synthetic test",
            "sku": "general",
            "vector": "web-intake",
            "source": "web",
            "metadata": {"intake_kind": "test"},
            "qualification_json": None,
        }])
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/internal/business-os/intake-feed",
                    headers={"X-Business-OS-Token": "business-os-feed-test-secret"},
                )
            assert response.status_code == 200
            assert response.json()["items"] == []
            assert response.json()["next_cursor"]["intake_id"] == "INT-TEST00000001"
        finally:
            governance_api.settings.business_os_intake_sync_token = original_secret
            intake_repository.list_after = original_list_after

    asyncio.run(run())

def test_llm_fallback_openrouter_to_gemini() -> None:
    async def run() -> None:
        calls: list[str] = []

        def fake_generate(*, provider, **_kwargs):
            calls.append(provider)
            if provider == "openrouter":
                raise ChatAPIError("openrouter down")
            return "Fallback answer from Gemini."

        with patch("noetfield_governance.public_chat._generate_sync", side_effect=fake_generate):
            reply, provider, _citations = await answer_public_question(
                message="What is Trust Brief?",
                provider="auto",
                gemini_api_key="gem-key",
                gemini_model="gemini-2.0-flash",
                openrouter_api_key="or-key",
                openrouter_model="google/gemini-2.0-flash-001",
                client_key="test-fallback",
            )
        assert reply == "Fallback answer from Gemini."
        assert provider == "gemini"
        assert calls == ["openrouter", "gemini"]

    asyncio.run(run())


def test_analytics_event_records_rollups_and_dashboard_summary() -> None:
    async def run() -> None:
        original_store = governance_api.analytics_store
        original_secret = governance_api.settings.admin_dashboard_secret
        governance_api.analytics_store = InMemoryAnalyticsStore()
        governance_api.settings.admin_dashboard_secret = SecretStr("traction-secret")
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                first = await client.post(
                    "/api/analytics/event",
                    json={
                        "event_name": "page_view",
                        "request_id": "RID-ANALYTICS-1",
                        "session_id": "as-test",
                        "page_path": "/copilot/pilot/",
                        "component": "page",
                        "metadata": {"title": "Pilot"},
                    },
                )
                submit = await client.post(
                    "/api/analytics/event",
                    json={
                        "event_name": "form_submit",
                        "request_id": "RID-ANALYTICS-1",
                        "session_id": "as-test",
                        "page_path": "/copilot/pilot/",
                        "component": "form",
                        "metadata": {
                            "contact_email": "buyer@example.com",
                            "organization": "Example Bank",
                            "vector": "copilot-governance",
                        },
                    },
                )
                forbidden = await client.get("/api/analytics/traction")
                summary = await client.get(
                    "/api/analytics/traction",
                    headers={"X-Admin-Secret": "traction-secret"},
                )
            assert first.status_code == 200
            assert submit.status_code == 200
            assert forbidden.status_code == 403
            assert summary.status_code == 200
            body = summary.json()
            assert body["totals"]["events"] == 2
            assert body["totals"]["sessions"] == 1
            assert body["totals"]["conversions"] == 1
            assert body["totals"]["leads"] == 1
            assert body["funnel"][-1]["stage"] == "Leads"
        finally:
            governance_api.analytics_store = original_store
            governance_api.settings.admin_dashboard_secret = original_secret

    asyncio.run(run())
