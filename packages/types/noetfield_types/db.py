"""PostgreSQL / asyncpg JSONB helpers."""

from __future__ import annotations

import json
from typing import Any


def coerce_jsonb_mapping(value: Any | None) -> dict[str, Any]:
    """Normalize JSONB column values from asyncpg (dict, str, or None)."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return {}
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
        return {}
    return {}
