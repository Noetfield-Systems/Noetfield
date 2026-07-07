"""Gov-sandbox Railway manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_railway_manifest_services() -> None:
    data = json.loads((ROOT / "data/nf-railway-gov-sandbox-manifest-v1.json").read_text(encoding="utf-8"))
    api = data["services"]["gov-sandbox-api"]
    web = data["services"]["gov-sandbox-web"]
    assert api["dockerfile_path"] == "governance-console/backend/Dockerfile"
    assert web["dockerfile_path"] == "governance-console/Dockerfile.www"
    assert data["forbidden_dockerfile"] == "infrastructure/docker/Dockerfile.api"
    assert (ROOT / api["dockerfile_path"]).is_file()
    assert (ROOT / web["dockerfile_path"]).is_file()


def test_staging_proxy_template() -> None:
    data = json.loads((ROOT / "data/nf-www-gov-proxy-staging-v1.json").read_text(encoding="utf-8"))
    assert data["enabled"] is False
    assert data["schema"] == "nf-www-gov-proxy-v1"


def test_sandbox_guard_mutating_detection() -> None:
    backend = ROOT / "governance-console" / "backend"
    sys.path.insert(0, str(backend))
    from middleware.sandbox_guard import _is_mutating  # noqa: E402

    assert _is_mutating("/evaluate", "POST") is True
    assert _is_mutating("/tle/draft", "POST") is True
    assert _is_mutating("/health", "GET") is False
    assert _is_mutating("/tle", "GET") is False
