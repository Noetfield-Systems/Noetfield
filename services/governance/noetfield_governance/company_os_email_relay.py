"""Private, narrowly scoped transactional email adapter for Noetfield Digital Agency OS.

Reuses the existing Noetfield platform Resend key server-side. It never exposes
the provider credential to a cross-project client and never accepts anonymous
email instructions. Independent OAC group/ventures are not granted this route.
"""
from __future__ import annotations

import hmac
import json
import os
import re
import urllib.error
import urllib.request
from typing import Literal

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field, field_validator

router = APIRouter()
EMAIL = re.compile(r"^[^\s@<>]{1,64}@[^\s@<>]{1,190}\.[A-Za-z]{2,24}$")
FROM = "Noetfield Digital <notifications@noetfield.com>"


class Message(BaseModel):
    kind: Literal["inbound_inquiry", "requested_proposal"]
    to: str = Field(min_length=5, max_length=254)
    subject: str = Field(min_length=5, max_length=180)
    text: str = Field(min_length=10, max_length=8000)
    idempotency_key: str = Field(min_length=16, max_length=96, pattern=r"^[A-Za-z0-9_-]+$")

    @field_validator("to")
    @classmethod
    def valid_recipient(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL.fullmatch(value):
            raise ValueError("Invalid recipient address")
        return value


@router.post("/api/internal/company-os/notify", include_in_schema=False)
def notify(message: Message, authorization: str | None = Header(default=None)):
    token = os.getenv("COMPANY_OS_EMAIL_RELAY_TOKEN", "").strip()
    if len(token) < 40:
        raise HTTPException(503, "Transactional relay not configured")
    supplied = (authorization or "").removeprefix("Bearer ").strip()
    if not hmac.compare_digest(supplied, token):
        raise HTTPException(401, "Unauthorized")
    provider = os.getenv("RESEND_API_KEY", "").strip()
    if not provider:
        raise HTTPException(503, "Email transport unavailable")
    payload = {
        "from": FROM,
        "to": [message.to],
        "subject": message.subject,
        "text": message.text,
    }
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + provider,
            "Idempotency-Key": "company-os-" + message.idempotency_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if not 200 <= response.status < 300:
                raise HTTPException(502, "Email provider did not accept the message")
            receipt = json.loads(response.read(4096))
    except (urllib.error.URLError, OSError, TimeoutError, ValueError):
        # Never persist or return provider response bodies, request contents or keys.
        raise HTTPException(502, "Email transport did not confirm acceptance")
    provider_id = receipt.get("id") if isinstance(receipt, dict) else None
    if not isinstance(provider_id, str) or not 6 <= len(provider_id) <= 160:
        raise HTTPException(502, "Email provider receipt missing")
    return {"accepted": True, "id": provider_id}
