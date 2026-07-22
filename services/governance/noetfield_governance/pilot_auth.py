"""Pilot API key authentication for governance v1 routes."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, Request
from pydantic import SecretStr

from noetfield_config import get_settings

WORKSPACE_READ_SCOPES = frozenset({"workspace:read", "workspace:admin"})
WORKSPACE_WRITE_SCOPES = frozenset({"workspace:write", "workspace:admin"})
ALL_PILOT_SCOPES = frozenset(
    {"workspace:read", "workspace:write", "workspace:admin", "governance:read", "governance:write"}
)
CLIENT_DEFAULT_SCOPES = frozenset({"governance:read", "governance:write", "workspace:read"})


@dataclass(frozen=True)
class PilotAuthContext:
    """Resolved pilot credentials for a governance API call."""

    tenant_id: UUID | None
    scopes: frozenset[str]
    key_label: str = "pilot"
    key_id: UUID | None = None


def _parse_scopes(raw: str) -> frozenset[str]:
    scopes = frozenset(part.strip() for part in raw.split("|") if part.strip())
    unknown = scopes - ALL_PILOT_SCOPES
    if unknown:
        raise ValueError(f"unknown pilot scopes: {sorted(unknown)}")
    return scopes


def _parse_key_entry(token: str) -> tuple[str, UUID | None, frozenset[str]] | None:
    """Parse one key entry: secret, optional tenant, scopes."""
    token = token.strip()
    if not token:
        return None
    if ":" not in token:
        return token, None, ALL_PILOT_SCOPES

    head, _, remainder = token.partition(":")
    try:
        tenant_id = UUID(head)
        if not remainder:
            return None
        if ":" not in remainder and "|" not in remainder:
            return remainder.strip(), tenant_id, ALL_PILOT_SCOPES
        secret, _, scope_raw = remainder.partition(":")
        if not secret:
            return None
        if scope_raw:
            return secret.strip(), tenant_id, _parse_scopes(scope_raw)
        return remainder.strip(), tenant_id, ALL_PILOT_SCOPES
    except ValueError:
        if "workspace:" in remainder or "|" in remainder:
            return head.strip(), None, _parse_scopes(remainder)
        return token, None, ALL_PILOT_SCOPES


def _parse_pilot_keys(raw: str) -> dict[str, tuple[UUID | None, frozenset[str]]]:
    """Map secret -> (optional tenant_id, scopes)."""
    mapping: dict[str, tuple[UUID | None, frozenset[str]]] = {}
    for part in raw.split(","):
        parsed = _parse_key_entry(part)
        if parsed is None:
            continue
        secret, tenant_id, scopes = parsed
        mapping[secret] = (tenant_id, scopes)
    return mapping


def _extract_bearer(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip() or None
    return request.headers.get("X-API-Key", "").strip() or None


def _secret(value: SecretStr | None) -> str:
    return value.get_secret_value().strip() if value else ""


def env_pilot_keys_configured() -> bool:
    return bool(_parse_pilot_keys(get_settings().governance_pilot_api_keys))


async def _store_has_active_keys(request: Request) -> bool:
    store = getattr(request.app.state, "pilot_key_store", None)
    if store is None:
        return False
    try:
        return int(await store.count_active()) > 0
    except Exception:
        return False


async def require_pilot_auth(request: Request) -> PilotAuthContext:
    settings = get_settings()
    if not settings.governance_pilot_auth_required:
        return PilotAuthContext(tenant_id=None, scopes=ALL_PILOT_SCOPES, key_label="open-pilot-dev")

    env_keys = _parse_pilot_keys(settings.governance_pilot_api_keys)
    presented = _extract_bearer(request)

    if presented and presented in env_keys:
        tenant_id, scopes = env_keys[presented]
        return PilotAuthContext(tenant_id=tenant_id, scopes=scopes, key_label="pilot")

    store = getattr(request.app.state, "pilot_key_store", None)
    if presented and store is not None:
        record = await store.lookup_by_secret(presented)
        if record is not None:
            return PilotAuthContext(
                tenant_id=record.tenant_id,
                scopes=frozenset(record.scopes) or ALL_PILOT_SCOPES,
                key_label=record.key_prefix or "pilot",
                key_id=record.key_id,
            )

    has_env = bool(env_keys)
    has_db = await _store_has_active_keys(request) if store is not None else False
    if not has_env and not has_db:
        raise HTTPException(
            status_code=503,
            detail="Governance pilot authentication is required but no keys are configured",
        )
    raise HTTPException(status_code=401, detail="Invalid or missing pilot API key")


def require_pilot_keys_admin(auth: PilotAuthContext) -> None:
    if "workspace:admin" in auth.scopes:
        return
    raise HTTPException(status_code=403, detail="Pilot scope workspace:admin required")


def assert_tenant_allowed(auth: PilotAuthContext, tenant_id: UUID) -> None:
    if auth.tenant_id is not None and auth.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="API key is not authorized for this tenant_id")


def require_workspace_read_scope(auth: PilotAuthContext) -> None:
    if auth.scopes & WORKSPACE_READ_SCOPES:
        return
    raise HTTPException(status_code=403, detail="Pilot scope workspace:read required")


def require_workspace_write_scope(auth: PilotAuthContext) -> None:
    if auth.scopes & WORKSPACE_WRITE_SCOPES:
        return
    raise HTTPException(status_code=403, detail="Pilot scope workspace:write required")
