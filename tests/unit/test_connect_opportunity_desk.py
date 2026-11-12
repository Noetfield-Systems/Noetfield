"""Noetfield Connect advisory triage and private API tests."""
import asyncio
from datetime import date
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from noetfield_governance import api as governance_api
from noetfield_governance.api import app
from noetfield_governance.opportunity_desk import triage_connect_record


def sample(kind="business"):
    return {
        "intake_id": "INT-ABCDEF123456",
        "request_id": "RID-CNX-1234567890",
        "created_at": "2026-11-12T00:00:00+00:00",
        "contact_name": "Example Person",
        "contact_email": "person@example.invalid",
        "organization": "Example Organization",
        "source": "web",
        "metadata": {
            "form_id": "nfConnectWizard",
            "topic": kind,
            "initiative": "noetfield",
            "proposal_title": "Pilot proposal",
            "proposal_url": "https://example.invalid/proposal",
            "deadline": "2026-11-15",
            "lead_source": "linkedin",
        },
    }


def test_connect_projection_routes_and_no_fake_outcomes():
    result = triage_connect_record(sample(), today=date(2026, 11, 12))
    assert result["priority_score"] == 85
    assert result["suggested_owner_role"] == "Sales owner"
    assert result["days_remaining"] == 3
    assert result["stage"] == "NEW"
    assert result["assignment_status"] == "ADVISORY_ONLY"
    assert result["execution_status"] == "NOT_DISPATCHED"
    assert result["cash_collected"] is None
    assert triage_connect_record({"metadata": {"form_id": "other"}}) is None
    assert triage_connect_record(sample("events"))["suggested_owner_role"] == "Partnerships owner"


def test_connect_desk_requires_admin_and_filters_nonconnect():
    async def run():
        old = governance_api.settings.admin_dashboard_secret
        try:
            with patch("noetfield_governance.intake_repository.list_recent",
                       new_callable=AsyncMock) as recent:
                recent.return_value = [sample(), {"metadata": {"form_id": "other"}}]
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    governance_api.settings.admin_dashboard_secret = SecretStr("")
                    assert (await client.get("/api/opportunities/desk")).status_code == 503
                    governance_api.settings.admin_dashboard_secret = SecretStr("desk-test-secret")
                    assert (await client.get("/api/opportunities/desk")).status_code == 403
                    assert (await client.get("/api/opportunities/desk",
                               headers={"X-Admin-Secret": "wrong"})).status_code == 403
                    response = await client.get("/api/opportunities/desk",
                                headers={"X-Admin-Secret": "desk-test-secret"})
                assert response.status_code == 200
                body = response.json()
                assert body["count"] == 1
                assert body["mode"] == "ADVISORY_ONLY"
                assert body["opportunities"][0]["source"] == "linkedin"
                recent.assert_awaited_once()
        finally:
            governance_api.settings.admin_dashboard_secret = old
    asyncio.run(run())
