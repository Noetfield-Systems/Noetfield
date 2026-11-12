/** Production HTTP acceptance for Noetfield Connect; synthetic requests are test-labeled. QA run 2026-11-12. */
"use strict";
const crypto=require("node:crypto");
const base="https://www.noetfield.com";
const platform="https://platform.noetfield.com";
const requestId="RID-E2E-CONNECT-"+crypto.randomBytes(8).toString("hex").toUpperCase();
function requireTrue(condition, message){if(!condition)throw new Error(message);}
async function request(url,opts={}){
  const controller=new AbortController();
  const timeout=setTimeout(()=>controller.abort(),16000);
  try{return await fetch(url,{...opts,signal:controller.signal,redirect:"manual",headers:{"Accept":"application/json",...(opts.headers||{})}})}
  finally{clearTimeout(timeout);}
}
(async()=>{
  const webpage=await request(base+"/connect/");
  const html=await webpage.text();
  console.log(JSON.stringify({step:"public connect route",http:webpage.status,hasWizard:html.includes("nfConnectWizard")}));
  requireTrue(webpage.status===200&&html.includes("nfConnectWizard"),"Public /connect/ route is not live with the real wizard");
  const desk=await request(platform+"/api/opportunities/desk/app");
  const shell=await desk.text();
  console.log(JSON.stringify({step:"private desk shell",http:desk.status,hasUI:shell.includes("Opportunity Desk.")}));
  requireTrue(desk.status===200&&shell.includes("Opportunity Desk."),"Production operator desk is not deployed");
  const guard=await request(platform+"/api/opportunities/desk");
  console.log(JSON.stringify({step:"private desk access control",http:guard.status}));
  requireTrue([403,503].includes(guard.status),"Private opportunity data accessible without authorization");
  const payload={
    organization:"Synthetic Connect CI Probe",contact_name:"Synthetic QA",
    contact_email:"e2e@noetfield.com",
    request_id:requestId,sku:"general",vector:"external-opportunities",source:"web",
    message:"SYNTHETIC TEST ONLY: verify that the live public Connect intake persists and deduplicates a test-labeled opportunity. This is not a customer, sale, partner, award, or booking.",
    metadata:{form_id:"nfConnectWizard",page:"/connect/",topic:"business",category:"business",
      intake_kind:"test",pipeline:"connect:production_smoke_test",initiative:"noetfield",
      proposal_title:"Synthetic production smoke request",lead_source:"github-ci"}
  };
  async function submit(){
    const response=await request(base+"/api/intake",{
      method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify(payload)});
    const body=await response.json().catch(()=>({}));
    console.log(JSON.stringify({step:"synthetic intake persistence",http:response.status,
      stored:body.intake_persisted,kind:body.intake_kind,deduped:body.deduped,
      ref:body.intake_id||null}));
    requireTrue(response.status===200&&body.intake_persisted===true&&
      body.intake_kind==="test"&&/^INT-/.test(body.intake_id||""),
      "Live test intake was not confirmed persisted");
    return body;
  }
  const first=await submit();
  const repeated=await submit();
  requireTrue(repeated.intake_id===first.intake_id&&repeated.deduped===true,
    "Live persistent intake idempotency failed");
  console.log("CONNECT_PRODUCTION_LIVE_ACCEPTANCE=PASS");
})().catch(err=>{console.error("CONNECT_PRODUCTION_LIVE_ACCEPTANCE=FAIL "+err.message);process.exitCode=1;});
