"""Shared asyncpg pool — one pool per DSN to avoid Railway Postgres connection exhaustion."""

from __future__ import annotations

import asyncio
import os

import asyncpg

_pools: dict[str, asyncpg.Pool] = {}
_lock = asyncio.Lock()


def normalize_dsn(database_url: str) -> str:
    return database_url.replace("postgresql+asyncpg://", "postgresql://")


def _pool_max_size() -> int:
    raw = (os.environ.get("PG_POOL_MAX_SIZE") or "4").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 4


def _pool_min_size() -> int:
    raw = (os.environ.get("PG_POOL_MIN_SIZE") or "0").strip()
    try:
        return max(0, int(raw))
    except ValueError:
        return 0


async def get_pool(database_url: str) -> asyncpg.Pool:
    dsn = normalize_dsn(database_url)
    existing = _pools.get(dsn)
    if existing is not None:
        return existing
    async with _lock:
        existing = _pools.get(dsn)
        if existing is not None:
            return existing
        pool = await asyncpg.create_pool(
            dsn,
            min_size=_pool_min_size(),
            max_size=_pool_max_size(),
        )
        _pools[dsn] = pool
        return pool


async def close_all_pools() -> None:
    async with _lock:
        pools = list(_pools.values())
        _pools.clear()
    for pool in pools:
        await pool.close()
