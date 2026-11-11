"""PII-free Business OS intake-feed contract tests."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from noetfield_governance import api as governance_api
from noetfield_governance.api import app

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

def test_contributor_feed_projects_only_allowlisted_non_pii_role_and_scope() -> None:
    async def run() -> None:
        from noetfield_governance import intake_repository

        original_secret = governance_api.settings.business_os_intake_sync_token
        original_list = intake_repository.list_after
        governance_api.settings.business_os_intake_sync_token = SecretStr("business-os-feed-test-secret")
        intake_repository.list_after = AsyncMock(return_value=[{
            "intake_id": "INT-ABCDE0000001",
            "created_at": "2026-11-10T20:00:00+00:00",
            "request_id": "RID-CONTRIBUTOR-123",
            "organization": "Sensitive Applicant Name",
            "contact_email": "sensitive@example.invalid",
            "message": "Private capability description not allowed into agent queues",
            "sku": "general",
            "vector": "work-with-us-contributor",
            "metadata": {
                "application_kind": "agent",
                "project_id": "buildrelay",
                "role": "qa",
                "evidence_url": "https://example.invalid/private-proof",
                "application_status": "APPLIED",
                "private_key": "never-forward-me",
            },
            "qualification_json": None,
        }])
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/internal/business-os/intake-feed",
                    headers={"X-Business-OS-Token": "business-os-feed-test-secret"},
                )
            assert response.status_code == 200
            item = response.json()["items"][0]
            assert item["vector"] == "work-with-us-contributor"
            assert item["contributor"] == {
                "application_kind": "agent", "project_id": "buildrelay", "role": "qa",
            }
            exported = json.dumps(response.json())
            for forbidden in ("Sensitive Applicant", "sensitive@", "Private capability",
                              "never-forward-me", "private-proof"):
                assert forbidden not in exported
        finally:
            governance_api.settings.business_os_intake_sync_token = original_secret
            intake_repository.list_after = original_list
    asyncio.run(run())


def test_invalid_contributor_metadata_routes_as_general_not_executable_intake() -> None:
    async def run() -> None:
        from noetfield_governance import intake_repository
        original_secret = governance_api.settings.business_os_intake_sync_token
        original_list = intake_repository.list_after
        governance_api.settings.business_os_intake_sync_token = SecretStr("business-os-feed-test-secret")
        intake_repository.list_after = AsyncMock(return_value=[{
            "intake_id": "INT-ABCDE0000002", "created_at": "2026-11-10T21:00:00+00:00",
            "request_id": None, "contact_email": "person@example.invalid",
            "sku": "general", "vector": "work-with-us-contributor",
            "metadata": {
                "application_kind": {"unexpected": "structure"},
                "project_id": "not-registered",
                "role": "execute-shell",
            }, "qualification_json": None,
        }])
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/internal/business-os/intake-feed",
                    headers={"X-Business-OS-Token": "business-os-feed-test-secret"},
                )
            assert response.status_code == 200
            item = response.json()["items"][0]
            assert item["vector"] == "general"
            assert "contributor" not in item
        finally:
            governance_api.settings.business_os_intake_sync_token = original_secret
            intake_repository.list_after = original_list
    asyncio.run(run())
