/**
 * Source of truth for /api/company-os-intake.
 * Bundled to Cloudflare Pages Functions by scripts/bundle-pages-functions.mjs.
 * Backend-only Company OS credential; no duplicate CRM, task queue or fake success.
 */
const ALLOWED_HOSTS=new Set([
 "business-os-core-production.up.railway.app",
 "company-os-staging-staging.up.railway.app"
]);
const MAX_BYTES=10000;
const INTENTS=new Set(["governance","automation","developer","partnership","support","research","pilot","other"]);
const AUDIENCES=new Set(["enterprise","operator","developer","founder","investor","partner","customer","researcher","other"]);
function json(obj,status=200){return new Response(JSON.stringify(obj),{status,headers:{
 "content-type":"application/json; charset=utf-8","cache-control":"no-store",
 "x-content-type-options":"nosniff","referrer-policy":"no-referrer"
}})}
function clean(v,max){return typeof v==="string"?v.trim().slice(0,max):""}
function emailOk(v){return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)&&v.length<=254}
function target(env){
 const value=env?.COMPANY_OS_INTAKE_URL,token=env?.COMPANY_OS_PROXY_TOKEN;
 if(typeof value!=="string"||typeof token!=="string"||token.length<32)return null;
 try{
  const u=new URL(value);
  if(u.protocol!=="https:"||!ALLOWED_HOSTS.has(u.hostname)||u.pathname!=="/api/intake"||u.search||u.hash||u.username||u.password)return null;
  return {url:u.toString(),token};
 }catch{return null}
}
async function handler(req){
 const method=req.method||"GET";
 if(method!=="POST")return json({accepted:false,error:"Method not allowed"},405);
 const headers=req.headers||{},origin=headers.origin||"",host=headers.host||"";
 // Browser POST must originate on the exact same host. Preview pages.dev is allowed
 // only from its own origin; other sites cannot cross-post with a browser.
 if(origin && (typeof host!=="string"||origin!=="https://"+host))
  return json({accepted:false,error:"Origin not allowed"},403);
 if(String(headers["content-type"]||"").split(";")[0].trim().toLowerCase()!=="application/json")
  return json({accepted:false,error:"Content type must be application/json"},415);
 const raw=typeof req.rawBody==="string"?req.rawBody:"";
 if(raw.length>MAX_BYTES||Number(headers["content-length"]||0)>MAX_BYTES)
  return json({accepted:false,error:"Request too large"},413);
 const data=req.body;
 if(!data||typeof data!=="object"||Array.isArray(data)||raw.length<2)
  return json({accepted:false,error:"Invalid request payload"},400);
 if(clean(data.website,200))return json({accepted:true},202); // Honeypot: never enters CRM.
 const name=clean(data.name,120),email=clean(data.email,254).toLowerCase();
 const company=clean(data.company,140),role=clean(data.role,100),problem=clean(data.problem,2500);
 const audience=clean(data.audience,50),intent=clean(data.intent,50);
 const urgency=clean(data.urgency,30),idempotency=clean(data.idempotency_key,64);
 if(name.length<2||!emailOk(email)||problem.length<10||data.consent!==true||
    !INTENTS.has(intent)||!AUDIENCES.has(audience)||
    !["now","30_days","quarter","exploring"].includes(urgency)||
    !/^nfcom-[a-z0-9-]{16,58}$/.test(idempotency))
  return json({accepted:false,error:"Check required information and consent"},422);
 const env=req.env||process.env;
 const upstream=target(env);
 if(!upstream)return json({accepted:false,error:"This request channel is not yet connected. Please use the contact page."},503);
 const ip=String(headers["cf-connecting-ip"]||"unavailable");
 const source=new TextEncoder().encode(upstream.token+"|"+ip);
 const hash=await crypto.subtle.digest("SHA-256",source);
 const fingerprint=Array.from(new Uint8Array(hash),b=>b.toString(16).padStart(2,"0")).join("");
 const body={
  brand:"noetfield",audience,intent,name,email,company,role,problem,urgency,
  estimated_value:0,consent:true,ai_consent:data.ai_consent===true,
  website:"",idempotency_key:idempotency
 };
 let response;
 try{
  response=await fetch(upstream.url,{
    method:"POST",redirect:"manual",headers:{
      "content-type":"application/json","accept":"application/json",
      "x-company-os-proxy-token":upstream.token,
      "x-company-os-client-hash":fingerprint
    },body:JSON.stringify(body),signal:AbortSignal.timeout(7500)
  });
 }catch{
  return json({accepted:false,error:"Intake temporarily unavailable. Please retry or contact operations."},503);
 }
 if(response.status!==202)
  return json({accepted:false,error:response.status===429?"Too many requests. Please try later.":"Intake temporarily unavailable."},response.status===429?429:503);
 let result;
 try{result=await response.json()}catch{return json({accepted:false,error:"Could not verify intake confirmation."},503)}
 if(result?.accepted!==true||typeof result.reference!=="string")
  return json({accepted:false,error:"Could not verify intake confirmation."},503);
 return json({accepted:true,reference:result.reference,route:result.route||"specialist_review",
   message:"Your request is queued for an internal specialist review. No outbound message was sent by an agent."},202);
}
module.exports=handler;
