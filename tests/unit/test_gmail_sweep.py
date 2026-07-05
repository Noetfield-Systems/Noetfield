"""Gmail message parsing and sweep worker tests."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from noetfield_governance.gmail_client import GmailMessage, message_to_signal_payload, parse_gmail_message
from noetfield_governance.gmail_sweep_worker import GmailSweepSettings, GmailSweepWorker


def test_parse_gmail_message_extracts_headers_and_body() -> None:
    payload = {
        "id": "msg123",
        "threadId": "thr456",
        "snippet": "Hello ops",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test subject"},
                {"name": "From", "value": "lead@example.com"},
                {"name": "To", "value": "operations@noetfield.com"},
                {"name": "Date", "value": "Mon, 05 Jul 2026 12:00:00 +0000"},
            ],
            "mimeType": "text/plain",
            "body": {"data": "SGVsbG8gb3Bz"},
        },
    }
    message = parse_gmail_message(payload)
    assert message.message_id == "msg123"
    assert message.subject == "Test subject"
    assert message.from_addr == "lead@example.com"
    assert "Hello" in message.body_text


def test_message_to_signal_payload_shape() -> None:
    message = GmailMessage(
        message_id="msg123",
        thread_id="thr456",
        subject="Subject",
        from_addr="lead@example.com",
        to_addrs=["operations@noetfield.com"],
        cc_addrs=[],
        received_at="Mon, 05 Jul 2026 12:00:00 +0000",
        snippet="snippet",
        body_text="body",
        headers={"message-id": "<abc@example.com>"},
    )
    payload = message_to_signal_payload(message, mailbox="operations@noetfield.com")
    assert payload["channel"] == "operations_inbox"
    assert payload["gmail_message_id"] == "msg123"


def test_gmail_sweep_worker_skips_processed_messages() -> None:
    async def run() -> None:
        settings = GmailSweepSettings(
            enabled=True,
            mailbox="operations@noetfield.com",
            service_account_json='{"type":"service_account","client_email":"x","private_key":"y"}',
            processed_label="nf-processed",
            search_query="label:INBOX",
            tenant_id=uuid4(),
            organization_id=uuid4(),
            max_messages=5,
        )
        store = AsyncMock()
        store.start_run.return_value = uuid4()
        store.is_processed.side_effect = [True, False]
        store.mark_processed.return_value = None
        store.finish_run.return_value = None

        client = MagicMock()
        client.list_messages.return_value = [
            MagicMock(message_id="seen", thread_id="t1"),
            MagicMock(message_id="new", thread_id="t2"),
        ]
        client.fetch_message.return_value = GmailMessage(
            message_id="new",
            thread_id="t2",
            subject="Inbound",
            from_addr="lead@example.com",
            to_addrs=["operations@noetfield.com"],
            cc_addrs=[],
            received_at="Mon, 05 Jul 2026 12:00:00 +0000",
            snippet="snippet",
            body_text="body",
            headers={},
        )
        client.mark_processed.return_value = None

        pipeline = AsyncMock()
        pipeline.ingest.return_value = (
            MagicMock(signal_id=uuid4()),
            MagicMock(),
        )

        worker = GmailSweepWorker(
            sweep_settings=settings,
            signal_pipeline=pipeline,
            sweep_store=store,
            client=client,
        )

        result = await worker.run_once()
        assert result["ok"] is True
        assert result["messages_seen"] == 2
        assert result["messages_skipped"] == 1
        assert result["messages_ingested"] == 1
        pipeline.ingest.assert_awaited_once()
        client.mark_processed.assert_called_once()

    asyncio.run(run())
