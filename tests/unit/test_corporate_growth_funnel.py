"""Read-only commercial growth funnel tests: metrics never manufacture outreach or cash."""
import asyncio
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app
from noetfield_governance.corporate_growth_funnel import (
    STAGE_EVIDENCE, growth_funnel_snapshot,
)


def test_independent_source_email_and_payment_stages_are_explicit():
    assert "research" in STAGE_EVIDENCE
    assert "qualified_contacts" in STAGE_EVIDENCE
    assert "verified_replies" in STAGE_EVIDENCE
    assert "meetings_held_documented" in STAGE_EVIDENCE
    assert "independently_verified_deliveries" in STAGE_EVIDENCE
    assert "customer_acceptances" in STAGE_EVIDENCE
    assert "not inbox delivery" in STAGE_EVIDENCE["smtp_accepted"]
    assert "not provider attested" in STAGE_EVIDENCE["meetings_booked_documented"]


def test_funnel_snapshot_uses_database_evidence_not_defaults_or_mock_outcomes():
    class FakeDB:
        def __init__(self):
            self.queries = []
            self.closed = False
        async def fetchrow(self, statement, *args):
            self.queries.append((statement, args))
            return {key: (91 if key=="research" else 88 if key=="research_pending_review"
                          else 3 if key=="qualified_contacts" else 0)
                    for key in STAGE_EVIDENCE if key!="paid_live_checkouts"} | {
                        "research_pending_review": 88
                    }
        async def fetch(self, statement, *args):
            self.queries.append((statement, args))
            if "GROUP BY lane" in statement:
                return [{"lane":"CORPORATE","research":61,"promoted":2},
                        {"lane":"RWA","research":30,"promoted":1}]
            if "LIMIT $1" in statement:
                return [{"source_key":"FW:TEST-1","organization":"Actual source example",
                         "lane":"RWA","score":72,"review_status":"DISCOVERED_ACCOUNT",
                         "original_url":"https://example.org/companies/acme",
                         "evidence_url":"https://example.org/companies/acme"}]
            return []
        async def close(self):
            self.closed = True

    async def check():
        db=FakeDB()
        with patch("noetfield_governance.corporate_growth_funnel.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db), patch(
            "noetfield_governance.corporate_growth_funnel._database_url",
            return_value="postgresql://test"), patch(
            "noetfield_governance.corporate_growth_funnel.prepare_research",
            new_callable=AsyncMock), patch(
            "noetfield_governance.corporate_growth_funnel.prepare_outreach",
            new_callable=AsyncMock), patch(
            "noetfield_governance.corporate_growth_funnel.prepare_workpackets",
            new_callable=AsyncMock):
            result=await growth_funnel_snapshot(object(),limit=12)
        assert db.closed is True
        assert result["stages"]["research"]==91
        assert result["stages"]["research_pending_review"]==88
        assert result["stages"]["qualified_contacts"]==3
        assert result["stages"]["smtp_accepted"]==0
        assert result["stages"]["paid_live_checkouts"]==0
        assert result["paid_checkout_amount_minor_by_currency"]=={}
        assert result["cash_settled_in_bank"]=="NOT_MEASURED"
        assert result["priority_source_review"][0]["source_key"]=="FW:TEST-1"
        assert result["automatic_email_sent"] is False
        pay_sql=next(x for x,params in db.queries if "e.payment_link_id=$1" in x)
        assert "e.reversed=false" in pay_sql
        assert "e.bound_at IS NOT NULL" in pay_sql
        assert "e.livemode=true" in pay_sql
        assert "e.payment_event_id" not in pay_sql  # no nonexistent column referenced
        closed_sql=next(x for x,params in db.queries if "closed_paid_engagements" in x)
        assert "w.state='VERIFIED'" in closed_sql
        assert "corp_workpacket_acceptances" in closed_sql
    asyncio.run(check())


def test_growth_endpoint_private_and_returns_actual_snapshot_only():
    async def check():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            denied=await client.get("/api/corporate-crm/growth/funnel")
            assert denied.status_code in (403,503)
        with patch("noetfield_governance.api._require_connect_desk_operator",
                   return_value=None),patch(
            "noetfield_governance.corporate_growth_funnel.growth_funnel_snapshot",
            new_callable=AsyncMock,return_value={
                "schema":"noetfield.corporate-growth-funnel.v1",
                "stages":{"research":91,"paid_live_checkouts":0},
                "automatic_email_sent":False,
            }) as worker:
            async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
                accepted=await client.get("/api/corporate-crm/growth/funnel?limit=8")
            assert accepted.status_code==200
            assert accepted.json()["stages"]["paid_live_checkouts"]==0
            assert worker.await_args.kwargs["limit"]==8
    asyncio.run(check())


def test_live_crm_renders_growth_metrics_without_claiming_automated_contact():
    from pathlib import Path
    html=(Path(__file__).resolve().parents[2]/
          "services/governance/noetfield_governance/private_corporate_crm.html").read_text()
    assert 'id="growth-funnel"' in html
    assert "/api/corporate-crm/growth/funnel" in html
    assert "refreshGrowthFunnel()" in html
    assert "a draft artifact is not a delivered engagement" in html
    assert "permission before promoting" in html
