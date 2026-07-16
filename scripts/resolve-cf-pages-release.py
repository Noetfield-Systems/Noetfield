#!/usr/bin/env python3
"""Validate Cloudflare Pages project/deployment JSON for an exact release.

The script reads Wrangler JSON from stdin and prints only validated, shell-safe
fields. It deliberately rejects mutable branch/project aliases as release origins.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from typing import Any
from urllib.parse import urlsplit

SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
HOST_LABEL_PATTERN = re.compile(r"^[a-z0-9-]+$")


def fail(message: str, code: int = 2) -> int:
    print(f"FAIL resolve-cf-pages-release: {message}", file=sys.stderr)
    return code


def read_json() -> Any:
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("empty Wrangler JSON")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        starts = [position for position in (raw.find("["), raw.find("{")) if position >= 0]
        if not starts:
            raise ValueError("Wrangler output contains no JSON") from None
        try:
            value, _end = decoder.raw_decode(raw[min(starts) :])
            return value
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid Wrangler JSON: {exc}") from exc


def nested(value: Any, *paths: tuple[str, ...]) -> Any:
    for path in paths:
        current = value
        for key in path:
            if not isinstance(current, dict) or key not in current:
                break
            current = current[key]
        else:
            if current not in (None, ""):
                return current
    return None


def rows(document: Any) -> list[dict[str, Any]]:
    value = document
    if isinstance(document, dict):
        value = document.get("result", document.get("deployments", document.get("projects")))
    if not isinstance(value, list):
        raise ValueError("Wrangler JSON is not a list")
    return [row for row in value if isinstance(row, dict)]


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def project_branch(row: dict[str, Any]) -> str:
    return text(
        nested(
            row,
            ("production_branch",),
            ("productionBranch",),
            ("source", "config", "production_branch"),
            ("source", "config", "productionBranch"),
        )
    )


def validate_project(document: Any, *, project_name: str, expected_branch: str) -> str:
    project = next(
        (
            row
            for row in rows(document)
            if text(nested(row, ("name",), ("project_name",), ("projectName",)))
            == project_name
        ),
        None,
    )
    if project is None:
        raise LookupError(f"Pages project not found: {project_name}")
    branch = project_branch(project)
    if not branch:
        raise ValueError(f"Pages project {project_name} has no production_branch metadata")
    if branch != expected_branch:
        raise ValueError(
            f"Pages project {project_name} production_branch={branch!r}; "
            f"expected {expected_branch!r}"
        )
    return branch


def deployment_fields(row: dict[str, Any]) -> dict[str, str]:
    metadata = nested(row, ("deployment_trigger", "metadata"), ("deploymentTrigger", "metadata"))
    if not isinstance(metadata, dict):
        metadata = {}
    source = nested(row, ("source", "config"), ("source",))
    if not isinstance(source, dict):
        source = {}
    return {
        "id": text(nested(row, ("id",), ("Id",), ("deployment_id",))),
        "url": text(nested(row, ("url",), ("URL",), ("deployment_url",), ("Deployment",))),
        "environment": text(nested(row, ("environment",), ("Environment",))).lower(),
        "branch": text(
            nested(
                metadata,
                ("branch",),
            )
            or nested(source, ("branch",))
            or nested(row, ("branch",), ("Branch",))
        ),
        "commit_hash": text(
            nested(metadata, ("commit_hash",), ("commitHash",))
            or nested(source, ("commit_hash",), ("commitHash",))
            or nested(row, ("commit_hash",), ("commitHash",), ("Source",))
        ).lower(),
    }


def immutable_url(value: str, *, project_name: str, branch: str) -> bool:
    parsed = urlsplit(value)
    labels = (parsed.hostname or "").split(".")
    if parsed.scheme != "https" or parsed.path not in ("", "/") or parsed.query:
        return False
    if len(labels) != 4 or labels[1:] != [project_name, "pages", "dev"]:
        return False
    token = labels[0]
    return bool(
        HOST_LABEL_PATTERN.fullmatch(token)
        and token not in {branch, "main", "production", "www"}
    )


def matching_deployments(
    document: Any,
    *,
    project_name: str,
    expected_branch: str,
    expected_sha: str,
) -> Iterable[dict[str, str]]:
    for row in rows(document):
        fields = deployment_fields(row)
        if (
            fields["environment"] == "production"
            and fields["branch"] == expected_branch
            and fields["commit_hash"] == expected_sha
            and fields["id"]
            and immutable_url(fields["url"], project_name=project_name, branch=expected_branch)
        ):
            yield fields


def validate_deployment(
    document: Any,
    *,
    project_name: str,
    expected_branch: str,
    expected_sha: str,
) -> dict[str, str]:
    if not SHA_PATTERN.fullmatch(expected_sha):
        raise ValueError("expected SHA must be a full lowercase 40-character git SHA")
    match = next(
        matching_deployments(
            document,
            project_name=project_name,
            expected_branch=expected_branch,
            expected_sha=expected_sha,
        ),
        None,
    )
    if match is None:
        raise ValueError(
            "no production deployment matches the exact branch, full SHA and immutable URL"
        )
    return match


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("project", "deployment"))
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--expected-branch", required=True)
    parser.add_argument("--expected-sha", default="")
    args = parser.parse_args()

    try:
        document = read_json()
        if args.kind == "project":
            branch = validate_project(
                document,
                project_name=args.project_name,
                expected_branch=args.expected_branch,
            )
            print(branch)
            return 0
        deployment = validate_deployment(
            document,
            project_name=args.project_name,
            expected_branch=args.expected_branch,
            expected_sha=args.expected_sha,
        )
        print(
            "\t".join(
                deployment[key]
                for key in ("id", "url", "commit_hash", "branch", "environment")
            )
        )
        return 0
    except LookupError as exc:
        return fail(str(exc), code=4)
    except (TypeError, ValueError) as exc:
        return fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
