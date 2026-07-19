"""Stripe commercial licensing webhooks — checkout.session.completed fulfillment."""

from __future__ import annotations

import json
import logging
from typing import Any

from noetfield_config import CANONICAL_INTAKE_EMAIL

from noetfield_governance.product_entitlement_store import get_product_entitlement_store
from noetfield_governance.research_product_catalog import resolve_research_product

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


def create_research_entitlement_outbox(details: dict[str, str]) -> dict[str, Any] | None:
    product = resolve_research_product(details.get("sku", ""))
    if not product:
        return None
    store = get_product_entitlement_store()
    entitlement, outbox = store.create_from_checkout(details, product)
    return {
        "schema": "noetfield.product-checkout-fulfillment.v0.1",
        "entitlement_id": entitlement.entitlement_id,
        "tenant_id": entitlement.tenant_id,
        "runway_id": entitlement.runway_id,
        "recipe_id": entitlement.recipe_id,
        "recipe_version": entitlement.recipe_version,
        "outbox_event_id": outbox.event_id,
        "outbox_status": outbox.status,
        "job_submit_ready": True,
        "submit_path": "/api/product/jobs/submit",
        "result_path_template": "/gate/research/result/?entitlement_id={entitlement_id}",
    }


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
    fulfillment = create_research_entitlement_outbox(details)
    emailed = notify_stripe_checkout(settings, details)
    logger.info(
        "stripe_checkout_completed session=%s sku=%s emailed=%s fulfillment=%s",
        details.get("session_id"),
        details.get("sku"),
        emailed,
        bool(fulfillment),
    )
    response: dict[str, object] = {
        "ok": True,
        "handled": True,
        "emailed": emailed,
        "session_id": details.get("session_id"),
    }
    if fulfillment:
        response["fulfillment"] = fulfillment
    return response
