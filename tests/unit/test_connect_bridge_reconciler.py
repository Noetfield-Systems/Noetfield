"""Contract tests for the existing-Postgres Connect recovery scheduler.

Tests exercise ACK, rejection, retry scheduling and explicit test exclusion.
No real webhook, email, applicant or external side effect.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from noetfield_governance.connect_bridge_reconciler import (
    ConnectBridgeReconciler, backoff_seconds, configured)
from noetfield_governance.intake_store import IntakeRecord


class FakeDB:
    def __init__(self, rows):
        self.rows = rows
        self.writes = []
        self.locked = False

    async def fetchval(self, query, *args):
        if "pg_try_advisory_lock" in query:
            if self.locked:
                return False
            self.locked = True
            return True
        return None

    async def fetch(self, query, *args):
        return self.rows

    async def execute(self, query, *args):
        self.writes.append((query, args))
        return "OK"


class FakeAcquire:
    def __init__(self, db):
        self.db = db

    async def __aenter__(self):
        return self.db

    async def __aexit__(self, *args):
        return False


class FakePool:
    def __init__(self, db):
        self.db = db

    def acquire(self):
        return FakeAcquire(self.db)


def source(metadata=None, email="alex@volunteer.org", rid="RID-NF-ABCDEF987654"):
    return IntakeRecord(intake_id="INT-ABCDEF987654", request_id=rid,
                        contact_name="Alex Example", contact_email=email,
                        organization="Indie", message="I can ship an API with tests and evidence.",
                        sku="general", vector="external-opportunities", source="web",
                        created_at="2026-11-13T00:00:00Z",
                        metadata=metadata or {"category": "people",
                                             "consent_contact": True,
                                             "initiative": "workforce"})


def test_retry_backoff_and_configuration_fail_closed():
    assert [backoff_seconds(n) for n in (1, 2, 3, 9)] == [60, 120, 240, 3600]
    settings = SimpleNamespace(public_intake_enabled=True, database_url="postgresql://localhost/test")
    with patch.dict("os.environ", {"WORKFORCE_CONNECT_BRIDGE_URL": "",
                                   "WORKFORCE_CONNECT_BRIDGE_KEY": ""}):
        assert not configured(settings)
    with patch.dict("os.environ", {"WORKFORCE_CONNECT_BRIDGE_URL": "https://workforce.example.org",
                                   "WORKFORCE_CONNECT_BRIDGE_KEY": "x" * 48}):
        assert configured(settings)


def test_source_backed_ack_write_never_creates_another_intake():
    async def run():
        db = FakeDB([{"intake_id": "INT-ABCDEF987654",
                      "request_id": "RID-NF-ABCDEF987654", "attempts": 0}])
        worker = ConnectBridgeReconciler("postgresql://localhost/test")
        worker.pool = FakePool(db)
        with patch("noetfield_governance.connect_bridge_reconciler.intake_repository.get_by_request_id",
                   new_callable=AsyncMock, return_value=source()) as get:
            with patch("noetfield_governance.connect_bridge_reconciler.deliver",
                       return_value={"delivered": True, "source_intake_id": "INT-ABCDEF987654",
                                     "case_id": "opp_nf_aaaaaaaaaaaaaaaaaaaaaaaa"}):
                result = await worker.run_once()
        assert result["acknowledged"] == 1
        assert result["retrying"] == 0
        assert get.await_count == 1
        writes = [args for sql, args in db.writes if "connect_workforce_delivery" in sql]
        assert len(writes) == 1
        assert writes[0][0] == "INT-ABCDEF987654"
        assert writes[0][1] == "ACKED"
        assert writes[0][3] == "opp_nf_aaaaaaaaaaaaaaaaaaaaaaaa"
        assert all("INSERT INTO noetfield.public_intakes" not in sql for sql, _ in db.writes)
        assert any("pg_advisory_unlock" in sql for sql, _ in db.writes)
    asyncio.run(run())


def test_retry_not_lost_and_synthetic_intake_excluded():
    async def run():
        for test_email, expected in [("alex@volunteer.org", "RETRY"),
                                     ("probe@example.invalid", "SKIPPED_TEST_OR_INELIGIBLE")]:
            db = FakeDB([{"intake_id": "INT-ABCDEF987654",
                          "request_id": "RID-NF-ABCDEF987654",
                          "attempts": 3}])
            worker = ConnectBridgeReconciler("postgresql://localhost/test")
            worker.pool = FakePool(db)
            with patch("noetfield_governance.connect_bridge_reconciler.intake_repository.get_by_request_id",
                       new_callable=AsyncMock, return_value=source(email=test_email)):
                with patch("noetfield_governance.connect_bridge_reconciler.deliver",
                           return_value={"delivered": False, "error": "UPSTREAM_HTTP_FAILURE"}) as sent:
                    await worker.run_once()
            writes = [args for sql, args in db.writes if "connect_workforce_delivery" in sql]
            assert len(writes) == 1
            assert writes[0][1] == expected
            assert writes[0][2] == 4
            if expected == "RETRY":
                assert writes[0][-1] == 480
                sent.assert_called_once()
            else:
                sent.assert_not_called()
    asyncio.run(run())
