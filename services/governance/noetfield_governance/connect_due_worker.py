"""Daily source-backed Noetfield Connect follow-up digest.

Uses existing PostgreSQL and the already-configured private operations Telegram.
Reports cases needing attention; never sends unapproved outreach to applicants,
creates workpackets, or treats a due date as evidence of completed work.
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import asyncpg

from noetfield_governance.telegram_client import send_message

logger = logging.getLogger("noetfield.governance.connect_followup")
_VANCOUVER = ZoneInfo("America/Vancouver")


def _secret(value: object | None) -> str:
    getter = getattr(value, "get_secret_value", None)
    return str(getter() if callable(getter) else value or "").strip()


def configured(settings: object) -> bool:
    return (os.getenv("CONNECT_FOLLOWUP_ENABLED", "true").strip().lower()
            not in {"0", "false", "off", "no"}
            and bool(getattr(settings, "public_intake_enabled", False))
            and bool(_secret(getattr(settings, "telegram_ops_bot_token", None)))
            and bool(str(getattr(settings, "telegram_ops_chat_id", "") or "").strip()))


def format_digest(day: str, items: list[dict[str, Any]], total: int) -> str:
    """No submitted message bodies, contact emails or cross-venture lead details."""
    lines = [
        "Noetfield Connect · daily operations follow-up",
        "Date (Vancouver): " + day,
        "Actionable source cases: " + str(total),
        "These are reminders, not executed tasks, contacted applicants or receipts.",
    ]
    for item in items[:20]:
        stage = str(item.get("stage") or "NEW")[:20]
        owner = str(item.get("owner") or "UNASSIGNED")[:80]
        due = str(item.get("due") or "UNSCHEDULED")[:12]
        source_id = str(item.get("intake_id") or "")[:90]
        lines.append(f"• {source_id} | {stage} | {owner} | due {due}")
    if total > len(items[:20]):
        lines.append("+" + str(total - len(items[:20])) + " other source cases. Review private desk.")
    lines.append("Review: https://platform.noetfield.com/api/opportunities/desk/app")
    return "\n".join(lines)


class ConnectDueWorker:
    def __init__(self, *, database_url: str, telegram_token: str,
                 telegram_chat_id: str) -> None:
        self.database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self.token = telegram_token
        self.chat_id = telegram_chat_id
        self.pool: asyncpg.Pool | None = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        if self.pool is not None:
            return
        self.pool = await asyncpg.create_pool(self.database_url, min_size=1, max_size=2)
        async with self.pool.acquire() as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.connect_followup_digest (
                digest_day date PRIMARY KEY,
                claim_id text NOT NULL,
                attempted_at timestamptz NOT NULL DEFAULT now(),
                state text NOT NULL DEFAULT 'CLAIMED',
                due_count integer NOT NULL DEFAULT 0,
                provider_message_id text,
                finished_at timestamptz
            )""")

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def due(self, day: str) -> tuple[list[dict[str, Any]], int]:
        assert self.pool is not None
        # YYYY-MM-DD is lexically ordered; source operator due_date is a
        # validated ISO date. Unscheduled cases older than a day need a review.
        condition = """metadata->>'form_id'='nfConnectWizard'
          AND COALESCE(metadata->>'intake_kind','lead')<>'test'
          AND COALESCE(qualification_json #>> '{connect_ops,stage}','NEW')
              NOT IN ('WON','LOST','ARCHIVED')
          AND (
             (qualification_json #>> '{connect_ops,due_date}') <= $1::text
             OR (
               nullif(qualification_json #>> '{connect_ops,due_date}','') IS NULL
               AND created_at < now() - interval '1 day'
             )
          )"""
        async with self.pool.acquire() as db:
            count = await db.fetchval(
                "SELECT count(*)::int FROM noetfield.public_intakes WHERE " + condition,
                day)
            rows = await db.fetch(
                """SELECT intake_id,
                          COALESCE(qualification_json #>> '{connect_ops,stage}', 'NEW') as stage,
                          COALESCE(qualification_json #>> '{connect_ops,owner}','') as owner,
                          COALESCE(qualification_json #>> '{connect_ops,due_date}','') as due
                   FROM noetfield.public_intakes WHERE """ + condition +
                """ ORDER BY created_at DESC, intake_id DESC LIMIT 20""", day)
        return [dict(row) for row in rows], int(count or 0)

    async def run_once(self) -> dict[str, Any]:
        async with self._lock:
            await self.connect()
            assert self.pool is not None
            day_date = datetime.now(_VANCOUVER).date()
            day = day_date.isoformat()
            items, total = await self.due(day)
            if total == 0:
                return {"state": "NO_DUE_CASES", "due_count": 0, "sent": False}
            claim_id = uuid.uuid4().hex
            async with self.pool.acquire() as db:
                claimed = await db.fetchrow(
                    """INSERT INTO noetfield.connect_followup_digest
                        (digest_day,claim_id,due_count) VALUES ($1::date,$2,$3)
                       ON CONFLICT DO NOTHING RETURNING digest_day""",
                    day_date, claim_id, total)
            if not claimed:
                return {"state": "ALREADY_ATTEMPTED_TODAY",
                        "due_count": total, "sent": False}
            message_id = ""
            try:
                result = await asyncio.to_thread(
                    send_message, token=self.token, chat_id=self.chat_id,
                    text=format_digest(day, items, total), parse_mode=None)
                if not isinstance(result, dict) or result.get("ok") is not True:
                    raise RuntimeError("TELEGRAM_DID_NOT_ACKNOWLEDGE")
                message = result.get("result")
                message_id = str(message.get("message_id", "")) if isinstance(message, dict) else ""
                state = "SENT_ACKNOWLEDGED"
            except Exception:
                logger.exception("connect_followup_digest_delivery_unconfirmed day=%s", day)
                state = "DELIVERY_UNCONFIRMED"
            async with self.pool.acquire() as db:
                await db.execute(
                    """UPDATE noetfield.connect_followup_digest
                       SET state=$3,provider_message_id=$4,finished_at=now()
                       WHERE digest_day=$1::date AND claim_id=$2""",
                    day_date, claim_id, state, message_id or None)
            logger.info("connect_followup_digest day=%s state=%s count=%s",
                        day, state, total)
            return {"state": state, "due_count": total,
                    "sent": state == "SENT_ACKNOWLEDGED"}

    async def status(self) -> dict[str, Any]:
        await self.connect()
        assert self.pool is not None
        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                """SELECT digest_day,state,due_count,finished_at,provider_message_id
                   FROM noetfield.connect_followup_digest
                   ORDER BY digest_day DESC LIMIT 1""")
        if not row:
            return {"configured": True, "latest": None}
        return {"configured": True, "latest": {
            "day": row["digest_day"].isoformat(), "state": row["state"],
            "due_count": row["due_count"],
            "finished_at": row["finished_at"].isoformat() if row["finished_at"] else None,
            "telegram_provider_acknowledged": bool(row["provider_message_id"])
                and row["state"] == "SENT_ACKNOWLEDGED",
        }}


_worker: ConnectDueWorker | None = None
_task: asyncio.Task[None] | None = None


def get_worker() -> ConnectDueWorker | None:
    return _worker


async def start_scheduler(settings: object) -> None:
    global _worker, _task
    if not configured(settings):
        logger.info("connect_followup_scheduler=DISABLED_OR_UNCONFIGURED")
        return
    if _task is not None and not _task.done():
        return
    _worker = ConnectDueWorker(
        database_url=str(getattr(settings, "database_url")),
        telegram_token=_secret(getattr(settings, "telegram_ops_bot_token")),
        telegram_chat_id=str(getattr(settings, "telegram_ops_chat_id")))
    # Startup must not fail if a reminder is temporarily unavailable.
    async def loop() -> None:
        while True:
            try:
                assert _worker is not None
                await _worker.run_once()
            except Exception:
                logger.exception("connect_followup_scheduler_tick_failed")
            await asyncio.sleep(3600)
    _task = asyncio.create_task(loop())


async def stop_scheduler() -> None:
    global _task, _worker
    if _task is not None:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
    if _worker is not None:
        await _worker.close()
        _worker = None
