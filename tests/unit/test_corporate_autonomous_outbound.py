"""Autonomous corporate introductory mail: genuine permission before any SMTP side effect."""
from __future__ import annotations

import asyncio
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from noetfield_governance.corporate_outbound import (
    CorporateCRMError,send_prequalified_corporate_introductions,
)


def _rows():
    return [
      {"deal_id":uuid.uuid4(),"account_name":"Acme Business",
       "offer":"ai_sales_os_pilot","owner":"Noetfield Revenue",
       "next_action":"Discuss workflow discovery","stage":"DISCOVERY"},
      {"deal_id":uuid.uuid4(),"account_name":"Some Asset Originator",
       "offer":"rwa_technical_sprint","owner":"Noetfield Revenue",
       "next_action":"Discuss technical readiness","stage":"NEW"}
    ]


def test_no_postal_mailbox_config_means_zero_sends_and_zero_db_queries():
    async def run():
        with patch("noetfield_governance.corporate_outbound._mailbox",
                   side_effect=CorporateCRMError("CORPORATE_SMTP_PROVIDER_NOT_CONFIGURED")),patch(
             "noetfield_governance.corporate_outbound.asyncpg.connect",
             new_callable=AsyncMock) as connect,patch(
             "noetfield_governance.corporate_outbound.send_sourced_outreach",
             new_callable=AsyncMock) as provider:
            result=await send_prequalified_corporate_introductions(object(),limit=2)
        assert result["state"]=="SENDER_NOT_CONFIGURED"
        assert result["attempted"]==0
        connect.assert_not_awaited()
        provider.assert_not_awaited()
    asyncio.run(run())


def test_unqualified_and_unpaid_sources_are_never_automatically_contacted():
    async def run():
        db=AsyncMock()
        db.fetchval.return_value=0
        db.fetch.return_value=[]
        with patch("noetfield_governance.corporate_outbound._mailbox",
                   return_value=("sales@noetfield.com","secret-provider-credential")),patch(
             "noetfield_governance.corporate_outbound._sender_footer",
             return_value="Verified real sender address and opt out footer"),patch(
             "noetfield_governance.corporate_outbound.asyncpg.connect",
             new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.corporate_outbound._schema",
             new_callable=AsyncMock),patch(
             "noetfield_governance.corporate_outbound._database_url",
             return_value="postgresql://test"),patch(
             "noetfield_governance.corporate_outbound.send_sourced_outreach",
             new_callable=AsyncMock) as sender:
            result=await send_prequalified_corporate_introductions(object(),limit=2)
        assert result["eligible"]==0
        assert result["attempted"]==0
        sender.assert_not_awaited()
        query=db.fetch.await_args.args[0]
        assert "r.promoted_deal_id" in query
        assert "r.contact_basis IN" in query
        assert "r.publication_no_solicitation_confirmed IS TRUE" in query
        assert "length(trim(r.outreach_role_relevance)) >= 20" in query
        assert "NOT EXISTS" in query and "corp_outreach_sends" in query
        assert "FIELDWORK_OPERATOR_QUALIFIED" in query
        assert "d.stage IN ('NEW','QUALIFYING','DISCOVERY'" in query
        assert result["research_only_recipients_contacted"]==0
    asyncio.run(run())


def test_source_authorized_real_provider_acceptance_once_with_no_fabricated_replies():
    async def run():
        db=AsyncMock()
        db.fetchval.return_value=0
        eligible=_rows()
        db.fetch.return_value=eligible
        sent=[]
        async def send(_settings,*,deal_id,subject,body,actor):
            sent.append({"deal_id":deal_id,"subject":subject,"body":body,"actor":actor})
            return {"new_provider_send":True,"state":"PROVIDER_ACCEPTED",
                    "delivered_to_inbox":False,"reply_verified":False}
        with patch("noetfield_governance.corporate_outbound._mailbox",
                   return_value=("sales@noetfield.com","secret-provider-credential")),patch(
             "noetfield_governance.corporate_outbound._sender_footer",
             return_value="Verified real sender address and opt out footer"),patch(
             "noetfield_governance.corporate_outbound.asyncpg.connect",
             new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.corporate_outbound._schema",
             new_callable=AsyncMock),patch(
             "noetfield_governance.corporate_outbound._database_url",
             return_value="postgresql://test"),patch(
             "noetfield_governance.corporate_outbound.send_sourced_outreach",
             new_callable=AsyncMock,side_effect=send) as provider:
            result=await send_prequalified_corporate_introductions(object(),limit=2)
            assert provider.await_count==2
        assert result["eligible"]==2 and result["attempted"]==2
        assert result["provider_accepted"]==2
        assert result["verified_replies_inferred"]==0
        assert result["customer_meetings_inferred"]==0
        assert result["paid_customers_inferred"]==0
        assert len(sent)==2
        assert all("workflow" in x["body"].lower() or "rwa" in x["body"].lower()
                   for x in sent)
        assert all("guaranteed" not in x["body"].lower() for x in sent)
    asyncio.run(run())


def test_smtp_failures_never_report_delivered_or_successful_sales():
    async def run():
        db=AsyncMock()
        db.fetchval.return_value=0
        db.fetch.return_value=[_rows()[0]]
        with patch("noetfield_governance.corporate_outbound._mailbox",
                   return_value=("sales@noetfield.com","provider-password")),patch(
             "noetfield_governance.corporate_outbound._sender_footer",
             return_value="Real postal address"),patch(
             "noetfield_governance.corporate_outbound.asyncpg.connect",
             new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.corporate_outbound._schema",
             new_callable=AsyncMock),patch(
             "noetfield_governance.corporate_outbound._database_url",
             return_value="postgresql://test"),patch(
             "noetfield_governance.corporate_outbound.send_sourced_outreach",
             new_callable=AsyncMock,return_value={
                 "state":"FAILED_UNCONFIRMED","new_provider_send":False}):
            result=await send_prequalified_corporate_introductions(object())
        assert result["state"]=="PARTIAL_OR_BLOCKED"
        assert result["provider_accepted"]==0
        assert result["failures"][0]["state"]=="FAILED_UNCONFIRMED"
        assert result["unverified_delivery_claims"]==0
    asyncio.run(run())


def test_daily_cap_and_limit_do_not_contact_more_than_six_verified_records():
    async def run():
        db=AsyncMock()
        db.fetchval.return_value=6
        with patch("noetfield_governance.corporate_outbound._mailbox",
                   return_value=("sales@noetfield.com","password")),patch(
             "noetfield_governance.corporate_outbound._sender_footer",
             return_value="address"),patch(
             "noetfield_governance.corporate_outbound.asyncpg.connect",
             new_callable=AsyncMock,return_value=db),patch(
             "noetfield_governance.corporate_outbound._schema",
             new_callable=AsyncMock),patch(
             "noetfield_governance.corporate_outbound._database_url",
             return_value="postgresql://test"),patch(
             "noetfield_governance.corporate_outbound.send_sourced_outreach",
             new_callable=AsyncMock) as sender:
            result=await send_prequalified_corporate_introductions(object())
        assert result["state"]=="DAILY_SEND_CAP" and result["daily_cap"]==6
        db.fetch.assert_not_awaited()
        sender.assert_not_awaited()
    asyncio.run(run())
    with pytest.raises(CorporateCRMError,match="INVALID_AUTONOMOUS_OUTREACH_LIMIT"):
        asyncio.run(send_prequalified_corporate_introductions(object(),limit=50))
