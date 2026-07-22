"""Admin API for generating, listing, and revoking pilot API keys."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, SecretStr

from noetfield_config import get_settings
from noetfield_governance.pilot_auth import (
    ALL_PILOT_SCOPES,
    CLIENT_DEFAULT_SCOPES,
    PilotAuthContext,
    _extract_bearer,
    _parse_pilot_keys,
    env_pilot_keys_configured,
    require_pilot_keys_admin,
)

router = APIRouter(
    prefix="/api/v1/admin/pilot-keys",
    tags=["pilot-keys-admin"],
    include_in_schema=True,
)


class CreatePilotKeyRequest(BaseModel):
    label: str = Field(min_length=1, max_length=200)
    tenant_id: UUID | None = None
    scopes: list[str] | None = None


class PilotKeyPublic(BaseModel):
    key_id: UUID
    key_prefix: str
    label: str
    tenant_id: UUID | None
    scopes: list[str]
    created_at: datetime
    revoked_at: datetime | None = None


class CreatePilotKeyResponse(PilotKeyPublic):
    secret: str


def _secret(value: SecretStr | None) -> str:
    return value.get_secret_value().strip() if value else ""


def resolve_admin_dashboard_secret() -> str:
    """Shared ADMIN_DASHBOARD_SECRET / Telegram fallback (mirrors api.py)."""
    settings = get_settings()
    return _secret(settings.admin_dashboard_secret) or _secret(settings.telegram_webhook_secret)


def _admin_secret_matches(request: Request) -> bool:
    expected = resolve_admin_dashboard_secret()
    if not expected:
        return False
    presented = (request.headers.get("X-Admin-Secret") or "").strip()
    return bool(presented) and presented == expected


async def _authorize_pilot_keys_admin(
    request: Request,
    *,
    for_create: bool = False,
) -> str:
    """Prefer Bearer workspace:admin; else X-Admin-Secret.

    Bootstrap: when DB has zero active keys and env has no pilot keys, X-Admin-Secret
    is sufficient for create. After keys exist, admin scope OR admin secret.
    """
    store = getattr(request.app.state, "pilot_key_store", None)
    if store is None:
        raise HTTPException(status_code=503, detail="Pilot key store is not available")

    active_count = int(await store.count_active())
    env_configured = env_pilot_keys_configured()
    bootstrap = for_create and active_count == 0 and not env_configured

    presented = _extract_bearer(request)
    if presented:
        # Env break-glass key with workspace:admin
        env_keys = _parse_pilot_keys(get_settings().governance_pilot_api_keys)
        if presented in env_keys:
            _tenant, scopes = env_keys[presented]
            auth = PilotAuthContext(tenant_id=_tenant, scopes=scopes, key_label="pilot")
            require_pilot_keys_admin(auth)
            return "pilot-env"

        record = await store.lookup_by_secret(presented)
        if record is not None:
            auth = PilotAuthContext(
                tenant_id=record.tenant_id,
                scopes=frozenset(record.scopes) or ALL_PILOT_SCOPES,
                key_label=record.key_prefix or "pilot",
                key_id=record.key_id,
            )
            require_pilot_keys_admin(auth)
            return "pilot-db"

    if _admin_secret_matches(request):
        return "admin-secret"

    if bootstrap:
        raise HTTPException(
            status_code=401,
            detail="Bootstrap requires X-Admin-Secret (ADMIN_DASHBOARD_SECRET)",
        )
    raise HTTPException(
        status_code=401,
        detail="Pilot key admin requires Bearer workspace:admin or X-Admin-Secret",
    )


def _normalize_scopes(raw: list[str] | None) -> list[str]:
    if raw is None:
        return sorted(ALL_PILOT_SCOPES)
    scopes = {part.strip() for part in raw if part and part.strip()}
    unknown = scopes - ALL_PILOT_SCOPES
    if unknown:
        raise HTTPException(status_code=400, detail=f"unknown pilot scopes: {sorted(unknown)}")
    if not scopes:
        return sorted(ALL_PILOT_SCOPES)
    return sorted(scopes)


def _record_public(record: Any) -> dict[str, Any]:
    return {
        "key_id": record.key_id,
        "key_prefix": record.key_prefix,
        "label": record.label,
        "tenant_id": record.tenant_id,
        "scopes": list(record.scopes),
        "created_at": record.created_at,
        "revoked_at": record.revoked_at,
    }


@router.post("", status_code=201, include_in_schema=True)
@router.post("/", status_code=201, include_in_schema=True)
async def create_pilot_key(request: Request, body: CreatePilotKeyRequest) -> dict[str, Any]:
    created_by = await _authorize_pilot_keys_admin(request, for_create=True)
    store = request.app.state.pilot_key_store
    scopes = _normalize_scopes(body.scopes)
    secret, record = await store.create(
        label=body.label,
        tenant_id=body.tenant_id,
        scopes=scopes,
        created_by=created_by,
    )
    payload = _record_public(record)
    payload["secret"] = secret
    return payload


@router.get("", include_in_schema=True)
@router.get("/", include_in_schema=True)
async def list_pilot_keys(request: Request) -> dict[str, Any]:
    await _authorize_pilot_keys_admin(request, for_create=False)
    store = request.app.state.pilot_key_store
    # Include revoked in list for operator visibility? Spec: list returns keys with revoked_at
    # "GET / → { keys: [{ ..., revoked_at }] }" — list_active never has revoked.
    # Spec table says list_active for store; response allows revoked_at field.
    # Use list_active for the operator table of active keys; revoked ones disappear from list
    # after revoke (still ok — revoke returns confirmation).
    keys = await store.list_active()
    return {"keys": [_record_public(k) for k in keys]}


@router.post("/{key_id}/revoke", include_in_schema=True)
async def revoke_pilot_key(request: Request, key_id: UUID) -> dict[str, Any]:
    await _authorize_pilot_keys_admin(request, for_create=False)
    store = request.app.state.pilot_key_store
    record = await store.revoke(key_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Pilot key not found")
    return {"ok": True, "key_id": key_id}


# Re-export defaults for console/docs consumers
FOUNDER_DEFAULT_SCOPES = sorted(ALL_PILOT_SCOPES)
CLIENT_RECOMMENDED_SCOPES = sorted(CLIENT_DEFAULT_SCOPES)
