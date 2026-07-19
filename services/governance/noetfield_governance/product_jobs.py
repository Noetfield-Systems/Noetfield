"""Product job submit + gateway proxy orchestration."""

from __future__ import annotations

from typing import Any

from noetfield_governance.job_gateway_client import build_job_intake, gateway_request
from noetfield_governance.product_entitlement_store import get_product_entitlement_store
from noetfield_governance.research_product_catalog import RESEARCH_RUNWAY_ID, is_research_recipe


def entitlement_payload(entitlement_id: str) -> dict[str, Any] | None:
    store = get_product_entitlement_store()
    entitlement = store.get_entitlement(entitlement_id)
    if not entitlement:
        return None
    outbox = store.get_outbox_for_entitlement(entitlement_id)
    return {
        "schema": "noetfield.product-entitlement.v0.1",
        "entitlement_id": entitlement.entitlement_id,
        "tenant_id": entitlement.tenant_id,
        "customer_email": entitlement.customer_email,
        "session_id": entitlement.session_id,
        "sku": entitlement.sku,
        "recipe_id": entitlement.recipe_id,
        "recipe_version": entitlement.recipe_version,
        "runway_id": entitlement.runway_id,
        "status": entitlement.status,
        "created_at": entitlement.created_at,
        "outbox": None
        if not outbox
        else {
            "event_id": outbox.event_id,
            "status": outbox.status,
            "job_id": outbox.job_id,
            "last_error": outbox.last_error,
        },
    }


def submit_product_job(settings: object, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    entitlement_id = str(body.get("entitlement_id") or "").strip()
    idempotency_key = str(body.get("idempotency_key") or "").strip()
    goal = body.get("goal")
    if not entitlement_id or not idempotency_key:
        return 400, {"error": "REQUEST_INVALID", "detail": "entitlement_id and idempotency_key are required"}
    if not isinstance(goal, dict):
        return 400, {"error": "REQUEST_INVALID", "detail": "goal object is required"}
    store = get_product_entitlement_store()
    entitlement = store.get_entitlement(entitlement_id)
    if not entitlement:
        return 404, {"error": "ENTITLEMENT_NOT_FOUND"}
    if entitlement.status != "active":
        return 409, {"error": "ENTITLEMENT_NOT_ACTIVE", "status": entitlement.status}
    if entitlement.runway_id != RESEARCH_RUNWAY_ID or not is_research_recipe(entitlement.recipe_id):
        return 422, {"error": "RECIPE_NOT_ALLOWED", "detail": "only approved research recipes are supported"}
    intake = build_job_intake(
        tenant_id=entitlement.tenant_id,
        entitlement_id=entitlement.entitlement_id,
        recipe_id=entitlement.recipe_id,
        recipe_version=entitlement.recipe_version,
        idempotency_key=idempotency_key,
        goal=goal,
        session_id=entitlement.session_id,
        customer_email=entitlement.customer_email,
    )
    status, payload = gateway_request(settings, "POST", "/v1/intake", intake)
    if status in (200, 202) and payload.get("job_id"):
        store.mark_outbox_submitted(entitlement_id, str(payload["job_id"]))
        payload["entitlement_id"] = entitlement_id
        payload["runway_id"] = RESEARCH_RUNWAY_ID
        payload["recipe_id"] = entitlement.recipe_id
        return status, payload
    store.mark_outbox_failed(entitlement_id, str(payload.get("error") or payload.get("detail") or status))
    return status, payload


def proxy_product_job(settings: object, method: str, job_id: str, action: str | None = None, body: dict[str, Any] | None = None, query: dict[str, str] | None = None) -> tuple[int, dict[str, Any]]:
    job_id = str(job_id or "").strip()
    if not job_id.startswith("rj_"):
        return 400, {"error": "JOB_ID_INVALID"}
    path = f"/v1/jobs/{job_id}"
    if action:
        path = f"{path}/{action}"
    if query:
        params = "&".join(f"{key}={__import__('urllib.parse').parse.quote(value)}" for key, value in query.items() if value)
        if params:
            path = f"{path}?{params}"
    return gateway_request(settings, method, path, body)
