"""Noetfield canonical Connect -> existing WorkforceOS people intake.

A server-side projection after Platform persisted the canonical source record.
This is not a second website intake, an A2A work dispatch, or an outcome receipt.
The consumer deduplicates by original intake_id.
"""
from __future__ import annotations

import json
import logging
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from noetfield_governance.intake_store import IntakeRecord

logger = logging.getLogger("noetfield.governance.workforce_connect_bridge")


def eligible(record: IntakeRecord) -> bool:
    m = record.metadata if isinstance(record.metadata, dict) else {}
    if record.vector == "external-opportunities":
        # Independent TrustField must not be mirrored into Noetfield workforce.
        return (m.get("category") == "people" and
                m.get("consent_contact") is True and
                m.get("initiative") != "trustfield")
    if record.vector == "work-with-us-contributor":
        return (m.get("consent_contact") is True and
                m.get("application_kind") in {"human", "agent", "organization"})
    return False


def deliver(record: IntakeRecord) -> dict[str, object]:
    if not eligible(record):
        return {"eligible": False, "delivered": False}
    secret = os.getenv("WORKFORCE_CONNECT_BRIDGE_KEY", "")
    base = os.getenv("WORKFORCE_CONNECT_BRIDGE_URL", "").rstrip("/")
    parsed = urlsplit(base)
    if len(secret) < 32 or parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return {"eligible": True, "delivered": False, "error": "BRIDGE_NOT_CONFIGURED"}
    endpoint = base + "/api/integrations/noetfield-connect"
    metadata = record.metadata if isinstance(record.metadata, dict) else {}
    payload = {
        "source_intake_id": record.intake_id,
        "source_request_id": record.request_id or "",
        "vector": record.vector,
        "contact_name": record.contact_name or "",
        "contact_email": record.contact_email,
        "organization": record.organization,
        "message": record.message,
        "metadata": metadata,
    }
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > 23000:
        return {"eligible": True, "delivered": False, "error": "BRIDGE_PAYLOAD_TOO_LARGE"}
    for attempt in range(3):
        request = Request(endpoint, data=encoded, method="POST", headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Workforce-Request": "workspace",
            "X-Noetfield-Bridge-Key": secret,
            "User-Agent": "Noetfield-Connect-Source-Bridge/1",
        })
        try:
            with urlopen(request, timeout=7) as response:
                if response.status != 200:
                    raise RuntimeError("BRIDGE_NOT_ACCEPTED")
                result = json.loads(response.read(4096))
            if (result.get("accepted") is not True or
                    result.get("source_intake_id") != record.intake_id or
                    not str(result.get("case_id", "")).startswith("opp_nf_")):
                raise RuntimeError("BRIDGE_INVALID_ACK")
            logger.info("workforce_connect_import_confirmed source_id=%s case_id=%s deduped=%s",
                        record.intake_id, result["case_id"], result.get("deduped"))
            return {"eligible": True, "delivered": True,
                    "case_id": result["case_id"],
                    "source_intake_id": record.intake_id,
                    "deduped": bool(result.get("deduped"))}
        except HTTPError as exc:
            if exc.code in {400, 401, 403, 404, 409, 413, 422}:
                logger.warning("workforce_connect_import_rejected source_id=%s status=%s",
                               record.intake_id, exc.code)
                return {"eligible": True, "delivered": False, "error": "UPSTREAM_REJECTED",
                        "http_status": exc.code}
            error = "UPSTREAM_HTTP_FAILURE"
        except (URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
            error = type(exc).__name__
        if attempt < 2:
            time.sleep(.35 * (attempt + 1))
    logger.warning("workforce_connect_import_pending source_id=%s reason=%s", record.intake_id, error)
    return {"eligible": True, "delivered": False, "error": error}


def probe() -> dict[str, object]:
    """Read-only live authentication/DB handshake. No contact data or writes."""
    secret = os.getenv("WORKFORCE_CONNECT_BRIDGE_KEY", "")
    base = os.getenv("WORKFORCE_CONNECT_BRIDGE_URL", "").rstrip("/")
    parsed = urlsplit(base)
    if len(secret) < 32 or parsed.scheme != "https" or not parsed.hostname:
        return {"connected": False, "reason": "NOT_CONFIGURED"}
    try:
        request = Request(base + "/api/integrations/noetfield-connect/health",
                          method="GET", headers={
                              "X-Noetfield-Bridge-Key": secret,
                              "Accept": "application/json",
                              "User-Agent": "Noetfield-Connect-Bridge-Probe/1"})
        with urlopen(request, timeout=6) as response:
            result = json.loads(response.read(4096))
        if (result.get("authenticated") is True and
                result.get("database") == "connected" and
                result.get("read_only") is True):
            return {"connected": True, "mode": "SIGNED_READ_ONLY_NO_CASE"}
        return {"connected": False, "reason": "INVALID_BRIDGE_ACK"}
    except HTTPError as exc:
        return {"connected": False, "reason": "UPSTREAM_HTTP", "http_status": exc.code}
    except (URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
        return {"connected": False, "reason": type(exc).__name__}


def _signed_bridge_request(path: str, *, payload: dict[str, object] | None = None) -> dict[str, object]:
    """Use the existing scoped bridge secret, never a WorkforceOS admin credential."""
    secret = os.getenv("WORKFORCE_CONNECT_BRIDGE_KEY", "")
    base = os.getenv("WORKFORCE_CONNECT_BRIDGE_URL", "").rstrip("/")
    parsed = urlsplit(base)
    if (len(secret) < 32 or parsed.scheme != "https" or not parsed.hostname
            or parsed.username or parsed.password or parsed.path not in ("", "/")):
        return {"connected": False, "error": "BRIDGE_NOT_CONFIGURED"}
    encoded = (json.dumps(payload, separators=(",", ":")).encode("utf-8")
               if payload is not None else None)
    if encoded is not None and len(encoded) > 4096:
        return {"connected": False, "error": "BRIDGE_REQUEST_TOO_LARGE"}
    try:
        request = Request(base + path, data=encoded,
                          method="POST" if encoded is not None else "GET",
                          headers={"X-Noetfield-Bridge-Key": secret,
                                   "Accept": "application/json",
                                   "User-Agent": "Noetfield-Connect-Operator-Bridge/1",
                                   **({"Content-Type": "application/json"} if encoded is not None else {})})
        with urlopen(request, timeout=8) as response:
            data = json.loads(response.read(8192))
        if not isinstance(data, dict):
            return {"connected": False, "error": "BRIDGE_RESPONSE_INVALID"}
        return {"connected": True, **data}
    except HTTPError as exc:
        return {"connected": False, "error": "BRIDGE_UPSTREAM_HTTP",
                "http_status": exc.code}
    except (URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
        return {"connected": False, "error": type(exc).__name__}


def readback_case(source_intake_id: str) -> dict[str, object]:
    """Authenticated source-key readback, no PII and no optimistic status."""
    if not __import__("re").fullmatch(r"INT-[A-Za-z0-9-]{6,80}", source_intake_id):
        return {"connected": False, "error": "SOURCE_ID_INVALID"}
    result = _signed_bridge_request(
        "/api/integrations/noetfield-connect/cases/" + source_intake_id)
    state = result.get("case")
    if result.get("connected") and (not isinstance(state, dict)
                                    or state.get("source_intake_id") != source_intake_id
                                    or not str(state.get("case_id", "")).startswith("opp_nf_")):
        return {"connected": False, "error": "BRIDGE_INVALID_CASE_ACK"}
    return result


def handoff_case(*, source_intake_id: str, request_id: str, owner: str,
                 next_action: str, due_date: str | None,
                 match_quality: str = "not_assessed",
                 assignment_reference: str = "") -> dict[str, object]:
    """Operator-approved owner handoff; no external runtime or email send."""
    payload: dict[str, object] = {
        "source_intake_id": source_intake_id, "request_id": request_id,
        "owner": owner, "next_action": next_action,
        "due_date": due_date, "match_quality": match_quality,
        "assignment_reference": assignment_reference,
    }
    result = _signed_bridge_request(
        "/api/integrations/noetfield-connect/handoff", payload=payload)
    state = result.get("case")
    if result.get("connected") and (result.get("accepted") is not True
                                    or not isinstance(state, dict)
                                    or state.get("source_intake_id") != source_intake_id
                                    or not str(state.get("case_id", "")).startswith("opp_nf_")):
        return {"connected": False, "error": "BRIDGE_INVALID_HANDOFF_ACK"}
    return result
