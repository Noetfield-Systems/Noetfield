"""OpenRouter client unit tests (mocked HTTP)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from noetfield_governance.openrouter_client import generate_reply


def test_openrouter_parses_chat_completion() -> None:
    payload = {
        "choices": [{"message": {"content": "Trust Brief costs $10,000."}}],
    }
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(payload).encode()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response):
        reply = generate_reply(
            api_key="test-key",
            model="google/gemini-2.0-flash-001",
            system_instruction="You are helpful.",
            user_message="Price?",
        )
    assert "10,000" in reply
