#!/usr/bin/env python3
"""Repo cleanliness verification v1 — track dirty count and triage threshold.

Mirrors noetfeld-os/autorun_sandboxes pattern.
Scans: git dirty files (untracked, modified, staged)
Threshold: > 30 files = escalate to triage_required
Output: JSON report with dirty count, file list, triage recommendation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRIAGE_THRESHOLD = 30


def run_cmd(cmd: list[str]) -> str:
    """Run shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return ""


def get_dirty_files() -> tuple[list[str], list[str], list[str]]:
    """Get untracked, modified, and staged files."""
    untracked = []
    modified = []
    staged = []

    # Untracked files
    output = run_cmd(["git", "ls-files", "--others", "--exclude-standard"])
    untracked = [f for f in output.splitlines() if f]

    # Modified (unstaged)
    output = run_cmd(["git", "diff", "--name-only"])
    modified = [f for f in output.splitlines() if f]

    # Staged
    output = run_cmd(["git", "diff", "--cached", "--name-only"])
    staged = [f for f in output.splitlines() if f]

    return untracked, modified, staged


def main() -> int:
    untracked, modified, staged = get_dirty_files()

    all_dirty = list(set(untracked + modified + staged))
    dirty_count = len(all_dirty)
    status = "TRIAGE_REQUIRED" if dirty_count > TRIAGE_THRESHOLD else "OK"

    report = {
        "schema": "repo-cleanliness-v1",
        "repo": str(ROOT),
        "dirty_count": dirty_count,
        "triage_threshold": TRIAGE_THRESHOLD,
        "status": status,
        "files": {
            "untracked": untracked,
            "modified": modified,
            "staged": staged,
        },
        "counts": {
            "untracked": len(untracked),
            "modified": len(modified),
            "staged": len(staged),
        },
        "recommendation": (
            f"ESCALATE: {dirty_count} files exceed threshold of {TRIAGE_THRESHOLD}. "
            "Run 'git status' and commit/stash before merging to main."
            if dirty_count > TRIAGE_THRESHOLD
            else f"OK: {dirty_count} files is within threshold."
        ),
    }

    print(json.dumps(report, indent=2))
    return 0 if status == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
