"""Shared asyncpg pool singleton."""

from __future__ import annotations

import pytest

from noetfield_types.postgres_pool import close_all_pools, get_pool, normalize_dsn


def test_normalize_dsn_strips_asyncpg_prefix() -> None:
    assert normalize_dsn("postgresql+asyncpg://user:pass@host/db") == "postgresql://user:pass@host/db"


@pytest.mark.asyncio
async def test_get_pool_returns_same_instance_per_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    created: list[object] = []

    class FakePool:
        async def close(self) -> None:
            return None

    async def fake_create_pool(dsn: str, *, min_size: int, max_size: int) -> FakePool:
        created.append((dsn, min_size, max_size))
        return FakePool()

    import noetfield_types.postgres_pool as pool_mod

    monkeypatch.setattr(pool_mod.asyncpg, "create_pool", fake_create_pool)
    await close_all_pools()

    dsn = "postgresql://example/test"
    first = await get_pool(dsn)
    second = await get_pool(dsn)
    assert first is second
    assert len(created) == 1
    await close_all_pools()
