#!/usr/bin/env python3
"""Validate the repo-local agent and boundary policy."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "repo-policy.json"


def fail(message: str) -> None:
    print(f"FAIL repo-policy: {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"OK   repo-policy: {message}")


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_policy() -> dict[str, Any]:
    try:
        data = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - CLI guard
        fail(f"invalid JSON in {POLICY_PATH.relative_to(ROOT)}: {exc}")
    if not isinstance(data, dict):
        fail("repo-policy.json must contain an object")
    return data


def require_file(path: str) -> None:
    if not (ROOT / path).is_file():
        fail(f"missing required file: {path}")


def require_contains(path: str, needle: str) -> None:
    require_file(path)
    text = (ROOT / path).read_text(encoding="utf-8")
    if needle not in text:
        fail(f"{path} missing required text: {needle}")


def changed_files() -> list[str]:
    result = run_git(["status", "--short"])
    if result.returncode != 0:
        fail(f"git status failed: {result.stderr.strip()}")
    files: list[str] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        # porcelain v1: XY path, with optional rename "old -> new"
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path)
    return files


def validate_policy_shape(policy: dict[str, Any]) -> None:
    required_top = {
        "schema",
        "repo",
        "authority_sources",
        "lanes",
        "boundaries",
        "forbidden_active_work",
        "cross_repo_dependency_policy",
        "generated_output_policy",
        "validator",
        "claims_intentionally_avoided",
    }
    missing = sorted(required_top - set(policy))
    if missing:
        fail(f"repo-policy.json missing keys: {', '.join(missing)}")
    if policy.get("schema") != "noetfield-repo-policy-v1":
        fail("unexpected schema")

    lanes = policy.get("lanes")
    if not isinstance(lanes, dict) or not lanes:
        fail("lanes must be a non-empty object")
    for required_lane in ("website", "platform-spine", "repo-policy", "docs-policy", "live-nerve"):
        if required_lane not in lanes:
            fail(f"missing lane: {required_lane}")

    boundaries = policy.get("boundaries")
    if not isinstance(boundaries, dict):
        fail("boundaries must be an object")
    if boundaries.get("one_lane_per_pass") is not True:
        fail("one_lane_per_pass must be true")
    max_files = boundaries.get("max_files_per_pass")
    if not isinstance(max_files, int) or max_files < 20 or max_files > 40:
        fail("max_files_per_pass must be an integer between 20 and 40")


def validate_authority_sources(policy: dict[str, Any]) -> None:
    sources = policy.get("authority_sources")
    if not isinstance(sources, list) or not sources:
        fail("authority_sources must be a non-empty list")
    for source in sources:
        if not isinstance(source, str):
            fail("authority_sources must contain strings")
        require_file(source)


def validate_wiring(policy: dict[str, Any]) -> None:
    require_contains("AGENTS.md", "repo-policy.json")
    require_contains(".cursor/rules/repo-boundary.mdc", "repo-policy.json")
    require_contains(".cursor/rules/repo-boundary.mdc", "alwaysApply: true")
    require_contains("docs/ops/REPO_POLICY_BOUNDARY_LOCKED_v1.md", "repo-policy.json")

    validator = policy.get("validator")
    if not isinstance(validator, dict):
        fail("validator must be an object")
    if validator.get("script") != "scripts/check_repo_policy.py":
        fail("validator.script must point to scripts/check_repo_policy.py")


def validate_changed_file_count(policy: dict[str, Any], files: list[str]) -> None:
    max_files = int(policy["boundaries"]["max_files_per_pass"])
    if len(files) > max_files:
        fail(f"dirty file count {len(files)} exceeds policy max {max_files}")
    ok(f"dirty file count within policy ({len(files)}/{max_files})")


def validate_clean_tree(files: list[str]) -> None:
    if files:
        fail("clean-tree guard failed; dirty files: " + ", ".join(files[:20]))
    ok("clean tree")


def validate_diff_check() -> None:
    result = run_git(["diff", "--check"])
    if result.returncode != 0:
        fail("git diff --check failed:\n" + result.stdout + result.stderr)
    ok("git diff --check")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repo-local policy lane")
    parser.add_argument("--clean-tree", action="store_true", help="fail if the working tree is dirty")
    args = parser.parse_args()

    policy = load_policy()
    ok("JSON syntax")
    validate_policy_shape(policy)
    ok("policy shape")
    validate_authority_sources(policy)
    ok("authority sources exist")
    validate_wiring(policy)
    ok("policy wiring")
    files = changed_files()
    validate_changed_file_count(policy, files)
    validate_diff_check()
    if args.clean_tree:
        validate_clean_tree(files)
    else:
        ok("clean-tree guard available via --clean-tree")
    ok("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
