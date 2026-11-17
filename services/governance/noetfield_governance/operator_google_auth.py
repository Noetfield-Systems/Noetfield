"""Authorize CRM/Connect Desk operators using the existing Noetfield Google identity provider.

Google access tokens are validated by the authoritative Supabase Auth /user endpoint,
never decoded locally. An explicit email allowlist is mandatory; investor access alone
does not authorize corporate data. No service-role key, admin key, or Google secret
is ever sent to the browser.
"""
from __future__ import annotations

import os
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException


def google_operator_configured() -> bool:
    return bool(_provider_settings() and _allowed_emails())


def _allowed_emails() -> frozenset[str]:
    return frozenset(
        part.strip().casefold()
        for part in os.environ.get("NOETFIELD_OPERATOR_GOOGLE_EMAILS", "").split(",")
        if part.strip()
    )


def _provider_settings() -> tuple[str, str] | None:
    base = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    anon = os.environ.get("SUPABASE_ANON_KEY", "").strip()
    parsed = urlparse(base)
    # Fail closed on unexpected provider endpoints; no attacker-controlled URL.
    if (parsed.scheme != "https" or not parsed.hostname
            or not parsed.hostname.endswith(".supabase.co")
            or parsed.username or parsed.password or parsed.port
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment
            or not anon):
        return None
    return base, anon


def _is_google_identity(user: dict) -> bool:
    metadata = user.get("app_metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    providers = metadata.get("providers")
    identities = user.get("identities")
    return (
        metadata.get("provider") == "google"
        or (isinstance(providers, list) and "google" in providers)
        or (isinstance(identities, list)
            and any(isinstance(item, dict) and item.get("provider") == "google"
                    for item in identities))
    )


async def verify_google_operator(access_token: str) -> str:
    config = _provider_settings()
    allowed = _allowed_emails()
    if not config or not allowed:
        raise HTTPException(503, detail="Google operator sign-in is not configured")
    if not access_token or len(access_token) > 8192:
        raise HTTPException(401, detail="Invalid Google authentication")
    base, anon = config
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=False) as client:
            response = await client.get(
                base + "/auth/v1/user",
                headers={"Authorization": "Bearer " + access_token, "apikey": anon},
            )
    except httpx.RequestError as exc:
        raise HTTPException(502, detail="Identity provider is temporarily unavailable") from exc
    if response.status_code != 200:
        raise HTTPException(401, detail="Google authentication was not accepted")
    try:
        user = response.json()
    except ValueError as exc:
        raise HTTPException(502, detail="Identity provider returned invalid data") from exc
    if not isinstance(user, dict):
        raise HTTPException(401, detail="Invalid Google authentication")
    email = user.get("email")
    if (not isinstance(email, str) or email.strip().casefold() not in allowed
            or not user.get("email_confirmed_at") or not _is_google_identity(user)
            or user.get("is_anonymous") is True):
        raise HTTPException(403, detail="This Google account is not an authorized operator")
    return email.strip().casefold()
