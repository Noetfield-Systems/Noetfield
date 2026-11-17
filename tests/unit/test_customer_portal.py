"""P1 Noetfield customer portal contracts: no cross-company reads, no fake cash."""
from __future__ import annotations
import asyncio
from unittest.mock import patch, AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app
from noetfield_governance.customer_portal import (
  authenticate_customer, customer_email_hash, customer_case_projection,
)

def sample_case(**overrides):
    item={
      "id":uuid4(),"account_name":"Example Capital",
      "source_intake_id":"INT-ABCDEF123456","offer":"rwa_technical_sprint",
      "commercial":{
        "stage":"SCOPE_ACCEPTED","offer":"rwa_technical_sprint",
        "scope_ref":"SOW-RWA-0001",
        "acceptance_evidence":"https://docs.example.org/signed.pdf",
      }, "payment":None
    }
    item.update(overrides)
    return item


def test_customer_projection_has_only_approved_checkout_after_signed_scope():
    case=sample_case()
    output=customer_case_projection(case)
    assert output["scope_accepted"]
    assert output["payment_status"]=="NOT_VERIFIED"
    assert output["approved_checkout_url"].startswith("https://buy.stripe.com/")
    assert not output["delivery_evidence"]
    assert not output["bank_settlement_verified"]
    unpaid=sample_case(commercial={"stage":"QUALIFY","offer":"rwa_technical_sprint"})
    assert customer_case_projection(unpaid)["approved_checkout_url"] is None


def test_paid_checkout_requires_canonical_bound_live_exact_receipt():
    case=sample_case(commercial={
      "stage":"IN_DELIVERY","offer":"rwa_technical_sprint",
      "scope_ref":"SOW-RWA-0001",
      "acceptance_evidence":"https://docs.example.org/signed.pdf",
      "payment_session_id":"cs_live_123456789",
    })
    good={"event_id":"evt_example","session_id":"cs_live_123456789",
       "amount_minor":47500,"currency":"usd","livemode":True,
       "payment_link_id":"plink_1UbG9CJ03eJkL57JNNK0P3cY",
       "source_intake_id":"INT-ABCDEF123456","reversed":False}
    assert customer_case_projection({**case,"payment":good})["payment_status"]=="PAID_LIVE"
    for bad in [{**good,"source_intake_id":"INT-OTHER123456"},
                {**good,"amount_minor":1},{**good,"livemode":False},
                {**good,"payment_link_id":"plink_fake"}]:
        assert customer_case_projection({**case,"payment":bad})["payment_status"]!="PAID_LIVE"
    assert customer_case_projection({**case,"payment":{**good,"reversed":True}})["payment_status"]=="REVERSED"


def test_private_customer_read_requires_verified_provider_token():
    async def run():
      async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        unauthorized=await c.get("/api/corporate-crm/customer/me")
        assert unauthorized.status_code in (401,403,503)
        unauthorizedGrant=await c.post("/api/corporate-crm/customers/access",
           json={"deal_id":str(uuid4()),"email":"buyer@example.net","actor":"Owner"})
        assert unauthorizedGrant.status_code in (403,503)
      with patch("noetfield_governance.customer_portal.authenticate_customer",
                 new_callable=AsyncMock,return_value={"provider_subject":"sub","email_hash":"hash"}) as verified,\
           patch("noetfield_governance.customer_portal.customer_cases",
                 new_callable=AsyncMock,return_value={"schema":"noetfield.customer-portal.v1","cases":[]}) as data:
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
           authorized=await c.get("/api/corporate-crm/customer/me",headers={"Authorization":"Bearer valid"})
        assert authorized.status_code==200
        assert authorized.json()["cases"]==[]
        assert "no-store" in authorized.headers["cache-control"]
        assert verified.await_args.args[0]=="valid"
        assert data.await_args.kwargs["identity"]["email_hash"]=="hash"
    asyncio.run(run())


def test_provider_auth_refuses_bad_session_and_unconfirmed_email():
    async def run():
        with patch("noetfield_governance.customer_portal._provider_settings",return_value=("https://tenant.supabase.co","anon")):
            with pytest.raises(HTTPException) as e:
                await authenticate_customer("")
            assert e.value.status_code==401
            response=type("Reply",(),{"status_code":200,"json":lambda self:
                      {"id":"customer-uuid","email":"buyer@example.org","email_confirmed_at":None}})()
            with patch("noetfield_governance.customer_portal.httpx.AsyncClient") as factory:
                client=factory.return_value.__aenter__.return_value
                client.get=AsyncMock(return_value=response)
                with pytest.raises(HTTPException) as denied:
                    await authenticate_customer("nonempty")
                assert denied.value.status_code==403
    asyncio.run(run())


def test_canonical_customer_email_is_casefolded_and_salted_from_public_ui():
    assert customer_email_hash("Buyer@Example.org")==customer_email_hash("buyer@example.org")
    assert "buyer@example.org" not in customer_email_hash("buyer@example.org")


def test_customer_html_never_embeds_any_client_data_or_admin_key():
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    html=(root/"services/governance/noetfield_governance/private_customer_portal.html").read_text()
    bridge=(root/"assets/noetfield-customer-bridge-v1.js").read_text()
    assert 'id="case-list"' in html and "/api/corporate-crm/customer/me" in html
    assert "X-Admin-Secret" not in html and "localStorage" not in html
    assert "noetfield.customer.google.v1" in html and "noetfield.customer.google.v1" in bridge
    assert 'target="_blank" rel="noopener noreferrer"' in html
    auth=(root/"assets/noetfield-invest-auth-v1.js").read_text()
    assert 'nf-customer-sso-return' in auth
