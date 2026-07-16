"""Exact Cloudflare Pages release-metadata contracts for NF-WEB-002."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "resolve-cf-pages-release.py"
SPEC = importlib.util.spec_from_file_location("resolve_cf_pages_release", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SHA = "626b9b68512b6c474f759bff134ca251b053960d"
DEPLOYMENT_ID = "01234567-89ab-cdef-0123-456789abcdef"
IMMUTABLE_URL = "https://abcdef12.noetfield-www.pages.dev"


def test_project_requires_the_expected_production_branch() -> None:
    document = [{"name": "noetfield-www", "production_branch": "main"}]
    assert (
        MODULE.validate_project(
            document,
            project_name="noetfield-www",
            expected_branch="main",
        )
        == "main"
    )


def test_project_accepts_authoritative_api_object() -> None:
    document = {
        "success": True,
        "result": {"name": "noetfield-www", "production_branch": "main"},
    }
    assert (
        MODULE.validate_project(
            document,
            project_name="noetfield-www",
            expected_branch="main",
        )
        == "main"
    )


@pytest.mark.parametrize(
    "document",
    [
        [
            {
                "id": DEPLOYMENT_ID,
                "url": IMMUTABLE_URL,
                "environment": "production",
                "deployment_trigger": {
                    "metadata": {"branch": "main", "commit_hash": SHA}
                },
            }
        ],
        [
            {
                "Id": DEPLOYMENT_ID,
                "Deployment": IMMUTABLE_URL,
                "Environment": "Production",
                "Branch": "main",
                "Source": SHA,
            }
        ],
    ],
)
def test_exact_production_deployment_accepts_api_and_wrangler_shapes(
    document: list[dict[str, object]],
) -> None:
    deployment = MODULE.validate_deployment(
        document,
        project_name="noetfield-www",
        expected_branch="main",
        expected_sha=SHA,
    )
    assert deployment == {
        "id": DEPLOYMENT_ID,
        "url": IMMUTABLE_URL,
        "environment": "production",
        "branch": "main",
        "commit_hash": SHA,
    }


@pytest.mark.parametrize(
    ("url", "environment", "commit_hash"),
    [
        ("https://noetfield-www.pages.dev", "production", SHA),
        ("https://main.noetfield-www.pages.dev", "production", SHA),
        (IMMUTABLE_URL, "preview", SHA),
        (IMMUTABLE_URL, "production", "0" * 40),
    ],
)
def test_deployment_rejects_mutable_or_inexact_release_identity(
    url: str,
    environment: str,
    commit_hash: str,
) -> None:
    document = [
        {
            "id": DEPLOYMENT_ID,
            "url": url,
            "environment": environment,
            "deployment_trigger": {
                "metadata": {"branch": "main", "commit_hash": commit_hash}
            },
        }
    ]
    with pytest.raises(ValueError, match="no production deployment matches"):
        MODULE.validate_deployment(
            document,
            project_name="noetfield-www",
            expected_branch="main",
            expected_sha=SHA,
        )
