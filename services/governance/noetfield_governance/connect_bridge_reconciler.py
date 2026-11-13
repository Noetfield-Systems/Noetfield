"""Reliable, replay-safe Connect -> WorkforceOS reconciliation on existing Platform PostgreSQL.

No duplicate CRM, no synthetic leads, no new Railway service. The canonical
public_intakes table owns records. This ledger stores ONLY delivery metadata.
A source consent and test check is repeated before every attempted handoff.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

import asyncpg

from noetfield_governance import intake_repository
from noetfield_governance.intake_test import is_test_intake
from noetfield_governance.workforce_connect_bridge import deliver, eligible

logger = logging.getLogger("noetfield.connect.reconciler")
_LOCK_ID = 614220113
_MAX_BATCH = 20


def backoff_seconds(attempts: int) -> int:
    """Bounded exponential retry: 60s, 120s, ... 1h."""
    return min(3600, 60 * (2 ** min(max(attempts - 1, 0), 6)))


def configured(settings: object) -> bool:
    return (
        str(os.getenv("CONNECT_BRIDGE_RECONCILE_ENABLED", "true")).lower()
        not in {"0", "false", "no", "off"}
        and bool(getattr(settings, "public_intake_enabled", False))
        and len(os.getenv("WORKFORCE_CONNECT_BRIDGE_KEY", "")) >= 32
        and os.getenv("WORKFORCE_CONNECT_BRIDGE_URL", "").startswith("https://")
        and bool(str(getattr(settings, "database_url", "") or ""))
    )


class ConnectBridgeReconciler:
    def __init__(self, database_url: str):
        self.database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self.pool: asyncpg.Pool | None = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        if self.pool is not None:
            return
        self.pool = await asyncpg.create_pool(self.database_url, min_size=1, max_size=2)
        async with self.pool.acquire() as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.connect_workforce_delivery (
                source_intake_id text PRIMARY KEY,
                state text NOT NULL,
                attempts integer NOT NULL DEFAULT 0,
                source_case_id text,
                last_error text,
                attempted_at timestamptz NOT NULL DEFAULT now(),
                next_retry_at timestamptz NOT NULL DEFAULT now(),
                acknowledged_at timestamptz,
                updated_at timestamptz NOT NULL DEFAULT now()
            )""")
            await db.execute("""CREATE INDEX IF NOT EXISTS connect_workforce_delivery_retry_idx
                ON noetfield.connect_workforce_delivery(state,next_retry_at)""")

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def run_once(self) -> dict[str, object]:
        async with self._lock:
            await self.connect()
            assert self.pool is not None
            async with self.pool.acquire() as db:
                # PostgreSQL advisory lock prevents simultaneous Railway instances
                # from racing. Our case importer is independently idempotent too.
                lock = await db.fetchval("SELECT pg_try_advisory_lock($1)", _LOCK_ID)
                if not lock:
                    return {"state": "ALREADY_RUNNING", "scanned": 0, "acknowledged": 0}
                try:
                    # Pick oldest unacknowledged CANONICAL sources, across all
                    # dates. Consent/venture filters are an optimization only;
                    # Python repeats authoritative eligibility before delivery.
                    rows = await db.fetch("""SELECT p.intake_id, p.request_id,
                             coalesce(d.attempts,0) AS attempts
                          FROM noetfield.public_intakes p
                          LEFT JOIN noetfield.connect_workforce_delivery d
                            ON d.source_intake_id=p.intake_id
                          WHERE ((p.vector='external-opportunities'
                                  AND p.metadata->>'category'='people'
                                  AND p.metadata->>'consent_contact'='true'
                                  AND coalesce(p.metadata->>'initiative','')<>'trustfield')
                            OR (p.vector='work-with-us-contributor'
                                AND p.metadata->>'consent_contact'='true'
                                AND p.metadata->>'application_kind'
                                    IN ('human','agent','organization')))
                            AND (d.source_intake_id IS NULL OR
                                 (d.state='RETRY' AND d.next_retry_at<=now()))
                          ORDER BY p.created_at ASC,p.intake_id ASC
                          LIMIT $1""", _MAX_BATCH)
                    acked = 0
                    retrying = 0
                    skipped = 0
                    for row in rows:
                        source_id, rid = row["intake_id"], row["request_id"]
                        try:
                            record = (await intake_repository.get_by_request_id(str(rid))
                                      if rid else None)
                            if (not record or record.intake_id != source_id or
                                    not eligible(record) or
                                    is_test_intake(metadata=record.metadata,
                                                   request_id=record.request_id,
                                                   contact_email=record.contact_email)):
                                # Excludes test/non-consented records permanently;
                                # missing source RID is visible for intervention.
                                state = "SKIPPED_TEST_OR_INELIGIBLE" if record else "SOURCE_NEEDS_REVIEW"
                                await self._save(db, source_id, state, int(row["attempts"]) + 1,
                                                 "", "SOURCE_NOT_ELIGIBLE_OR_MISSING", 3600)
                                skipped += 1
                                continue
                            result = await asyncio.to_thread(deliver, record)
                            if result.get("delivered") and result.get("source_intake_id") == source_id:
                                await self._save(db, source_id, "ACKED", int(row["attempts"]) + 1,
                                                 str(result.get("case_id") or ""), "", 0)
                                acked += 1
                            else:
                                attempts = int(row["attempts"]) + 1
                                await self._save(db, source_id, "RETRY", attempts, "",
                                                 str(result.get("error") or "NO_ACK")[:100],
                                                 backoff_seconds(attempts))
                                retrying += 1
                        except Exception as exc:
                            attempts = int(row["attempts"]) + 1
                            logger.exception("connect_bridge_reconcile_error source_id=%s", source_id)
                            await self._save(db, source_id, "RETRY", attempts, "",
                                             type(exc).__name__[:100],
                                             backoff_seconds(attempts))
                            retrying += 1
                    if rows:
                        logger.info("connect_bridge_reconcile scanned=%s acked=%s retry=%s skip=%s",
                                    len(rows), acked, retrying, skipped)
                    return {"state": "COMPLETE", "scanned": len(rows),
                            "acknowledged": acked, "retrying": retrying, "skipped": skipped}
                finally:
                    await db.execute("SELECT pg_advisory_unlock($1)", _LOCK_ID)

    @staticmethod
    async def _save(db: object, source_id: str, state: str,
                    attempts: int, case_id: str, error: str, delay_sec: int) -> None:
        await db.execute("""INSERT INTO noetfield.connect_workforce_delivery
                (source_intake_id,state,attempts,source_case_id,last_error,
                 attempted_at,next_retry_at,acknowledged_at,updated_at)
              VALUES ($1,$2,$3,$4,$5,now(),now()+($6*interval '1 second'),
                      CASE WHEN $2='ACKED' THEN now() ELSE NULL END,now())
              ON CONFLICT (source_intake_id) DO UPDATE SET
                state=EXCLUDED.state, attempts=EXCLUDED.attempts,
                source_case_id=EXCLUDED.source_case_id,
                last_error=EXCLUDED.last_error,
                attempted_at=now(),next_retry_at=EXCLUDED.next_retry_at,
                acknowledged_at=EXCLUDED.acknowledged_at,updated_at=now()""",
                         source_id, state, attempts, case_id or None, error or None,
                         delay_sec)

    async def status(self) -> dict[str, object]:
        await self.connect()
        assert self.pool is not None
        async with self.pool.acquire() as db:
            rows = await db.fetch("""SELECT state, count(*)::int AS total
                     FROM noetfield.connect_workforce_delivery GROUP BY state""")
            last = await db.fetchrow("""SELECT source_intake_id,state,attempts,attempted_at
                      FROM noetfield.connect_workforce_delivery
                      ORDER BY attempted_at DESC LIMIT 1""")
        return {"configured": True, "delivery_states": {r["state"]: r["total"] for r in rows},
                "last_attempt": ({
                    "source_intake_id": last["source_intake_id"], "state": last["state"],
                    "attempts": last["attempts"],
                    "at": last["attempted_at"].isoformat(),
                } if last else None),
                "scope": "source_intake_id delivery only; no applicant PII or receipts"}


_worker: ConnectBridgeReconciler | None = None
_task: asyncio.Task[None] | None = None


def get_worker() -> ConnectBridgeReconciler | None:
    return _worker


async def start_scheduler(settings: object) -> None:
    global _worker, _task
    if not configured(settings):
        logger.info("connect_bridge_reconciler=DISABLED_OR_UNCONFIGURED")
        return
    if _task is not None and not _task.done():
        return
    _worker = ConnectBridgeReconciler(str(getattr(settings, "database_url")))
    async def loop() -> None:
        while True:
            try:
                assert _worker is not None
                await _worker.run_once()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("connect_bridge_reconciler_tick_failed")
            await asyncio.sleep(300)
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
    if _worker:
        await _worker.close()
        _worker = None
