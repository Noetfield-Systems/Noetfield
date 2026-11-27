"""P0 source-only discovery + real provider acknowledgment contracts."""
from __future__ import annotations
import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport,AsyncClient
from noetfield_governance.api import app
from noetfield_governance.corporate_discovery import _valid_source,_fieldwork_config
from noetfield_governance.corporate_outbound import send_sourced_outreach, _digest
from noetfield_governance.corporate_crm import CorporateCRMError


def research(lane="CORPORATE",**kwargs):
    item={
      "original_source_id":"github:organization:examplecorp",
      "organization":"Example Corporate", "research_lane":lane,
      "official_source_url":"https://github.com/examplecorp",
      "company_website":"https://examplecorp.org",
      "evidence_url":"https://github.com/examplecorp",
      "source_provider":"ORIGINAL_GITHUB",
      "review_status":"PROFILE_REVIEWED",
      "identity_status":"SOURCE_ACCOUNT_NOT_VERIFIED_CUSTOMER",
      "person_contact_exported":False,
      "message_sent":False,
      "original_public_research_score":73}
    item.update(kwargs)
    return item


def test_fieldwork_bridged_records_remain_unverified_public_organizations_only():
    assert _valid_source(research())["lane"]=="CORPORATE"
    assert _valid_source(research("RWA"))["lane"]=="RWA"
    assert _valid_source(research(review_status="DO_NOT_CONTACT")) is None
    assert _valid_source(research(person_contact_exported=True)) is None
    assert _valid_source(research(message_sent=True)) is None
    assert _valid_source(research(identity_status="VERIFIED_BUYER")) is None
    assert _valid_source(research(official_source_url="http://unsafe")) is None


def test_fieldwork_scoped_provider_refuses_unconfigured_or_unapproved_origin(monkeypatch):
    monkeypatch.setenv("FIELDWORK_NOETFIELD_BRIDGE_KEY","short")
    monkeypatch.setenv("FIELDWORK_NOETFIELD_BRIDGE_URL",
                       "https://fieldwork-outreach-arqant.up.railway.app")
    with pytest.raises(CorporateCRMError,match="UNCONFIGURED"):
        _fieldwork_config()
    monkeypatch.setenv("FIELDWORK_NOETFIELD_BRIDGE_KEY","X"*48)
    monkeypatch.setenv("FIELDWORK_NOETFIELD_BRIDGE_URL","https://attacker.example.org")
    with pytest.raises(CorporateCRMError):
        _fieldwork_config()


def test_smtp_outreach_is_never_called_without_documented_contact_permission():
    async def run():
        key=str(uuid4())
        fake=AsyncMock()
        fake.fetchrow.return_value=None
        with patch("noetfield_governance.corporate_outbound._sender_footer",
                   return_value="Noetfield Systems Inc. Verified Address"),\
             patch("noetfield_governance.corporate_outbound._mailbox",
                   return_value=("operations@noetfield.com","private_app_password")),\
             patch("noetfield_governance.corporate_outbound.asyncpg.connect",
                   new_callable=AsyncMock,return_value=fake),\
             patch("noetfield_governance.corporate_outbound._schema",
                   new_callable=AsyncMock),\
             patch("noetfield_governance.corporate_outbound._send_provider") as sent:
            with pytest.raises(CorporateCRMError,match="VERIFIED_CONTACT_PERMISSION"):
                await send_sourced_outreach(object(),deal_id=key,
                  subject="RWA discovery",body="Could we discuss your technical readiness for RWA?",
                  actor="Noetfield Revenue")
            sent.assert_not_called()
    with patch("noetfield_governance.corporate_outbound._database_url",
               return_value="postgresql://unused"):
        asyncio.run(run())


def test_smtp_provider_ack_is_not_claimed_as_inbox_delivery_or_reply():
    async def run():
        key=str(uuid4())
        fake=AsyncMock()
        row={"email":"buyer@example.org","contact_basis":"OPTED_IN",
             "contact_evidence":"https://example.org/consent",
             "review_status":"CONTACT_CHANNEL_VERIFIED","stage":"QUALIFYING",
             "owner":"Revenue","next_action":"Review response","next_date":None}
        fake.fetchrow.side_effect=[row,{"id":uuid4()}]
        with patch("noetfield_governance.corporate_outbound._sender_footer",
                   return_value="Noetfield Systems Inc. Verified Address"),\
             patch("noetfield_governance.corporate_outbound._mailbox",
                   return_value=("operations@noetfield.com","private_app_password")),\
             patch("noetfield_governance.corporate_outbound.asyncpg.connect",
                   new_callable=AsyncMock,return_value=fake),\
             patch("noetfield_governance.corporate_outbound._schema",
                   new_callable=AsyncMock),\
             patch("noetfield_governance.corporate_outbound._send_provider",
                   return_value=True) as provider:
            outcome=await send_sourced_outreach(object(),deal_id=key,
                   subject="Operations pilot discovery",
                   body="Would a brief conversation about your operations priorities be helpful?",
                   actor="Noetfield Revenue")
            assert outcome["state"]=="PROVIDER_ACCEPTED"
            assert outcome["new_provider_send"] is True
            assert outcome["delivered_to_inbox"] is False
            assert outcome["reply_verified"] is False
            assert provider.call_count==1
            assert provider.call_args.args[2]=="buyer@example.org"
    with patch("noetfield_governance.corporate_outbound._database_url",
               return_value="postgresql://unused"):
        asyncio.run(run())


def test_outreach_hash_never_exposes_email():
    assert _digest("buyer@example.org")!= "buyer@example.org"


def test_operator_research_and_provider_send_denied_to_guest():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
            assert (await c.get("/api/corporate-crm/research")).status_code in (403,503)
            assert (await c.get("/api/corporate-crm/outreach/metrics")).status_code in (403,503)
            assert (await c.post("/api/corporate-crm/outreach/send",json={
                "deal_id":str(uuid4()),"subject":"RWA meeting",
                "body":"Would a brief conversation about your readiness be relevant?",
                "actor":"Noetfield Revenue"})).status_code in (403,503)
    asyncio.run(run())


def test_operator_ui_distinguishes_public_research_and_verified_send():
    from pathlib import Path
    p=Path(__file__).resolve().parents[2]/"services/governance/noetfield_governance/private_corporate_crm.html"
    html=p.read_text()
    assert "Corporate discovery · original sources" in html
    assert "Verified contact full name" in html
    assert "/api/corporate-crm/research/sync" in html
    assert "Send through verified provider" in html
    assert "Not proof of recipient delivery" in html
    assert "verified inbound replies" in html
