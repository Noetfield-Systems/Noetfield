#!/usr/bin/env python3
"""Weekly security sweep — findings → public.improvement_queue (no report files)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from nf_improvement_queue_enqueue import enqueue_rows  # noqa: E402

SOURCE = "github:security-sweep-weekly"
RUN_ID = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("stripe_live", re.compile(r"sk_live_[0-9a-zA-Z]{16,}")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----")),
    ("github_pat", re.compile(r"ghp_[0-9a-zA-Z]{36,}")),
    ("vercel_token", re.compile(r"vercel_[a-z0-9_]{20,}", re.I)),
]

TRACKED_DENY_GLOBS = (
    ".env",
    ".env.local",
    ".env.production",
    "secrets.env",
    "*.pem",
    "*.p12",
)


def run_cmd(cmd: list[str], *, cwd: Path | None = None) -> tuple[int, str]:
    result = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, ((result.stdout or "") + (result.stderr or "")).strip()


def tracked_files() -> list[str]:
    code, out = run_cmd(["git", "ls-files"])
    if code != 0:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def scan_tracked_secrets() -> list[str]:
    findings: list[str] = []
    for rel in tracked_files():
        if any(Path(rel).match(glob) for glob in TRACKED_DENY_GLOBS):
            findings.append(f"tracked sensitive path: {rel}")
            continue
        path = ROOT / rel
        if not path.is_file() or path.stat().st_size > 500_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{label} pattern in tracked file: {rel}")
    return findings


def pip_audit_findings() -> list[str]:
    code, out = run_cmd(
        ["python3", "-m", "pip_audit", "-f", "json"],
    )
    if code != 0 and not out:
        return ["pip-audit: command failed or not installed"]
    try:
        rows = json.loads(out or "[]")
    except json.JSONDecodeError:
        return [f"pip-audit: unparsable output ({out[:200]})"]
    hits: list[str] = []
    for row in rows if isinstance(rows, list) else []:
        name = row.get("name") or row.get("dependency") or "unknown"
        vulns = row.get("vulns") or []
        for vuln in vulns[:3]:
            vid = vuln.get("id") or vuln.get("aliases", ["?"])[0]
            hits.append(f"pip vulnerability {name}: {vid}")
    return hits[:25]


def npm_audit_findings() -> list[str]:
    if not (ROOT / "package-lock.json").is_file():
        return []
    run_cmd(["npm", "ci", "--ignore-scripts"], cwd=ROOT)
    code, out = run_cmd(["npm", "audit", "--json"], cwd=ROOT)
    try:
        data = json.loads(out or "{}")
    except json.JSONDecodeError:
        return [f"npm audit: unparsable output ({out[:200]})"]
    advisories = (data.get("vulnerabilities") or {}) if isinstance(data, dict) else {}
    hits: list[str] = []
    for name, meta in advisories.items():
        severity = str(meta.get("severity") or "unknown")
        if severity in ("high", "critical", "moderate"):
            hits.append(f"npm {severity}: {name}")
    if code != 0 and not hits:
        hits.append("npm audit: nonzero exit with no parsed vulnerabilities")
    return hits[:25]


def collect_findings(*, skip_npm: bool) -> list[dict]:
    raw: list[tuple[str, str, str, bool]] = []

    for item in scan_tracked_secrets():
        raw.append((item, "tracked_secret_scan", "security_hygiene", False))

    for item in pip_audit_findings():
        raw.append((item, "pip_audit", "dependency_risk", True))

    if not skip_npm:
        for item in npm_audit_findings():
            raw.append((item, "npm_audit", "dependency_risk", True))

    rows: list[dict] = []
    for finding, check_id, roi, machine_safe in raw:
        rows.append(
            {
                "finding": finding[:8000],
                "source": f"{SOURCE}:{check_id}",
                "expected_roi": roi,
                "machine_safe": machine_safe,
                "status": "open",
                "metadata": {
                    "sweep": "security-sweep-weekly",
                    "run_id": RUN_ID,
                    "check_id": check_id,
                },
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-npm", action="store_true")
    args = parser.parse_args()

    rows = collect_findings(skip_npm=args.skip_npm)
    if args.dry_run:
        print(json.dumps({"findings": rows, "count": len(rows)}, indent=2))
        return 0

    count = enqueue_rows(rows) if rows else 0
    summary = {"sweep": SOURCE, "run_id": RUN_ID, "findings": len(rows), "enqueued": count}
    if args.json:
        print(json.dumps(summary))
    else:
        print(
            f"nf_security_sweep: findings={len(rows)} enqueued={count} run_id={RUN_ID}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
