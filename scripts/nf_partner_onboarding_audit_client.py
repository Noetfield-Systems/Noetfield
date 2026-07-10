"""Insert public.partner_onboarding_audit_runs rows via Supabase REST."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from nf_vault_env import ensure_noetfield_supabase_env  # noqa: E402


def _config() -> tuple[str, str]:
    ensure_noetfield_supabase_env()
    url = (
        os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""
    ).rstrip("/")
    key = (
        os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    )
    if not url or not key:
        raise RuntimeError("NOETFIELD_SUPABASE_URL and service role key required")
    return url, key


def insert_audit_run(
    *,
    run_id: str,
    score: int,
    status: str,
    critical_count: int,
    high_count: int,
    findings: list[dict[str, Any]],
) -> None:
    base, key = _config()
    body = [
        {
            "run_id": run_id,
            "score": score,
            "status": status,
            "critical_count": critical_count,
            "high_count": high_count,
            "findings": findings,
        }
    ]
    req = urllib.request.Request(
        f"{base}/rest/v1/partner_onboarding_audit_runs",
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status not in (200, 201, 204):
                raise RuntimeError(f"supabase insert HTTP {resp.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"supabase insert failed HTTP {exc.code}: {detail}") from exc
