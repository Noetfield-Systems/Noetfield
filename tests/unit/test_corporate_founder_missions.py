"""Founder CRM live mission controller and paid-only E2E bridge acceptance."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import uuid
from unittest.mock import AsyncMock,patch

import pytest
from httpx import ASGITransport,AsyncClient

from noetfield_governance.api import app
from noetfield_governance.corporate_founder_ai import _source_signature
from noetfield_governance.corporate_founder_missions import (
    _plain,compose_review_draft,materialize_missions,founder_mission_board,
)
from noetfield_governance.corporate_workpacket import (
    auto_dispatch_paid_ready_work,WorkPacketError,
)


MODEL={"fit_label":"POSSIBLE_FIT",
    "evidence_phrase":"business automation",
    "reason":"The official description mentions business automation, which could justify a scoped sales-workflow conversation.",
    "buyer_role":"Operations Lead",
    "next_move":"Verify the published partnerships contact and role relevance."}


def source_row(**changes):
    row={"source_key":"fieldwork:source:business-001",
        "organization":"Example Business Systems","lane":"CORPORATE",
        "score":89,"original_url":"https://example.org/our-work",
        "website":"https://example.org","page_url":"https://example.org/",
        "site_title":"Example Business Systems",
        "site_description":"Technology and business automation consulting.",
        "scan_state":"PUBLISHED_GENERAL_BUSINESS_EMAIL",
        "published_general_channel":"partnerships@example.org",
        "channel_evidence_url":"https://example.org/contact",
        "contact_page_url":"https://example.org/contact",
        "team_page_url":"https://example.org/team",
        "scanned_at":"2026-11-17T12:00:00Z",
        "review_status":"DISCOVERED_ACCOUNT",
        "promoted_deal_id":None,"deal_stage":None,"workpacket_state":None,
        "analysis_json":json.dumps(MODEL),
        "model_route":"AGENT_FABRIC_CLOUDFLARE_GLM",
        "artifact_sha256":"a"*64}
    row.update(changes)
    row.setdefault("ai_source_signature",_source_signature(row))
    return row


def test_ai_source_to_real_public_channel_generates_reviewable_draft_not_send():
    out=_plain(source_row())
    assert out["state"]=="INTRO_REVIEW_READY"
    assert out["priority"]>70
    assert out["fit_hypothesis"]=="POSSIBLE_FIT"
    assert out["buyer_role_to_research"]=="Operations Lead"
    assert out["draft"]["to_public_business_channel"]=="partnerships@example.org"
    assert out["draft"]["status"]=="DRAFT_ONLY_NOT_SENT"
    assert "business automation" in out["draft"]["body"]
    assert out["permission_to_send_inferred"] is False
    assert out["email_sent_by_mission"] is False
    assert out["paid_checkout_inferred"] is False
    assert out["source_verified_as_buyer"] is False


def test_wrong_model_source_hash_and_fake_evidence_never_create_outreach_draft():
    old=_plain(source_row(ai_source_signature="0"*64))
    assert old["state"]=="AGENT_RESEARCH_PENDING"
    assert old["draft"] is None
    fake={**MODEL,"evidence_phrase":"we require a $500,000 contract today"}
    forged=_plain(source_row(analysis_json=json.dumps(fake)))
    assert forged["state"]=="AGENT_RESEARCH_PENDING"
    assert forged["draft"] is None


def test_suppression_and_verified_delivery_are_separate_canonical_states():
    suppressed=_plain(source_row(review_status="DO_NOT_CONTACT"))
    assert suppressed["state"]=="SUPPRESSED" and not suppressed["draft"]
    paid=_plain(source_row(promoted_deal_id=uuid.uuid4(),
                   workpacket_state="ACKNOWLEDGED"))
    assert paid["state"]=="DELIVERY_IN_PROGRESS"
    assert paid["customer_acceptance_inferred"] is False
    delivered=_plain(source_row(promoted_deal_id=uuid.uuid4(),
                   workpacket_state="VERIFIED"))
    assert delivered["state"]=="VERIFIED_DELIVERY"
    assert delivered["customer_acceptance_inferred"] is False


def test_research_without_contact_or_model_explains_specific_next_move():
    row=source_row(analysis_json="",published_general_channel="",
                   contact_page_url="",team_page_url="")
    assert _plain(row)["state"]=="AGENT_RESEARCH_PENDING"
    site=source_row(analysis_json="",scanned_at=None)
    assert _plain(site)["state"]=="SOURCE_RESEARCH_PENDING"
    no_site=source_row(scan_state="NO_USABLE_WEBSITE",analysis_json="")
    assert _plain(no_site)["state"]=="OFFICIAL_SOURCE_NEEDED"
    assert compose_review_draft(row,{"evidence_phrase":""}) is None


def test_paid_auto_dispatch_fails_closed_without_live_source_bound_payment():
    async def run():
        db=AsyncMock()
        db.fetch.return_value=[]
        with patch("noetfield_governance.corporate_workpacket.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.corporate_workpacket.prepare_workpackets",
             new_callable=AsyncMock),patch(
             "noetfield_governance.corporate_workpacket._database_url",
             return_value="postgresql://test"),patch(
             "noetfield_governance.corporate_workpacket.dispatch_paid_workpacket",
             new_callable=AsyncMock) as dispatch:
            result=await auto_dispatch_paid_ready_work(object(),limit=3)
        assert result["eligible_paid_cases"]==0
        assert result["dispatch_acknowledged"]==0
        assert result["unpaid_work_dispatched"]==0
        dispatch.assert_not_awaited()
        query=db.fetch.await_args.args[0]
        assert "e.livemode IS TRUE" in query
        assert "e.reversed IS FALSE" in query
        assert "e.bound_at IS NOT NULL" in query
        assert "acceptance_evidence" in query
        assert "payment_event_id" in query
        assert "dispatch_attempts < 3" in query
    asyncio.run(run())
    with pytest.raises(WorkPacketError):
        asyncio.run(auto_dispatch_paid_ready_work(object(),limit=99))


def test_real_paid_eligible_jobs_use_canonical_idempotent_dispatcher_only():
    ids=[str(uuid.uuid4()),str(uuid.uuid4())]
    async def run():
        db=AsyncMock()
        db.fetch.return_value=[{"deal_id":uuid.UUID(x)} for x in ids]
        async def fake(settings,*,deal_id):
            return {"state":"ACKNOWLEDGED","provider_acknowledged":True} if deal_id==ids[0] else {
                "state":"READY","dispatch_state":"PROVIDER_CONTRACT_NOT_CONFIGURED",
                "provider_acknowledged":False}
        with patch("noetfield_governance.corporate_workpacket.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.corporate_workpacket.prepare_workpackets",
             new_callable=AsyncMock),patch(
             "noetfield_governance.corporate_workpacket._database_url",
             return_value="postgresql://test"),patch(
             "noetfield_governance.corporate_workpacket.dispatch_paid_workpacket",
             new_callable=AsyncMock,side_effect=fake) as dispatch:
            result=await auto_dispatch_paid_ready_work(object(),limit=2)
        assert dispatch.await_count==2
        assert result["eligible_paid_cases"]==2
        assert result["dispatch_acknowledged"]==1
        assert result["blocked_or_unconfirmed"]==1
        assert result["state"]=="PARTIAL_OR_BLOCKED"
        assert result["delivery_verified"]==0
        assert result["customer_acceptance_inferred"]==0
    asyncio.run(run())


def test_private_founder_missions_endpoint_and_refresh_are_protected():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),
                               base_url="http://test") as c:
            assert (await c.get("/api/corporate-crm/founder/missions")).status_code in (403,503)
            assert (await c.post("/api/corporate-crm/founder/missions/refresh")).status_code in (403,503)
        report={"schema":"noetfield.founder-mission-board.v1","missions":[],
                "states":{"INTRO_REVIEW_READY":0}}
        refreshed={"state":"COMPLETE","scanned":2,"created_or_changed":1}
        with patch("noetfield_governance.api._require_connect_desk_operator",
                   return_value=None),patch(
             "noetfield_governance.corporate_founder_missions.founder_mission_board",
             new_callable=AsyncMock,return_value=report),patch(
             "noetfield_governance.corporate_founder_missions.materialize_missions",
             new_callable=AsyncMock,return_value=refreshed):
            async with AsyncClient(transport=ASGITransport(app=app),
                                  base_url="http://test") as c:
                assert (await c.get("/api/corporate-crm/founder/missions")).json()==report
                assert (await c.post("/api/corporate-crm/founder/missions/refresh")).json()==refreshed
    asyncio.run(run())


@pytest.mark.skipif(not os.getenv("CONNECT_TEST_POSTGRES_URL"),reason="Disposable PostgreSQL required")
def test_real_postgres_one_evidence_one_idempotent_mission_and_no_fake_deal(monkeypatch):
    import asyncpg
    from noetfield_governance.corporate_founder_missions import prepare_missions
    async def run():
        url=os.environ["CONNECT_TEST_POSTGRES_URL"]
        key="founder:mission:test:"+uuid.uuid4().hex
        db=await asyncpg.connect(url)
        try:
            await db.execute("CREATE SCHEMA IF NOT EXISTS noetfield")
            await prepare_missions(db)
            official="https://example.org/case/"+uuid.uuid4().hex
            row=source_row(source_key=key,score=100,original_url=official)
            signature=_source_signature(row)
            await db.execute("""INSERT INTO noetfield.corp_research_sources(
              source_key,organization,lane,original_url,website,evidence_url,
              review_status,score)
              VALUES($1,'Example Business Systems','CORPORATE',$2,
               'https://example.org',$2,'PROFILE_REVIEWED',100)""",
               key,official)
            await db.execute("""INSERT INTO noetfield.corp_founder_scout(
              source_key,page_url,site_title,site_description,
              published_general_channel,channel_evidence_url,
              contact_page_url,scan_state)
              VALUES($1,$2,$3,$4,$5,$6,$6,'PUBLISHED_GENERAL_BUSINESS_EMAIL')""",
              key,row["page_url"],row["site_title"],row["site_description"],
              row["published_general_channel"],row["channel_evidence_url"])
            await db.execute("""INSERT INTO noetfield.corp_founder_ai(
              source_key,source_signature,analysis_json,model,generation_id,
              model_route,artifact_sha256)
              VALUES($1,$2,$3,'glm-test','gen-test','AGENT_FABRIC_CLOUDFLARE_GLM',$4)""",
              key,signature,json.dumps(MODEL),"a"*64)
        finally:
            await db.close()
        with patch("noetfield_governance.corporate_founder_missions._database_url",
                   return_value=url):
            first=await materialize_missions(object(),limit=150)
            again=await materialize_missions(object(),limit=150)
            board=await founder_mission_board(object(),limit=40)
        assert first["state"]=="COMPLETE"
        assert again["created_or_changed"]==0
        assert any(m["source_key"]==key and m["state"]=="INTRO_REVIEW_READY"
                   for m in board["missions"])
        db=await asyncpg.connect(url)
        try:
            assert await db.fetchval("""SELECT count(*)::int
               FROM noetfield.corp_founder_mission_events
               WHERE source_key=$1""",key)==1
            assert await db.fetchval("""SELECT count(*)::int FROM
               noetfield.corp_crm_deals WHERE summary LIKE $1""","%"+key+"%")==0
        finally:await db.close()
    asyncio.run(run())


def test_founder_cockpit_responsive_text_without_manual_primary_work():
    from pathlib import Path
    html=(Path(__file__).resolve().parents[2]/
        "services/governance/noetfield_governance/private_corporate_crm.html").read_text()
    assert 'id="founder-missions-list"' in html
    assert 'id="founder-missions-status"' in html
    assert "What your AI team is doing next" in html
    assert "Copy prepared introduction" in html
    assert "No message sent." in html
    assert ".founder-mission-list{grid-template-columns:repeat(2" in html
    assert "/api/corporate-crm/founder/missions?limit=12" in html
