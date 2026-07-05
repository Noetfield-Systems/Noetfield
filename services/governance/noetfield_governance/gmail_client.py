"""Gmail API client for operations@ inbox sweep (Workspace domain delegation)."""

from __future__ import annotations

import base64
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2 import service_account

logger = logging.getLogger("noetfield.governance.gmail")

GMAIL_SCOPES = (
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
)


@dataclass(frozen=True)
class GmailMessageRef:
    message_id: str
    thread_id: str


@dataclass(frozen=True)
class GmailMessage:
    message_id: str
    thread_id: str
    subject: str
    from_addr: str
    to_addrs: list[str]
    cc_addrs: list[str]
    received_at: str
    snippet: str
    body_text: str
    headers: dict[str, str]


class GmailClient:
    def __init__(self, *, service_account_json: str, impersonate_user: str) -> None:
        info = json.loads(service_account_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=list(GMAIL_SCOPES))
        self._creds = creds.with_subject(impersonate_user)
        self._user = impersonate_user
        self._label_cache: dict[str, str] = {}

    def _token(self) -> str:
        self._creds.refresh(Request())
        token = self._creds.token
        if not token:
            raise RuntimeError("gmail_token_unavailable")
        return token

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        url = f"https://gmail.googleapis.com/gmail/v1/users/{urllib.parse.quote(self._user)}/{path}"
        data = None
        headers = {"Authorization": f"Bearer {self._token()}", "Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"gmail_http_{exc.code}:{detail}") from exc

    def ensure_label(self, label_name: str) -> str:
        cached = self._label_cache.get(label_name)
        if cached:
            return cached
        labels = self._request("GET", "labels").get("labels") or []
        for row in labels:
            if str(row.get("name") or "") == label_name:
                label_id = str(row.get("id") or "")
                self._label_cache[label_name] = label_id
                return label_id
        created = self._request(
            "POST",
            "labels",
            body={
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            },
        )
        label_id = str(created.get("id") or "")
        if not label_id:
            raise RuntimeError("gmail_label_create_failed")
        self._label_cache[label_name] = label_id
        return label_id

    def list_messages(self, *, query: str, max_results: int = 25) -> list[GmailMessageRef]:
        params = urllib.parse.urlencode({"q": query, "maxResults": str(max_results)})
        payload = self._request("GET", f"messages?{params}")
        refs: list[GmailMessageRef] = []
        for row in payload.get("messages") or []:
            message_id = str(row.get("id") or "")
            thread_id = str(row.get("threadId") or "")
            if message_id:
                refs.append(GmailMessageRef(message_id=message_id, thread_id=thread_id))
        return refs

    def fetch_message(self, message_id: str) -> GmailMessage:
        payload = self._request("GET", f"messages/{urllib.parse.quote(message_id)}?format=full")
        return parse_gmail_message(payload)

    def mark_processed(self, *, message_id: str, processed_label: str) -> None:
        label_id = self.ensure_label(processed_label)
        self._request(
            "POST",
            f"messages/{urllib.parse.quote(message_id)}/modify",
            body={
                "addLabelIds": [label_id],
                "removeLabelIds": ["UNREAD"],
            },
        )


def _header_map(payload: dict[str, Any]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for row in (payload.get("payload") or {}).get("headers") or []:
        name = str(row.get("name") or "").strip()
        value = str(row.get("value") or "").strip()
        if name:
            headers[name.lower()] = value
    return headers


def _decode_body_data(data: str) -> str:
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return raw.decode("utf-8", errors="replace")
    except (ValueError, UnicodeDecodeError):
        return ""


def _extract_text_part(part: dict[str, Any]) -> str:
    mime = str(part.get("mimeType") or "")
    body = part.get("body") or {}
    data = str(body.get("data") or "")
    if mime == "text/plain" and data:
        return _decode_body_data(data)
    for child in part.get("parts") or []:
        if not isinstance(child, dict):
            continue
        text = _extract_text_part(child)
        if text:
            return text
    if mime == "text/html" and data:
        return _decode_body_data(data)
    return ""


def parse_gmail_message(payload: dict[str, Any]) -> GmailMessage:
    headers = _header_map(payload)
    subject = headers.get("subject", "")
    from_addr = headers.get("from", "")
    to_addrs = [item.strip() for item in headers.get("to", "").split(",") if item.strip()]
    cc_addrs = [item.strip() for item in headers.get("cc", "").split(",") if item.strip()]
    received_at = headers.get("date", "")
    snippet = str(payload.get("snippet") or "")
    body_text = _extract_text_part(payload.get("payload") or {})
    if not body_text:
        body_text = snippet
    return GmailMessage(
        message_id=str(payload.get("id") or ""),
        thread_id=str(payload.get("threadId") or ""),
        subject=subject,
        from_addr=from_addr,
        to_addrs=to_addrs,
        cc_addrs=cc_addrs,
        received_at=received_at,
        snippet=snippet,
        body_text=body_text[:8000],
        headers=headers,
    )


def message_to_signal_payload(message: GmailMessage, *, mailbox: str) -> dict[str, object]:
    return {
        "channel": "operations_inbox",
        "mailbox": mailbox,
        "gmail_message_id": message.message_id,
        "gmail_thread_id": message.thread_id,
        "subject": message.subject,
        "from": message.from_addr,
        "to": message.to_addrs,
        "cc": message.cc_addrs,
        "received_at": message.received_at,
        "snippet": message.snippet,
        "body_text": message.body_text,
        "headers": {
            "message-id": message.headers.get("message-id", ""),
            "reply-to": message.headers.get("reply-to", ""),
        },
    }
