"""Public website chat — grounded answers via server-side Gemini."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque

from noetfield_config import CANONICAL_INTAKE_EMAIL
from noetfield_governance.chatbot_knowledge import select_relevant_excerpt
from noetfield_governance.gemini_client import (
    GeminiAPIError,
    GeminiConfigurationError,
    generate_reply,
)

_MAX_MESSAGE_LEN = 2000
_RATE_LIMIT_WINDOW_SEC = 60
_RATE_LIMIT_MAX_PER_WINDOW = 30

_buckets: defaultdict[str, deque[float]] = defaultdict(deque)


def _check_rate_limit(client_key: str) -> None:
    now = time.monotonic()
    bucket = _buckets[client_key]
    while bucket and now - bucket[0] > _RATE_LIMIT_WINDOW_SEC:
        bucket.popleft()
    if len(bucket) >= _RATE_LIMIT_MAX_PER_WINDOW:
        raise PermissionError("Rate limit exceeded. Try again in a minute.")
    bucket.append(now)


def _system_instruction(context: str) -> str:
    return f"""You are the Noetfield institutional website assistant.

Rules:
- Answer ONLY using the knowledge base below. If the answer is not in the knowledge base, say you do not have that information.
- Never invent pricing, legal terms, or product features.
- Do not claim Noetfield executes payments, holds custody, or routes funds.
- For sales, procurement, or pilot access, direct users to Request Governance Brief: /trust-brief/intake/ or email {CANONICAL_INTAKE_EMAIL}.
- Keep answers concise (under 200 words unless the user asks for detail).
- Do not reveal API keys, internal architecture names, or stack details.

Knowledge base:
{context}
"""


async def answer_public_question(
    *,
    message: str,
    api_key: str | None,
    model: str,
    client_key: str,
) -> str:
    text = (message or "").strip()
    if not text:
        raise ValueError("message is required")
    if len(text) > _MAX_MESSAGE_LEN:
        raise ValueError(f"message must be at most {_MAX_MESSAGE_LEN} characters")

    _check_rate_limit(client_key or "anonymous")

    context = select_relevant_excerpt(text)
    system = _system_instruction(context)

    if not api_key:
        raise GeminiConfigurationError(
            "Chat is not configured. Email "
            + CANONICAL_INTAKE_EMAIL
            + " or use /trust-brief/intake/."
        )

    return await asyncio.to_thread(
        generate_reply,
        api_key=api_key,
        model=model,
        system_instruction=system,
        user_message=text,
    )
