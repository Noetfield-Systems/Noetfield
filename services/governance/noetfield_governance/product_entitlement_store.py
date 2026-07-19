"""In-memory entitlement + outbox store for research product checkout fulfillment."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import hashlib
from typing import Any, Literal
from uuid import uuid4

EntitlementStatus = Literal["active", "consumed", "revoked"]
OutboxStatus = Literal["pending_submit", "submitted", "failed"]


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256(":".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}_{digest}"


@dataclass(frozen=True)
class ProductEntitlement:
    entitlement_id: str
    tenant_id: str
    customer_email: str
    session_id: str
    sku: str
    recipe_id: str
    recipe_version: str
    runway_id: str
    status: EntitlementStatus
    created_at: str
    stripe_amount_total: str | None = None
    stripe_currency: str | None = None


@dataclass(frozen=True)
class ProductJobOutboxEvent:
    event_id: str
    entitlement_id: str
    session_id: str
    recipe_id: str
    runway_id: str
    status: OutboxStatus
    created_at: str
    job_id: str | None = None
    last_error: str | None = None


@dataclass
class ProductEntitlementStore:
    entitlements: dict[str, ProductEntitlement] = field(default_factory=dict)
    outbox: dict[str, ProductJobOutboxEvent] = field(default_factory=dict)
    outbox_by_entitlement: dict[str, str] = field(default_factory=dict)

    def create_from_checkout(self, checkout: dict[str, str], product: dict[str, Any]) -> tuple[ProductEntitlement, ProductJobOutboxEvent]:
        session_id = str(checkout.get("session_id") or "")
        customer_email = str(checkout.get("customer_email") or "unknown@noetfield.com").strip().lower()
        tenant_id = _stable_id("tenant", customer_email, session_id)
        entitlement_id = _stable_id("ent", session_id, product["recipe_id"])
        created_at = _now_iso()
        entitlement = ProductEntitlement(
            entitlement_id=entitlement_id,
            tenant_id=tenant_id,
            customer_email=customer_email,
            session_id=session_id,
            sku=str(checkout.get("sku") or product.get("gtm_sku") or ""),
            recipe_id=str(product["recipe_id"]),
            recipe_version=str(product["recipe_version"]),
            runway_id=str(product["runway_id"]),
            status="active",
            created_at=created_at,
            stripe_amount_total=str(checkout.get("amount_total") or "") or None,
            stripe_currency=str(checkout.get("currency") or "") or None,
        )
        event_id = _stable_id("pjo", entitlement_id, uuid4().hex[:8])
        outbox_event = ProductJobOutboxEvent(
            event_id=event_id,
            entitlement_id=entitlement_id,
            session_id=session_id,
            recipe_id=entitlement.recipe_id,
            runway_id=entitlement.runway_id,
            status="pending_submit",
            created_at=created_at,
        )
        self.entitlements[entitlement_id] = entitlement
        self.outbox[event_id] = outbox_event
        self.outbox_by_entitlement[entitlement_id] = event_id
        return entitlement, outbox_event

    def get_entitlement(self, entitlement_id: str) -> ProductEntitlement | None:
        return self.entitlements.get(entitlement_id)

    def get_outbox_for_entitlement(self, entitlement_id: str) -> ProductJobOutboxEvent | None:
        event_id = self.outbox_by_entitlement.get(entitlement_id)
        if not event_id:
            return None
        return self.outbox.get(event_id)

    def mark_outbox_submitted(self, entitlement_id: str, job_id: str) -> ProductJobOutboxEvent | None:
        event = self.get_outbox_for_entitlement(entitlement_id)
        if not event:
            return None
        updated = ProductJobOutboxEvent(
            event_id=event.event_id,
            entitlement_id=event.entitlement_id,
            session_id=event.session_id,
            recipe_id=event.recipe_id,
            runway_id=event.runway_id,
            status="submitted",
            created_at=event.created_at,
            job_id=job_id,
        )
        self.outbox[event.event_id] = updated
        entitlement = self.entitlements.get(entitlement_id)
        if entitlement:
            self.entitlements[entitlement_id] = ProductEntitlement(
                **{**entitlement.__dict__, "status": "consumed"}
            )
        return updated

    def mark_outbox_failed(self, entitlement_id: str, error: str) -> ProductJobOutboxEvent | None:
        event = self.get_outbox_for_entitlement(entitlement_id)
        if not event:
            return None
        updated = ProductJobOutboxEvent(
            event_id=event.event_id,
            entitlement_id=event.entitlement_id,
            session_id=event.session_id,
            recipe_id=event.recipe_id,
            runway_id=event.runway_id,
            status="failed",
            created_at=event.created_at,
            job_id=event.job_id,
            last_error=error[:500],
        )
        self.outbox[event.event_id] = updated
        return updated


_STORE = ProductEntitlementStore()


def get_product_entitlement_store() -> ProductEntitlementStore:
    return _STORE
