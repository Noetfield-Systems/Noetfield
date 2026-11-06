"""Stripe Live commercial licensing webhooks with durable idempotency."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import UTC, datetime
from typing import Any

from noetfield_config import CANONICAL_INTAKE_EMAIL

logger = logging.getLogger("noetfield.governance.stripe")

_SUPPORTED_EVENTS = {
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
    "checkout.session.async_payment_failed",
    "invoice.payment_failed",
    "charge.refunded",
    "charge.dispute.created",
    "charge.dispute.closed",
    "charge.dispute.funds_withdrawn",
    "charge.dispute.funds_reinstated",
    "radar.early_fraud_warning.created",
}


def _secret(value: object | None) -> str:
    if value is None:
        return ""
    getter = getattr(value, "get_secret_value", None)
    if callable(getter):
        return str(getter() or "").strip()
    return str(value).strip()


def verify_stripe_signature(
    payload: bytes,
    sig_header: str,
    secret: str,
    *,
    tolerance_seconds: int = 300,
    now: int | None = None,
) -> bool:
    """Verify Stripe's v1 signature over the exact raw request body."""
    if not secret or not payload or not sig_header:
        return False
    timestamp = ""
    signatures: list[str] = []
    for part in sig_header.split(","):
        key, separator, value = part.strip().partition("=")
        if not separator:
            continue
        if key == "t":
            timestamp = value
        elif key == "v1":
            signatures.append(value)
    try:
        signed_at = int(timestamp)
    except (TypeError, ValueError):
        return False
    current_time = int(time.time()) if now is None else int(now)
    if abs(current_time - signed_at) > max(0, tolerance_seconds):
        return False
    signed_payload = str(signed_at).encode("ascii") + b"." + payload
    expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, candidate) for candidate in signatures)


def _money(amount: object, currency: object) -> str:
    try:
        value = int(amount) / 100
    except (TypeError, ValueError):
        return "not supplied"
    code = str(currency or "usd").upper()
    return f"{value:,.2f} {code}"


def _base_details(event: dict[str, Any], obj: dict[str, Any]) -> dict[str, str]:
    metadata = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    customer_details = (
        obj.get("customer_details") if isinstance(obj.get("customer_details"), dict) else {}
    )
    return {
        "event_id": str(event.get("id") or ""),
        "event_type": str(event.get("type") or ""),
        "livemode": str(bool(event.get("livemode"))).lower(),
        "object_id": str(obj.get("id") or ""),
        "sku": str(metadata.get("gtm_sku") or metadata.get("sku") or "commercial_license"),
        "customer_id": str(obj.get("customer") or ""),
        "customer_email": str(
            customer_details.get("email")
            or obj.get("customer_email")
            or obj.get("receipt_email")
            or ""
        ),
    }


def parse_stripe_event(event: dict[str, Any]) -> dict[str, str] | None:
    """Return a bounded internal notification record for supported commercial events."""
    event_type = str(event.get("type") or "")
    if event_type not in _SUPPORTED_EVENTS:
        return None
    data = event.get("data") if isinstance(event.get("data"), dict) else {}
    obj = data.get("object") if isinstance(data.get("object"), dict) else {}
    details = _base_details(event, obj)

    if event_type in {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
        "checkout.session.async_payment_failed",
    }:
        payment_status = str(obj.get("payment_status") or "")
        if event_type == "checkout.session.completed" and payment_status not in {
            "paid",
            "no_payment_required",
        }:
            # Do not call an asynchronous or unpaid Checkout session a sale.
            return None
        is_failure = event_type == "checkout.session.async_payment_failed"
        details.update(
            {
                "kind": "payment_failure" if is_failure else "payment",
                "payment_status": "failed" if is_failure else payment_status or "paid",
                "amount": _money(obj.get("amount_total"), obj.get("currency")),
                "payment_link_id": str(obj.get("payment_link") or ""),
                "failure_reason": str(obj.get("last_payment_error", {}).get("message") or "")
                if isinstance(obj.get("last_payment_error"), dict)
                else "",
            }
        )
        return details

    if event_type == "invoice.payment_failed":
        details.update(
            {
                "kind": "invoice_failure",
                "amount": _money(obj.get("amount_due"), obj.get("currency")),
                "invoice_number": str(obj.get("number") or ""),
                "hosted_invoice_url": str(obj.get("hosted_invoice_url") or ""),
                "failure_reason": str(obj.get("last_finalization_error", {}).get("message") or "")
                if isinstance(obj.get("last_finalization_error"), dict)
                else "",
            }
        )
        return details

    if event_type == "charge.refunded":
        details.update(
            {
                "kind": "refund",
                "amount": _money(obj.get("amount_refunded"), obj.get("currency")),
                "payment_intent": str(obj.get("payment_intent") or ""),
                "risk_status": "refunded",
                "reason": str(obj.get("failure_message") or ""),
            }
        )
        return details

    if event_type.startswith("charge.dispute."):
        evidence = obj.get("evidence_details") if isinstance(obj.get("evidence_details"), dict) else {}
        due_by = evidence.get("due_by")
        details.update(
            {
                "kind": "dispute",
                "amount": _money(obj.get("amount"), obj.get("currency")),
                "payment_intent": str(obj.get("payment_intent") or ""),
                "charge_id": str(obj.get("charge") or ""),
                "risk_status": str(obj.get("status") or ""),
                "reason": str(obj.get("reason") or ""),
                "evidence_due_by": (
                    datetime.fromtimestamp(int(due_by), tz=UTC).isoformat()
                    if due_by
                    else ""
                ),
            }
        )
        return details

    details.update(
        {
            "kind": "early_fraud_warning",
            "amount": _money(obj.get("fraudulent_amount") or obj.get("amount"), obj.get("currency")),
            "charge_id": str(obj.get("charge") or ""),
            "risk_status": str(obj.get("actionable") or ""),
            "reason": str(obj.get("fraud_type") or ""),
        }
    )
    return details


def parse_checkout_completed(event: dict[str, Any]) -> dict[str, str] | None:
    """Backward-compatible checkout parser used by the public API tests."""
    details = parse_stripe_event(event)
    if not details or details.get("kind") != "payment":
        return None
    return {
        "session_id": details.get("object_id", ""),
        "customer_email": details.get("customer_email", ""),
        "amount_total": str(
            (event.get("data", {}).get("object") or {}).get("amount_total") or ""
        ),
        "currency": str(
            (event.get("data", {}).get("object") or {}).get("currency") or "usd"
        ).upper(),
        "sku": details.get("sku", "commercial_license"),
    }


def notify_stripe_event(settings: object, details: dict[str, str]) -> bool:
    from noetfield_governance.intake_notify import send_intake_email

    inbox = getattr(settings, "intake_email_to", None) or CANONICAL_INTAKE_EMAIL
    inbox = str(inbox).strip() or CANONICAL_INTAKE_EMAIL
    kind = details.get("kind", "event")
    labels = {
        "payment": "PAYMENT RECEIVED",
        "payment_failure": "PAYMENT FAILED",
        "invoice_failure": "INVOICE PAYMENT FAILED",
        "refund": "REFUND",
        "dispute": "DISPUTE / CHARGEBACK",
        "early_fraud_warning": "EARLY FRAUD WARNING",
    }
    subject = f"Noetfield — Stripe {labels.get(kind, 'EVENT')} · {details.get('sku', 'license')}"
    lines = [
        f"Stripe Live commercial event: {labels.get(kind, kind)}",
        "",
        f"event_id: {details.get('event_id', '')}",
        f"event_type: {details.get('event_type', '')}",
        f"livemode: {details.get('livemode', '')}",
        f"object_id: {details.get('object_id', '')}",
        f"sku: {details.get('sku', '')}",
        f"customer_email: {details.get('customer_email', '')}",
        f"amount: {details.get('amount', 'not supplied')}",
        f"status: {details.get('payment_status') or details.get('risk_status', '')}",
    ]
    for key in ("payment_link_id", "invoice_number", "hosted_invoice_url", "payment_intent",
                "charge_id", "reason", "failure_reason", "evidence_due_by"):
        value = details.get(key, "")
        if value:
            lines.append(f"{key}: {value}")
    lines.extend(
        [
            "",
            "Operations action: reconcile this event in Stripe Dashboard before changing access,",
            "accounting, or customer status. This notification is not a receipt or fulfillment event.",
            "Commercial licensing only — no custody or payment execution.",
        ]
    )
    return send_intake_email(
        settings,
        to_addrs=[inbox],
        subject=subject,
        text="\n".join(lines),
        reply_to=details.get("customer_email") or None,
    )


def notify_stripe_checkout(settings: object, details: dict[str, str]) -> bool:
    """Backward-compatible notifier for checkout completion."""
    return notify_stripe_event(
        settings,
        {
            "event_id": details.get("session_id", ""),
            "event_type": "checkout.session.completed",
            "livemode": "true",
            "object_id": details.get("session_id", ""),
            "sku": details.get("sku", "commercial_license"),
            "customer_email": details.get("customer_email", ""),
            "kind": "payment",
            "payment_status": "paid",
            "amount": _money(details.get("amount_total"), details.get("currency")),
        },
    )


async def _claim_event(
    settings: object,
    event: dict[str, Any],
    payload: bytes,
) -> tuple[bool, str]:
    database_url = _secret(getattr(settings, "database_url", None))
    if not database_url:
        return False, "database_not_configured"
    import asyncpg

    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    event_id = str(event.get("id") or "")
    event_type = str(event.get("type") or "")
    if not event_id:
        return False, "event_id_missing"
    digest = hashlib.sha256(payload).hexdigest()
    connection = await asyncpg.connect(database_url)
    try:
        row = await connection.fetchrow(
            """
            insert into noetfield.stripe_webhook_events
                (event_id, event_type, livemode, payload_sha256, status, attempts)
            values ($1, $2, $3, $4, 'processing', 1)
            on conflict (event_id) do update
            set status = 'processing',
                attempts = noetfield.stripe_webhook_events.attempts + 1,
                payload_sha256 = excluded.payload_sha256,
                updated_at = now(),
                last_error = null
            where noetfield.stripe_webhook_events.status in ('received', 'failed')
               or (
                    noetfield.stripe_webhook_events.status = 'processing'
                    and noetfield.stripe_webhook_events.updated_at < now() - interval '10 minutes'
               )
            returning event_id
            """,
            event_id,
            event_type,
            bool(event.get("livemode")),
            digest,
        )
        return row is not None, event_id
    finally:
        await connection.close()


async def _finish_event(
    settings: object,
    event_id: str,
    *,
    status: str,
    error: str | None = None,
) -> None:
    database_url = _secret(getattr(settings, "database_url", None))
    import asyncpg

    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    connection = await asyncpg.connect(database_url)
    try:
        await connection.execute(
            """
            update noetfield.stripe_webhook_events
            set status = $2,
                last_error = $3,
                processed_at = case when $2 = 'processed' then now() else processed_at end,
                updated_at = now()
            where event_id = $1
            """,
            event_id,
            status,
            error,
        )
    finally:
        await connection.close()


async def handle_stripe_webhook(
    settings: object,
    payload: bytes,
    sig_header: str,
) -> dict[str, object]:
    secret = _secret(getattr(settings, "stripe_webhook_secret", None))
    if not secret:
        return {"ok": False, "error": "stripe_webhook_not_configured"}
    if not verify_stripe_signature(payload, sig_header, secret):
        return {"ok": False, "error": "invalid_signature"}
    try:
        event = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"ok": False, "error": "invalid_payload"}
    if not isinstance(event, dict):
        return {"ok": False, "error": "invalid_payload"}
    details = parse_stripe_event(event)
    if not details:
        return {"ok": True, "handled": False, "type": event.get("type")}

    try:
        claimed, event_id = await _claim_event(settings, event, payload)
    except Exception:
        logger.exception("stripe_webhook_store_unavailable")
        return {"ok": False, "error": "store_unavailable"}
    if not claimed:
        return {"ok": True, "handled": False, "duplicate": True, "event_id": event_id}

    emailed = await asyncio.to_thread(notify_stripe_event, settings, details)
    if not emailed:
        try:
            await _finish_event(settings, event_id, status="failed", error="operations_email_failed")
        except Exception:
            logger.exception("stripe_webhook_event_failure_state_unavailable event_id=%s", event_id)
        return {"ok": False, "error": "notification_failed", "event_id": event_id}

    try:
        await _finish_event(settings, event_id, status="processed")
    except Exception:
        # A duplicate notification on retry is preferable to losing a payment alert,
        # but the event remains visible as processing and is reconciled by event_id.
        logger.exception("stripe_webhook_event_completion_failed event_id=%s", event_id)
        return {"ok": False, "error": "store_unavailable", "event_id": event_id}

    logger.info(
        "stripe_event_processed event_id=%s type=%s sku=%s",
        event_id,
        details.get("event_type"),
        details.get("sku"),
    )
    return {"ok": True, "handled": True, "event_id": event_id, "emailed": emailed}
