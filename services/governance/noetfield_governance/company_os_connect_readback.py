"""Scoped Platform operator readback of Company OS real intake/tasks/runs.

One authenticated GET keyed by the canonical source intake ID. No new queue,
agent dispatch, contact PII or fabricated external effects.
"""
from __future__ import annotations

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def readback(intake_id: str) -> dict[str, object]:
    if not re.fullmatch(r"INT-[A-Z0-9]{12}", intake_id):
        return {"connected": False, "error": "INVALID_SOURCE_INTAKE_ID"}
    token = os.getenv("CONNECT_BUSINESS_OS_READ_TOKEN", "")
    base = os.getenv("CONNECT_BUSINESS_OS_READ_URL", "").rstrip("/")
    parsed = urlsplit(base)
    if (len(token) < 32 or parsed.scheme != "https" or not parsed.hostname
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.path not in ("", "/")):
        return {"connected": False, "error": "COMPANY_OS_READ_NOT_CONFIGURED"}
    request = Request(base + "/api/internal/connect/cases/" + intake_id,
                      method="GET", headers={
                          "Accept": "application/json",
                          "X-Noetfield-Connect-Read-Token": token,
                          "User-Agent": "Noetfield-Platform-Connect-CompanyOS/1"})
    try:
        with urlopen(request, timeout=7) as response:
            payload = json.loads(response.read(20000))
        if not isinstance(payload, dict):
            return {"connected": False, "error": "INVALID_UPSTREAM_RESPONSE"}
        if (payload.get("found") is not True or
                payload.get("source_intake_id") != intake_id or
                payload.get("source") != "existing_company_os_core"):
            return {"connected": False, "error": "UNTRUSTED_UPSTREAM_ACK"}
        return {"connected": True, "found": True, **payload}
    except HTTPError as exc:
        if exc.code == 404:
            return {"connected": True, "found": False, "source_intake_id": intake_id,
                    "state": "NOT_YET_INGESTED_IN_COMPANY_OS",
                    "task_count": 0, "run_count": 0,
                    "external_effects_verified": False}
        return {"connected": False, "error": "UPSTREAM_HTTP", "http_status": exc.code}
    except (OSError, URLError, TimeoutError, ValueError) as exc:
        return {"connected": False, "error": type(exc).__name__}
