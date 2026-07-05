"""Client-facing public chat copy — loaded from data/chatbot/public-chat-greeting.json."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_GREETING_PATH = _REPO_ROOT / "data" / "chatbot" / "public-chat-greeting.json"


@lru_cache(maxsize=1)
def public_chat_greeting_payload() -> dict[str, object]:
    data = json.loads(_GREETING_PATH.read_text(encoding="utf-8"))
    greeting = str(data.get("greeting") or "").strip()
    if not greeting:
        raise RuntimeError("public-chat-greeting.json missing greeting")
    citations = data.get("citations") or []
    if not isinstance(citations, list):
        raise RuntimeError("public-chat-greeting.json citations must be a list")
    guidance = str(data.get("llm_greeting_guidance") or "").strip()
    return {
        "greeting": greeting,
        "citations": [str(c).strip() for c in citations if str(c).strip()],
        "llm_greeting_guidance": guidance,
    }


def public_chat_greeting_text() -> str:
    return str(public_chat_greeting_payload()["greeting"])


def public_chat_greeting_citations() -> list[str]:
    return list(public_chat_greeting_payload()["citations"])  # type: ignore[arg-type]


def public_chat_greeting_llm_guidance() -> str:
    return str(public_chat_greeting_payload().get("llm_greeting_guidance") or "")
