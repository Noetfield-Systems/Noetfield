/**
 * Noetfield commercial intake -> EXISTING Company OS.
 * Cloudflare Pages Function; service credential never reaches browser.
 * No CRM, queue, agent registry or lead copy in this Function.
 */
const ALLOWED_HOSTS=new Set([
  "business-os-core-production.up.railway.app",
  "company-os-staging-staging.up.railway.app"
]);
const MAX_BYTES=10000;
const allowedIntents=new Set(["governance","automation","developer","partnership","support","research","pilot","other"]);
const allowedAudiences=new Set(["enterprise","operator","developer","founder","investor","partner","customer","researcher","other"]);
function json(obj,status=200){
 return new Response(JSON.stringify(obj),{status,headers:{
   "content-type":"application/json; charset=utf-8","cache-control":"no-store",
   "x-content-type-options":"nosniff","referrer-policy":"no-referrer"
 }});
}
function clean(s,max){return typeof s==="string"?s.trim().slice(0,max):""}
function isEmail(s){return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s)&&s.length<=254}
function internalTarget(env){
 const raw=env?.COMPANY_OS_INTAKE_URL,secret=env?.COMPANY_OS_PROXY_TOKEN;
 if(typeof raw!=="string"||typeof secret!=="string"||secret.length<32) return null;
 try {
  const url=new URL(raw);
  if(url.protocol!=="https:"||!ALLOWED_HOSTS.has(url.hostname)||url.pathname!=="/api/intake"||url.search||url.hash||url.username||url.password)
   return null;
  return {url:url.toString(),secret};
 }catch {return null}
}
export async function onRequestPost({request,env}){
 if(request.headers.get("content-type")?.split(";")[0].trim().toLowerCase()!=="application/json")
  return json({accepted:false,error:"Content type must be application/json."},415);
 const origin=request.headers.get("origin");
 if(origin && origin!==new URL(request.url).origin) return json({accepted:false,error:"Origin not allowed."},403);
 const size=Number(request.headers.get("content-length")||0);
 if(!Number.isSafeInteger(size)||size>MAX_BYTES) return json({accepted:false,error:"Request too large."},413);
 let raw;
 try{
   raw=await request.text();
   if(raw.length>MAX_BYTES)return json({accepted:false,error:"Request too large."},413);
 }catch{return json({accepted:false,error:"Invalid request."},400)}
 let data;
 try{data=JSON.parse(raw)}catch{return json({accepted:false,error:"Malformed JSON."},400)}
 if(!data||typeof data!=="object"||Array.isArray(data))return json({accepted:false,error:"Invalid payload."},400);
 // Honeypot is never processed as a real buyer.
 if(clean(data.website,200))return json({accepted:true},202);
 const name=clean(data.name,120),email=clean(data.email,254).toLowerCase();
 const company=clean(data.company,140),role=clean(data.role,100),problem=clean(data.problem,2500);
 const intent=clean(data.intent,50),audience=clean(data.audience,50);
 const urgency=clean(data.urgency,30),idempotency=clean(data.idempotency_key,64);
 if(name.length<2||!isEmail(email)||problem.length<10||data.consent!==true
   ||!allowedIntents.has(intent)||!allowedAudiences.has(audience)
   ||!["now","30_days","quarter","exploring"].includes(urgency)
   ||!/^nfcom-[a-z0-9-]{16,58}$/.test(idempotency))
   return json({accepted:false,error:"Check the required information and consent."},422);
 const upstream=internalTarget(env);
 if(!upstream)return json({accepted:false,error:"Intake not yet connected. Please use the regular contact page."},503);
 const ip=request.headers.get("CF-Connecting-IP")||"unavailable";
 // Stable pseudonymous fingerprint, salted per deployment; no raw IP in downstream.
 const source=new TextEncoder().encode(upstream.secret+"|"+ip);
 const digest=await crypto.subtle.digest("SHA-256",source);
 const clientHash=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,"0")).join("");
 const payload={
   brand:"noetfield",audience,intent,name,email,company,role,problem,urgency,
   estimated_value:0,consent:true,ai_consent:data.ai_consent===true,
   website:"",idempotency_key:idempotency
 };
 let resp;
 try{
   resp=await fetch(upstream.url,{
     method:"POST",redirect:"manual",headers:{
       "content-type":"application/json","accept":"application/json",
       "x-company-os-proxy-token":upstream.secret,
       "x-company-os-client-hash":clientHash
     },body:JSON.stringify(payload),signal:AbortSignal.timeout(7500)
   });
 }catch{return json({accepted:false,error:"Intake temporarily unavailable. Please try again or contact operations."},503)}
 if(resp.status!==202)return json({accepted:false,error:resp.status===429?"Too many requests. Please try later.":"Intake temporarily unavailable."},resp.status===429?429:503);
 let accepted;
 try{accepted=await resp.json()}catch{return json({accepted:false,error:"Intake confirmation unavailable."},503)}
 if(accepted?.accepted!==true||typeof accepted.reference!=="string")
   return json({accepted:false,error:"Intake confirmation unavailable."},503);
 // Never expose backend URLs, operator credentials or internal model payloads.
 return json({accepted:true,reference:accepted.reference,route:accepted.route||"specialist_review",
   message:"Your request is queued for an internal specialist review. We have not sent external messages."},202);
}
export async function onRequest({request,env}){
 if(request.method==="POST")return onRequestPost({request,env});
 return json({accepted:false,error:"Method not allowed."},405);
}
