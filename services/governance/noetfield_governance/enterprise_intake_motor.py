"""Best-effort Motor event envelope for qualified enterprise intake (outbox when gateway unset)."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from noetfield_governance.enterprise_intake_qualifier import QUALIFICATION_SCHEMA
from noetfield_governance.intake_store import IntakeRecord

logger = logging.getLogger("noetfield.governance.enterprise_intake.motor")

MOTOR_EVENT_TYPE = "noetfield.enterprise_intake.received"


@dataclass(frozen=True)
class EnterpriseIntakeMotorReceipt:
    mode: str
    event_type: str
    idempotency_key: str
    payload: dict[str, Any]
    delivered: bool
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "event_type": self.event_type,
            "idempotency_key": self.idempotency_key,
            "delivered": self.delivered,
            "detail": self.detail,
            "payload": self.payload,
        }


def build_enterprise_intake_motor_payload(
    *,
    record: IntakeRecord,
    qualification_json: dict[str, Any],
) -> dict[str, Any]:
    rid = (record.request_id or record.intake_id or "").strip()
    return {
        "event": MOTOR_EVENT_TYPE,
        "schema": QUALIFICATION_SCHEMA,
        "idempotency_key": f"noetfield-intake:{rid}",
        "occurred_at": datetime.now(UTC).isoformat(),
        "data": {
            "intake_id": record.intake_id,
            "request_id": record.request_id,
            "organization": record.organization,
            "contact_email": record.contact_email,
            "vector": record.vector,
            "sku": record.sku,
            "qualification": qualification_json,
        },
    }


def emit_enterprise_intake_motor_event(
    *,
    record: IntakeRecord,
    qualification_json: dict[str, Any],
    motor_gateway_url: str | None,
    timeout_sec: float = 8.0,
) -> EnterpriseIntakeMotorReceipt:
    """POST to Motor gateway when configured; otherwise return an outbox receipt."""
    payload = build_enterprise_intake_motor_payload(
        record=record,
        qualification_json=qualification_json,
    )
    idem = str(payload["idempotency_key"])
    url = (motor_gateway_url or "").strip()

    if not url:
        logger.info(
            "enterprise_intake_motor_outbox intake_id=%s idempotency_key=%s",
            record.intake_id,
            idem,
        )
        return EnterpriseIntakeMotorReceipt(
            mode="outbox",
            event_type=MOTOR_EVENT_TYPE,
            idempotency_key=idem,
            payload=payload,
            delivered=False,
            detail="motor_gateway_url_unset",
        )

    body = json.dumps(payload, default=str).encode("utf-8")
    req = urllib.request.Request(
        url.rstrip("/") + "/v1/events",
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Noetfield-Enterprise-Intake/1.0",
            "Idempotency-Key": idem,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            if resp.status >= 400:
                detail = f"http_{resp.status}"
                logger.warning(
                    "enterprise_intake_motor_http_error intake_id=%s status=%s",
                    record.intake_id,
                    resp.status,
                )
                return EnterpriseIntakeMotorReceipt(
                    mode="gateway",
                    event_type=MOTOR_EVENT_TYPE,
                    idempotency_key=idem,
                    payload=payload,
                    delivered=False,
                    detail=detail,
                )
    except urllib.error.URLError as exc:
        logger.warning(
            "enterprise_intake_motor_delivery_failed intake_id=%s error=%s",
            record.intake_id,
            exc,
        )
        return EnterpriseIntakeMotorReceipt(
            mode="gateway",
            event_type=MOTOR_EVENT_TYPE,
            idempotency_key=idem,
            payload=payload,
            delivered=False,
            detail=str(exc),
        )

    return EnterpriseIntakeMotorReceipt(
        mode="gateway",
        event_type=MOTOR_EVENT_TYPE,
        idempotency_key=idem,
        payload=payload,
        delivered=True,
        detail=None,
    )
