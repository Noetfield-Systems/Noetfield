"""Stripe commercial licensing webhooks — checkout.session.completed fulfillment."""

from __future__ import annotations

import json
import logging
from typing import Any

from noetfield_config import CANONICAL_INTAKE_EMAIL

logger = logging.getLogger("noetfield.governance.stripe")


def _secret(value: object | None) -> str:
    if value is None:
        return ""
    getter = getattr(value, "get_secret_value", None)
    if callable(getter):
        return str(getter() or "").strip()
    return str(value).strip()


def verify_stripe_signature(payload: bytes, sig_header: str, secret: str) -> bool:
    if not secret:
        return False
    try:
        import stripe  # type: ignore[import-untyped]

        stripe.Webhook.construct_event(payload, sig_header, secret)
        return True
    except Exception as exc:
        logger.warning("stripe_signature_invalid %s", exc)
        return False


def parse_checkout_completed(event: dict[str, Any]) -> dict[str, str] | None:
    if event.get("type") not in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
        return None
    obj = event.get("data", {}).get("object") or {}
    if not isinstance(obj, dict):
        return None
    session_id = str(obj.get("id") or "")
    customer_email = str(obj.get("customer_details", {}).get("email") or obj.get("customer_email") or "")
    amount = obj.get("amount_total")
    currency = str(obj.get("currency") or "usd").upper()
    metadata = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    sku = str(metadata.get("gtm_sku") or metadata.get("sku") or "commercial_license")
    return {
        "session_id": session_id,
        "customer_email": customer_email,
        "amount_total": str(amount) if amount is not None else "",
        "currency": currency,
        "sku": sku,
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
    details = parse_checkout_completed(event)
    if not details:
        return {"ok": True, "handled": False, "type": event.get("type")}
    emailed = notify_stripe_checkout(settings, details)
    logger.info(
        "stripe_checkout_completed session=%s sku=%s emailed=%s",
        details.get("session_id"),
        details.get("sku"),
        emailed,
    )
    return {"ok": True, "handled": True, "emailed": emailed, "session_id": details.get("session_id")}
