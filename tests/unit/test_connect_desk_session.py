"""Operator sign-in tests: scoped persisted cookie, CSRF, origin and logout."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from noetfield_governance import api as governance_api
from noetfield_governance.api import app
from noetfield_governance.connect_desk_auth import (
    SHORT_SESSION_SECONDS, LONG_SESSION_SECONDS,
    issue_session, validate_session,
)


def test_scope_expiry_tamper_and_secret_rotation():
    token, csrf, expires = issue_session("long-secret-for-qa", remember=True, now=1000)
    assert validate_session("long-secret-for-qa", token, now=1001)
    assert not validate_session("rotated-secret", token, now=1001)
    assert not validate_session("long-secret-for-qa", token, now=expires)
    assert not validate_session("long-secret-for-qa", token + "changed", now=1001)
    assert not validate_session("long-secret-for-qa", "invalid", now=1001)
    assert csrf
    assert expires == 1000 + LONG_SESSION_SECONDS
    short, _, ttl = issue_session("long-secret-for-qa", remember=False, now=1000)
    assert ttl == 1000 + SHORT_SESSION_SECONDS
    assert validate_session("long-secret-for-qa", short, now=1001)


def test_login_restore_scoped_cookie_csrf_and_logout():
    async def run():
        old_admin = governance_api.settings.admin_dashboard_secret
        old_telegram = governance_api.settings.telegram_webhook_secret
        try:
            governance_api.settings.admin_dashboard_secret = SecretStr("operator-test-strong-key")
            governance_api.settings.telegram_webhook_secret = SecretStr("")
            with (
                patch("noetfield_governance.intake_repository.list_recent", new_callable=AsyncMock) as recent,
                patch("noetfield_governance.intake_repository.update_connect_opportunity", new_callable=AsyncMock) as save,
            ):
                recent.return_value = []
                save.return_value = {"stage": "QUALIFYING", "revision": 1}
                async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
                    no_auth = await client.get("/api/opportunities/desk")
                    assert no_auth.status_code == 403
                    no_session = await client.get("/api/opportunities/desk/session")
                    assert no_session.json()["authenticated"] is False
                    login_url = "/api/opportunities/desk/session"
                    wrong_origin = await client.post(
                        login_url, headers={"Origin": "https://bad.example"},
                        json={"secret": "operator-test-strong-key", "remember": True},
                    )
                    assert wrong_origin.status_code == 403
                    incorrect = await client.post(
                        login_url, headers={"Origin": "https://test"},
                        json={"secret": "wrong", "remember": True},
                    )
                    assert incorrect.status_code == 403
                    login = await client.post(
                        login_url, headers={"Origin": "https://test"},
                        json={"secret": "operator-test-strong-key", "remember": True},
                    )
                    assert login.status_code == 200, login.text
                    assert login.json()["authenticated"] is True
                    assert login.json()["remembered"] is True
                    cookie = login.headers["set-cookie"]
                    assert "HttpOnly" in cookie
                    assert "Secure" in cookie
                    assert "SameSite=strict" in cookie or "SameSite=Strict" in cookie
                    assert "Max-Age=604800" in cookie
                    assert "operator-test-strong-key" not in cookie
                    restored = await client.get(login_url)
                    assert restored.json()["authenticated"] is True
                    csrf = restored.json()["csrf"]
                    assert csrf and csrf != "operator-test-strong-key"
                    desk = await client.get("/api/opportunities/desk")
                    assert desk.status_code == 200
                    # Scoped cookie must NOT unlock broader platform administrator APIs.
                    unrelated = await client.get("/api/intake/recent")
                    assert unrelated.status_code == 403

                    payload = {"expected_revision": 0, "stage": "QUALIFYING",
                               "owner": "Founder", "next_action": "Review fit",
                               "due_date": None, "note": ""}
                    route = "/api/opportunities/desk/INT-ABCDEF123456"
                    without_csrf = await client.patch(route, json=payload, headers={"Origin": "https://test"})
                    assert without_csrf.status_code == 403
                    wrong_csrf = await client.patch(route, json=payload, headers={
                        "Origin": "https://test", "X-Desk-CSRF": "forged"})
                    assert wrong_csrf.status_code == 403
                    cross_origin = await client.patch(route, json=payload, headers={
                        "Origin": "https://hostile.example", "X-Desk-CSRF": csrf})
                    assert cross_origin.status_code == 403
                    valid = await client.patch(route, json=payload, headers={
                        "Origin": "https://test", "X-Desk-CSRF": csrf})
                    assert valid.status_code == 200, valid.text
                    assert valid.json()["persisted"] is True
                    save.assert_awaited_once()

                    signed_out = await client.delete(login_url, headers={
                        "Origin": "https://test", "X-Desk-CSRF": csrf})
                    assert signed_out.status_code == 200
                    assert signed_out.json()["signed_out"] is True
                    assert (await client.get("/api/opportunities/desk")).status_code == 403

                    session_only = await client.post(login_url, headers={"Origin": "https://test"},
                        json={"secret": "operator-test-strong-key", "remember": False})
                    assert session_only.status_code == 200
                    assert "Max-Age=" not in session_only.headers["set-cookie"]
        finally:
            governance_api.settings.admin_dashboard_secret = old_admin
            governance_api.settings.telegram_webhook_secret = old_telegram
    asyncio.run(run())
