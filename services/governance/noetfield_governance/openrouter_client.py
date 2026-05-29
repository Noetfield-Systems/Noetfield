"""Server-side OpenRouter client — API key never exposed to browsers."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from noetfield_governance.chat_errors import ChatAPIError, ChatConfigurationError

logger = logging.getLogger("noetfield.governance.openrouter")

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_HTTP_REFERER = "https://www.noetfield.com"
DEFAULT_APP_TITLE = "Noetfield Website Chat"


def generate_reply(
    *,
    api_key: str,
    model: str,
    system_instruction: str,
    user_message: str,
    timeout_seconds: float = 60.0,
    http_referer: str = DEFAULT_HTTP_REFERER,
    app_title: str = DEFAULT_APP_TITLE,
) -> str:
    if not api_key.strip():
        raise ChatConfigurationError("OPENROUTER_API_KEY is not configured on the server.")

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.35,
        "max_tokens": 1024,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OPENROUTER_CHAT_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": http_referer,
            "X-Title": app_title,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        logger.warning("openrouter_http_error status=%s detail=%s", exc.code, detail)
        raise ChatAPIError(f"OpenRouter API error ({exc.code})") from exc
    except urllib.error.URLError as exc:
        logger.warning("openrouter_network_error %s", exc)
        raise ChatAPIError("Unable to reach OpenRouter API") from exc

    try:
        reply = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        logger.warning("openrouter_unexpected_shape %s", data)
        raise ChatAPIError("Unexpected OpenRouter response shape") from exc

    if not reply:
        raise ChatAPIError("Empty reply from OpenRouter")
    return reply
