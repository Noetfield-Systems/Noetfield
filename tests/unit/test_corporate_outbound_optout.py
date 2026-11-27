"""Real B2B outreach: published-channel evidence, sender identity and opt-out."""
from __future__ import annotations

import asyncio
from email.message import EmailMessage
from unittest.mock import AsyncMock,MagicMock,patch
from uuid import uuid4

import pytest
from httpx import ASGITransport,AsyncClient
from noetfield_governance.api import app
from noetfield_governance.corporate_crm import CorporateCRMError
from noetfield_governance.corporate_outbound import (
 _sender_footer,_send_provider,_digest,unsubscribe_subject,_corporate_identity,
 send_sourced_outreach,reconcile_real_replies,_imap_headers,
)
from noetfield_governance.corporate_discovery import promote_corporate_source
from noetfield_governance.communication_policy import Relationship


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
    sent=[]
    class FakeSMTP:
        def __enter__(self):return self
        def __exit__(self,*args):return False
        def login(self,*args):return None
        def send_message(self,message):sent.append(message);return {}
    with patch("noetfield_governance.corporate_outbound.smtplib.SMTP_SSL",return_value=FakeSMTP()):
        accepted=_send_provider("operations@noetfield.com","private-password",
            "buyer@example.org","Operations pilot","Relevant commercial question",
            "<receipt-id@noetfield.com>", identity=_corporate_identity("operations@noetfield.com"),
            relationship=Relationship("noetfield-corporate","Noetfield Systems Inc.",
                "buyer@example.org","fixture","NOETFIELD_CORPORATE","Revenue","Review response",context_checked=True))
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
        with patch("noetfield_governance.corporate_outbound._sender_footer",
                   return_value="Noetfield Systems Inc. Verified Address"),\
             patch("noetfield_governance.corporate_outbound._mailbox",
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
              "recipient_hash":digest,"status":"PROVIDER_ACCEPTED"}
        msg=EmailMessage()
        msg["From"]="Buyer <buyer@example.org>"
        msg["Subject"]="Unsubscribe"
        msg["Message-ID"]="<optout-001@buyer.example>"
        msg["In-Reply-To"]="<msg@noetfield.com>"
        db=AsyncMock()
        db.fetch.side_effect=[[sent],[{"recipient_hash":digest}]]
        db.transaction=MagicMock()
        db.fetchrow.side_effect=[{"uidvalidity":77,"last_uid":100},{"recipient_hash":digest}]
        with patch("noetfield_governance.corporate_outbound._sender_footer",
                   return_value="Noetfield Systems Inc. Verified Address"),\
             patch("noetfield_governance.corporate_outbound._mailbox",
                   return_value=("operations@noetfield.com","private-password")),\
             patch("noetfield_governance.corporate_outbound._database_url",
                   return_value="postgresql://unused"),\
             patch("noetfield_governance.corporate_outbound.asyncpg.connect",
                   new_callable=AsyncMock,return_value=db),\
             patch("noetfield_governance.corporate_outbound._schema",new_callable=AsyncMock),\
             patch("noetfield_governance.corporate_outbound._imap_headers",
                   return_value=(77,[("155",msg)],False)):
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


def test_missing_real_sender_postal_address_has_no_outbox_claim(monkeypatch):
    monkeypatch.delenv("CORPORATE_OUTREACH_MAILING_ADDRESS",raising=False)
    async def check():
        with patch("noetfield_governance.corporate_outbound._mailbox",
                   return_value=("operations@noetfield.com","private-password")),\
             patch("noetfield_governance.corporate_outbound.asyncpg.connect",
                   new_callable=AsyncMock) as connect,\
             patch("noetfield_governance.corporate_outbound._send_provider") as send:
            with pytest.raises(CorporateCRMError,match="REAL_BUSINESS_POSTAL_ADDRESS_REQUIRED"):
                await send_sourced_outreach(object(),deal_id=str(uuid4()),
                    subject="RWA scoped pilot opportunity",
                    body="Relevant commercial outreach with a traceable scope.",
                    actor="Noetfield Revenue")
            connect.assert_not_awaited()
            send.assert_not_called()
    asyncio.run(check())


def test_reconciliation_reuses_existing_six_hour_worker_and_distinguishes_reply_from_optout():
    from noetfield_governance.corporate_discovery_scheduler import reconcile_proven_outreach
    async def check():
        with patch("noetfield_governance.corporate_outbound.reconcile_real_replies",
                   new_callable=AsyncMock,
                   return_value={"provider_ack_sent":2,"scanned_headers":3,
                                 "new_verified_replies":1,"new_suppressed_recipients":1}) as impl:
            result=await reconcile_proven_outreach(object())
            assert result["state"]=="COMPLETE"
            assert result["new_verified_replies"]==1
            assert result["new_suppressed_recipients"]==1
            assert impl.await_args.kwargs["limit"]==120
    asyncio.run(check())


def test_imap_pages_never_skip_oldest_or_failed_fetch():
    class FakeIMAP:
        def __enter__(self): return self
        def __exit__(self,*args): return False
        def login(self,*args): pass
        def select(self,*args,**kwargs): return "OK",[]
        def response(self,*args): return "UIDVALIDITY",[b"77"]
        def uid(self,cmd,*args):
            if cmd=="SEARCH":
                return "OK",[b"5 6 7 8"]
            if args[0]=="7":
                return "NO",[]
            return "OK",[(b"header",b"From: buyer@example.org\r\nMessage-ID: <reply@example.org>\r\n\r\n")]
    with patch("noetfield_governance.corporate_outbound.imaplib.IMAP4_SSL",return_value=FakeIMAP()):
        epoch,items,more=_imap_headers("operations@noetfield.com","fixture",2)
        assert epoch==77 and [uid for uid,_ in items]==["5","6"] and more
        epoch,items,more=_imap_headers("operations@noetfield.com","fixture",2,uidvalidity=77,last_uid=6)
        assert items==[] and more
        # UIDVALIDITY reset starts a fresh scan even if the previous UID was high.
        epoch,items,more=_imap_headers("operations@noetfield.com","fixture",2,uidvalidity=12,last_uid=999)
        assert [uid for uid,_ in items]==["5","6"]
