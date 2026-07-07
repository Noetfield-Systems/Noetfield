"""Sandbox abuse controls — rate limit + optional API key for mutating routes."""

from __future__ import annotations

import os
import time
from collections import defaultdict
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

MUTATING_PREFIXES = (
    "/evaluate",
    "/tle",
    "/connectors",
    "/evidence",
    "/api/v1/sandbox",
    "/audit",
)

_rate_buckets: dict[str, list[float]] = defaultdict(list)
_RATE_WINDOW_SEC = 60.0
_RATE_MAX = int(os.getenv("NF_SANDBOX_RATE_LIMIT_PER_MIN", "120"))


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _is_mutating(path: str, method: str) -> bool:
    if method in ("GET", "HEAD", "OPTIONS"):
        return False
    return any(path == p or path.startswith(f"{p}/") for p in MUTATING_PREFIXES)


class SandboxGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method.upper()

        if _is_mutating(path, method):
            api_key = os.getenv("NF_SANDBOX_API_KEY", "").strip()
            if api_key:
                provided = request.headers.get("x-nf-sandbox-key", "").strip()
                if provided != api_key:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "sandbox key required for write operations"},
                    )

            ip = _client_ip(request)
            now = time.monotonic()
            bucket = _rate_buckets[ip]
            bucket[:] = [t for t in bucket if now - t < _RATE_WINDOW_SEC]
            if len(bucket) >= _RATE_MAX:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "rate limit exceeded"},
                )
            bucket.append(now)

        return await call_next(request)
