import test from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";

const source=await readFile(new URL("../../functions/api/company-os-intake.js",import.meta.url),"utf8");
const {onRequestPost}=await import("data:text/javascript;base64,"+Buffer.from(source).toString("base64"));
const target="https://company-os-staging-staging.up.railway.app/api/intake";
const env={COMPANY_OS_PROXY_TOKEN:"private-example-token-only-for-test-000000000000",COMPANY_OS_INTAKE_URL:target};
function payload(overrides={}){
 return {name:"QA Buyer",email:"buyer@example.test",company:"Example Org",role:"CTO",
  intent:"governance",audience:"enterprise",urgency:"30_days",
  problem:"We need governed deployments with independent verification.",
  consent:true,ai_consent:false,website:"",
  idempotency_key:"nfcom-123e4567-e89b-12d3-a456-426614174000",...overrides};
}
function request(body=payload(),extra={}){
 return new Request("https://www.noetfield.com/api/company-os-intake",{
  method:"POST",headers:{"content-type":"application/json","origin":"https://www.noetfield.com","CF-Connecting-IP":"203.0.113.45",...extra},
  body:JSON.stringify(body)
 });
}
test("valid commercial intake is proxied with private service credential and confirmed event reference",async t=>{
 const prior=globalThis.fetch;
 let saw;
 globalThis.fetch=async(url,opts)=>{
   saw={url,opts};
   return new Response(JSON.stringify({accepted:true,reference:"evt_test_record_only",route:"enterprise_solution"}),{status:202,headers:{"content-type":"application/json"}});
 };
 t.after(()=>{globalThis.fetch=prior});
 const r=await onRequestPost({request:request(),env});
 const json=await r.json();
 assert.equal(r.status,202);
 assert.equal(json.accepted,true);
 assert.equal(json.reference,"evt_test_record_only");
 assert.equal(saw.url,target);
 assert.equal(saw.opts.headers["x-company-os-proxy-token"],env.COMPANY_OS_PROXY_TOKEN);
 assert.match(saw.opts.headers["x-company-os-client-hash"],/^[a-f0-9]{64}$/);
 const forwarded=JSON.parse(saw.opts.body);
 assert.equal(forwarded.brand,"noetfield");
 assert.equal(forwarded.idempotency_key,payload().idempotency_key);
 assert.equal(forwarded.estimated_value,0);
 assert.equal(forwarded.ai_consent,false);
 assert.equal(JSON.stringify(json).includes(env.COMPANY_OS_PROXY_TOKEN),false);
});
test("missing server-only identity fails closed without success or external request",async t=>{
 const old=globalThis.fetch;let count=0;
 globalThis.fetch=()=>{count++;throw Error("should not run")};
 t.after(()=>{globalThis.fetch=old});
 const r=await onRequestPost({request:request(),env:{}});
 assert.equal(r.status,503);
 assert.equal((await r.json()).accepted,false);
 assert.equal(count,0);
});
test("origin mismatch and consent failure are rejected before dispatch",async()=>{
 const foreign=await onRequestPost({request:request(payload(),{origin:"https://example.test"}),env});
 assert.equal(foreign.status,403);
 const denied=await onRequestPost({request:request(payload({consent:false})),env});
 assert.equal(denied.status,422);
 const forged=await onRequestPost({request:request(payload({idempotency_key:"unsafe/../../"})),env});
 assert.equal(forged.status,422);
});
test("upstream must match explicit HTTPS company OS host and path",async()=>{
 for(const url of ["https://evil.example/api/intake","http://company-os-staging-staging.up.railway.app/api/intake","https://company-os-staging-staging.up.railway.app/other","https://company-os-staging-staging.up.railway.app/api/intake?redirect=1"]){
  const r=await onRequestPost({request:request(),env:{...env,COMPANY_OS_INTAKE_URL:url}});
  assert.equal(r.status,503,url);
 }
});
test("rejected or unavailable upstream is not misrepresented as a submitted lead",async t=>{
 const old=globalThis.fetch;
 t.after(()=>{globalThis.fetch=old});
 globalThis.fetch=async()=>new Response(JSON.stringify({accepted:false}),{status:401});
 let r=await onRequestPost({request:request(),env});
 assert.equal(r.status,503);
 assert.equal((await r.json()).accepted,false);
 globalThis.fetch=async()=>{throw Error("network down")};
 r=await onRequestPost({request:request(),env});
 assert.equal(r.status,503);
});
test("honeypot is excluded from actual company event stream",async t=>{
 const old=globalThis.fetch;let called=false;
 globalThis.fetch=async()=>{called=true;throw Error("should not call")};
 t.after(()=>{globalThis.fetch=old});
 const r=await onRequestPost({request:request(payload({website:"https://spam.example"})),env});
 assert.equal(r.status,202);
 assert.equal(called,false);
});
