"""Signed HTTP client for the shared Runway Job Gateway."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any
from urllib import error, request


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).digest().hex()


def sign_gateway_request(
    secret: str,
    method: str,
    path: str,
    timestamp: str,
    nonce: str,
    body: bytes,
) -> str:
    canonical = "\n".join(
        [
            method.upper(),
            path,
            timestamp,
            nonce,
            _sha256_hex(body),
        ]
    )
    return hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()


def gateway_configured(settings: object) -> bool:
    base = str(getattr(settings, "runway_job_gateway_base_url", "") or "").strip()
    key_id = str(getattr(settings, "runway_job_gateway_key_id", "") or "").strip()
    secret = _secret(getattr(settings, "runway_job_gateway_hmac_secret", None))
    return bool(base and key_id and secret)


def _secret(value: object | None) -> str:
    if value is None:
        return ""
    getter = getattr(value, "get_secret_value", None)
    if callable(getter):
        return str(getter() or "").strip()
    return str(value).strip()


def gateway_request(
    settings: object,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    if not gateway_configured(settings):
        return 503, {"error": "RUNWAY_JOB_GATEWAY_NOT_CONFIGURED", "detail": "Gateway credentials unset — HOLD preserved"}
    base = str(getattr(settings, "runway_job_gateway_base_url", "") or "").strip().rstrip("/")
    key_id = str(getattr(settings, "runway_job_gateway_key_id", "") or "").strip()
    secret = _secret(getattr(settings, "runway_job_gateway_hmac_secret", None))
    body = b"" if payload is None else json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    timestamp = __import__("datetime").datetime.now(__import__("datetime").UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    nonce = hashlib.sha256(f"{timestamp}:{key_id}".encode("utf-8")).hexdigest()[:32]
    signature = sign_gateway_request(secret, method, path, timestamp, nonce, body)
    url = f"{base}{path}"
    headers = {
        "Authorization": f"NOETFIELD-HMAC {key_id}:{signature}",
        "X-Noetfield-Timestamp": timestamp,
        "X-Noetfield-Nonce": nonce,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    req = request.Request(url, data=body if method.upper() != "GET" else None, headers=headers, method=method.upper())
    try:
        with request.urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            parsed = json.loads(raw) if raw else {"error": "GATEWAY_HTTP_ERROR"}
        except json.JSONDecodeError:
            parsed = {"error": "GATEWAY_HTTP_ERROR", "detail": raw[:500]}
        return exc.code, parsed
    except Exception as exc:  # pragma: no cover - network guard
        return 502, {"error": "GATEWAY_UNREACHABLE", "detail": str(exc)[:500]}


def build_job_intake(
    *,
    tenant_id: str,
    entitlement_id: str,
    recipe_id: str,
    recipe_version: str,
    idempotency_key: str,
    goal: dict[str, Any],
    session_id: str | None = None,
    customer_email: str | None = None,
) -> dict[str, Any]:
    goal_payload = dict(goal)
    if session_id:
        goal_payload.setdefault("checkout_session_id", session_id)
    if customer_email:
        goal_payload.setdefault("customer_email", customer_email)
    return {
        "schema": "noetfield.job-intake.v0.1",
        "tenant_id": tenant_id,
        "entitlement_id": entitlement_id,
        "runway_id": "research",
        "recipe_id": recipe_id,
        "recipe_version": recipe_version,
        "idempotency_key": idempotency_key,
        "requested_at": __import__("datetime").datetime.now(__import__("datetime").UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "caller_site": "noetfield.com",
        "input": {"goal": goal_payload},
    }
