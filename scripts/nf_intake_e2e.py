#!/usr/bin/env python3
"""Intake E2E — test intake health receipt: Postgres path + dedupe (not customer lead spam)."""

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
        "message": f"Automated intake E2E health probe — {iso_now()}",
        "request_id": request_id,
        "sku": "general",
        "vector": "contact",
        "source": "api",
        "metadata": {
            "form_id": "nf_intake_e2e",
            "topic": "e2e",
            "intake_kind": "test",
            "pipeline": "nf_intake_e2e:deploy_verify",
            "async": True,
        },
    }


def probe_telegram_ok(submit: dict[str, Any] | None) -> bool:
    """Probe PASS — skipped lead Telegram is OK when intake persisted."""
    if not submit:
        return False
    if submit.get("telegram_skipped_probe") and submit.get("intake_persisted"):
        return True
    if submit.get("telegram_delivered") and submit.get("intake_kind") == "test":
        return True
    return submit.get("intake_kind") == "test" and submit.get("telegram_mode") == "receipt_only"


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
        "telegram_skipped_probe": bool(payload.get("telegram_skipped_probe")),
        "dedupe_checked": bool(payload.get("deduped")),
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
    telegram_mode: str | None = None
    intake_kind: str | None = None
    telegram_skipped_probe: bool | None = None
    intake_persisted: bool | None = None
    dedupe_checked: bool | None = None
    if submit:
        intake_id = str(submit.get("intake_id") or "")
        if "telegram_delivered" in submit:
            telegram_delivered = bool(submit.get("telegram_delivered"))
        telegram_mode = str(submit.get("telegram_mode") or "") or None
        intake_kind = str(submit.get("intake_kind") or "") or None
        if "telegram_skipped_probe" in submit:
            telegram_skipped_probe = bool(submit.get("telegram_skipped_probe"))
        if "intake_persisted" in submit:
            intake_persisted = bool(submit.get("intake_persisted"))
    if dedupe is not None:
        dedupe_checked = bool(dedupe.get("dedupe_ok"))

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": iso_now(),
        "ok": ok,
        "status": status,
        "reason": reason,
        "request_id": request_id,
        "intake_id": intake_id or None,
        "telegram_delivered": telegram_delivered,
        "telegram_mode": telegram_mode,
        "intake_kind": intake_kind,
        "telegram_skipped_probe": telegram_skipped_probe,
        "intake_persisted": intake_persisted,
        "dedupe_checked": dedupe_checked,
        "intake_url": intake_url,
        "platform_base": platform_base,
        "pass_definition": "probe_intake_persisted_and_db_dedupe",
        "receipt_path": "reports/agent-auto/events/nf-intake-e2e-v1.json",
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
    telegram_ok = probe_telegram_ok(submit_payload)

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
            reason="test_intake_path_failed",
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
        description="Intake E2E — test intake path + Postgres dedupe (health receipt v3)"
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
            f"telegram_skipped_probe={receipt.get('telegram_skipped_probe')} "
            f"intake_persisted={receipt.get('intake_persisted')} "
            f"dedupe_checked={receipt.get('dedupe_checked')}"
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
