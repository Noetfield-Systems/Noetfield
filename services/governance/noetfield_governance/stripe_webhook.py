"""Stripe commercial billing webhooks.

This module handles Noetfield's own software and professional-service sales only.
It does not process payments for third parties, custody funds, or move money.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Protocol

import asyncpg

from noetfield_config import CANONICAL_INTAKE_EMAIL

logger = logging.getLogger("noetfield.governance.stripe")

CHECKOUT_EVENTS = {
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
}
INVOICE_EVENTS = {
    "invoice.finalized",
    "invoice.paid",
    "invoice.payment_failed",
    "invoice.voided",
    "invoice.marked_uncollectible",
}
SUPPORTED_EVENTS = CHECKOUT_EVENTS | INVOICE_EVENTS


def _secret(value: object | None) -> str:
    if value is None:
        return ""
    getter = getattr(value, "get_secret_value", None)
    if callable(getter):
        return str(getter() or "").strip()
    return str(value).strip()


def verify_stripe_signature(payload: bytes, sig_header: str, secret: str) -> bool:
    """Verify the exact raw request body using Stripe's official SDK."""
    if not secret or not sig_header:
        return False
    try:
        import stripe  # type: ignore[import-untyped]

        stripe.Webhook.construct_event(payload, sig_header, secret)
        return True
    except Exception as exc:
        logger.warning("stripe_signature_invalid error_type=%s", type(exc).__name__)
        return False


class StripeWebhookEventStore(Protocol):
    async def reserve(self, event_id: str, event_type: str, object_id: str) -> bool: ...
    async def mark_processed(self, event_id: str) -> None: ...
    async def mark_failed(self, event_id: str, error: str) -> None: ...


class InMemoryStripeWebhookEventStore:
    """Test/local-only event receipt store. Production must use PostgreSQL."""

    def __init__(self) -> None:
        self._statuses: dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def reserve(self, event_id: str, event_type: str, object_id: str) -> bool:
        async with self._lock:
            status = self._statuses.get(event_id)
            if status in {"processing", "processed"}:
                return False
            self._statuses[event_id] = "processing"
            return True

    async def mark_processed(self, event_id: str) -> None:
        async with self._lock:
            self._statuses[event_id] = "processed"

    async def mark_failed(self, event_id: str, error: str) -> None:
        async with self._lock:
            self._statuses[event_id] = "failed"


class PostgresStripeWebhookEventStore:
    """Durable event de-duplication with a short lease for crashed workers."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._database_url)

    async def reserve(self, event_id: str, event_type: str, object_id: str) -> bool:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            inserted = await connection.fetchval(
                """
                insert into noetfield.stripe_webhook_events
                  (stripe_event_id, event_type, stripe_object_id, status, attempts)
                values ($1, $2, $3, 'processing', 1)
                on conflict (stripe_event_id) do nothing
                returning stripe_event_id
                """,
                event_id,
                event_type,
                object_id,
            )
            if inserted:
                return True
            reclaimed = await connection.fetchval(
                """
                update noetfield.stripe_webhook_events
                set status = 'processing',
                    attempts = attempts + 1,
                    updated_at = now(),
                    last_error = null
                where stripe_event_id = $1
                  and (
                    status = 'failed'
                    or (status = 'processing' and updated_at < now() - interval '5 minutes')
                  )
                returning stripe_event_id
                """,
                event_id,
            )
            return bool(reclaimed)

    async def mark_processed(self, event_id: str) -> None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                update noetfield.stripe_webhook_events
                set status = 'processed', processed_at = now(), updated_at = now(),
                    last_error = null
                where stripe_event_id = $1
                """,
                event_id,
            )

    async def mark_failed(self, event_id: str, error: str) -> None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                update noetfield.stripe_webhook_events
                set status = 'failed', updated_at = now(), last_error = $2
                where stripe_event_id = $1
                """,
                event_id,
                error[:1000],
            )


_WEBHOOK_STORES: dict[str, StripeWebhookEventStore] = {}
_MEMORY_WEBHOOK_STORE = InMemoryStripeWebhookEventStore()


def _event_store_for(settings: object) -> StripeWebhookEventStore:
    mode = str(getattr(settings, "runtime_event_store", "memory") or "memory").lower()
    database_url = str(getattr(settings, "database_url", "") or "").strip()
    if mode != "postgres" or not database_url:
        return _MEMORY_WEBHOOK_STORE
    if database_url not in _WEBHOOK_STORES:
        _WEBHOOK_STORES[database_url] = PostgresStripeWebhookEventStore(database_url)
    return _WEBHOOK_STORES[database_url]


def parse_checkout_completed(event: dict[str, Any]) -> dict[str, str] | None:
    if event.get("type") not in CHECKOUT_EVENTS:
        return None
    obj = event.get("data", {}).get("object") or {}
    if not isinstance(obj, dict):
        return None
    payment_status = str(obj.get("payment_status") or "")
    if payment_status not in {"paid", "no_payment_required"}:
        return None
    customer_details = obj.get("customer_details")
    customer_details = customer_details if isinstance(customer_details, dict) else {}
    metadata = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    return {
        "session_id": str(obj.get("id") or ""),
        "customer_id": str(obj.get("customer") or ""),
        "customer_email": str(customer_details.get("email") or obj.get("customer_email") or ""),
        "amount_total": str(obj.get("amount_total") if obj.get("amount_total") is not None else ""),
        "currency": str(obj.get("currency") or "usd").upper(),
        "sku": str(metadata.get("gtm_sku") or metadata.get("sku") or "commercial_license"),
        "payment_status": payment_status,
    }


def parse_invoice_event(event: dict[str, Any]) -> dict[str, str] | None:
    if event.get("type") not in INVOICE_EVENTS:
        return None
    obj = event.get("data", {}).get("object") or {}
    if not isinstance(obj, dict):
        return None
    customer_details = obj.get("customer_details")
    customer_details = customer_details if isinstance(customer_details, dict) else {}
    customer_email = str(customer_details.get("email") or obj.get("customer_email") or "")
    metadata = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    return {
        "invoice_id": str(obj.get("id") or ""),
        "invoice_number": str(obj.get("number") or ""),
        "customer_id": str(obj.get("customer") or ""),
        "customer_email": customer_email,
        "amount_due": str(obj.get("amount_due") if obj.get("amount_due") is not None else ""),
        "amount_paid": str(obj.get("amount_paid") if obj.get("amount_paid") is not None else ""),
        "currency": str(obj.get("currency") or "usd").upper(),
        "status": str(obj.get("status") or ""),
        "hosted_invoice_url": str(obj.get("hosted_invoice_url") or ""),
        "sku": str(metadata.get("gtm_sku") or metadata.get("sku") or ""),
    }


def notify_stripe_checkout(settings: object, details: dict[str, str]) -> bool:
    from noetfield_governance.intake_notify import send_intake_email

    inbox = getattr(settings, "intake_email_to", None) or CANONICAL_INTAKE_EMAIL
    inbox = str(inbox).strip() or CANONICAL_INTAKE_EMAIL
    subject = f"Noetfield — Stripe checkout · {details.get('sku', 'license')}"
    body = (
        "Stripe commercial license checkout completed.\n\n"
        f"session_id: {details.get('session_id', '')}\n"
        f"sku: {details.get('sku', '')}\n"
        f"customer_id: {details.get('customer_id', '')}\n"
        f"customer_email: {details.get('customer_email', '')}\n"
        f"amount_total: {details.get('amount_total', '')} {details.get('currency', '')}\n\n"
        "Reply to customer from operations@ with onboarding and intake link.\n"
        "Commercial licensing only — no custody or payment execution.\n"
    )
    customer = details.get("customer_email", "").strip()
    return send_intake_email(
        settings,
        to_addrs=[inbox],
        subject=subject,
        text=body,
        reply_to=customer or None,
    )


def notify_stripe_invoice(settings: object, details: dict[str, str], event_type: str) -> bool:
    from noetfield_governance.intake_notify import send_intake_email

    inbox = getattr(settings, "intake_email_to", None) or CANONICAL_INTAKE_EMAIL
    inbox = str(inbox).strip() or CANONICAL_INTAKE_EMAIL
    subject = f"Noetfield — Stripe invoice {event_type.removeprefix('invoice.')}"
    amount = details.get("amount_paid") if event_type == "invoice.paid" else details.get("amount_due")
    lines = [
        "Stripe invoice lifecycle event.",
        "",
        f"event: {event_type}",
        f"invoice_id: {details.get('invoice_id', '')}",
        f"invoice_number: {details.get('invoice_number', '')}",
        f"status: {details.get('status', '')}",
        f"sku: {details.get('sku', '')}",
        f"customer_id: {details.get('customer_id', '')}",
        f"customer_email: {details.get('customer_email', '')}",
        f"amount: {amount or ''} {details.get('currency', '')}",
    ]
    if details.get("hosted_invoice_url"):
        lines.extend(["", f"hosted_invoice_url: {details['hosted_invoice_url']}"])
    lines.extend(["", "Noetfield commercial receivable only; reconcile against Stripe before marking internal records paid."])
    return send_intake_email(
        settings,
        to_addrs=[inbox],
        subject=subject,
        text="\n".join(lines),
        reply_to=details.get("customer_email") or None,
    )


async def handle_stripe_webhook(
    settings: object,
    payload: bytes,
    sig_header: str,
    event_store: StripeWebhookEventStore | None = None,
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

    event_type = str(event.get("type") or "")
    if event_type not in SUPPORTED_EVENTS:
        return {"ok": True, "handled": False, "type": event_type}
    event_id = str(event.get("id") or "").strip()
    obj = event.get("data", {}).get("object") or {}
    object_id = str(obj.get("id") or "") if isinstance(obj, dict) else ""
    if not event_id:
        return {"ok": False, "error": "missing_event_id"}

    store = event_store or _event_store_for(settings)
    reserved = await store.reserve(event_id, event_type, object_id)
    if not reserved:
        logger.info("stripe_webhook_duplicate event_id=%s event_type=%s", event_id, event_type)
        return {"ok": True, "handled": False, "duplicate": True, "event_id": event_id}

    try:
        checkout = parse_checkout_completed(event)
        if checkout:
            emailed = notify_stripe_checkout(settings, checkout)
            await store.mark_processed(event_id)
            logger.info(
                "stripe_checkout_completed event_id=%s session=%s sku=%s emailed=%s",
                event_id,
                checkout.get("session_id"),
                checkout.get("sku"),
                emailed,
            )
            return {
                "ok": True,
                "handled": True,
                "event_id": event_id,
                "emailed": emailed,
                "session_id": checkout.get("session_id"),
            }

        invoice = parse_invoice_event(event)
        if invoice:
            emailed = notify_stripe_invoice(settings, invoice, event_type)
            await store.mark_processed(event_id)
            logger.info(
                "stripe_invoice_event event_id=%s invoice=%s type=%s emailed=%s",
                event_id,
                invoice.get("invoice_id"),
                event_type,
                emailed,
            )
            return {
                "ok": True,
                "handled": True,
                "event_id": event_id,
                "emailed": emailed,
                "invoice_id": invoice.get("invoice_id"),
                "type": event_type,
            }

        await store.mark_processed(event_id)
        return {"ok": True, "handled": False, "event_id": event_id, "type": event_type}
    except Exception as exc:
        try:
            await store.mark_failed(event_id, f"{type(exc).__name__}: {exc}")
        except Exception:
            logger.exception("stripe_webhook_mark_failed_error event_id=%s", event_id)
        raise
