#!/usr/bin/env python3
"""Build and attest the exact NF-REL-002 Cloudflare Pages deployment units."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST_PATH = ROOT / "governance" / "www-public-artifact-v1.json"
DIST = ROOT / "www-pages-dist"
RECEIPT_PATH = ROOT / "tmp" / "nf-rel-002" / "public-artifact-manifest.json"

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
    ".agents",
    ".claude",
    ".cursor",
    ".git",
    ".github",
    ".noetfield",
    ".sina-agent",
    ".vscode",
    "L0-law",
    "L1-operational",
    "L2-knowledge",
    "L3-external",
    "Noetfield-All-Documents",
    "_archive",
    "api",
    "apps",
    "config",
    "data",
    "docs",
    "governance-console",
    "infra",
    "infrastructure",
    "node_modules",
    "ops",
    "os",
    "packages",
    "receipts",
    "reports",
    "scripts",
    "tests",
    "tmp",
    "tools",
    "var",
}
FORBIDDEN_SUFFIXES = {
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
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_allowlist() -> dict[str, object]:
    data = json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))
    if data.get("schema") != "noetfield-www-public-artifact-allowlist-v1":
        raise ValueError("unsupported public artifact allowlist schema")
    return data


def exact_list(data: dict[str, object], key: str) -> list[str]:
    raw = data.get(key)
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise ValueError(f"{key} must be a list of paths")
    if raw != sorted(set(raw)):
        raise ValueError(f"{key} must be unique and byte-sorted")
    return raw


def validate_relative_path(rel: str, *, function: bool = False) -> None:
    path = PurePosixPath(rel)
    if path.is_absolute() or ".." in path.parts or rel != path.as_posix():
        raise ValueError(f"unsafe artifact path: {rel}")
    if not path.parts:
        raise ValueError("empty artifact path")
    if any(part.startswith(".") for part in path.parts):
        raise ValueError(f"dot-path is not public: {rel}")
    if not function:
        if rel in FORBIDDEN_ROOT_FILES:
            raise ValueError(f"internal root file is not public: {rel}")
        if path.parts[0] in FORBIDDEN_PREFIXES:
            raise ValueError(f"internal prefix is not public: {rel}")
        lower_name = path.name.lower()
        if (
            path.suffix.lower() in FORBIDDEN_SUFFIXES
            or ".bak" in lower_name
            or lower_name.endswith(("~", ".swp", ".swo"))
        ):
            raise ValueError(f"backup/source/temporary file is not public: {rel}")
    elif path.parts[0] != "functions" or path.suffix != ".js":
        raise ValueError(f"invalid Pages Function path: {rel}")


def validate_source_files(data: dict[str, object]) -> tuple[list[str], list[str]]:
    static_files = exact_list(data, "static_files")
    function_files = exact_list(data, "pages_function_files")
    public_json = exact_list(data, "public_json_files")
    json_in_static = sorted(rel for rel in static_files if rel.endswith(".json"))
    if json_in_static != public_json:
        raise ValueError(
            "every deployed JSON file must be explicitly named in public_json_files"
        )

    for rel in static_files:
        validate_relative_path(rel)
        source = ROOT / rel
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"missing or non-regular public source: {rel}")
    for rel in function_files:
        validate_relative_path(rel, function=True)
        source = ROOT / rel
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"missing or non-regular Pages Function: {rel}")
    return static_files, function_files


def actual_files(root: Path) -> list[str]:
    if not root.is_dir():
        return []
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())


def function_files_on_disk() -> list[str]:
    root = ROOT / "functions"
    return sorted(
        f"functions/{path.relative_to(root).as_posix()}"
        for path in root.rglob("*")
        if path.is_file()
    )


def build_receipt(
    data: dict[str, object], static_files: list[str], function_files: list[str]
) -> dict[str, object]:
    static_rows = [
        {
            "deployment_path": f"/{rel}",
            "source_path": rel,
            "sha256": sha256_file(DIST / rel),
        }
        for rel in static_files
    ]
    function_rows = [
        {
            "deployment_path": rel,
            "source_path": rel,
            "sha256": sha256_file(ROOT / rel),
        }
        for rel in function_files
    ]
    return {
        "schema": "nf-rel-002-public-artifact-manifest-v1",
        "baseline_sha": data["baseline_sha"],
        "allowlist_path": ALLOWLIST_PATH.relative_to(ROOT).as_posix(),
        "allowlist_sha256": sha256_file(ALLOWLIST_PATH),
        "static_file_count": len(static_rows),
        "pages_function_file_count": len(function_rows),
        "artifact_file_count": len(static_rows) + len(function_rows),
        "static_files": static_rows,
        "pages_functions": function_rows,
    }


def render_receipt(receipt: dict[str, object]) -> str:
    return json.dumps(receipt, indent=2, sort_keys=True) + "\n"


def verify_exact(
    data: dict[str, object], static_files: list[str], function_files: list[str]
) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    if not DIST.is_dir():
        errors.append("artifact directory is absent")
        return {}, errors

    actual_static = actual_files(DIST)
    if actual_static != static_files:
        missing = sorted(set(static_files) - set(actual_static))
        unexpected = sorted(set(actual_static) - set(static_files))
        errors.extend(f"missing static artifact path: {path}" for path in missing)
        errors.extend(f"unexpected static artifact path: {path}" for path in unexpected)

    actual_functions = function_files_on_disk()
    if actual_functions != function_files:
        missing = sorted(set(function_files) - set(actual_functions))
        unexpected = sorted(set(actual_functions) - set(function_files))
        errors.extend(f"missing Pages Function: {path}" for path in missing)
        errors.extend(f"unexpected Pages Function: {path}" for path in unexpected)

    if errors:
        return {}, errors

    receipt = build_receipt(data, static_files, function_files)
    expected_text = render_receipt(receipt)
    if not RECEIPT_PATH.is_file():
        errors.append(f"artifact manifest is absent: {RECEIPT_PATH.relative_to(ROOT)}")
    elif RECEIPT_PATH.read_text(encoding="utf-8") != expected_text:
        errors.append("artifact manifest content/hash set does not match exact artifact")
    return receipt, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("build", "verify"), required=True)
    args = parser.parse_args()

    try:
        data = load_allowlist()
        static_files, function_files = validate_source_files(data)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL public artifact allowlist: {exc}")
        return 1

    if args.mode == "build":
        if not DIST.is_dir():
            print("FAIL public artifact build: www-pages-dist must be recreated first")
            return 1
        if actual_files(DIST):
            print("FAIL public artifact build: www-pages-dist must start empty")
            return 1
        for rel in static_files:
            destination = DIST / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, destination)
        receipt = build_receipt(data, static_files, function_files)
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(render_receipt(receipt), encoding="utf-8")
        print(
            "build-public-www-artifact: "
            f"{len(static_files)} static + {len(function_files)} function files"
        )
        return 0

    receipt, errors = verify_exact(data, static_files, function_files)
    if errors:
        for error in errors:
            print(f"FAIL public artifact: {error}")
        return 1
    receipt_hash = sha256_file(RECEIPT_PATH)
    print(
        "verify-public-www-artifact: PASS "
        f"({receipt['artifact_file_count']} files, manifest_sha256={receipt_hash})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
