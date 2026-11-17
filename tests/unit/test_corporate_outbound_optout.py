"""Real B2B outreach: published-channel evidence, sender identity and opt-out."""
from __future__ import annotations

import asyncio
from email.message import EmailMessage
from unittest.mock import AsyncMock,patch
from uuid import uuid4

import pytest
from httpx import ASGITransport,AsyncClient
from noetfield_governance.api import app
from noetfield_governance.corporate_crm import CorporateCRMError
from noetfield_governance.corporate_outbound import (
 _sender_footer,_send_provider,_digest,unsubscribe_subject,
 send_sourced_outreach,reconcile_real_replies,
)
from noetfield_governance.corporate_discovery import promote_corporate_source


def test_only_explicit_unsubscribe_subjects_trigger_suppression():
    for subject in ["Unsubscribe","RE: Unsubscribe","remove me","stop emails","stop messages"]:
        assert unsubscribe_subject(subject)
    for subject in ["Re: Operations pilot discussion","this email discusses unsubscribes",
                    "not unsubscribe","", "subject: unrelated"]:
        assert not unsubscribe_subject(subject)


def test_outbound_commercial_sender_requires_real_mailing_address(monkeypatch):
    monkeypatch.delenv("CORPORATE_OUTREACH_MAILING_ADDRESS",raising=False)
    with pytest.raises(CorporateCRMError,match="REAL_BUSINESS_POSTAL_ADDRESS"):
        _sender_footer("operations@noetfield.com")
    monkeypatch.setenv("CORPORATE_OUTREACH_MAILING_ADDRESS",
                       "123 Verified Business Street, Vancouver, BC, Canada")
    footer=_sender_footer("operations@noetfield.com")
    assert "Noetfield Systems Inc." in footer
    assert "123 Verified Business Street" in footer
    assert "Unsubscribe" in footer
    assert "operations@noetfield.com" in footer


def test_real_smtp_message_has_identification_and_unsubscribe_headers(monkeypatch):
    monkeypatch.setenv("CORPORATE_OUTREACH_MAILING_ADDRESS",
                       "123 Verified Business Street, Vancouver, BC, Canada")
    smtp=type("SMTPContext",(),{})()
    sent=[]
    def enter(self):return self
    def exit(self,*args):return False
    smtp.__enter__=enter.__get__(smtp)
    smtp.__exit__=exit.__get__(smtp)
    def send(m):sent.append(m);return {}
    smtp.login=lambda *args:None
    smtp.send_message=send
    with patch("noetfield_governance.corporate_outbound.smtplib.SMTP_SSL",return_value=smtp):
        accepted=_send_provider("operations@noetfield.com","private-password",
            "buyer@example.org","Operations pilot","Relevant commercial question",
            "<receipt-id@noetfield.com>")
    assert accepted and len(sent)==1
    msg=sent[0]
    assert "mailto:operations@noetfield.com?subject=Unsubscribe" in msg["List-Unsubscribe"]
    assert "Verified Business Street" in msg.get_content()
    assert "Noetfield Systems Inc." in msg.get_content()


def test_publication_basis_fails_without_specific_original_review():
    async def run():
        with patch("noetfield_governance.corporate_discovery.asyncpg.connect",
                   new_callable=AsyncMock) as connect:
            for relevance,reviewed in [("",False),("Short",True),
                 ("This employee oversees the relevant workflow purchasing duties.",False)]:
                with pytest.raises(CorporateCRMError,match="PUBLICATION_NO_SOLICITATION"):
                    await promote_corporate_source(object(),source_key="directory:corporate:099",
                        contact_name="Jane Buyer",contact_email="buyer@example.org",
                        contact_basis="PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL",
                        contact_evidence="https://example.org/contact",
                        owner="Revenue",next_action="Qualify buyer",
                        role_relevance=relevance,publication_no_solicitation=reviewed)
            connect.assert_not_awaited()
    asyncio.run(run())


def test_suppressed_recipient_is_not_emailed_even_with_original_permission():
    async def run():
        row={"email":"buyer@example.org","contact_basis":"OPTED_IN",
             "contact_evidence":"https://example.org/consent",
             "review_status":"CONTACT_CHANNEL_VERIFIED","stage":"QUALIFYING"}
        db=AsyncMock()
        db.fetchrow.return_value=row
        db.fetchval.return_value=1
        with patch("noetfield_governance.corporate_outbound._mailbox",
                   return_value=("operations@noetfield.com","private-password")),\
             patch("noetfield_governance.corporate_outbound._database_url",
                   return_value="postgresql://unused"),\
             patch("noetfield_governance.corporate_outbound.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),\
             patch("noetfield_governance.corporate_outbound._schema",new_callable=AsyncMock),\
             patch("noetfield_governance.corporate_outbound._send_provider") as provider:
            with pytest.raises(CorporateCRMError,match="OUTREACH_RECIPIENT_SUPPRESSED"):
                await send_sourced_outreach(object(),deal_id=str(uuid4()),
                    subject="Relevant workflow",body="An actual, relevant scoped workflow proposal.",
                    actor="Revenue")
            provider.assert_not_called()
    asyncio.run(run())


def test_imap_subject_unsubscribe_is_suppression_not_positive_buyer_reply():
    async def run():
        digest=_digest("buyer@example.org")
        sent={"id":uuid4(),"provider_message_id":"<msg@noetfield.com>",
              "recipient_hash":digest}
        msg=EmailMessage()
        msg["From"]="Buyer <buyer@example.org>"
        msg["Subject"]="Unsubscribe"
        msg["Message-ID"]="<optout-001@buyer.example>"
        msg["In-Reply-To"]="<msg@noetfield.com>"
        db=AsyncMock()
        db.fetch.side_effect=[[sent],[{"recipient_hash":digest}]]
        db.fetchrow.return_value={"recipient_hash":digest}
        with patch("noetfield_governance.corporate_outbound._mailbox",
                   return_value=("operations@noetfield.com","private-password")),\
             patch("noetfield_governance.corporate_outbound._database_url",
                   return_value="postgresql://unused"),\
             patch("noetfield_governance.corporate_outbound.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),\
             patch("noetfield_governance.corporate_outbound._schema",new_callable=AsyncMock),\
             patch("noetfield_governance.corporate_outbound._imap_headers",
                   return_value=[("155",msg)]):
            result=await reconcile_real_replies(object())
            assert result["new_suppressed_recipients"]==1
            assert result["new_verified_replies"]==0
            assert "corp_outreach_suppression" in db.fetchrow.await_args.args[0]
    asyncio.run(run())


def test_manual_suppression_not_exposed_to_public():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            resp=await client.post("/api/corporate-crm/outreach/suppress",
              json={"deal_id":str(uuid4()),"actor":"Revenue"})
            assert resp.status_code in (403,503)
    asyncio.run(run())
