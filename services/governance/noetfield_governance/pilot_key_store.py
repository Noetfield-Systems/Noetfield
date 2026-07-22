"""Pilot API key persistence — hashed secrets in Postgres or in-memory for tests."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID, uuid4

import asyncpg

KEY_PREFIX_LEN = 16
SECRET_PREFIX = "nf_pilot_"


@dataclass(frozen=True)
class PilotKeyRecord:
    key_id: UUID
    key_prefix: str
    key_hash: str
    label: str
    tenant_id: UUID | None
    scopes: list[str]
    created_at: datetime
    revoked_at: datetime | None = None
    created_by: str = "system"


def hash_pilot_secret(secret: str, pepper: str) -> str:
    """SHA-256 hex of pepper + secret (pepper from EVENT_INTEGRITY_SECRET)."""
    return hashlib.sha256(f"{pepper}{secret}".encode("utf-8")).hexdigest()


def generate_secret() -> str:
    return f"{SECRET_PREFIX}{secrets.token_urlsafe(32)}"


def _prefix_for(secret: str) -> str:
    return secret[:KEY_PREFIX_LEN]


class PilotKeyStore(Protocol):
    async def connect(self) -> None: ...

    async def close(self) -> None: ...

    async def create(
        self,
        *,
        label: str,
        tenant_id: UUID | None,
        scopes: list[str],
        created_by: str = "system",
    ) -> tuple[str, PilotKeyRecord]: ...

    async def lookup_by_secret(self, secret: str) -> PilotKeyRecord | None: ...

    async def list_active(self) -> list[PilotKeyRecord]: ...

    async def revoke(self, key_id: UUID) -> PilotKeyRecord | None: ...

    async def count_active(self) -> int: ...


class InMemoryPilotKeyStore:
    """Unit tests / non-postgres mode."""

    def __init__(self, pepper: str) -> None:
        self._pepper = pepper
        self._by_id: dict[UUID, PilotKeyRecord] = {}
        self._hash_to_id: dict[str, UUID] = {}

    async def connect(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def create(
        self,
        *,
        label: str,
        tenant_id: UUID | None,
        scopes: list[str],
        created_by: str = "system",
    ) -> tuple[str, PilotKeyRecord]:
        secret = generate_secret()
        key_hash = hash_pilot_secret(secret, self._pepper)
        if key_hash in self._hash_to_id:
            raise RuntimeError("pilot key hash collision")
        record = PilotKeyRecord(
            key_id=uuid4(),
            key_prefix=_prefix_for(secret),
            key_hash=key_hash,
            label=label.strip() or "pilot",
            tenant_id=tenant_id,
            scopes=list(scopes),
            created_at=datetime.now(UTC),
            created_by=created_by or "system",
        )
        self._by_id[record.key_id] = record
        self._hash_to_id[key_hash] = record.key_id
        return secret, record

    async def lookup_by_secret(self, secret: str) -> PilotKeyRecord | None:
        key_hash = hash_pilot_secret(secret, self._pepper)
        key_id = self._hash_to_id.get(key_hash)
        if key_id is None:
            return None
        record = self._by_id.get(key_id)
        if record is None or record.revoked_at is not None:
            return None
        return record

    async def list_active(self) -> list[PilotKeyRecord]:
        return sorted(
            (r for r in self._by_id.values() if r.revoked_at is None),
            key=lambda r: r.created_at,
            reverse=True,
        )

    async def revoke(self, key_id: UUID) -> PilotKeyRecord | None:
        record = self._by_id.get(key_id)
        if record is None:
            return None
        if record.revoked_at is not None:
            return record
        revoked = PilotKeyRecord(
            key_id=record.key_id,
            key_prefix=record.key_prefix,
            key_hash=record.key_hash,
            label=record.label,
            tenant_id=record.tenant_id,
            scopes=list(record.scopes),
            created_at=record.created_at,
            revoked_at=datetime.now(UTC),
            created_by=record.created_by,
        )
        self._by_id[key_id] = revoked
        return revoked

    async def count_active(self) -> int:
        return sum(1 for r in self._by_id.values() if r.revoked_at is None)


class PostgresPilotKeyStore:
    """asyncpg-backed store; URL rewrite mirrors PostgresIntakeStore."""

    def __init__(self, database_url: str, pepper: str) -> None:
        self._database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self._pepper = pepper
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._database_url)

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def create(
        self,
        *,
        label: str,
        tenant_id: UUID | None,
        scopes: list[str],
        created_by: str = "system",
    ) -> tuple[str, PilotKeyRecord]:
        await self.connect()
        assert self._pool is not None
        secret = generate_secret()
        key_hash = hash_pilot_secret(secret, self._pepper)
        key_prefix = _prefix_for(secret)
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                insert into noetfield.pilot_api_keys (
                  key_prefix, key_hash, label, tenant_id, scopes, created_by
                )
                values ($1, $2, $3, $4, $5::text[], $6)
                returning key_id, key_prefix, key_hash, label, tenant_id, scopes,
                          created_at, revoked_at, created_by
                """,
                key_prefix,
                key_hash,
                label.strip() or "pilot",
                tenant_id,
                list(scopes),
                created_by or "system",
            )
        return secret, _row_to_record(row)

    async def lookup_by_secret(self, secret: str) -> PilotKeyRecord | None:
        await self.connect()
        assert self._pool is not None
        key_hash = hash_pilot_secret(secret, self._pepper)
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                select key_id, key_prefix, key_hash, label, tenant_id, scopes,
                       created_at, revoked_at, created_by
                from noetfield.pilot_api_keys
                where key_hash = $1 and revoked_at is null
                limit 1
                """,
                key_hash,
            )
        if row is None:
            return None
        return _row_to_record(row)

    async def list_active(self) -> list[PilotKeyRecord]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select key_id, key_prefix, key_hash, label, tenant_id, scopes,
                       created_at, revoked_at, created_by
                from noetfield.pilot_api_keys
                where revoked_at is null
                order by created_at desc
                """
            )
        return [_row_to_record(row) for row in rows]

    async def revoke(self, key_id: UUID) -> PilotKeyRecord | None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                update noetfield.pilot_api_keys
                set revoked_at = coalesce(revoked_at, now())
                where key_id = $1
                returning key_id, key_prefix, key_hash, label, tenant_id, scopes,
                          created_at, revoked_at, created_by
                """,
                key_id,
            )
        if row is None:
            return None
        return _row_to_record(row)

    async def count_active(self) -> int:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            value = await connection.fetchval(
                """
                select count(*)::int
                from noetfield.pilot_api_keys
                where revoked_at is null
                """
            )
        return int(value or 0)


def _row_to_record(row: asyncpg.Record) -> PilotKeyRecord:
    scopes = list(row["scopes"] or [])
    return PilotKeyRecord(
        key_id=row["key_id"],
        key_prefix=row["key_prefix"],
        key_hash=row["key_hash"],
        label=row["label"],
        tenant_id=row["tenant_id"],
        scopes=scopes,
        created_at=row["created_at"],
        revoked_at=row["revoked_at"],
        created_by=row["created_by"] or "system",
    )
