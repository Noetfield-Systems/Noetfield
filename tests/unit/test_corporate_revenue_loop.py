"""Idempotent daily corporate revenue automation, no direct buyer outreach."""
import asyncio
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app
from noetfield_governance.corporate_revenue_loop import (
    CorporateRevenueLoop, enabled, format_private_digest,
)


def test_cycle_requires_explicit_enablement_and_canonical_crm_bootstrap(monkeypatch):
    monkeypatch.delenv("CORPORATE_REVENUE_LOOP_ENABLED", raising=False)
    monkeypatch.setenv("NOETFIELD_CORPORATE_CRM_BOOTSTRAP_ENABLED", "1")
    settings=SimpleNamespace(database_url="postgresql://localhost/unused")
    assert not enabled(settings)
    monkeypatch.setenv("CORPORATE_REVENUE_LOOP_ENABLED", "1")
    assert enabled(settings)
    monkeypatch.setenv("NOETFIELD_CORPORATE_CRM_BOOTSTRAP_ENABLED", "0")
    assert not enabled(settings)


def test_private_digest_reports_counts_not_customers_or_unverified_revenue():
    body=format_private_digest("2026-11-16",recovered=2,failures=1,due=3,priority=4)
    assert "Historical source imports: 2" in body
    assert "CRM follow-ups due: 3" in body
    assert "NOT customer outreach" in body
    assert "paid orders" in body
    assert "@" not in body


def test_daily_cycle_is_idempotent_and_has_no_customer_send():
    settings=SimpleNamespace(database_url="postgresql://localhost/unused",
                             telegram_ops_bot_token="",telegram_ops_chat_id="")
    db=AsyncMock()
    db.fetchrow.return_value={"cycle_date":date(2026,11,16),"attempt_count":1}
    worker=CorporateRevenueLoop(settings)
    async def run():
        with patch.object(worker,"_db",new_callable=AsyncMock,return_value=db), \
             patch("noetfield_governance.corporate_revenue_loop.recover_intakes",
                   new_callable=AsyncMock,
                   return_value={"imported":2,"failed":0}) as rec, \
             patch("noetfield_governance.corporate_revenue_loop.revenue_plan",
                   new_callable=AsyncMock,
                   return_value={"due_count_all":3,"actions":[{},{}]}) as plan, \
             patch("noetfield_governance.corporate_revenue_loop.send_message") as send:
            result=await worker.run_once()
            assert result["state"] == "COMPLETE"
            assert result["recovered"]==2 and result["due"]==3
            assert result["customer_outreach_sent"] is False
            assert result["notification"]=="NOT_CONFIGURED"
            assert rec.await_args.kwargs["execute"] is True
            assert plan.await_count == 1
            send.assert_not_called()
            db.fetchrow.return_value=None
            duplicate=await worker.run_once()
            assert duplicate["state"]=="ALREADY_ATTEMPTED_TODAY"
            assert rec.await_count == 1
    asyncio.run(run())


def test_operator_cycle_api_denied_to_guest():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            a=await client.get("/api/corporate-crm/operations/cycle-status")
            b=await client.post("/api/corporate-crm/operations/run-cycle")
            assert a.status_code in (403,503)
            assert b.status_code in (403,503)
        fake=SimpleNamespace(
            status=AsyncMock(return_value={"configured":True,"latest":{"state":"COMPLETE"}}),
            run_once=AsyncMock(return_value={"state":"ALREADY_ATTEMPTED_TODAY","changed":False}))
        with patch("noetfield_governance.api._require_connect_desk_operator",return_value=None),\
             patch("noetfield_governance.api.get_corporate_revenue_worker",return_value=fake):
            async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
                status=await client.get("/api/corporate-crm/operations/cycle-status")
                run=await client.post("/api/corporate-crm/operations/run-cycle")
            assert status.status_code==200
            assert run.status_code==200
            assert run.json()["changed"] is False
    asyncio.run(run())
