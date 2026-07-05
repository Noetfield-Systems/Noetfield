#!/usr/bin/env python3
"""Intake E2E — Telegram + DB PASS: submit test intake, telegram_delivered, Postgres dedupe."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from nf_factory_lib_v1 import iso_now, write_event, write_sina  # noqa: E402

USER_AGENT = "noetfield-intake-e2e/2.0"
SCHEMA_VERSION = "nf-intake-e2e-v2"
DEFAULT_PLATFORM_BASE = "https://platform.noetfield.com"
DEFAULT_WWW_BASE = "https://www.noetfield.com"


def make_request_id() -> str:
    return f"RID-E2E-{int(time.time())}"


def fetch_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    timeout: float = 25.0,
) -> tuple[int, dict[str, Any]]:
    data = None
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return int(resp.status), payload if isinstance(payload, dict) else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"detail": raw[:500]}
        return int(exc.code), payload if isinstance(payload, dict) else {"detail": raw[:500]}


def intake_health_url(base: str) -> str:
    return f"{base.rstrip('/')}/api/intake/health"


def e2e_intake_body(request_id: str) -> dict[str, Any]:
    return {
        "organization": "NF E2E Deploy Verify",
        "contact_name": "NF E2E Bot",
        "contact_email": "e2e@noetfield.com",
        "message": f"Automated intake E2E — {iso_now()}. Ignore.",
        "request_id": request_id,
        "sku": "general",
        "vector": "contact",
        "source": "api",
        "metadata": {
            "form_id": "nf_intake_e2e",
            "topic": "e2e",
            "async": True,
        },
    }


def skip_reason_for_target(*, intake_url: str, platform_base: str) -> str | None:
    platform_code, platform_health = fetch_json(intake_health_url(platform_base))
    if platform_code != 200:
        return f"platform_intake_health_unreachable:{platform_code}"
    if platform_health.get("storage") != "postgres":
        return "platform_intake_storage_not_postgres"

    parsed = urllib.parse.urlparse(intake_url)
    target_base = f"{parsed.scheme}://{parsed.netloc}"
    if target_base.rstrip("/") == platform_base.rstrip("/"):
        return None

    target_code, target_health = fetch_json(intake_health_url(target_base))
    if target_code != 200:
        return f"target_intake_health_unreachable:{target_code}"
    if not target_health.get("www_telegram_configured") and not target_health.get("ops_telegram_configured"):
        return "target_intake_telegram_not_configured"
    return None


def submit_test_intake(intake_url: str, body: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    code, payload = fetch_json(intake_url, method="POST", body=body, timeout=30.0)
    ok = 200 <= code < 300 and bool(payload.get("intake_id") or payload.get("ok"))
    return ok, {"http_status": code, **payload}


def verify_db_dedupe(
    intake_url: str,
    *,
    request_id: str,
    expected_intake_id: str,
    body: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    code, payload = fetch_json(intake_url, method="POST", body=body, timeout=30.0)
    got = str(payload.get("intake_id") or "")
    ok = 200 <= code < 300 and got == expected_intake_id
    return ok, {
        "http_status": code,
        "expected_intake_id": expected_intake_id,
        "dedupe_intake_id": got or None,
        "dedupe_ok": ok,
    }


def build_receipt(
    *,
    ok: bool,
    status: str,
    request_id: str,
    intake_url: str,
    platform_base: str,
    reason: str | None,
    submit: dict[str, Any] | None,
    dedupe: dict[str, Any] | None,
) -> dict[str, Any]:
    intake_id = ""
    telegram_delivered: bool | None = None
    if submit:
        intake_id = str(submit.get("intake_id") or "")
        if "telegram_delivered" in submit:
            telegram_delivered = bool(submit.get("telegram_delivered"))

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": iso_now(),
        "ok": ok,
        "status": status,
        "reason": reason,
        "request_id": request_id,
        "intake_id": intake_id or None,
        "telegram_delivered": telegram_delivered,
        "intake_url": intake_url,
        "platform_base": platform_base,
        "pass_definition": "telegram_delivered_and_db_dedupe",
        "submit": submit,
        "dedupe": dedupe,
    }


def write_receipt(receipt: dict[str, Any]) -> None:
    write_event("nf-intake-e2e-v1.json", receipt, ROOT)
    write_sina("nf-intake-e2e-v1.json", receipt)


def run_e2e(
    *,
    intake_url: str,
    platform_base: str,
    force: bool,
) -> dict[str, Any]:
    request_id = make_request_id()
    body = e2e_intake_body(request_id)

    if not force:
        skip = skip_reason_for_target(intake_url=intake_url, platform_base=platform_base)
        if skip:
            receipt = build_receipt(
                ok=True,
                status="skipped",
                request_id=request_id,
                intake_url=intake_url,
                platform_base=platform_base,
                reason=skip,
                submit=None,
                dedupe=None,
            )
            write_receipt(receipt)
            return receipt

    submit_ok, submit_payload = submit_test_intake(intake_url, body)
    intake_id = str(submit_payload.get("intake_id") or "")
    telegram_ok = bool(submit_payload.get("telegram_delivered"))

    if not submit_ok:
        receipt = build_receipt(
            ok=False,
            status="fail",
            request_id=request_id,
            intake_url=intake_url,
            platform_base=platform_base,
            reason="intake_submit_failed",
            submit=submit_payload,
            dedupe=None,
        )
        write_receipt(receipt)
        return receipt

    if not telegram_ok:
        receipt = build_receipt(
            ok=False,
            status="fail",
            request_id=request_id,
            intake_url=intake_url,
            platform_base=platform_base,
            reason="telegram_not_delivered",
            submit=submit_payload,
            dedupe=None,
        )
        write_receipt(receipt)
        return receipt

    dedupe_ok, dedupe_payload = verify_db_dedupe(
        intake_url,
        request_id=request_id,
        expected_intake_id=intake_id,
        body=body,
    )
    if not dedupe_ok:
        receipt = build_receipt(
            ok=False,
            status="fail",
            request_id=request_id,
            intake_url=intake_url,
            platform_base=platform_base,
            reason="db_dedupe_failed",
            submit=submit_payload,
            dedupe=dedupe_payload,
        )
        write_receipt(receipt)
        return receipt

    receipt = build_receipt(
        ok=True,
        status="pass",
        request_id=request_id,
        intake_url=intake_url,
        platform_base=platform_base,
        reason=None,
        submit=submit_payload,
        dedupe=dedupe_payload,
    )
    write_receipt(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Intake E2E — telegram_delivered + Postgres dedupe (PASS definition v2)"
    )
    parser.add_argument("--intake-url", default="", help="POST target (default: {www}/api/intake)")
    parser.add_argument("--www-base", default=DEFAULT_WWW_BASE, help="WWW base when --intake-url omitted")
    parser.add_argument("--platform-base", default=DEFAULT_PLATFORM_BASE)
    parser.add_argument("--force", action="store_true", help="Run even when telegram/storage prechecks fail")
    parser.add_argument("--json", action="store_true", help="Print receipt JSON to stdout")
    args = parser.parse_args()

    intake_url = (args.intake_url or "").strip() or f"{args.www_base.rstrip('/')}/api/intake"
    receipt = run_e2e(
        intake_url=intake_url,
        platform_base=args.platform_base.rstrip("/"),
        force=args.force,
    )

    if args.json:
        print(json.dumps(receipt, indent=2))
    elif receipt["status"] == "skipped":
        print(f"nf_intake_e2e: SKIP reason={receipt.get('reason')}")
    elif receipt["ok"]:
        print(
            "nf_intake_e2e: PASS "
            f"request_id={receipt.get('request_id')} "
            f"intake_id={receipt.get('intake_id')} "
            f"telegram_delivered=true db_dedupe=true"
        )
    else:
        print(
            f"nf_intake_e2e: FAIL reason={receipt.get('reason')} "
            f"request_id={receipt.get('request_id')}",
            file=sys.stderr,
        )

    if receipt["status"] == "skipped":
        return 0
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
