#!/usr/bin/env python3
"""Insert rows into public.improvement_queue via Supabase REST (no local reports)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def supabase_config() -> tuple[str, str]:
    url = (
        os.environ.get("NOETFIELD_SUPABASE_URL")
        or os.environ.get("SUPABASE_URL")
        or ""
    ).rstrip("/")
    key = (
        os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    )
    if not url or not key:
        raise RuntimeError(
            "NOETFIELD_SUPABASE_URL and NOETFIELD_SUPABASE_SERVICE_ROLE_KEY required"
        )
    return url, key


def enqueue_rows(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    base, key = supabase_config()
    payload = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/rest/v1/improvement_queue",
        data=payload,
        method="POST",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status not in (200, 201, 204):
                raise RuntimeError(f"supabase insert HTTP {resp.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"supabase insert failed HTTP {exc.code}: {detail}") from exc
    return len(rows)


def enqueue_finding(
    *,
    finding: str,
    source: str,
    expected_roi: str | None = None,
    machine_safe: bool = False,
    metadata: dict[str, Any] | None = None,
) -> int:
    row = {
        "finding": finding[:8000],
        "source": source[:200],
        "expected_roi": expected_roi,
        "machine_safe": bool(machine_safe),
        "status": "open",
        "metadata": metadata or {},
    }
    return enqueue_rows([row])


def main() -> int:
    parser = argparse.ArgumentParser(description="Enqueue improvement_queue row(s)")
    parser.add_argument("--finding", default="", help="Single finding text")
    parser.add_argument("--source", default="", help="Source label, e.g. repo-health-daily")
    parser.add_argument("--expected-roi", default="")
    parser.add_argument("--machine-safe", action="store_true")
    parser.add_argument("--json-file", default="", help="JSON array of row objects")
    parser.add_argument("--json", action="store_true", help="Print enqueue count JSON")
    args = parser.parse_args()

    if args.json_file:
        rows = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise SystemExit("json-file must contain an array")
        count = enqueue_rows(rows)
    elif args.finding and args.source:
        count = enqueue_finding(
            finding=args.finding,
            source=args.source,
            expected_roi=args.expected_roi or None,
            machine_safe=args.machine_safe,
        )
    else:
        parser.error("provide --finding + --source or --json-file")

    if args.json:
        print(json.dumps({"enqueued": count}))
    else:
        print(f"nf_improvement_queue_enqueue: enqueued={count}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
