"""ASGI tests for pilot keys admin API (in-memory store)."""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from httpx import ASGITransport, AsyncClient

from noetfield_config import get_settings
from noetfield_governance.api import app, startup_platform
from noetfield_governance.pilot_key_store import InMemoryPilotKeyStore


@asynccontextmanager
async def admin_test_client() -> AsyncIterator[AsyncClient]:
    await startup_platform()
    store = InMemoryPilotKeyStore(pepper="unit-test-pepper")
    app.state.pilot_key_store = store
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def _reload_settings() -> None:
    get_settings.cache_clear()


def _clear_pilot_env() -> None:
    for key in (
        "GOVERNANCE_PILOT_AUTH_REQUIRED",
        "GOVERNANCE_PILOT_API_KEYS",
        "ADMIN_DASHBOARD_SECRET",
    ):
        os.environ.pop(key, None)
    _reload_settings()


def test_bootstrap_create_list_revoke_with_admin_secret() -> None:
    os.environ["ADMIN_DASHBOARD_SECRET"] = "bootstrap-admin-secret"
    os.environ["GOVERNANCE_PILOT_API_KEYS"] = ""
    _reload_settings()

    async def run() -> None:
        async with admin_test_client() as client:
            headers = {"X-Admin-Secret": "bootstrap-admin-secret"}
            create = await client.post(
                "/api/v1/admin/pilot-keys",
                headers=headers,
                json={"label": "Founder console", "scopes": ["workspace:admin", "governance:read"]},
            )
            assert create.status_code == 201, create.text
            body = create.json()
            assert body["secret"].startswith("nf_pilot_")
            assert body["label"] == "Founder console"
            assert "key_id" in body
            secret = body["secret"]
            key_id = body["key_id"]

            listed = await client.get("/api/v1/admin/pilot-keys", headers=headers)
            assert listed.status_code == 200
            keys = listed.json()["keys"]
            assert len(keys) == 1
            assert keys[0]["key_id"] == key_id
            assert "secret" not in keys[0]

            bearer = {"Authorization": f"Bearer {secret}"}
            listed2 = await client.get("/api/v1/admin/pilot-keys", headers=bearer)
            assert listed2.status_code == 200

            revoke = await client.post(f"/api/v1/admin/pilot-keys/{key_id}/revoke", headers=bearer)
            assert revoke.status_code == 200
            assert revoke.json() == {"ok": True, "key_id": key_id}

            listed3 = await client.get("/api/v1/admin/pilot-keys", headers=headers)
            assert listed3.status_code == 200
            assert listed3.json()["keys"] == []

    try:
        asyncio.run(run())
    finally:
        _clear_pilot_env()


def test_create_rejects_without_credentials() -> None:
    os.environ["ADMIN_DASHBOARD_SECRET"] = "bootstrap-admin-secret"
    os.environ["GOVERNANCE_PILOT_API_KEYS"] = ""
    _reload_settings()

    async def run() -> None:
        async with admin_test_client() as client:
            res = await client.post(
                "/api/v1/admin/pilot-keys",
                json={"label": "nope"},
            )
            assert res.status_code == 401

    try:
        asyncio.run(run())
    finally:
        _clear_pilot_env()


def test_db_key_authenticates_governance_when_auth_required() -> None:
    os.environ["ADMIN_DASHBOARD_SECRET"] = "bootstrap-admin-secret"
    os.environ["GOVERNANCE_PILOT_AUTH_REQUIRED"] = "true"
    os.environ["GOVERNANCE_PILOT_API_KEYS"] = ""
    _reload_settings()

    async def run() -> None:
        async with admin_test_client() as client:
            create = await client.post(
                "/api/v1/admin/pilot-keys",
                headers={"X-Admin-Secret": "bootstrap-admin-secret"},
                json={
                    "label": "Founder",
                    "scopes": [
                        "workspace:admin",
                        "workspace:read",
                        "workspace:write",
                        "governance:read",
                        "governance:write",
                    ],
                },
            )
            assert create.status_code == 201
            secret = create.json()["secret"]

            presets = await client.get(
                "/api/v1/governance/scenario-presets/bank",
                headers={"Authorization": f"Bearer {secret}"},
            )
            assert presets.status_code == 200

            bad = await client.get(
                "/api/v1/governance/scenario-presets/bank",
                headers={"Authorization": "Bearer wrong"},
            )
            assert bad.status_code == 401

    try:
        asyncio.run(run())
    finally:
        _clear_pilot_env()


def test_env_key_still_works_over_db() -> None:
    os.environ["GOVERNANCE_PILOT_AUTH_REQUIRED"] = "true"
    os.environ["GOVERNANCE_PILOT_API_KEYS"] = "env-break-glass:workspace:admin|governance:read"
    _reload_settings()

    async def run() -> None:
        async with admin_test_client() as client:
            res = await client.get(
                "/api/v1/governance/scenario-presets/bank",
                headers={"Authorization": "Bearer env-break-glass"},
            )
            assert res.status_code == 200

    try:
        asyncio.run(run())
    finally:
        _clear_pilot_env()
