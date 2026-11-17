"use strict";
/* Real Chromium regression against the actual private CRM HTML. All API calls
 * go to a deterministic local fake, never production, Stripe or SMTP. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const http=require("node:http");
const path=require("node:path");
const { chromium }=require("playwright");

const html=fs.readFileSync(path.join(__dirname,"../services/governance/noetfield_governance/private_corporate_crm.html"),"utf8");
const research=Array.from({length:22},(_,index)=>({
 source_key:"github:organization:source-"+index,
 organization:"Business Source "+String(index+1).padStart(2,"0"),
 lane:index%5===0?"RWA":"CORPORATE",original_url:"https://example.org/sources/"+index,
 review_status:"PROFILE_REVIEWED",score:90-index,promoted_deal_id:null
}));
const events={qualify:[],outreach:0};
const dealId="99771110-1111-4111-8111-111111111111";
let confirmed=null;
function json(res,data,status=200){
 res.writeHead(status,{"content-type":"application/json","cache-control":"no-store"});
 res.end(JSON.stringify(data));
}
const server=http.createServer(async(req,res)=>{
 const url=new URL(req.url,"http://localhost"),key=req.method+" "+url.pathname;
 if(key==="GET /api/corporate-crm/app"){res.writeHead(200,{"content-type":"text/html; charset=utf-8"});res.end(html);return;}
 if(key==="GET /api/opportunities/desk/session"){json(res,{authenticated:true,csrf:"test-csrf"});return;}
 if(key==="GET /api/opportunities/desk/google-config"){json(res,{google_enabled:false});return;}
 if(key==="GET /api/corporate-crm/board"){json(res,{
  accounts:confirmed?[{id:"a1111111-1111-4111-8111-111111111111",name:confirmed.organization,kind:"buyer",sector:"professional_services",owner:"Noetfield Revenue"}]:[],
  people:[],deals:confirmed?[{id:dealId,account_name:confirmed.organization,stage:"NEW",offer:"ai_sales_os_pilot",estimated_minor:0,currency:"cad",summary:"Source verified",owner:"Noetfield Revenue",next_date:"",next_action:"Qualify customer scope"}]:[],
  metrics:{open:confirmed?1:0,due:0,total_accounts:confirmed?1:0,paid_verified_by_currency_minor:{}}
 });return;}
 if(key==="GET /api/corporate-crm/research"){json(res,{items:research,total_staged:research.length});return;}
 if(key==="GET /api/corporate-crm/research/status"){json(res,{last:{state:"COMPLETE"}});return;}
 if(key==="GET /api/corporate-crm/outreach/metrics"){json(res,{sending_status:{},provider_verified_replies:0,suppressed_recipients:0});return;}
 if(key==="GET /api/corporate-crm/operations/plan"){json(res,{actions:[],sample_is_complete:true,forecast_estimated_minor_sample:{},matched_paid_checkouts_minor_all:{},due_count_all:0});return;}
 if(key==="GET /api/corporate-crm/operations/cycle-status"){json(res,{configured:false});return;}
 if(key==="GET /api/corporate-crm/growth/funnel"){json(res,{stages:{research:research.length,paid_live_checkouts:0},evidence_definitions:{},priority_source_review:[]});return;}
 if(key==="GET /api/corporate-crm/deals/"+dealId){json(res,{
  deal:{id:dealId,account_name:confirmed.organization,stage:"NEW",revision:0,source_channel:"FIELDWORK_OPERATOR_QUALIFIED",
   source_intake_id:"",account_id:"a1111111-1111-4111-8111-111111111111",
   offer:"ai_sales_os_pilot",estimated_minor:0,currency:"cad",owner:"Noetfield Revenue",
   next_action:"Qualify customer scope",summary:"Research source",accepted_scope_url:""},
  activity:[],commercial_case:{}
 });return;}
 if(key==="POST /api/corporate-crm/research/promote"){
  let raw="";for await(const c of req)raw+=c;
  let data;try{data=JSON.parse(raw)}catch{json(res,{detail:"INVALID_JSON"},400);return;}
  events.qualify.push({data,csrf:req.headers["x-desk-csrf"]});
  if(data.contact_email==="fail@example.org"){json(res,{detail:"VERIFIED_CONTACT_REVIEW_REQUIRED"},422);return;}
  if(!data.source_key||!data.contact_name||!data.contact_evidence||!data.contact_basis
   ||req.headers["x-desk-csrf"]!=="test-csrf"){json(res,{detail:"INVALID_REVIEW"},422);return;}
  if(data.contact_basis==="PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL"&&
    (!data.publication_no_solicitation||data.role_relevance.length<20)){
    json(res,{detail:"ROLE_RELEVANCE_REVIEW_REQUIRED"},422);return;
  }
  confirmed=research.find(x=>x.source_key===data.source_key);
  if(!confirmed){json(res,{detail:"UNKNOWN_SOURCE"},422);return;}
  confirmed.promoted_deal_id=dealId;
  json(res,{promoted:true,deal_id:dealId,outreach_sent:false,payment_verified:false});return;
 }
 if(key==="POST /api/corporate-crm/outreach/send"){events.outreach++;json(res,{detail:"NOT_ALLOWED"},403);return;}
 json(res,{detail:"UNEXPECTED_MOCK_ENDPOINT:"+key},404);
});
const sleep=ms=>new Promise(done=>setTimeout(done,ms));
async function run(){
 await new Promise(resolve=>server.listen(0,"127.0.0.1",resolve));
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
  const base="http://127.0.0.1:"+server.address().port;
  for(const width of [320,390,768,1440]){
   const page=await browser.newPage({viewport:{width,height:800}});
   const errors=[];page.on("pageerror",error=>errors.push(error.message));
   await page.route("https://fonts.googleapis.com/**",route=>route.abort());
   await page.route("https://fonts.gstatic.com/**",route=>route.abort());
   await page.goto(base+"/api/corporate-crm/app",{waitUntil:"domcontentloaded"});
   await page.waitForFunction(()=>document.querySelector("#fieldwork-status")?.textContent?.includes("22 public organization sources"),{timeout:15000});
   await page.getByRole("button",{name:"Qualify for Corporate CRM"}).last().click();
   const dialog=page.locator("#research-qualify-dialog");
   await dialog.waitFor({state:"visible"});
   assert.equal(await page.locator("#research-qualify-form").isVisible(),true,
    "Qualify must show a visible form, never leave a disabled hidden button");
   assert.equal(await page.locator('[name="contact_name"]').evaluate(el=>el===document.activeElement),true);
   const over=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
   const offenders=await page.evaluate(()=>[...document.querySelectorAll("body *")]
     .map(el=>({tag:el.tagName,id:el.id,cls:String(el.className||"").slice(0,55),
       left:Math.round(el.getBoundingClientRect().left),right:Math.round(el.getBoundingClientRect().right),
       width:Math.round(el.getBoundingClientRect().width)}))
     .filter(x=>x.right>innerWidth+3).sort((a,b)=>b.right-a.right).slice(0,16));
   assert.ok(over<=2,"Horizontal page overflow at "+width+"px: "+over+" / "+JSON.stringify(offenders));
   assert.equal(await page.locator("#research-qualify-submit").isEnabled(),true);
   await page.keyboard.press("Escape");await dialog.waitFor({state:"hidden"});
   await page.getByRole("button",{name:"Qualify for Corporate CRM"}).last().click();
   await dialog.waitFor({state:"visible"});
   await page.locator("[data-qualify-cancel]").click();
   await dialog.waitFor({state:"hidden"});
   if(width===390){
    const qualify=page.getByRole("button",{name:"Qualify for Corporate CRM"}).last();
    await qualify.click();
    const form=page.locator("#research-qualify-form");
    await form.locator('[name="contact_name"]').fill("Jane Example");
    await form.locator('[name="contact_email"]').fill("fail@example.org");
    await form.locator('[name="contact_evidence"]').fill("https://example.org/contacts/jane");
    await form.locator('[name="contact_basis"]').selectOption("PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL");
    assert.equal(await form.locator('[name="role_relevance"]').isVisible(),true,
     "Published business contact must require relevance evidence");
    await form.locator('[name="role_relevance"]').fill("This is a published partnership contact for a current operations role.");
    await form.locator('[name="publication_no_solicitation"]').check();
    await form.locator("#research-qualify-submit").click();
    await page.waitForFunction(()=>document.querySelector("#research-qualify-status")?.textContent?.includes("VERIFIED_CONTACT_REVIEW_REQUIRED"));
    assert.equal(await form.locator("#research-qualify-submit").isEnabled(),true,
     "Server validation failure must reenable the submit button");
    await form.locator('[name="contact_email"]').fill("jane@example.org");
    await form.locator("#research-qualify-submit").click();
    await dialog.waitFor({state:"hidden"});
    await page.waitForFunction(()=>document.querySelector("#feedback")?.textContent?.includes("Qualified opportunity opened in CRM"),{timeout:15000});
    assert.equal(await page.locator("#side-panel").getByText("Business Source 22",{exact:false}).count()>0,true);
    assert.equal(events.qualify.length,2,"Only explicit form submit reaches promotion");
    assert.equal(events.qualify[1].csrf,"test-csrf");
    assert.equal(events.qualify[1].data.publication_no_solicitation,true);
    assert.ok(events.qualify[1].data.role_relevance.length>=20);
    assert.equal(events.outreach,0,"Qualify must not send marketing email");
   }
   await page.locator('[data-view="accounts"]').click();
   assert.equal(await page.locator("#list-title").textContent(),"Corporate accounts");
   await page.locator('[data-view="people"]').click();
   assert.equal(await page.locator("#list-title").textContent(),"Professional contacts");
   await page.locator('[data-view="partners"]').click();
   await page.locator('[data-view="pipeline"]').click();
   await page.locator("#create-toggle").click();
   assert.equal(await page.locator("#deal-panel").isVisible(),true);
   await page.locator("#create-toggle").click();
   assert.equal(await page.locator("#data-view").isVisible(),true);
   assert.deepEqual(errors,[],"No uncaught browser script errors at "+width+"px");
   console.log("PASS CRM Chromium "+width+"px: qualify modal, close, nav, forms, responsive");
   await page.close();
  }
  assert.equal(events.outreach,0);
  console.log("PASS CRM qualification form: server 422 recovery, source evidence, CSRF, mocked success, no email");
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
}
run().catch(error=>{console.error(error);server.close();process.exitCode=1});
