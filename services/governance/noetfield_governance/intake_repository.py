"""Intake persistence facade — memory or PostgreSQL."""

from __future__ import annotations

import logging
from typing import Any, Literal, Protocol

from noetfield_config import Settings
from noetfield_governance.intake_store import IntakeRecord
from noetfield_governance.intake_store import get_by_request_id as memory_get_by_request_id
from noetfield_governance.intake_store import list_recent as memory_list_recent
from noetfield_governance.intake_store import list_after as memory_list_after
from noetfield_governance.intake_store import record_intake as memory_record_intake
from noetfield_governance.intake_store import update_email_archive_status as memory_update_email_archive_status
from noetfield_governance.postgres_intake_store import PostgresIntakeStore

logger = logging.getLogger("noetfield.governance.intake")

IntakePersistence = Literal["auto", "memory", "postgres"]


class IntakeStoreBackend(Protocol):
    async def record(
        self,
        *,
        organization: str,
        contact_email: str,
        message: str,
        request_id: str | None = None,
        contact_name: str | None = None,
        sku: str = "trust_brief",
        vector: str = "web-intake",
        source: str = "api",
        metadata: dict[str, Any] | None = None,
        qualification_json: dict[str, Any] | None = None,
    ) -> IntakeRecord: ...

    async def list_recent(self, *, limit: int = 50) -> list[dict[str, Any]]: ...

    async def list_after(
        self,
        *,
        created_after: str | None = None,
        intake_after: str = "",
        limit: int = 50,
    ) -> list[dict[str, Any]]: ...

    async def get_by_request_id(self, request_id: str) -> IntakeRecord | None: ...

    async def update_email_archive_status(
        self,
        *,
        request_id: str,
        status: str,
        detail: str | None = None,
    ) -> dict[str, Any] | None: ...

    async def close(self) -> None: ...


class _MemoryIntakeBackend:
    async def record(self, **kwargs: Any) -> IntakeRecord:
        return memory_record_intake(**kwargs)

    async def list_recent(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return memory_list_recent(limit=limit)

    async def list_after(
        self,
        *,
        created_after: str | None = None,
        intake_after: str = "",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return memory_list_after(
            created_after=created_after,
            intake_after=intake_after,
            limit=limit,
        )

    async def get_by_request_id(self, request_id: str) -> IntakeRecord | None:
        row = memory_get_by_request_id(request_id)
        if row is None:
            return None
        return IntakeRecord(**row)

    async def update_email_archive_status(
        self,
        *,
        request_id: str,
        status: str,
        detail: str | None = None,
    ) -> dict[str, Any] | None:
        return memory_update_email_archive_status(
            request_id=request_id,
            status=status,
            detail=detail,
        )

    async def close(self) -> None:
        return None


_backend: IntakeStoreBackend | None = None
_backend_label: str = "memory"


def resolve_persistence(settings: Settings) -> IntakePersistence:
    pref = getattr(settings, "intake_persistence", "auto")
    if pref in ("memory", "postgres"):
        return pref
    if settings.runtime_event_store == "postgres":
        return "postgres"
    return "memory"


async def init_intake_repository(settings: Settings | None = None) -> str:
    global _backend, _backend_label
    if settings is None:
        from noetfield_config import get_settings

        settings = get_settings()
    mode = resolve_persistence(settings)
    if mode == "postgres":
        store = PostgresIntakeStore(settings.database_url)
        await store.connect()
        _backend = store
        _backend_label = "postgres"
        logger.info("intake_repository mode=postgres")
    else:
        _backend = _MemoryIntakeBackend()
        _backend_label = "memory"
        logger.info("intake_repository mode=memory")
    return _backend_label


async def close_intake_repository() -> None:
    global _backend
    if _backend is not None:
        await _backend.close()
    _backend = None


def storage_label() -> str:
    return _backend_label


async def record_intake(**kwargs: Any) -> IntakeRecord:
    if _backend is None:
        await init_intake_repository()
    assert _backend is not None
    return await _backend.record(**kwargs)


async def list_recent(*, limit: int = 50) -> list[dict[str, Any]]:
    if _backend is None:
        return memory_list_recent(limit=limit)
    return await _backend.list_recent(limit=limit)


async def list_after(
    *,
    created_after: str | None = None,
    intake_after: str = "",
    limit: int = 50,
) -> list[dict[str, Any]]:
    if _backend is None:
        return memory_list_after(
            created_after=created_after,
            intake_after=intake_after,
            limit=limit,
        )
    assert _backend is not None
    return await _backend.list_after(
        created_after=created_after,
        intake_after=intake_after,
        limit=limit,
    )


async def get_by_request_id(request_id: str) -> IntakeRecord | None:
    if _backend is None:
        await init_intake_repository()
    assert _backend is not None
    return await _backend.get_by_request_id(request_id)


async def update_email_archive_status(
    *,
    request_id: str,
    status: str,
    detail: str | None = None,
) -> dict[str, Any] | None:
    if _backend is None:
        await init_intake_repository()
    assert _backend is not None
    return await _backend.update_email_archive_status(
        request_id=request_id,
        status=status,
        detail=detail,
    )


async def update_connect_opportunity(
    *, intake_id: str, expected_revision: int, stage: str,
    owner: str, next_action: str, due_date: str | None, note: str,
) -> dict[str, Any] | None:
    """Persist operator decisions on the existing source row, not another CRM."""
    if _backend is None:
        await init_intake_repository()
    if not isinstance(_backend, PostgresIntakeStore):
        raise RuntimeError("OPPORTUNITY_PERSISTENCE_UNAVAILABLE")
    return await _backend.update_connect_state(
        intake_id=intake_id, expected_revision=expected_revision,
        stage=stage, owner=owner, next_action=next_action,
        due_date=due_date, note=note,
    )



async def _connect_postgres() -> PostgresIntakeStore:
    if _backend is None:
        await init_intake_repository()
    if not isinstance(_backend, PostgresIntakeStore):
        raise RuntimeError("OPPORTUNITY_PERSISTENCE_UNAVAILABLE")
    return _backend


async def list_connect_page(*, limit: int = 50, offset: int = 0) -> dict[str, Any]:
    return await (await _connect_postgres()).list_connect_page(limit=limit, offset=offset)


async def list_connect_by_intake(*, intake_id: str, limit: int = 50) -> list[dict[str, Any]]:
    return await (await _connect_postgres()).list_connect_by_intake(
        intake_id=intake_id, limit=limit,
    )


async def append_connect_activity(**kwargs: Any) -> dict[str, Any] | None:
    return await (await _connect_postgres()).append_connect_activity(**kwargs)


async def create_connect_invitation(**kwargs: Any) -> dict[str, Any] | None:
    return await (await _connect_postgres()).create_connect_invitation(**kwargs)


async def respond_connect_invitation(**kwargs: Any) -> dict[str, Any] | None:
    return await (await _connect_postgres()).respond_connect_invitation(**kwargs)


async def public_connect_participant_status(**kwargs: Any) -> dict[str, Any] | None:
    return await (await _connect_postgres()).public_connect_participant_status(**kwargs)


async def append_public_connect_feedback(**kwargs: Any) -> dict[str, Any] | None:
    return await (await _connect_postgres()).append_public_connect_feedback(**kwargs)


async def record_connect_outcome(**kwargs: Any) -> dict[str, Any] | None:
    return await (await _connect_postgres()).record_connect_outcome(**kwargs)


async def get_connect_delivery_source(*, intake_id: str) -> dict[str, Any] | None:
    return await (await _connect_postgres()).get_connect_delivery_source(intake_id=intake_id)


async def claim_connect_invitation_send(**kwargs: Any) -> dict[str, Any] | None:
    return await (await _connect_postgres()).claim_connect_invitation_send(**kwargs)


async def finish_connect_invitation_send(**kwargs: Any) -> dict[str, Any] | None:
    return await (await _connect_postgres()).finish_connect_invitation_send(**kwargs)


def intake_status_payload(record: IntakeRecord | dict[str, Any]) -> dict[str, object]:
    if isinstance(record, IntakeRecord):
        data = {
            "intake_id": record.intake_id,
            "request_id": record.request_id,
            "created_at": record.created_at,
            "email_archive_status": record.email_archive_status,
            "email_archive_updated_at": record.email_archive_updated_at,
            "email_archive_detail": record.email_archive_detail,
        }
    else:
        data = {
            "intake_id": record.get("intake_id"),
            "request_id": record.get("request_id"),
            "created_at": record.get("created_at"),
            "email_archive_status": record.get("email_archive_status"),
            "email_archive_updated_at": record.get("email_archive_updated_at"),
            "email_archive_detail": record.get("email_archive_detail"),
        }
    return data
