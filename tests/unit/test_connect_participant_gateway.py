"""Noetfield Connect applicant-scoped status and feedback API.

Tests do not create a real lead or use production records.
"""
import asyncio
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from noetfield_governance.api import app


RID = "RID-CNX-7F6ED554310A4ABC8A1E"
EMAIL = "applicant@example.invalid"


def run(coro):
    return asyncio.run(coro)


def test_participant_status_is_source_backed_and_omits_private_case_fields():
    async def scenario():
        with patch("noetfield_governance.api.redis_runtime.is_enabled",return_value=False):
            with patch("noetfield_governance.api.intake_repository.public_connect_participant_status",
                       new_callable=AsyncMock) as readback:
                readback.return_value={
                    "found":True,"intake_id":"INT-ABCDE1234567","stage":"QUALIFYING",
                    "detail":"Your proposal is being reviewed for relevance and fit.",
                    "created_at":"2026-11-13T12:00:00+00:00",
                    "updated_at":None,"independently_verified":False,
                    "receipt_type":"SOURCE_BACKED_PARTICIPANT_STATUS",
                }
                transport=ASGITransport(app=app)
                async with AsyncClient(transport=transport,base_url="http://test") as client:
                    response=await client.post("/api/connect/participant/status",
                        json={"request_id":RID,"email":EMAIL})
                assert response.status_code==200,response.text
                assert response.json()["stage"]=="QUALIFYING"
                assert response.json()["independently_verified"] is False
                assert not any(k in response.json() for k in
                               ("contact_email","owner","notes","revenue","lead_score"))
                readback.assert_awaited_once_with(request_id=RID,email=EMAIL)
    run(scenario())


def test_participant_status_does_not_enumerate_other_intakes():
    async def scenario():
        with patch("noetfield_governance.api.redis_runtime.is_enabled",return_value=False):
            with patch("noetfield_governance.api.intake_repository.public_connect_participant_status",
                       new_callable=AsyncMock,return_value=None):
                transport=ASGITransport(app=app)
                async with AsyncClient(transport=transport,base_url="http://test") as client:
                    unknown=await client.post("/api/connect/participant/status",
                        json={"request_id":RID,"email":EMAIL})
                    invalid=await client.post("/api/connect/participant/status",
                        json={"request_id":"INT-ABC","email":EMAIL})
                    malformed=await client.post("/api/connect/participant/status",
                        json={"request_id":RID,"email":"not-an-email"})
                assert unknown.status_code==404
                assert invalid.status_code==422
                assert malformed.status_code==422
    run(scenario())


def test_feedback_requires_existing_case_and_source_receipt():
    async def scenario():
        with patch("noetfield_governance.api.redis_runtime.is_enabled",return_value=False):
            with patch("noetfield_governance.api.intake_repository.append_public_connect_feedback",
                       new_callable=AsyncMock) as save:
                save.return_value={"recorded":True,"deduped":False,
                                   "intake_id":"INT-ABCDE1234567","feedback_id":"a"*32}
                transport=ASGITransport(app=app)
                async with AsyncClient(transport=transport,base_url="http://test") as client:
                    response=await client.post("/api/connect/participant/feedback",
                        json={"request_id":RID,"email":EMAIL,"rating":4,
                              "message":"Good path, please make the status clearer.",
                              "feedback_id":"a"*32})
                    assert response.status_code==200,response.text
                    assert response.json()["recorded"] is True
                    assert response.json()["intake_id"]=="INT-ABCDE1234567"
                    save.assert_awaited_once()
                    save.return_value=None
                    missing=await client.post("/api/connect/participant/feedback",
                        json={"request_id":RID,"email":EMAIL,"rating":4,
                              "message":"Still good.","feedback_id":"b"*32})
                    assert missing.status_code==404
    run(scenario())


def test_feedback_rejects_invalid_score_and_oversized_content():
    async def scenario():
        transport=ASGITransport(app=app)
        async with AsyncClient(transport=transport,base_url="http://test") as client:
            for payload in [
                {"rating":0,"message":"Valid feedback text"},
                {"rating":6,"message":"Valid feedback text"},
                {"rating":3,"message":"x"*1201},
                {"rating":3,"message":"no"},
            ]:
                response=await client.post("/api/connect/participant/feedback",json={
                    "request_id":RID,"email":EMAIL,"feedback_id":"c"*32,**payload})
                assert response.status_code==422,response.text
    run(scenario())
