"""Commercial private API: authenticated routes and non-PII readbacks."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app


def test_commercial_routes_not_public():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            response=await client.get("/api/operations/commercial/funnel")
            assert response.status_code in (403,503)
            response=await client.post("/api/operations/commercial/cases",json={
                "intake_id":"INT-ABCDEF123456","action":"open",
                "offer":"rwa_technical_sprint","owner":"Revenue","next_action":"Qualify"
            })
            assert response.status_code in (403,503)
    asyncio.run(run())


def test_authorized_commercial_operator_updates_only_source_case():
    async def run():
        with patch("noetfield_governance.api._require_connect_desk_operator",return_value=None),patch(
            "noetfield_governance.commercial_pipeline.operate",
            new_callable=AsyncMock,return_value={
                "intake_id":"INT-ABCDEF123456","offer":"rwa_technical_sprint",
                "stage":"QUALIFY","revision":1,
            }
        ) as operation:
            async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
                response=await client.post("/api/operations/commercial/cases",json={
                    "intake_id":"INT-ABCDEF123456","action":"open",
                    "offer":"rwa_technical_sprint",
                    "owner":"Revenue owner","next_action":"Get private-credit rights documents"
                })
            assert response.status_code==200
            assert response.json()["stage"]=="QUALIFY"
            assert operation.await_args.kwargs["intake_id"]=="INT-ABCDEF123456"
            assert operation.await_args.kwargs["action"]=="open"
    asyncio.run(run())


def test_commercial_operator_funnel_no_contact_pii():
    async def run():
        with patch("noetfield_governance.api._require_connect_desk_operator",return_value=None),patch(
            "noetfield_governance.commercial_pipeline.readback",
            new_callable=AsyncMock,return_value={
                "schema":"noetfield.commercial-funnel.v1",
                "items":[{"intake_id":"INT-ABCDEF123456","offer":"ai_sales_os_pilot",
                          "stage":"QUALIFY","payment":None}],
                "no_customer_pii":True,
            }
        ):
            async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
                response=await client.get("/api/operations/commercial/funnel")
            assert response.status_code==200
            assert response.json()["items"][0]["payment"] is None
            assert "contact_email" not in response.text
    asyncio.run(run())
