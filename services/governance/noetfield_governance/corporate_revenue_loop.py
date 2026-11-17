"""Low-cost daily corporate revenue loop inside the existing Platform API.

Each Vancouver day is claimed exactly once in PostgreSQL; retries of failed
claims are bounded. The loop projects real Noetfield intakes into the existing
CRM and sends only aggregate counters to the existing private Telegram channel.
It cannot send outreach, charge buyers, approve SOWs or mark deliveries complete.
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any

import asyncpg

from noetfield_governance.commercial_pipeline import _database_url
from noetfield_governance.corporate_revenue_ops import recover_intakes, revenue_plan
from noetfield_governance.telegram_client import send_message

logger = logging.getLogger("noetfield.governance.corporate_revenue_loop")
_VANCOUVER = ZoneInfo("America/Vancouver")


def _secret(value: object) -> str:
    getter = getattr(value, "get_secret_value", None)
    return str(getter() if callable(getter) else value or "").strip()


def enabled(settings: object) -> bool:
    return (os.getenv("CORPORATE_REVENUE_LOOP_ENABLED", "false").lower() in
            ("1", "true", "yes", "on")
            and os.getenv("NOETFIELD_CORPORATE_CRM_BOOTSTRAP_ENABLED") == "1"
            and bool(_secret(getattr(settings, "database_url", ""))))


def format_private_digest(day: str, *, recovered: int, failures: int,
                          due: int, priority: int) -> str:
    return ("Noetfield Corporate Revenue · verified daily cycle\n"
            "Vancouver date: " + day + "\n"
            "Historical source imports: " + str(recovered) + "\n"
            "Failed source imports: " + str(failures) + "\n"
            "CRM follow-ups due: " + str(due) + "\n"
            "Prioritized review actions: " + str(priority) + "\n"
            "Suggested actions are NOT customer outreach, confirmed meetings, "
            "paid orders or dispatched delivery.\n"
            "Private console: https://platform.noetfield.com/api/corporate-crm/app")


class CorporateRevenueLoop:
    def __init__(self, settings: object) -> None:
        self.settings = settings
        self._lock = asyncio.Lock()

    async def _db(self) -> asyncpg.Connection:
        return await asyncpg.connect(_database_url(self.settings))

    async def _prepare(self, db: asyncpg.Connection) -> None:
        await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_revenue_cycles (
            cycle_date date PRIMARY KEY,
            claim_id text NOT NULL,
            attempt_count int NOT NULL DEFAULT 1,
            state text NOT NULL DEFAULT 'CLAIMED',
            recovered_count int NOT NULL DEFAULT 0,
            failed_count int NOT NULL DEFAULT 0,
            due_count int NOT NULL DEFAULT 0,
            priority_count int NOT NULL DEFAULT 0,
            notification_state text NOT NULL DEFAULT 'NOT_ATTEMPTED',
            attempted_at timestamptz NOT NULL DEFAULT now(),
            finished_at timestamptz
        )""")

    async def run_once(self) -> dict[str, Any]:
        async with self._lock:
            day = datetime.now(_VANCOUVER).date()
            claim_id = uuid.uuid4().hex
            db = await self._db()
            try:
                await self._prepare(db)
                claimed = await db.fetchrow("""INSERT INTO noetfield.corp_revenue_cycles
                   (cycle_date,claim_id) VALUES ($1,$2)
                   ON CONFLICT (cycle_date) DO UPDATE SET
                     claim_id=EXCLUDED.claim_id,attempt_count=noetfield.corp_revenue_cycles.attempt_count+1,
                     state='CLAIMED',attempted_at=now()
                   WHERE noetfield.corp_revenue_cycles.state='FAILED'
                     AND noetfield.corp_revenue_cycles.attempt_count<3
                   RETURNING cycle_date,attempt_count""",day,claim_id)
            finally:
                await db.close()
            if not claimed:
                return {"state": "ALREADY_ATTEMPTED_TODAY", "changed": False}
            try:
                recovered = await recover_intakes(self.settings, execute=True, limit=80)
                plan = await revenue_plan(self.settings)
                completed = int(recovered["imported"])
                failed = int(recovered["failed"])
                due = int(plan["due_count_all"])
                priorities = len(plan["actions"])
                notification = "NOT_CONFIGURED"
                token = _secret(getattr(self.settings, "telegram_ops_bot_token", None))
                chat_id = str(getattr(self.settings, "telegram_ops_chat_id", "") or "").strip()
                if token and chat_id:
                    try:
                        response = await asyncio.to_thread(
                            send_message, token=token, chat_id=chat_id,
                            text=format_private_digest(day.isoformat(),
                                 recovered=completed, failures=failed,
                                 due=due, priority=priorities), parse_mode=None)
                        notification = ("SENT_ACKNOWLEDGED" if isinstance(response, dict)
                                        and response.get("ok") is True else "DELIVERY_UNCONFIRMED")
                    except Exception:
                        logger.exception("corporate_revenue_digest_unconfirmed")
                        notification = "DELIVERY_UNCONFIRMED"
                db = await self._db()
                try:
                    await db.execute("""UPDATE noetfield.corp_revenue_cycles SET
                        state='COMPLETE',recovered_count=$3,failed_count=$4,
                        due_count=$5,priority_count=$6,notification_state=$7,finished_at=now()
                        WHERE cycle_date=$1 AND claim_id=$2""",
                        day,claim_id,completed,failed,due,priorities,notification)
                finally:
                    await db.close()
                logger.info("corporate_revenue_loop=COMPLETE recovered=%s failed=%s due=%s",
                            completed,failed,due)
                return {"state":"COMPLETE", "recovered":completed,
                        "failed":failed, "due":due, "priority_actions":priorities,
                        "notification":notification, "customer_outreach_sent":False}
            except Exception:
                logger.exception("corporate_revenue_loop_failed")
                db = await self._db()
                try:
                    await db.execute("""UPDATE noetfield.corp_revenue_cycles
                        SET state='FAILED', finished_at=now()
                        WHERE cycle_date=$1 AND claim_id=$2""",day,claim_id)
                finally:
                    await db.close()
                return {"state":"FAILED", "changed":False, "retry_bounded":True}

    async def status(self) -> dict[str, Any]:
        db = await self._db()
        try:
            await self._prepare(db)
            row = await db.fetchrow("""SELECT cycle_date, attempt_count, state,
                recovered_count,failed_count,due_count,priority_count,
                notification_state,finished_at
                FROM noetfield.corp_revenue_cycles
                ORDER BY cycle_date DESC LIMIT 1""")
        finally:
            await db.close()
        if row is None:
            return {"configured":enabled(self.settings), "latest":None}
        return {"configured":enabled(self.settings), "latest":{
            "day":row["cycle_date"].isoformat(), "state":row["state"],
            "attempts":row["attempt_count"], "recovered":row["recovered_count"],
            "failed":row["failed_count"], "due":row["due_count"],
            "prioritized":row["priority_count"],
            "notification":row["notification_state"],
            "finished_at":row["finished_at"].isoformat() if row["finished_at"] else None,
        }}


_worker: CorporateRevenueLoop | None = None
_task: asyncio.Task[None] | None = None


def get_worker() -> CorporateRevenueLoop | None:
    return _worker


async def start_scheduler(settings: object) -> None:
    global _worker, _task
    if not enabled(settings):
        logger.info("corporate_revenue_scheduler=DISABLED")
        return
    if _task is not None and not _task.done():
        return
    _worker = CorporateRevenueLoop(settings)
    logger.warning("corporate_revenue_scheduler=ENABLED")

    async def loop() -> None:
        while True:
            try:
                assert _worker is not None
                result = await _worker.run_once()
                # Read the durable PostgreSQL receipt, not just a process-local claim.
                receipt = (await _worker.status()).get("latest") or {}
                logger.warning(
                    "corporate_revenue_cycle_readback state=%s receipt_day=%s "
                    "recovered=%s failed=%s due=%s prioritized=%s "
                    "attempts=%s result=%s",
                    receipt.get("state", "NONE"), receipt.get("day", "NONE"),
                    receipt.get("recovered", 0), receipt.get("failed", 0),
                    receipt.get("due", 0), receipt.get("prioritized", 0),
                    receipt.get("attempts", 0), result.get("state", "UNKNOWN"),
                )
            except Exception:
                logger.exception("corporate_revenue_scheduler_tick_failed")
            await asyncio.sleep(3600)

    _task = asyncio.create_task(loop())


async def stop_scheduler() -> None:
    global _worker, _task
    if _task is not None:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
    _worker = None
