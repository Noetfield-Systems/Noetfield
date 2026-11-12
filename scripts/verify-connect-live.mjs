#!/usr/bin/env node
/**
 * Noetfield Connect public E2E contract: real Cloudflare -> Platform Postgres.
 * Synthetic submissions only; never counted as leads or sent as outreach.
 * Withholds all credentials; no auth is required for the public test path.
 */
import assert from "node:assert/strict";
import {randomBytes} from "node:crypto";

const WWW=(process.env.CONNECT_WWW_BASE||"https://www.noetfield.com").replace(/\/$/,"");
const PLATFORM=(process.env.CONNECT_PLATFORM_BASE||"https://platform.noetfield.com").replace(/\/$/,"");
const TIMEOUT=Number(process.env.CONNECT_TEST_TIMEOUT_MS||25000);
function timeoutSignal(){return AbortSignal.timeout(TIMEOUT);}
async function req(url,opts={}){
  const res=await fetch(url,{...opts,signal:timeoutSignal(),headers:{"Accept":"application/json","User-Agent":"noetfield-connect-e2e/1.0",...(opts.headers||{})}});
  const raw=await res.text();
  let parsed={};try{parsed=JSON.parse(raw);}catch{}
  return {status:res.status,ok:res.ok,text:raw,data:parsed,url:res.url};
}
function check(value,msg){assert.ok(value,msg);}
const token=randomBytes(8).toString("hex").toUpperCase();
const rid="RID-E2E-CNX-"+token;
const record={
  organization:"Noetfield Connect E2E Probe",
  contact_name:"Automated Connect E2E",
  contact_email:"e2e@noetfield.com",
  message:"Automated Noetfield Connect end-to-end record with event category, explicit synthetic status and repeatable idempotency check.",
  request_id:rid,
  sku:"general",
  vector:"external-opportunities",
  source:"web",
  metadata:{
    form_id:"nf_intake_e2e",topic:"e2e",intake_kind:"test",
    pipeline:"nf_connect_e2e:production_verify",
    page:"/connect/",category:"events",initiative:"noetfield",
    next_step:"async",lead_source:"linkedin",test_only:true
  }
};
const checks=[];
for(const [url,needle] of [["/connect/","Noetfield Connect"],["/opportunities/","opportunities"]]){
  const p=await req(WWW+url,{headers:{"Accept":"text/html"}});
  check(p.ok&&p.status===200,url+" public HTML not reachable: "+p.status);
  check(p.text.toLowerCase().includes(needle.toLowerCase()),url+" HTML lacks expected page content");
  checks.push(url+" HTML 200 and meaningful content");
}
const health=await req(PLATFORM+"/api/intake/health");
check(health.ok,"platform intake health failed: "+health.status);
check(health.data.storage==="postgres","platform intake is not PostgreSQL-backed");
checks.push("Platform intake health: postgres");
const first=await req(WWW+"/api/intake",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(record)});
check(first.ok,"Connect intake submit failed: "+first.status+" "+String(first.data?.detail||"").slice(0,100));
check(first.data.intake_persisted===true,"Noetfield www failed to confirm durable persistence");
check(/^INT-[A-Z0-9]{12}$/.test(String(first.data.intake_id||"")),"No canonical Platform intake ID returned");
check(first.data.intake_kind==="test","Synthetic record was not marked as test");
checks.push("Public Connect intake POST -> canonical Platform source ID");
const second=await req(WWW+"/api/intake",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(record)});
check(second.ok&&second.data.intake_persisted===true,"Dedupe retry was not persisted");
check(second.data.intake_id===first.data.intake_id,"Duplicate request created another intake");
check(second.data.deduped===true,"Dedupe acknowledgement missing");
checks.push("Repeated POST is idempotent and deduped");
const status=await req(PLATFORM+"/api/intake/status?request_id="+encodeURIComponent(rid));
check(status.ok,"Canonical intake readback unavailable: "+status.status);
check(status.data.intake_id===first.data.intake_id,"Readback points to incorrect intake");
checks.push("Readback matches same canonical intake");
process.stdout.write(JSON.stringify({ok:true,schema:"noetfield.connect-live-e2e.v1",checks,intake_id:first.data.intake_id,request_id:rid,synthetic:true,leads_created:0,bookings_created:0,verified_revenue:0},null,2)+"\n");
