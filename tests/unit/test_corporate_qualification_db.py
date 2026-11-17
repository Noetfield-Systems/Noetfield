"""Real PostgreSQL acceptance of Fieldwork research -> Corporate CRM qualification.

Uses the disposable CI PostgreSQL service; never touches production or sends mail.
"""
from __future__ import annotations

import asyncio
import os
from uuid import uuid4
from unittest.mock import patch

import asyncpg
import pytest

from noetfield_governance.corporate_crm import CorporateCRMError
from noetfield_governance.corporate_discovery import promote_corporate_source


@pytest.mark.skipif(not os.getenv("CONNECT_TEST_POSTGRES_URL"),reason="CI disposable PostgreSQL required")
def test_real_qualification_persists_account_person_deal_and_is_idempotent():
    async def scenario():
        url=os.environ["CONNECT_TEST_POSTGRES_URL"]
        uid=uuid4().hex
        key="original:corporate:"+uid
        org="Qualification E2E Test "+uid[:12]
        email="contact"+uid[:12]+"@example.org"
        source="https://example.org/research/"+uid
        async with asyncpg.create_pool(url,min_size=1,max_size=2) as pool:
            async with pool.acquire() as db:
                await db.execute("CREATE SCHEMA IF NOT EXISTS noetfield")
                from noetfield_governance.corporate_discovery import _schema
                await _schema(db)
                await db.execute("""INSERT INTO noetfield.corp_research_sources
                   (source_key,organization,lane,original_url,website,evidence_url,review_status,score)
                   VALUES($1,$2,'CORPORATE',$3,'https://example.org',$3,'PROFILE_REVIEWED',85)""",
                   key,org,source)
            kwargs=dict(source_key=key,contact_name="Jane Example",contact_email=email,
                contact_basis="PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL",
                contact_evidence=source,owner="Noetfield Revenue",
                next_action="Schedule discovery with actual contact",
                role_relevance="Published company partnerships contact; AI sales workflow services are relevant.",
                publication_no_solicitation=True)
            with patch("noetfield_governance.corporate_discovery._database_url",return_value=url),\
                 patch("noetfield_governance.corporate_crm._database_url",return_value=url):
                with pytest.raises(CorporateCRMError,match="PUBLICATION_NO_SOLICITATION"):
                    await promote_corporate_source(object(),**{**kwargs,"publication_no_solicitation":False})
                result=await promote_corporate_source(object(),**kwargs)
                assert result["promoted"] is True and result["outreach_sent"] is False
                assert result["payment_verified"] is False and result["deal_id"]
                retry=await promote_corporate_source(object(),**kwargs)
                assert retry["promoted"] is False and retry["idempotent"] is True
                assert retry["deal_id"]==result["deal_id"]
            async with pool.acquire() as db:
                record=await db.fetchrow("""SELECT s.promoted_deal_id,s.contact_evidence,
                  s.contact_basis,s.publication_no_solicitation_confirmed,
                  a.name,p.full_name,p.email,d.offer,d.source_channel,d.stage,d.estimated_minor
                  FROM noetfield.corp_research_sources s
                  JOIN noetfield.corp_crm_deals d ON d.id=s.promoted_deal_id
                  JOIN noetfield.corp_crm_accounts a ON a.id=d.account_id
                  JOIN noetfield.corp_crm_people p ON p.id=d.person_id
                  WHERE s.source_key=$1""",key)
                assert record is not None
                assert str(record["promoted_deal_id"])==result["deal_id"]
                assert record["name"]==org and record["full_name"]=="Jane Example"
                assert record["email"]==email
                assert record["contact_basis"]=="PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL"
                assert record["publication_no_solicitation_confirmed"] is True
                assert record["contact_evidence"]==source
                assert record["source_channel"]=="FIELDWORK_OPERATOR_QUALIFIED"
                assert record["stage"]=="NEW" and record["estimated_minor"]==0
                assert record["offer"]=="ai_sales_os_pilot"
                assert await db.fetchval(
                    "SELECT count(*)::int FROM noetfield.corp_crm_deals WHERE id=$1",
                    record["promoted_deal_id"])==1
    asyncio.run(scenario())
