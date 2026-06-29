#!/usr/bin/env python3
"""Verify the stored Noetfield live nerve receipt is fresh and scoped."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "governance" / "NOETFIELD_LIVE_NERVE_RECEIPT.json"
REQUIRED_STATUS = {"PASS", "DEGRADED", "FAIL"}


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_receipt() -> dict[str, Any]:
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def main() -> int:
    failures: list[str] = []
    receipt = load_receipt()

    if receipt.get("schema") != "noetfield-live-nerve-receipt-v1":
        failures.append("wrong receipt schema")
    if receipt.get("scope") != "website-platform-public":
        failures.append("receipt scope must be website-platform-public")
    if receipt.get("gate") not in REQUIRED_STATUS:
        failures.append("receipt gate must be PASS, DEGRADED, or FAIL")

    semantics = receipt.get("scope_semantics")
    if not isinstance(semantics, dict):
        failures.append("missing scope_semantics")
    else:
        status_language = semantics.get("status_language")
        if not isinstance(status_language, dict) or set(status_language) != REQUIRED_STATUS:
            failures.append("scope_semantics.status_language must define PASS, DEGRADED, FAIL")
        if semantics.get("ecosystem_green") is not False:
            failures.append("website receipt must not claim ecosystem_green=true")
        sourcea = semantics.get("sourcea_foundation_drift")
        if not isinstance(sourcea, dict) or sourcea.get("blocks_www_deploy") is not False:
            failures.append("SourceA foundation drift must be warning-only for www deploy")

    freshness = receipt.get("receipt_freshness")
    if not isinstance(freshness, dict):
        failures.append("missing receipt_freshness")
    else:
        expires_at = parse_time(freshness.get("expires_at"))
        generated_at = parse_time(freshness.get("generated_at"))
        valid_for = freshness.get("valid_for_seconds")
        if generated_at is None:
            failures.append("receipt_freshness.generated_at is invalid")
        if expires_at is None:
            failures.append("receipt_freshness.expires_at is invalid")
        elif datetime.now(timezone.utc) > expires_at:
            failures.append("live nerve receipt is expired; run make verify-live-nerve")
        if not isinstance(valid_for, int) or valid_for <= 0:
            failures.append("receipt_freshness.valid_for_seconds must be positive integer")

    nodes = receipt.get("nodes")
    if not isinstance(nodes, dict) or "N14_RECEIPT_FRESHNESS" not in nodes:
        failures.append("missing N14_RECEIPT_FRESHNESS node")

    if failures:
        print("verify-live-nerve-receipt: FAIL")
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print("verify-live-nerve-receipt: PASS")
    print(
        "scope={scope} gate={gate} expires_at={expires_at}".format(
            scope=receipt.get("scope"),
            gate=receipt.get("gate"),
            expires_at=receipt.get("receipt_freshness", {}).get("expires_at"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
