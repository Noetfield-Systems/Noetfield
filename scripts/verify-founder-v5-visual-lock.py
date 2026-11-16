#!/usr/bin/env python3
"""Protect the Founder-approved PR #388 V5 visual against accidental design regression.

Compares *exact Git blobs*, not screenshots of a self-rewritten design. Commercial
ideas can be shipped on the relevant inner pages; the approved photographic
Homepage and its stylesheet cannot be silently replaced by another agent.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = ROOT / "config" / "noetfield-founder-v5-visual-lock.json"


def git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\x00"
    return hashlib.sha1(header + data).hexdigest()


def main() -> int:
    try:
        lock = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"FAIL founder-v5-visual-lock: invalid lock manifest: {exc}", file=sys.stderr)
        return 1
    if lock.get("status") != "LOCKED":
        print("FAIL founder-v5-visual-lock: lock must remain LOCKED", file=sys.stderr)
        return 1
    if lock.get("approved_visual_source", {}).get("commit_sha") != (
        "340fe2dec55819a997e8aeec60d52f33317a1894"
    ):
        print("FAIL founder-v5-visual-lock: V5 founder-approved reference changed", file=sys.stderr)
        return 1
    files = lock.get("protected_file_blobs")
    if not isinstance(files, list) or len(files) != 2:
        print("FAIL founder-v5-visual-lock: expected two approved visual artifacts", file=sys.stderr)
        return 1
    expected_paths = {"index.html", "assets/noetfield-institutional-v3.css"}
    if {entry.get("path") for entry in files} != expected_paths:
        print("FAIL founder-v5-visual-lock: locked file inventory changed", file=sys.stderr)
        return 1
    errors = []
    for item in files:
        relative = item["path"]
        file = ROOT / relative
        try:
            data = file.read_bytes()
        except OSError as exc:
            errors.append(f"{relative}: missing/unreadable: {exc}")
            continue
        actual = git_blob_sha1(data)
        expected = item["git_blob_sha1"]
        if actual != expected:
            errors.append(
                f"{relative}: visual-regression blob mismatch; "
                f"V5={expected} current={actual}"
            )
    if errors:
        print("FAIL founder-v5-visual-lock: Founder-approved photo-led PR #388 changed!", file=sys.stderr)
        for error in errors:
            print("  " + error, file=sys.stderr)
        print(
            "This is not a generic website-improvement task. Do not replace the "
            "approved Hero, imagery or CSS. Read "
            ".cursor/incidents/INCIDENT-2026-11-16-001-v5-visual-overwrite-and-growth-work-loss.md. "
            "Change the reference only after a specific Founder-directed visual amendment.",
            file=sys.stderr,
        )
        return 1
    print("PASS founder-v5-visual-lock: exact founder-approved V5 Homepage and CSS blobs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
