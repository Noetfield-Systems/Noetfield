"""Server-side Gemini client — API key never exposed to browsers."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger("noetfield.governance.gemini")

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiConfigurationError(RuntimeError):
    """Raised when the API key is missing."""


class GeminiAPIError(RuntimeError):
    """Raised when the upstream API returns an error."""


def generate_reply(
    *,
    api_key: str,
    model: str,
    system_instruction: str,
    user_message: str,
    timeout_seconds: float = 45.0,
) -> str:
    if not api_key.strip():
        raise GeminiConfigurationError("GEMINI_API_KEY is not configured on the server.")

    url = f"{GEMINI_BASE}/models/{model}:generateContent"
    payload: dict[str, Any] = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {
            "temperature": 0.35,
            "maxOutputTokens": 1024,
        },
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-goog-api-key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        logger.warning("gemini_http_error status=%s detail=%s", exc.code, detail)
        raise GeminiAPIError(f"Gemini API error ({exc.code})") from exc
    except urllib.error.URLError as exc:
        logger.warning("gemini_network_error %s", exc)
        raise GeminiAPIError("Unable to reach Gemini API") from exc

    try:
        parts = data["candidates"][0]["content"]["parts"]
        texts = [p["text"] for p in parts if isinstance(p.get("text"), str)]
        reply = "\n".join(texts).strip()
    except (KeyError, IndexError, TypeError) as exc:
        logger.warning("gemini_unexpected_shape %s", data)
        raise GeminiAPIError("Unexpected Gemini response shape") from exc

    if not reply:
        raise GeminiAPIError("Empty reply from Gemini")
    return reply
