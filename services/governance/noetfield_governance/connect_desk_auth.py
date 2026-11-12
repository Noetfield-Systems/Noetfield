"""Scoped, signed, revocable-by-key-rotation Connect operator sessions.

Uses the existing Noetfield Platform administrator secret only for initial
authorization and HMAC signing. Never stores the master secret in a cookie,
browser JavaScript or a second database. Browser 'remember' is opt-in.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import urlparse

from fastapi import HTTPException, Request

COOKIE_NAME = "__Host-nf-connect-desk"
LONG_SESSION_SECONDS = 7 * 24 * 60 * 60
SHORT_SESSION_SECONDS = 8 * 60 * 60
_PURPOSE = b"noetfield:connect-desk:session:v1:"


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _signature(secret: str, body: str) -> str:
    return _b64(hmac.new(secret.encode(), _PURPOSE + body.encode(), hashlib.sha256).digest())


def issue_session(secret: str, *, remember: bool, now: int | None = None) -> tuple[str, str, int]:
    if not secret:
        raise ValueError("AUTHENTICATION_NOT_CONFIGURED")
    timestamp = int(time.time()) if now is None else int(now)
    expires = timestamp + (LONG_SESSION_SECONDS if remember else SHORT_SESSION_SECONDS)
    payload = {
        "version": 1, "scope": "connect-desk", "issued": timestamp,
        "expires": expires, "nonce": secrets.token_urlsafe(24),
    }
    body = _b64(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    token = body + "." + _signature(secret, body)
    return token, csrf_token(secret, token), expires


def validate_session(secret: str, token: str | None, *, now: int | None = None) -> bool:
    if not secret or not token or len(token) > 1400:
        return False
    try:
        body, signature = token.split(".", 1)
        if not hmac.compare_digest(signature, _signature(secret, body)):
            return False
        payload = json.loads(_unb64(body))
        timestamp = int(time.time()) if now is None else int(now)
        return (
            payload.get("scope") == "connect-desk"
            and payload.get("version") == 1
            and isinstance(payload.get("issued"), int)
            and isinstance(payload.get("expires"), int)
            and timestamp >= payload["issued"] - 30
            and timestamp < payload["expires"]
            and payload["expires"] - payload["issued"] <= LONG_SESSION_SECONDS
            and isinstance(payload.get("nonce"), str)
            and len(payload["nonce"]) >= 30
        )
    except (ValueError, TypeError, KeyError, AttributeError, UnicodeError):
        return False


def csrf_token(secret: str, token: str) -> str:
    return _b64(hmac.new(secret.encode(), b"noetfield:connect-desk:csrf:v1:" + token.encode(), hashlib.sha256).digest())


def check_origin(request: Request) -> None:
    """Require same-host browser writes, including authentication and sign-out."""
    origin = request.headers.get("origin", "")
    host = request.headers.get("host", "").lower()
    parsed = urlparse(origin)
    allowed_schemes = ("http", "https") if host.split(":")[0] in ("localhost", "127.0.0.1", "test") else ("https",)
    if not origin or parsed.scheme not in allowed_schemes or parsed.netloc.lower() != host or parsed.path not in ("", "/"):
        raise HTTPException(status_code=403, detail="CROSS_ORIGIN_WRITE_DENIED")


def require_session(request: Request, secret: str) -> bool:
    """Only the Connect Desk endpoints accept this scoped browser session."""
    token = request.cookies.get(COOKIE_NAME)
    if not validate_session(secret, token):
        return False
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        check_origin(request)
        header = request.headers.get("X-Desk-CSRF", "")
        if not header or not hmac.compare_digest(header, csrf_token(secret, token)):
            raise HTTPException(status_code=403, detail="DESK_CSRF_DENIED")
    return True
