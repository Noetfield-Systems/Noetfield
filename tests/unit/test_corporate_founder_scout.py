"""Founder scout acceptance: no invented buyers, public-source evidence and bounded work."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app
from noetfield_governance.corporate_founder_scout import (
    _source_url, _page_summary, _priority, fetch_official_signals,
    run_scout_batch, founder_scout_board,
)


def test_only_original_public_https_company_websites_are_valid():
    assert _source_url("https://www.example.org/about?utm=source")=="https://www.example.org/about"
    for host in ("http://example.org", "https://127.0.0.1/admin",
                 "https://localhost.localdomain", "https://metadata.internal/health",
                 "https://username:pass@example.org", "https://example.org:444/admin",
                 "https://example.org.evil.local", "https://[::1]/",
                 "https://example.org/?redirect=https://127.0.0.1"):
        if host.startswith("https://example.org/?"):
            # Tracking queries are discarded before the request.
            assert _source_url(host)=="https://example.org/"
        else:
            assert _source_url(host)==""


def test_published_generic_mailbox_is_not_made_up_person_or_permission():
    page='''<html><head><title>Example &amp; Co.</title>
     <meta name="description" content="Business process and sales operations"></head>
     <body><a href="mailto:founder@example.org">Personal founder mailbox</a>
      <a href="mailto:partnerships@example.org?subject=Hi">Partnerships</a>
      <a href="/contact">Contact team</a><a href="/team">Leadership team</a>
      <a href="https://evil.example.net/contact">Outside URL</a></body></html>'''
    result=_page_summary("https://www.example.org/",page)
    assert result["title"]=="Example & Co."
    assert result["public_channel"]=="partnerships@example.org"
    assert result["contact_url"]=="https://www.example.org/contact"
    assert result["team_url"]=="https://www.example.org/team"
    assert result["scan_state"]=="PUBLISHED_GENERAL_BUSINESS_EMAIL"
    assert "founder@example.org" not in str(result)
    assert "evil.example.net" not in str(result)


def test_first_party_contact_page_is_research_not_a_verified_person():
    page='<a href="/contact-us">Reach our sales team</a><a href="/leadership">Team</a>'
    out=_page_summary("https://example.org/",page)
    assert out["scan_state"]=="NO_CHANNEL_OBSERVED" or out["team_url"]
    card=_priority({"source_key":"sme:source:1","organization":"Company One",
        "lane":"CORPORATE","score":87,"original_url":"https://example.org"})
    assert card["contact_verified_person"] is False
    assert card["customer_qualified"] is False
    assert card["email_sent"] is False
    assert card["paid"] is False
    assert card["recommendation_basis"]=="ORIGINAL_SOURCE_ONLY"
    assert "AI Sales OS" in card["offer_hypothesis"]


def test_no_website_does_not_fallback_to_arbitrary_github_source():
    async def case():
        r=await fetch_official_signals("")
        assert r["scan_state"]=="NO_USABLE_WEBSITE"
        assert r["page_url"]==""
    asyncio.run(case())


def test_private_agent_scout_api_and_bounded_work_without_email_or_llm_calls():
    async def case():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
            guest=await c.get("/api/corporate-crm/founder/scout")
            assert guest.status_code in (403,503)
            denied=await c.post("/api/corporate-crm/founder/scout/run",json={"limit":5})
            assert denied.status_code in (403,503)
        report={"schema":"noetfield.founder-scout.v1",
                "summary":{"research_organizations":91,"websites_checked":2},
                "prospects":[],"messages_sent":0,"paid_sales_inferred":0}
        outcome={"state":"COMPLETE","scanned":2,"models_called":0,
                 "provider_cost_minor":0,"messages_sent":0,"contacts_qualified":0}
        with patch("noetfield_governance.api._require_connect_desk_operator",
                   return_value=None),patch(
             "noetfield_governance.corporate_founder_scout.founder_scout_board",
             new_callable=AsyncMock,return_value=report) as board,patch(
             "noetfield_governance.corporate_founder_scout.run_scout_batch",
             new_callable=AsyncMock,return_value=outcome) as run:
            async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
                got=await c.get("/api/corporate-crm/founder/scout?limit=10")
                scanned=await c.post("/api/corporate-crm/founder/scout/run",
                            json={"limit":2,"source_key":"original:corp:123"})
                too_many=await c.post("/api/corporate-crm/founder/scout/run",json={"limit":50})
            assert got.status_code==200 and got.json()["summary"]["research_organizations"]==91
            assert scanned.status_code==200 and scanned.json()["messages_sent"]==0
            assert scanned.json()["models_called"]==0
            assert too_many.status_code==422
            assert board.await_args.kwargs["limit"]==10
            assert run.await_args.kwargs["source_key"]=="original:corp:123"
    asyncio.run(case())


def test_source_batch_saves_automatically_without_any_person_or_deal_creation():
    async def case():
        source={"source_key":"github:company:example","organization":"Example Inc",
                "website":"https://example.org","original_url":"https://github.com/example"}
        db=AsyncMock()
        db.fetch.return_value=[source]
        read={"scan_state":"PUBLIC_CONTACT_PAGE","page_url":"https://example.org/",
              "contact_url":"https://example.org/contact","title":"Example Inc",
              "description":"Sales systems","public_channel":"","team_url":"","error":""}
        with patch("noetfield_governance.corporate_founder_scout.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.corporate_founder_scout.prepare_scout",
             new_callable=AsyncMock),patch(
             "noetfield_governance.corporate_founder_scout.fetch_official_signals",
             new_callable=AsyncMock,return_value=read) as research:
            result=await run_scout_batch(object(),limit=5)
            assert result["scanned"]==1
            assert result["found_contact_pages"]==1
            assert result["contacts_qualified"]==0 and result["messages_sent"]==0
            assert result["models_called"]==0
            research.assert_awaited_once_with("https://example.org")
            writes=[c.args[0].lower() for c in db.execute.await_args_list]
            assert len(writes)==1 and "corp_founder_scout" in writes[0]
            assert "corp_crm_people" not in writes[0] and "corp_crm_deals" not in writes[0]
    with patch("noetfield_governance.corporate_founder_scout._database_url",return_value="postgresql://test"):
        asyncio.run(case())


def test_founder_cockpit_language_and_manual_ops_are_secondary():
    from pathlib import Path
    src=(Path(__file__).resolve().parents[2]/
         "services/governance/noetfield_governance/private_corporate_crm.html").read_text()
    assert "Your next customers, without the busywork." in src
    assert 'id="founder-scan-next"' in src
    assert 'id="founder-scout-list"' in src
    assert 'id="operator-tools"' in src
    assert '<details class="advanced-tools"' in src
    assert "/api/corporate-crm/founder/scout/run" in src
    assert "data-founder-scan" in src
    assert "No unverified names, customers" in src
