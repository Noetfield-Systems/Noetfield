"""Real PostgreSQL acceptance for persisted Noetfield Connect opportunity updates.

Runs against disposable PostgreSQL in GitHub Actions; never writes to live leads.
"""
from __future__ import annotations

import asyncio
import json
import os
from datetime import date

import asyncpg
import pytest

from noetfield_governance.postgres_intake_store import PostgresIntakeStore
from noetfield_governance.opportunity_desk import triage_connect_record


@pytest.mark.skipif(not os.getenv("CONNECT_TEST_POSTGRES_URL"), reason="Disposable PostgreSQL URL required")
def test_actual_database_state_and_revision_locking():
    async def run() -> None:
        url = os.environ["CONNECT_TEST_POSTGRES_URL"]
        con = await asyncpg.connect(url)
        try:
            await con.execute("CREATE SCHEMA IF NOT EXISTS noetfield")
            await con.execute("""CREATE TABLE IF NOT EXISTS noetfield.public_intakes (
                intake_id text PRIMARY KEY,
                metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
                qualification_json jsonb
            )""")
            await con.execute("""INSERT INTO noetfield.public_intakes
                (intake_id, metadata, qualification_json)
                VALUES ($1, $2::jsonb, $3::jsonb)""",
                "INT-ABCDEF123456",
                json.dumps({"form_id": "nfConnectWizard", "topic": "growth",
                            "connect_ops": {"stage": "WON", "owner": "Forged browser"} }),
                json.dumps({"tier": "existing-server-data"}),
            )
            await con.execute("""INSERT INTO noetfield.public_intakes (intake_id, metadata)
                VALUES ('INT-OTHER123456', '{"form_id":"unrelated"}'::jsonb)""")
        finally:
            await con.close()

        store = PostgresIntakeStore(url)
        try:
            first = await store.update_connect_state(
                intake_id="INT-ABCDEF123456", expected_revision=0,
                stage="QUALIFYING", owner="Founder", next_action="Verify terms",
                due_date="2026-11-19", note="Review proposed referral structure",
            )
            assert first is not None
            assert first["revision"] == 1
            assert first["stage"] == "QUALIFYING"
            assert first["owner"] == "Founder"
            assert len(first["history"]) == 1
            second = await store.update_connect_state(
                intake_id="INT-ABCDEF123456", expected_revision=1,
                stage="ENGAGED", owner="Founder", next_action="Send scoped response",
                due_date="2026-11-22", note="Received business model details",
            )
            assert second is not None
            assert second["revision"] == 2
            assert len(second["history"]) == 2
            with pytest.raises(ValueError, match="OPPORTUNITY_VERSION_CONFLICT"):
                await store.update_connect_state(
                    intake_id="INT-ABCDEF123456", expected_revision=1,
                    stage="WON", owner="Nobody", next_action="",
                    due_date=None, note="Outdated concurrent change",
                )
            assert await store.update_connect_state(
                intake_id="INT-OTHER123456", expected_revision=0,
                stage="NEW", owner="", next_action="", due_date=None, note="",
            ) is None
            assert await store.update_connect_state(
                intake_id="INT-MISSING1234", expected_revision=0,
                stage="NEW", owner="", next_action="", due_date=None, note="",
            ) is None
        finally:
            await store.close()

        con = await asyncpg.connect(url)
        try:
            raw = await con.fetchrow(
                "SELECT metadata,qualification_json FROM noetfield.public_intakes WHERE intake_id=$1",
                "INT-ABCDEF123456",
            )
            original = dict(json.loads(raw["metadata"]))
            persisted = dict(json.loads(raw["qualification_json"]))
            assert original["connect_ops"]["stage"] == "WON"  # Forged client metadata untrusted
            assert persisted["tier"] == "existing-server-data"  # No destructive overwrite
            assert persisted["connect_ops"]["stage"] == "ENGAGED"
            assert persisted["connect_ops"]["revision"] == 2
            projected = triage_connect_record({
                "intake_id": "INT-ABCDEF123456",
                "metadata": original, "qualification_json": persisted,
            }, today=date(2026,11,12))
            assert projected["owner"] == "Founder"
            assert projected["stage"] == "ENGAGED"
            assert projected["revision"] == 2
            assert projected["cash_collected"] is None
        finally:
            await con.close()
    asyncio.run(run())
