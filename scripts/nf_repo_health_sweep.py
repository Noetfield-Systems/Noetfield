#!/usr/bin/env python3
"""Daily repo health sweep — findings → public.improvement_queue (no report files)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from nf_improvement_queue_enqueue import enqueue_rows  # noqa: E402

SOURCE = "github:repo-health-daily"
RUN_ID = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(label: str, cmd: list[str], *, cwd: Path | None = None) -> tuple[bool, str]:
    result = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    out = (result.stdout or "") + (result.stderr or "")
    detail = out.strip().splitlines()
    tail = detail[-1] if detail else f"exit {result.returncode}"
    if result.returncode != 0:
        return False, f"{label}: {tail}"[:2000]
    return True, f"{label}: ok"


def collect_findings() -> list[dict]:
    findings: list[dict] = []
    checks = [
        (["make", "validate"], "compile_and_whitespace", "repo_stability", True),
        (["python3", "scripts/check_repo_policy.py"], "repo_policy", "policy_compliance", True),
        (
            ["python3", "-m", "pytest", "tests/unit", "-q", "--tb=line"],
            "unit_tests",
            "regression_safety",
            False,
        ),
    ]
    for cmd, check_id, roi, machine_safe in checks:
        ok, detail = run_cmd(check_id, cmd)
        if not ok:
            findings.append(
                {
                    "finding": detail,
                    "source": f"{SOURCE}:{check_id}",
                    "expected_roi": roi,
                    "machine_safe": machine_safe,
                    "status": "open",
                    "metadata": {
                        "sweep": "repo-health-daily",
                        "run_id": RUN_ID,
                        "check_id": check_id,
                        "command": " ".join(cmd),
                    },
                }
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = collect_findings()
    if args.dry_run:
        print(json.dumps({"findings": rows, "count": len(rows)}, indent=2))
        return 0

    count = enqueue_rows(rows) if rows else 0
    summary = {"sweep": SOURCE, "run_id": RUN_ID, "findings": len(rows), "enqueued": count}
    if args.json:
        print(json.dumps(summary))
    else:
        print(
            f"nf_repo_health_sweep: findings={len(rows)} enqueued={count} run_id={RUN_ID}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
