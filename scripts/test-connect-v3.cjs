const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const html=fs.readFileSync(path.join(root,"connect/index.html"),"utf8");
const js=fs.readFileSync(path.join(root,"assets/noetfield-connect-v3.js"),"utf8");
const css=fs.readFileSync(path.join(root,"assets/noetfield-connect-v3.css"),"utf8");
assert.match(html,/Noetfield Connect/);
assert.match(html,/window\.NFIntakeCore/);
assert.match(html,/core\.postIntake\(/);
assert.match(html,/connect-wizard-v3/);
assert.match(html,/name="skillStack"/);
assert.match(html,/name="availability"/);
assert.match(html,/name="portfolioUrl"/);
assert.match(html,/name="sourceContext"/);
assert.match(html,/name="linkedinURL"/);
assert.match(html,/name="analyticsConsent"/);
assert.match(html,/id="connectTracking"/);
assert.match(html,/id="connectFeedback"/);
assert.match(html,/id="connectResult"/);
assert.match(html,/noetfield-connect-v3\.css/);
assert.match(html,/noetfield-connect-v3\.js/);
assert.match(html,/referral_code:safeTag/);
assert.match(html,/nf-connect-saved/);
assert.match(html,/intake_persisted!==true/);
new vm.Script(js,{filename:"connect-v3.js"});
assert.ok(css.length>3000,"premium styling missing");
for(const t of ["connect.analytics_optin","connect.status_checked","connect.feedback_recorded","connect.intake_persisted"]){
  assert.ok(js.includes(t),"missing core journey "+t);
}
assert.ok(js.includes("params.get(\"source\")"),"attribution missing");
assert.ok(js.includes('analytics.checked'),"analytics must be opt-in");
assert.ok(js.includes('receipt.request_id'),"private RID tracking missing");
assert.ok(js.includes('"/api/connect/participant/status"'),"status endpoint not wired");
assert.ok(js.includes('"/api/connect/participant/feedback"'),"feedback endpoint not wired");

function res(){
 const state={status:200,headers:{},body:null};
 return {state,setHeader(k,v){state.headers[k]=v},
   status(code){state.status=code;return this},
   json(body){state.body=body;return this}};
}
async function proxyChecks(){
 for(const name of ["status","feedback"]){
  const handler=require(path.join(root,"api/connect/participant",name+".js"));
  const p={request_id:"RID-CNX-"+"A".repeat(20),email:"applicant@example.invalid"};
  if(name==="feedback"){p.feedback_id="b".repeat(32);p.rating=4;p.message="Please improve the status view.";}
  const requests=[
   [{method:"GET",headers:{},body:p},405],
   [{method:"POST",headers:{origin:"https://evil.example",host:"www.noetfield.com"},body:p},403],
   [{method:"POST",headers:{},body:{...p,extraneous:"data"}},422],
   [{method:"POST",headers:{},body:{...p,email:"invalid"}},422],
  ];
  for(const [req,expected] of requests){
   const reply=res();await handler(req,reply);assert.equal(reply.state.status,expected,name+" invalid request");
  }
  const original=global.fetch;
  try{
   global.fetch=async (url,opts)=>{
     assert.ok(url.endsWith("/api/connect/participant/"+name),"canonical platform proxy path");
     assert.equal(opts.method,"POST");
     assert.equal(JSON.parse(opts.body).email,"applicant@example.invalid");
     return {ok:true,status:200,json:async()=>name==="feedback"?
       {recorded:true,intake_id:"INT-123456789ABC",feedback_id:p.feedback_id}:
       {found:true,intake_id:"INT-123456789ABC",stage:"NEW",detail:"Received",
        created_at:"2026-11-13T00:00:00Z",owner:"PRIVATE_NEVER_RETURN"}};
   };
   const reply=res();await handler({method:"POST",headers:{},body:p},reply);
   assert.equal(reply.state.status,200);
   assert.equal(reply.state.body.intake_id,"INT-123456789ABC");
   assert.equal(reply.state.body.owner,undefined,"operator data leak");
  }finally{global.fetch=original}
 }
 console.log("PASS: Noetfield Connect v3 frontend, verified proxy guards and statuses");
}
proxyChecks().catch(err=>{console.error(err);process.exit(1)});
