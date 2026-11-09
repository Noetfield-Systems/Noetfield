"""Public intake API and LLM fallback."""

from __future__ import annotations

import asyncio
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


def test_private_intake_recent_fails_closed_and_requires_admin_secret() -> None:
    async def run() -> None:
        from unittest.mock import AsyncMock
        from noetfield_governance import intake_repository

        old_admin = governance_api.settings.admin_dashboard_secret
        old_telegram = governance_api.settings.telegram_webhook_secret
        old_recent = intake_repository.list_recent
        intake_repository.list_recent = AsyncMock(return_value=[{
            "intake_id":"INT-ABCDEF123456",
            "contact_email":"private@example.test",
            "message":"Sensitive customer enquiry",
        }])
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                governance_api.settings.admin_dashboard_secret = SecretStr("")
                governance_api.settings.telegram_webhook_secret = SecretStr("")
                unconfigured = await client.get("/api/intake/recent")
                assert unconfigured.status_code == 503
                governance_api.settings.admin_dashboard_secret = SecretStr("operations-test-secret")
                unauthorized = await client.get("/api/intake/recent")
                incorrect = await client.get(
                    "/api/intake/recent", headers={"X-Admin-Secret":"wrong"}
                )
                authorized = await client.get(
                    "/api/intake/recent",
                    headers={"X-Admin-Secret":"operations-test-secret"},
                )
            assert unauthorized.status_code == 403
            assert incorrect.status_code == 403
            assert authorized.status_code == 200
            assert authorized.json()["records"][0]["intake_id"] == "INT-ABCDEF123456"
            intake_repository.list_recent.assert_awaited_once()
        finally:
            governance_api.settings.admin_dashboard_secret = old_admin
            governance_api.settings.telegram_webhook_secret = old_telegram
            intake_repository.list_recent = old_recent

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
