"""Operator Google SSO regression tests: verified identity, explicit allowlist, session guard."""
import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app
from noetfield_governance.operator_google_auth import (
    _is_google_identity, google_operator_configured, verify_google_operator,
)


def test_google_identity_requires_verified_provider_metadata():
    assert _is_google_identity({"app_metadata": {"providers": ["email", "google"]}})
    assert _is_google_identity({"identities": [{"provider": "google"}]})
    assert not _is_google_identity({"user_metadata": {"provider": "google"}})
    assert not _is_google_identity({"app_metadata": {"provider": "email"}})


def test_google_operator_unconfigured_fails_closed(monkeypatch):
    monkeypatch.delenv("NOETFIELD_OPERATOR_GOOGLE_EMAILS", raising=False)
    assert not google_operator_configured()
    with pytest.raises(HTTPException) as err:
        asyncio.run(verify_google_operator("not-a-token"))
    assert err.value.status_code == 503


def test_google_operator_only_allows_verified_allowlisted_google(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://testexample.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-public-anon")
    monkeypatch.setenv("NOETFIELD_OPERATOR_GOOGLE_EMAILS", "owner@example.com")

    payload = {"email": "Owner@Example.com", "email_confirmed_at": "2026-11-16T00:00:00Z",
               "app_metadata": {"providers": ["google"]}}

    async def run(user, status=200):
        transport = httpx.MockTransport(lambda request: httpx.Response(status, json=user))
        real_client = httpx.AsyncClient
        def make_client(*args, **kwargs):
            return real_client(transport=transport, timeout=kwargs.get("timeout"))
        with patch("noetfield_governance.operator_google_auth.httpx.AsyncClient",
                   side_effect=make_client):
            return await verify_google_operator("valid-test-token")
    # MockTransport tests are exercised without network or real credentials.
    assert asyncio.run(run(payload)) == "owner@example.com"
    for invalid in [
        dict(payload, email="stranger@example.com"),
        dict(payload, email_confirmed_at=None),
        dict(payload, app_metadata={"provider": "email"}),
        dict(payload, is_anonymous=True),
    ]:
        with pytest.raises(HTTPException) as err:
            asyncio.run(run(invalid))
        assert err.value.status_code == 403
    with pytest.raises(HTTPException) as err:
        asyncio.run(run({}, 401))
    assert err.value.status_code == 401


def test_google_session_issues_same_scoped_cookie_and_rejects_cross_origin():
    async def run():
        with patch("noetfield_governance.api._admin_dashboard_secret", return_value="test-" + "s"*40), \
             patch("noetfield_governance.api.google_operator_configured",return_value=True), \
             patch("noetfield_governance.api.verify_google_operator",
                   new_callable=AsyncMock, return_value="owner@example.com"):
            async with AsyncClient(transport=ASGITransport(app=app),base_url="https://test") as client:
                wrong_origin=await client.post("/api/opportunities/desk/session/google",
                    json={"access_token":"test-token","remember":True},headers={"Origin":"https://wrong.test"})
                assert wrong_origin.status_code==403
                accepted=await client.post("/api/opportunities/desk/session/google",
                    json={"access_token":"test-token","remember":True},headers={"Origin":"https://test"})
                assert accepted.status_code==200
                assert accepted.json()["remembered"] is True
                cookie=accepted.headers.get("set-cookie","")
                assert "__Host-nf-connect-desk" in cookie and "Max-Age=604800" in cookie
                assert "httponly" in cookie.lower() and "secure" in cookie.lower()
                status=await client.get("/api/opportunities/desk/session")
                assert status.json()["authenticated"] is True
    asyncio.run(run())


def test_public_bridge_contains_no_credentials_and_crm_ui_offers_google():
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    bridge=(root/"auth/operator-bridge/index.html").read_text()
    crm=(root/"services/governance/noetfield_governance/private_corporate_crm.html").read_text()
    desk=(root/"assets/opportunity-desk.html").read_text()
    assert 'targetOrigin="https://platform.noetfield.com"' in bridge
    assert '"/auth/operator-bridge/"' in bridge
    bridge_js=(root/"assets/noetfield-operator-bridge-v2.js").read_text()
    assert 'src="/assets/noetfield-operator-bridge-v2.js"' in bridge
    assert "<script>" not in bridge
    assert 'type:"noetfield.operator.google.v1"' in bridge_js
    assert "access_token:session.access_token" in bridge_js
    assert 'https://www.noetfield.com' in crm and 'https://noetfield.com' in crm
    assert 'https://www.noetfield.com' in desk and 'https://noetfield.com' in desk
    assert 'id="remember" checked' in crm
    assert "<script>" not in (root/"auth/callback/index.html").read_text()
    assert "<script>" not in (root/"auth/sign-in/index.html").read_text()
    assert 'id="google-signin"' in crm and 'id="google-login"' in desk
    assert 'autocomplete="current-password"' in crm
    assert 'autocomplete="current-password"' in desk
