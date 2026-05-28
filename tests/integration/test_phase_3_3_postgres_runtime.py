"""PostgreSQL runtime verification for Phase 3.3.

These tests require a real PostgreSQL/pgvector database. They are designed for
CI service containers and local developer runs after `make apply-migrations`.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

from scripts.apply_postgres_migrations import apply_migrations
from scripts.phase_3_2_backend_smoke import run_smoke


def test_phase_3_3_postgres_runtime_smoke() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is required for PostgreSQL runtime verification")

    migrations_dir = Path("infrastructure/supabase/migrations")
    asyncio.run(apply_migrations(database_url, migrations_dir))
    asyncio.run(run_smoke(use_postgres=True, database_url=database_url))
