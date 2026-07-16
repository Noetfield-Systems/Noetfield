#!/usr/bin/env python3
"""Fail closed unless public output exactly matches the tracked allowlist."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "www-pages-dist"
ALLOWLIST = ROOT / "governance" / "www-public-artifact-v1.json"
DENYLIST = ROOT / "governance" / "PUBLIC_OUTPUT_DENYLIST.json"

FORBIDDEN_ROOT_FILES = {
    "AGENTS.md",
    "README.md",
    "repo-policy.json",
    "Makefile",
    "PRODUCT_BRIEF.md",
    "FOUNDER_CANON.md",
    "package.json",
    "package-lock.json",
    "pyproject.toml",
    "wrangler.toml",
    "railway.toml",
}
FORBIDDEN_PREFIXES = {
    ".agents/",
    ".claude/",
    ".cursor/",
    ".git/",
    ".github/",
    ".noetfield/",
    ".sina-agent/",
    ".vscode/",
    "L0-law/",
    "L1-operational/",
    "L2-knowledge/",
    "L3-external/",
    "Noetfield-All-Documents/",
    "_archive/",
    "api/",
    "apps/",
    "config/",
    "data/",
    "docs/",
    "governance-console/",
    "infra/",
    "infrastructure/",
    "node_modules/",
    "ops/",
    "os/",
    "packages/",
    "receipts/",
    "reports/",
    "scripts/",
    "tests/",
    "tmp/",
    "tools/",
    "var/",
}
FORBIDDEN_SUFFIXES = (
    ".bak",
    ".gz",
    ".orig",
    ".py",
    ".pyc",
    ".rej",
    ".sh",
    ".sql",
    ".tar",
    ".tmp",
    ".toml",
    ".tsx",
    ".ts",
    ".zip",
    "~",
    ".swp",
    ".swo",
)


def expected_files() -> set[str]:
    data = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    return set(data["static_files"])


def denylist() -> dict[str, list[str]]:
    return json.loads(DENYLIST.read_text(encoding="utf-8"))


def actual_files(output: Path) -> set[str]:
    return {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }


def forbidden_reason(rel_path: str) -> str | None:
    if rel_path in FORBIDDEN_ROOT_FILES:
        return "internal root file"
    if any(rel_path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        return "internal/source prefix"
    lower = rel_path.lower()
    if ".bak" in Path(lower).name or lower.endswith(FORBIDDEN_SUFFIXES):
        return "backup/source/editor/archive/temporary file"
    return None


def scan(output: Path) -> list[dict[str, str]]:
    if not output.is_dir():
        return [{"path": "<artifact>", "reason": "artifact directory is absent"}]

    expected = expected_files()
    actual = actual_files(output)
    findings: list[dict[str, str]] = []
    for path in sorted(expected - actual):
        findings.append({"path": path, "reason": "allowlisted artifact path is missing"})
    for path in sorted(actual - expected):
        findings.append({"path": path, "reason": "unexpected path is not allowlisted"})

    denied = denylist()
    exact = {path.lstrip("/") for path in denied.get("exact_paths", [])}
    prefixes = tuple(path.lstrip("/") for path in denied.get("prefix_paths", []))
    for path in sorted(actual):
        reason = forbidden_reason(path)
        if path in exact:
            reason = "PUBLIC_OUTPUT_DENYLIST exact path"
        elif path.startswith(prefixes):
            reason = "PUBLIC_OUTPUT_DENYLIST prefix path"
        if reason:
            findings.append({"path": path, "reason": reason})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    output = Path(args.output)
    findings = scan(output)
    unexpected = [
        finding
        for finding in findings
        if finding["reason"].startswith("unexpected")
        or "internal" in finding["reason"]
        or "DENYLIST" in finding["reason"]
        or "backup" in finding["reason"]
    ]
    payload = {
        "ok": not findings,
        "output": str(output),
        "blocked_count": len(findings),
        "unexpected_count": len(unexpected),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif findings:
        for finding in findings[:100]:
            print(
                f"FAIL public-output-allowlist: {finding['path']} "
                f"({finding['reason']})"
            )
        if len(findings) > 100:
            print(f"FAIL public-output-allowlist: {len(findings) - 100} more findings")
    else:
        print(
            "OK   public-output-allowlist: exact artifact; "
            f"{len(actual_files(output))} static files; unexpected=0"
        )
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
