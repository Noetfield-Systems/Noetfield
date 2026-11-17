"""Real-provider Founder sales intelligence: grounded outputs, budgets and isolation."""
from __future__ import annotations

import asyncio
import os
import json
import uuid
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

import pytest
from httpx import ASGITransport,AsyncClient

from noetfield_governance.api import app
from noetfield_governance.corporate_founder_ai import (
    _validate_model_analysis, _model_input, analyze_public_company,
    run_ai_batch, founder_ai_board, prepare_ai, configured,
)


SAMPLE={"organization":"Visible Service Company","lane":"CORPORATE",
    "source_key":"sme:ca:test","original_url":"https://example.org/original",
    "page_url":"https://example.org/",
    "site_title":"Business technology services",
    "site_description":"Professional managed services and IT operations."}

VALID={"fit_label":"POSSIBLE_FIT","evidence_phrase":"managed services",
    "reason":"The site mentions managed services, which may require lead follow-up.",
    "buyer_role":"Operations Lead",
    "next_move":"Check for evidence of a public operations or partnership channel."}


def test_model_rejects_fabricated_public_evidence_or_invalid_roles():
    source=_model_input(SAMPLE)
    assert _validate_model_analysis(VALID,source)["fit_label"]=="POSSIBLE_FIT"
    for invalid in (
        {**VALID,"evidence_phrase":"we have confirmed a 5 million dollar budget"},
        {**VALID,"fit_label":"STRONG_FIT","evidence_phrase":""},
        {**VALID,"buyer_role":"Jane Smith, confirmed CEO"},
        {**VALID,"fit_label":"CUSTOMER_PAID"},
        {**VALID,"contact_email":"inferred@example.org"},
        {**VALID,"reason":""},
    ):
        with pytest.raises(ValueError):
            _validate_model_analysis(invalid,source)


def test_absent_model_provider_is_never_reported_as_success(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY",raising=False)
    monkeypatch.delenv("OPENROUTER_MODEL",raising=False)
    assert not configured()
    outcome=asyncio.run(run_ai_batch(object(),limit=2))
    assert outcome["state"]=="NOT_CONFIGURED"
    assert outcome["models_called"]==0


def test_real_openrouter_request_has_bounded_tokens_and_usage_receipt(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY","private-test-key")
    monkeypatch.setenv("CORPORATE_AI_ENABLE_LEGACY_OPENROUTER","1")
    monkeypatch.setenv("OPENROUTER_MODEL","test/cost-efficient-model")
    captured={}
    class FakeResponse:
        status_code=200
        def json(self):
            return {"id":"gen-real-test","model":"test/response-model",
              "choices":[{"message":{"content":json.dumps(VALID)}}],
              "usage":{"prompt_tokens":180,"completion_tokens":100,"cost":0.0004}}
    class FakeClient:
        def __init__(self,*args,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):return False
        async def post(self,url,**kwargs):
            captured.update(url=url,**kwargs)
            return FakeResponse()
    async def exercise():
        with patch("noetfield_governance.corporate_founder_ai.httpx.AsyncClient",
                   FakeClient):
            output=await analyze_public_company(SAMPLE)
        assert output["analysis"]["evidence_phrase"]=="managed services"
        assert output["prompt_tokens"]==180 and output["completion_tokens"]==100
        assert output["cost_usd"]==0.0004 and output["cost_from_provider"] is True
        assert output["generation_id"]=="gen-real-test"
        assert captured["url"]=="https://openrouter.ai/api/v1/chat/completions"
        assert captured["json"]["max_tokens"]==380
        assert captured["json"]["model"]=="test/cost-efficient-model"
        assert captured["json"]["usage"]=={"include":True}
        assert captured["headers"]["Authorization"]=="Bearer private-test-key"
        assert "private-test-key" not in json.dumps(captured["json"])
        assert "contact_email" not in json.dumps(captured["json"])
    asyncio.run(exercise())


def test_real_fabric_source_job_uses_safely_scoped_credentials_and_receipt(monkeypatch):
    from noetfield_governance.corporate_founder_ai import _source_signature
    import hashlib
    monkeypatch.setenv("CORPORATE_FABRIC_CRM_BASE_URL",
                       "https://noetfield-agent-fabric-staging-staging.up.railway.app")
    monkeypatch.setenv("CORPORATE_FABRIC_CRM_BRIDGE_TOKEN","f"*64)
    monkeypatch.delenv("CORPORATE_AI_LLM_API_KEY",raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY",raising=False)
    captured={}
    class FakeReply:
        status_code=200
        def json(self):
            sent=captured["payload"]
            plain={"schema":"noetfield.agent-fabric.founder-crm-analysis.v1",
               "state":"SUCCEEDED","task_id":sent["task_id"],
               "source_key":sent["source_key"],
               "source_signature":sent["source_signature"],
               "analysis":VALID,"provider":"cloudflare_glm",
               "model":"@cf/zai-org/glm-4.7-flash",
               "generation_id":"real-upstream-provider-001",
               "input_tokens":135,"output_tokens":76,"cost_usd":None,
               "cost_from_provider":False,
               "external_actions_executed":False,
               "authority":"UNVERIFIED_ADVISORY_MODEL_OUTPUT"}
            plain["artifact_sha256"]=hashlib.sha256(
                json.dumps(plain,sort_keys=True,ensure_ascii=False).encode()
            ).hexdigest()
            return plain
    class FakeClient:
        def __init__(self,*a,**k): pass
        async def __aenter__(self):return self
        async def __aexit__(self,*a):return False
        async def post(self,url,**kwargs):
            captured.update(url=url,payload=kwargs["json"],
                            headers=kwargs["headers"])
            return FakeReply()
    async def go():
        with patch("noetfield_governance.corporate_founder_ai.httpx.AsyncClient",FakeClient):
            return await analyze_public_company(SAMPLE)
    result=asyncio.run(go())
    assert result["analysis"]==VALID
    assert result["model_route"]=="AGENT_FABRIC_CLOUDFLARE_GLM"
    assert result["generation_id"]=="real-upstream-provider-001"
    assert len(result["artifact_sha256"])==64
    assert result["cost_usd"] is None and result["cost_from_provider"] is False
    assert captured["url"].endswith("/api/internal/v1/founder-crm/analyze")
    assert captured["headers"]["X-Founder-CRM-Bridge-Key"]=="f"*64
    assert "Authorization" not in captured["headers"]
    assert captured["payload"]["source_signature"]==_source_signature(SAMPLE)
    assert captured["payload"]["source"]["published_site_description"]==SAMPLE["site_description"]
    assert "contact_email" not in json.dumps(captured["payload"])
    assert "person_name" not in json.dumps(captured["payload"])


def test_fabric_receipt_tampering_is_not_treated_as_real_agent_success(monkeypatch):
    monkeypatch.setenv("CORPORATE_FABRIC_CRM_BASE_URL","https://fabric.example.org")
    monkeypatch.setenv("CORPORATE_FABRIC_CRM_BRIDGE_TOKEN","f"*64)
    monkeypatch.delenv("CORPORATE_AI_LLM_API_KEY",raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY",raising=False)
    class FakeReply:
        status_code=200
        def json(self):
            return {"schema":"noetfield.agent-fabric.founder-crm-analysis.v1",
              "state":"SUCCEEDED","analysis":VALID,
              "provider":"cloudflare_glm","artifact_sha256":"0"*64}
    class FakeClient:
        def __init__(self,*a,**kw):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*a):return False
        async def post(self,*a,**kw):return FakeReply()
    async def go():
        with patch("noetfield_governance.corporate_founder_ai.httpx.AsyncClient",FakeClient):
            with pytest.raises(ValueError,match="MODEL_FABRIC_RECEIPT_INVALID"):
                await analyze_public_company(SAMPLE)
    asyncio.run(go())


def test_existing_company_os_model_used_first_and_openrouter_401_not_required(monkeypatch):
    from noetfield_governance.corporate_founder_ai import _model_routes
    monkeypatch.setenv("CORPORATE_AI_LLM_BASE_URL","https://api.deepseek.com/v1")
    monkeypatch.setenv("CORPORATE_AI_LLM_API_KEY","company-secret-not-exposed")
    monkeypatch.setenv("CORPORATE_AI_LLM_MODEL","deepseek-chat")
    monkeypatch.setenv("OPENROUTER_API_KEY","expired-platform-key")
    monkeypatch.setenv("CORPORATE_AI_ENABLE_LEGACY_OPENROUTER","1")
    monkeypatch.setenv("OPENROUTER_MODEL","old-test-model")
    routes=_model_routes()
    assert routes[0]["url"]=="https://api.deepseek.com/v1/chat/completions"
    assert routes[0]["model"]=="deepseek-flash"
    assert routes[0]["route"]=="COMPANY_OS_EXISTING_MODEL"
    assert routes[1]["route"]=="PLATFORM_OPENROUTER"
    responses=[]
    class Resp:
        def __init__(self,status):self.status_code=status
        def json(self):
            return {"model":"deepseek-chat","id":"real-provider-request",
                "choices":[{"message":{"content":json.dumps(VALID)}}],
                "usage":{"prompt_tokens":20,"completion_tokens":30}}
    class Client:
        def __init__(self,*args,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):return False
        async def post(self,url,**kwargs):
            responses.append((url,kwargs["headers"]["Authorization"]))
            return Resp(200)
    async def execute():
        with patch("noetfield_governance.corporate_founder_ai.httpx.AsyncClient",Client):
            return await analyze_public_company(SAMPLE)
    result=asyncio.run(execute())
    assert result["model_route"]=="COMPANY_OS_EXISTING_MODEL"
    assert result["cost_usd"] is None and result["cost_from_provider"] is False
    assert len(responses)==1 and responses[0][0].startswith("https://api.deepseek.com/")
    assert responses[0][1]=="Bearer company-secret-not-exposed"


def test_company_os_distinct_fallback_precedes_invalid_platform_key(monkeypatch):
    from noetfield_governance.corporate_founder_ai import _model_routes
    monkeypatch.setenv("CORPORATE_AI_LLM_BASE_URL","https://api.deepseek.com/v1")
    monkeypatch.setenv("CORPORATE_AI_LLM_API_KEY","bad-primary-key")
    monkeypatch.setenv("CORPORATE_AI_LLM_MODEL","deepseek-chat")
    monkeypatch.setenv("CORPORATE_AI_COMPANY_FALLBACK_API_KEY","distinct-company-fallback")
    monkeypatch.setenv("CORPORATE_AI_COMPANY_FALLBACK_MODEL","fallback-model")
    monkeypatch.setenv("OPENROUTER_API_KEY","bad-platform-key")
    monkeypatch.setenv("CORPORATE_AI_ENABLE_LEGACY_OPENROUTER","1")
    monkeypatch.setenv("OPENROUTER_MODEL","platform-model")
    routes=_model_routes()
    assert [x["route"] for x in routes]==[
       "COMPANY_OS_EXISTING_MODEL","COMPANY_OS_OPENROUTER_FALLBACK",
       "PLATFORM_OPENROUTER"]
    calls=[]
    class Resp:
        def __init__(self,code):self.status_code=code
        def json(self):
            return {"id":"real-fallback-model","model":"fallback-model",
                "choices":[{"message":{"content":json.dumps(VALID)}}],
                "usage":{"prompt_tokens":100,"completion_tokens":30}}
    class Client:
        def __init__(self,*args,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):return False
        async def post(self,url,**kwargs):
            calls.append(kwargs["headers"]["Authorization"])
            return Resp(401 if len(calls)==1 else 200)
    async def exercise():
        with patch("noetfield_governance.corporate_founder_ai.httpx.AsyncClient",Client):
            return await analyze_public_company(SAMPLE)
    res=asyncio.run(exercise())
    assert res["model_route"]=="COMPANY_OS_OPENROUTER_FALLBACK"
    assert res["generation_id"]=="real-fallback-model"
    assert res["cost_usd"] is None
    assert calls==["Bearer bad-primary-key","Bearer distinct-company-fallback"]


def test_primary_provider_unauthorized_is_fallback_only_not_fake_model_receipt(monkeypatch):
    monkeypatch.setenv("CORPORATE_AI_LLM_BASE_URL","https://api.deepseek.com/v1")
    monkeypatch.setenv("CORPORATE_AI_LLM_API_KEY","expired-model-key")
    monkeypatch.setenv("CORPORATE_AI_LLM_MODEL","deepseek-chat")
    monkeypatch.setenv("OPENROUTER_API_KEY","also-expired-key")
    monkeypatch.setenv("CORPORATE_AI_ENABLE_LEGACY_OPENROUTER","1")
    monkeypatch.setenv("OPENROUTER_MODEL","openrouter/some-model")
    urls=[]
    class Response:
        status_code=401
    class Client:
        def __init__(self,*args,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):return False
        async def post(self,url,**kwargs):
            urls.append(url)
            return Response()
    async def execute():
        with patch("noetfield_governance.corporate_founder_ai.httpx.AsyncClient",Client):
            with pytest.raises(ValueError,match="MODEL_HTTP_401_PLATFORM_OPENROUTER"):
                await analyze_public_company(SAMPLE)
    asyncio.run(execute())
    assert urls==["https://api.deepseek.com/v1/chat/completions",
                 "https://openrouter.ai/api/v1/chat/completions"]


def test_paid_primary_and_fabric_configured_free_legacy_never_runs(monkeypatch):
    from noetfield_governance.corporate_founder_ai import _model_routes
    monkeypatch.setenv("CORPORATE_AI_LLM_BASE_URL","https://api.deepseek.com")
    monkeypatch.setenv("CORPORATE_AI_LLM_API_KEY","paid-deepseek-credential")
    monkeypatch.setenv("CORPORATE_AI_LLM_MODEL","deepseek-flash")
    monkeypatch.setenv("CORPORATE_FABRIC_CRM_BASE_URL","https://fabric.example.org")
    monkeypatch.setenv("CORPORATE_FABRIC_CRM_BRIDGE_TOKEN","f"*64)
    monkeypatch.setenv("OPENROUTER_API_KEY","expired-openrouter-free-key")
    monkeypatch.setenv("OPENROUTER_MODEL","some-model:free")
    monkeypatch.setenv("CORPORATE_AI_ENABLE_LEGACY_OPENROUTER","1")
    routes=_model_routes()
    assert [r["route"] for r in routes]==[
        "COMPANY_OS_EXISTING_MODEL","AGENT_FABRIC_SOURCE_SPECIALIST"]
    class Reply:
        status_code=200
        def json(self):
            return {"id":"actual-deepseek-001","model":"deepseek-flash",
                "choices":[{"message":{"content":json.dumps(VALID)}}],
                "usage":{"prompt_tokens":50,"completion_tokens":80}}
    seen=[]
    class Client:
        def __init__(self,*args,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):return False
        async def post(self,url,**kwargs):
            seen.append(url);return Reply()
    async def run():
        with patch("noetfield_governance.corporate_founder_ai.httpx.AsyncClient",Client):
            return await analyze_public_company(SAMPLE)
    reply=asyncio.run(run())
    assert reply["model_route"]=="COMPANY_OS_EXISTING_MODEL"
    assert reply["generation_id"]=="actual-deepseek-001"
    assert seen==["https://api.deepseek.com/chat/completions"]


def test_native_paid_deepseek_request_is_supported_json_nonthinking_not_openrouter(monkeypatch):
    monkeypatch.setenv("CORPORATE_AI_LLM_BASE_URL","https://api.deepseek.com")
    monkeypatch.setenv("CORPORATE_AI_LLM_API_KEY","paid-deepseek-native-key")
    monkeypatch.setenv("CORPORATE_AI_LLM_MODEL","deepseek-chat")
    monkeypatch.delenv("CORPORATE_FABRIC_CRM_BRIDGE_TOKEN",raising=False)
    monkeypatch.delenv("CORPORATE_AI_COMPANY_FALLBACK_API_KEY",raising=False)
    monkeypatch.delenv("CORPORATE_AI_ENABLE_LEGACY_OPENROUTER",raising=False)
    observed=[]
    class Reply:
        status_code=200
        def json(self):
            return {"id":"paid-deepseek-v4-flash-verified","model":"deepseek-flash",
              "choices":[{"message":{"content":json.dumps(VALID)}}],
              "usage":{"prompt_tokens":54,"completion_tokens":78}}
    class Client:
        def __init__(self,*a,**kw):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*a):return False
        async def post(self,url,**kwargs):
            observed.append((url,kwargs["json"]))
            return Reply()
    async def go():
        with patch("noetfield_governance.corporate_founder_ai.httpx.AsyncClient",Client):
            return await analyze_public_company(SAMPLE)
    out=asyncio.run(go())
    assert out["model_route"]=="COMPANY_OS_EXISTING_MODEL"
    assert len(observed)==1
    assert observed[0][0]=="https://api.deepseek.com/chat/completions"
    body=observed[0][1]
    assert body["model"]=="deepseek-flash"
    assert body["thinking"]=={"type":"disabled"}
    assert body["response_format"]=={"type":"json_object"}
    assert "usage" not in body


def test_direct_paid_failure_and_fabric_503_fall_through_to_separate_paid_route(monkeypatch):
    from noetfield_governance.corporate_founder_ai import _model_routes
    monkeypatch.setenv("CORPORATE_AI_LLM_BASE_URL","https://api.deepseek.com")
    monkeypatch.setenv("CORPORATE_AI_LLM_API_KEY","broken-paid-provider-key")
    monkeypatch.setenv("CORPORATE_AI_LLM_MODEL","deepseek-flash")
    monkeypatch.setenv("CORPORATE_FABRIC_CRM_BASE_URL","https://fabric.example.org")
    monkeypatch.setenv("CORPORATE_FABRIC_CRM_BRIDGE_TOKEN","f"*64)
    monkeypatch.setenv("CORPORATE_AI_COMPANY_FALLBACK_API_KEY","paid-company-fallback-key")
    monkeypatch.setenv("CORPORATE_AI_COMPANY_FALLBACK_MODEL","paid/fallback-model")
    monkeypatch.setenv("OPENROUTER_API_KEY","expired-legacy")
    monkeypatch.setenv("OPENROUTER_MODEL","old:free")
    monkeypatch.delenv("CORPORATE_AI_ENABLE_LEGACY_OPENROUTER",raising=False)
    assert [x["route"] for x in _model_routes()]==[
        "COMPANY_OS_EXISTING_MODEL","AGENT_FABRIC_SOURCE_SPECIALIST",
        "COMPANY_OS_OPENROUTER_FALLBACK"]
    calls=[]
    class Reply:
        def __init__(self,status):self.status_code=status
        def json(self):
            return {"id":"accepted-paid-backup","model":"paid/fallback-model",
                "choices":[{"message":{"content":json.dumps(VALID)}}],
                "usage":{"prompt_tokens":45,"completion_tokens":45}}
    class Client:
        def __init__(self,*a,**k):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*a):return False
        async def post(self,url,**kwargs):
            calls.append(url)
            return Reply(401 if len(calls)==1 else 503 if len(calls)==2 else 200)
    async def go():
        with patch("noetfield_governance.corporate_founder_ai.httpx.AsyncClient",Client):
            return await analyze_public_company(SAMPLE)
    answer=asyncio.run(go())
    assert answer["model_route"]=="COMPANY_OS_OPENROUTER_FALLBACK"
    assert answer["generation_id"]=="accepted-paid-backup"
    assert calls==[
       "https://api.deepseek.com/chat/completions",
       "https://fabric.example.org/api/internal/v1/founder-crm/analyze",
       "https://openrouter.ai/api/v1/chat/completions"]


def test_fabric_cached_failed_receipt_is_skipped_for_other_paid_model(monkeypatch):
    monkeypatch.delenv("CORPORATE_AI_LLM_API_KEY",raising=False)
    monkeypatch.setenv("CORPORATE_FABRIC_CRM_BASE_URL","https://fabric.example.org")
    monkeypatch.setenv("CORPORATE_FABRIC_CRM_BRIDGE_TOKEN","f"*64)
    monkeypatch.setenv("CORPORATE_AI_COMPANY_FALLBACK_API_KEY","paid-company-fallback-key")
    monkeypatch.setenv("CORPORATE_AI_COMPANY_FALLBACK_MODEL","paid/fallback")
    monkeypatch.delenv("OPENROUTER_API_KEY",raising=False)
    visited=[]
    class Reply:
        def __init__(self,status):self.status_code=status
        def json(self):
            if self.status_code==200 and len(visited)==2:
                return {"schema":"noetfield.agent-fabric.founder-task.v1",
                    "state":"FAILED","task_id":visited[0][1]["task_id"],
                    "source_key":SAMPLE["source_key"],
                    "source_signature":visited[0][1]["source_signature"],
                    "external_actions_executed":False}
            return {"model":"paid/fallback","id":"paid-validated",
                "choices":[{"message":{"content":json.dumps(VALID)}}]}
    class Client:
        def __init__(self,*args,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):return False
        async def post(self,url,**kwargs):
            visited.append((url,kwargs["json"]))
            return Reply(409 if len(visited)==1 else 200)
        async def get(self,url,**kwargs):
            visited.append((url,None))
            return Reply(200)
    async def go():
        with patch("noetfield_governance.corporate_founder_ai.httpx.AsyncClient",Client):
            return await analyze_public_company(SAMPLE)
    out=asyncio.run(go())
    assert out["model_route"]=="COMPANY_OS_OPENROUTER_FALLBACK"
    assert len(visited)==3
    assert "/tasks/" in visited[1][0]


def test_free_and_unopted_legacy_openrouter_are_not_silent_model_dependencies(monkeypatch):
    from noetfield_governance.corporate_founder_ai import _model_routes
    monkeypatch.delenv("CORPORATE_AI_LLM_API_KEY",raising=False)
    monkeypatch.delenv("CORPORATE_FABRIC_CRM_BRIDGE_TOKEN",raising=False)
    monkeypatch.delenv("CORPORATE_AI_COMPANY_FALLBACK_API_KEY",raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY","expired-legacy-key")
    monkeypatch.setenv("OPENROUTER_MODEL","openrouter/legacy-model")
    monkeypatch.delenv("CORPORATE_AI_ENABLE_LEGACY_OPENROUTER",raising=False)
    assert _model_routes()==[]
    monkeypatch.setenv("CORPORATE_AI_ENABLE_LEGACY_OPENROUTER","1")
    monkeypatch.setenv("OPENROUTER_MODEL","free-model:free")
    assert _model_routes()==[]
    monkeypatch.setenv("CORPORATE_AI_LLM_API_KEY","paid-company-key")
    monkeypatch.setenv("CORPORATE_AI_LLM_BASE_URL","https://api.deepseek.com")
    monkeypatch.setenv("CORPORATE_AI_LLM_MODEL","deepseek-flash:free")
    assert _model_routes()==[]


def test_founder_ai_endpoints_are_operator_only_and_bounded():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
            assert (await c.get("/api/corporate-crm/founder/ai")).status_code in (403,503)
            assert (await c.post("/api/corporate-crm/founder/ai/run",
                      json={"limit":2})).status_code in (403,503)
        fake={"model_analyses_completed":1,"analyses":[],"no_outreach_sent":True}
        done={"state":"COMPLETE","attempted":1,"completed":1,"models_called":1}
        with patch("noetfield_governance.api._require_connect_desk_operator",return_value=None),patch(
             "noetfield_governance.corporate_founder_ai.founder_ai_board",
             new_callable=AsyncMock,return_value=fake) as read,patch(
             "noetfield_governance.corporate_founder_ai.run_ai_batch",
             new_callable=AsyncMock,return_value=done) as worker:
            async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
                assert (await c.get("/api/corporate-crm/founder/ai")).json()["model_analyses_completed"]==1
                result=await c.post("/api/corporate-crm/founder/ai/run",
                            json={"limit":2,"source_key":"sme:ca:42"})
                assert result.status_code==200 and result.json()["models_called"]==1
                too_many=await c.post("/api/corporate-crm/founder/ai/run",json={"limit":100})
                assert too_many.status_code==422
            assert worker.await_args.kwargs["source_key"]=="sme:ca:42"
            assert read.await_count==1
    asyncio.run(run())


@pytest.mark.skipif(not os.getenv("CONNECT_TEST_POSTGRES_URL"),reason="Disposable PostgreSQL required")
def test_postgres_ai_receipts_are_idempotent_capped_and_never_create_buyer(monkeypatch):
    import asyncpg
    from noetfield_governance.corporate_founder_ai import _source_signature
    async def run():
        url=os.environ["CONNECT_TEST_POSTGRES_URL"]
        source_key="ai-research:"+uuid.uuid4().hex
        site="https://example.org/public/"+source_key
        db=await asyncpg.connect(url)
        try:
            await db.execute("CREATE SCHEMA IF NOT EXISTS noetfield")
            await prepare_ai(db)
            await db.execute("""INSERT INTO noetfield.corp_research_sources(
               source_key,organization,lane,original_url,website,evidence_url,
               review_status,score)
               VALUES($1,'Example AI Sourcing Co','CORPORATE',$2,'https://example.org',
                 $2,'PROFILE_REVIEWED',96)""",source_key,site)
            await db.execute("""INSERT INTO noetfield.corp_founder_scout(
              source_key,page_url,site_title,site_description,scan_state)
              VALUES($1,'https://example.org/','Business technology services',
               'Professional managed services and IT operations.',
               'PUBLIC_CONTACT_PAGE')""",source_key)
        finally:
            await db.close()
        monkeypatch.setenv("OPENROUTER_API_KEY","test-key")
        monkeypatch.setenv("CORPORATE_AI_ENABLE_LEGACY_OPENROUTER","1")
        monkeypatch.setenv("OPENROUTER_MODEL","test-model")
        model_result={"analysis":VALID,"model":"test/model",
          "generation_id":"gen-integration","prompt_tokens":100,
          "completion_tokens":80,"cost_usd":0.0003,"cost_from_provider":True}
        with patch("noetfield_governance.corporate_founder_ai._database_url",
                   return_value=url),patch(
             "noetfield_governance.corporate_founder_ai.analyze_public_company",
             new_callable=AsyncMock,return_value=model_result) as provider:
            first=await run_ai_batch(object(),source_key=source_key,limit=1)
            assert first["completed"]==1 and first["models_called"]==1
            again=await run_ai_batch(object(),source_key=source_key,limit=1)
            assert again["attempted"]==0 and again["models_called"]==0
            assert provider.await_count==1
            board=await founder_ai_board(object())
            assert board["model_analyses_completed"]>=1
            assert board["no_outreach_sent"] is True
        db=await asyncpg.connect(url)
        try:
            row=await db.fetchrow("""SELECT analysis_json,generation_id,
              prompt_tokens,completion_tokens,cost_usd
              FROM noetfield.corp_founder_ai WHERE source_key=$1""",source_key)
            assert row is not None
            assert json.loads(row["analysis_json"])==VALID
            assert row["generation_id"]=="gen-integration"
            assert float(row["cost_usd"])==0.0003
            assert await db.fetchval(
              "SELECT count(*)::int FROM noetfield.corp_crm_deals WHERE summary LIKE $1",
              "%"+source_key+"%")==0
        finally:
            await db.close()
    asyncio.run(run())


def test_founder_ui_shows_ai_as_unverified_hypothesis_not_sale():
    from pathlib import Path
    html=(Path(__file__).resolve().parents[2]/
          "services/governance/noetfield_governance/private_corporate_crm.html").read_text()
    assert 'id="founder-ai-next"' in html
    assert 'id="founder-ai-status"' in html
    assert "AI hypothesis, not a verified customer" in html
    assert "/api/corporate-crm/founder/ai/run" in html
