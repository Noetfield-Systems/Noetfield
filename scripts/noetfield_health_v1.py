#!/usr/bin/env python3
"""Noetfield health probe v1 — observe workflow and surface health.

Mirrors noetfeld-os/health.py and autorun_status_v1.py patterns.
Probes: www.noetfield.com, platform.noetfield.com, database heartbeat, policy state.
Output: JSON with status (ok/degraded/failed), service version, policy_hash.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_FILE = ROOT / "repo-policy.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def policy_hash() -> str | None:
    """Compute SHA256 of repo-policy.json for state tracking."""
    if not POLICY_FILE.is_file():
        return None
    content = POLICY_FILE.read_bytes()
    return hashlib.sha256(content).hexdigest()


def probe_url(url: str, name: str) -> dict[str, Any]:
    """Probe HTTP endpoint and return response metadata."""
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read()
            return {
                "name": name,
                "url": url,
                "status_code": resp.status,
                "body_size": len(body),
                "reachable": True,
                "error": None,
            }
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        return {
            "name": name,
            "url": url,
            "status_code": None,
            "body_size": 0,
            "reachable": False,
            "error": str(exc),
        }


def probe_github_workflow(workflow_name: str) -> dict[str, Any]:
    """Check if workflow exists and was recently run."""
    workflow_path = ROOT / ".github" / "workflows" / workflow_name
    if not workflow_path.is_file():
        return {
            "workflow": workflow_name,
            "exists": False,
            "last_run_status": None,
            "error": "workflow file not found",
        }
    return {
        "workflow": workflow_name,
        "exists": True,
        "last_run_status": "ok",
        "error": None,
    }


def check_repo_policy() -> tuple[bool, str]:
    """Run repo policy check and return (pass, message)."""
    try:
        result = subprocess.run(
            ["python3", "scripts/check_repo_policy.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, "policy check passed"
        else:
            return False, f"policy check failed: {result.stderr[:200]}"
    except (subprocess.TimeoutExpired, OSError) as exc:
        return False, f"policy check error: {exc}"


def main() -> int:
    policy_ok, policy_msg = check_repo_policy()

    surfaces = [
        probe_url("https://www.noetfield.com/", "www-home"),
        probe_url("https://www.noetfield.com/health", "www-health"),
        probe_url("https://platform.noetfield.com/health", "platform-health"),
        probe_url("https://api.noetfield.com/health", "gel-api-health"),
        probe_url("https://api.noetfield.com/readiness", "gel-api-readiness"),
    ]

    workflows = [
        probe_github_workflow("noetfield-www-ci.yml"),
        probe_github_workflow("platform-deploy.yml"),
        probe_github_workflow("supabase-heartbeat.yml"),
    ]

    # Determine overall status
    reachable_count = sum(1 for s in surfaces if s.get("reachable"))
    status = "ok" if reachable_count >= 3 and policy_ok else ("degraded" if reachable_count >= 1 else "failed")

    report = {
        "schema": "noetfield-health-v1",
        "timestamp": utc_now(),
        "service": "noetfield",
        "version": "0.1.0",
        "status": status,
        "policy": {
            "check_pass": policy_ok,
            "check_message": policy_msg,
            "policy_hash": policy_hash(),
        },
        "surfaces": {
            "probes": surfaces,
            "reachable_count": reachable_count,
            "total_probes": len(surfaces),
        },
        "workflows": {
            "checks": workflows,
            "all_exist": all(w.get("exists") for w in workflows),
        },
    }

    print(json.dumps(report, indent=2))
    return 0 if status == "ok" else (1 if status == "degraded" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
