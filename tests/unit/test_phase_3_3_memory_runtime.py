"""Fast backend runtime verification that does not require PostgreSQL."""

from __future__ import annotations

import asyncio

from scripts.phase_3_2_backend_smoke import run_smoke


def test_phase_3_3_memory_runtime_smoke() -> None:
    asyncio.run(run_smoke(use_postgres=False, database_url=None))
