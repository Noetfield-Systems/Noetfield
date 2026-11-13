/* Noetfield Connect v3 progressive experience. Existing NFIntakeCore remains the sole intake writer. */
(function(){"use strict";
var form=document.getElementById("connectWizard");
if(!form)return;
var params=new URLSearchParams(location.search);
var tracking=document.getElementById("participantTrack");
var receipt={request_id:"",email:"",intake_id:""};
var intent=form.elements.namedItem("intent");
var analytics=form.elements.namedItem("analyticsConsent");
var sessionId=(window.crypto&&window.crypto.randomUUID)?window.crypto.randomUUID():"";
function get(name){var el=form.elements.namedItem(name);return el?String(el.value||"").trim():"";}
function text(selector,content){var el=document.querySelector(selector);if(el)el.textContent=content;}
function setText(node,content){if(node)node.textContent=content;}
function api(path,payload){
 return fetch(path,{method:"POST",credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json"},
  body:JSON.stringify(payload)}).then(async function(response){
    var data=await response.json().catch(function(){return{}});
    if(!response.ok)throw Error(typeof data.detail==="string"?data.detail:"REQUEST_FAILED");
    return data;
  });
}
function trackEvent(name,detail){
 if(!analytics||!analytics.checked)return;
 api("/api/analytics/event",{
   event_name:name,session_id:sessionId||null,page_path:"/connect/",
   utm_source:(params.get("source")||params.get("utm_source")||"direct").slice(0,70),
   utm_campaign:(params.get("utm_campaign")||"").slice(0,70),
   component:"nf_connect_wizard",
   metadata:{intent:get("intent")||"unset",initiative:get("initiative")||"unset",
             origin:"consented_web",stage:detail||"none"}
 }).catch(function(){});
}
function showConditional(){
 var kind=get("intent");
 var mapping={people:"peopleQualifiers",growth:"growthQualifiers",
              capital:"capitalQualifiers",business:"businessQualifiers"};
 ["peopleQualifiers","growthQualifiers","capitalQualifiers","businessQualifiers"].forEach(function(id){
   var block=document.getElementById(id);if(!block)return;
   block.hidden=id!==mapping[kind];
   block.querySelectorAll("input,select,textarea").forEach(function(el){
     el.disabled=block.hidden;
   });
 });
 var skill=form.elements.namedItem("skillStack");
 if(skill){skill.required=kind==="people";skill.minLength=kind==="people"?3:0;}
 var context=document.getElementById("sourceContextLabel");
 if(context)context.hidden=false;
}
function chooseFromLink(){
 var fromLink=(params.get("type")||params.get("intent")||"").toLowerCase();
 var source=(params.get("source")||params.get("utm_source")||"").toLowerCase();
 if(fromLink==="freelancer"||fromLink==="developer"||fromLink==="talent"||fromLink==="collaborator"){
   intent.value="people";
 }else if(["people","growth","partnership","capital","events","business","other"].includes(fromLink)){
   intent.value=fromLink;
 }
 // Safe, allowlisted offer attribution. Query strings never inject HTML or
 // bypass intake: customers must still review/edit and submit the real form.
 var offerKey=(params.get("offer")||"").toLowerCase();
 var preset={
   "verification-pilot":{
     title:"Independent AI execution verification pilot",
     description:"I want an independent review of a real agent run, code change or API workflow with scoped acceptance criteria and evidence.",
     initiative:"noetfield"
   },
   "software-build":{
     title:"Real software build / repair project",
     description:"I want to build, repair or publish a working software product with real source, testing and accountable delivery.",
     initiative:"noetfield"
   },
   "rwa-sprint":{
     title:"RWA policy-to-execution engineering sprint",
     description:"I want to scope a real-world asset readiness, policy-to-code or onchain integration engineering engagement.",
     initiative:"noetfield"
   }
 }[offerKey];
 if(preset){
   intent.value="business";
   var init=form.elements.namedItem("initiative");
   if(init&&[...init.options].some(function(option){return option.value===preset.initiative;}))init.value=preset.initiative;
   ["title","description"].forEach(function(name){
     var field=form.elements.namedItem(name);
     if(field&&!field.value)field.value=preset[name];
   });
   var sourceContext=form.elements.namedItem("sourceContext");
   if(sourceContext&&!sourceContext.value)sourceContext.value="Offered service: "+offerKey;
 }
 var isPeople=intent.value==="people";
 if(isPeople){
    var init=form.elements.namedItem("initiative");
    if(init&&!init.value)init.value="portfolio";
    var role=form.elements.namedItem("participantRole");
    if(role&&(!role.value||role.value==="founder"))role.value="human_contributor";
    form.elements.namedItem("nextStep").value="collaborate";
    document.querySelectorAll(".tile").forEach(function(tile){
      tile.classList.toggle("is-featured",tile.getAttribute("data-choose")==="people");
    });
 }
 if(isPeople&&source==="linkedin"){
   var hero=document.querySelector(".hero h1");
   if(hero)hero.innerHTML="Your expertise deserves <em>a real next step.</em>";
   text(".hero .lede","You reached out on LinkedIn. Share your expertise, work samples and one concrete contribution. Your message becomes a real, trackable review case—not another lost inbox conversation.");
   text("#heroTruth","No signup · Direct application · Private case tracking");
   var button=document.querySelector('.heroactions a.primary');
   if(button)button.textContent="Share what you can build ↗";
   var tile=document.querySelector('.tile[data-choose="people"]');
   if(tile){tile.querySelector("b").textContent="Builders & independent talent";
      tile.querySelector("p").textContent="Propose an actionable first contribution, scoped project, or founding collaboration.";}
 }
 showConditional();
}
intent.addEventListener("change",function(){showConditional();trackEvent("connect.route_selected",get("intent"));});
document.querySelectorAll("[data-choose]").forEach(function(tile){
 tile.addEventListener("click",function(){setTimeout(showConditional,0);});
});
form.querySelectorAll("[data-next]").forEach(function(button){
 button.addEventListener("click",function(){
   var at=form.querySelector(".steps .current");
   if(at)trackEvent("connect.step_completed",at.id);
 });
});
analytics.addEventListener("change",function(){if(analytics.checked)trackEvent("connect.analytics_optin","step3");});
window.addEventListener("nf-connect-saved",function(event){
 var data=event.detail||{};
 if(!data.intake_id||!data.request_id||!data.email)return;
 receipt={request_id:data.request_id,email:data.email,intake_id:data.intake_id};
 var box=document.getElementById("connectResult");
 if(box)box.hidden=false;
 text("#resultCase",data.intake_id);text("#resultReference",data.request_id);
 if(tracking){tracking.elements.namedItem("request_id").value=data.request_id;tracking.elements.namedItem("email").value=data.email;}
 trackEvent("connect.intake_persisted",data.intent||"unknown");
 if(box&&box.scrollIntoView)box.scrollIntoView({behavior:"smooth",block:"nearest"});
});
function statusLabels(stage){
 var labels={NEW:"Received",QUALIFYING:"Under review",ROUTED:"Specialist review",ENGAGED:"Engaged",
 NEGOTIATING:"Terms review",PILOT:"Pilot stage",WON:"Internally marked won",LOST:"Closed",ARCHIVED:"Archived"};
 return labels[stage]||stage;
}
tracking.addEventListener("submit",async function(event){
 event.preventDefault();var rid=String(tracking.elements.namedItem("request_id").value||"").trim();
 var email=String(tracking.elements.namedItem("email").value||"").trim();
 var target=document.getElementById("participantTrackOutput");
 if(!tracking.reportValidity())return;
 var button=tracking.querySelector('button[type="submit"]');button.disabled=true;
 setText(target,"Reading the saved case…");
 try{
   var data=await api("/api/connect/participant/status",{request_id:rid,email:email});
   if(!data.found||!data.intake_id)throw Error("SOURCE_RECORD_UNAVAILABLE");
   receipt={request_id:rid,email:email,intake_id:data.intake_id};
   setText(target,("Case: ")+data.intake_id+"\n"+
      ("Stage: ")+statusLabels(data.stage)+"\n"+
      ("Received: ")+String(data.created_at||"").slice(0,10)+"\n"+
      (data.detail));
   document.getElementById("connectFeedback").hidden=false;
   trackEvent("connect.status_checked","verified_source_read");
 }catch(error){
   setText(target,("Reference not found or unavailable: ")+error.message);
   document.getElementById("connectFeedback").hidden=true;
 }finally{button.disabled=false}
});
document.getElementById("participantFeedback").addEventListener("submit",async function(event){
 event.preventDefault();var formFeedback=event.currentTarget;
 if(!formFeedback.reportValidity()||!receipt.request_id||!receipt.email)return;
 var button=formFeedback.querySelector('button[type="submit"]'),out=document.getElementById("participantFeedbackOutput");
 button.disabled=true;setText(out,"Saving feedback to your case…");
 var id=(window.crypto&&window.crypto.randomUUID)?window.crypto.randomUUID().replace(/-/g,""):"fback"+Date.now().toString(36)+"00000000";
 try{
   var data=await api("/api/connect/participant/feedback",{
      request_id:receipt.request_id,email:receipt.email,
      rating:Number(formFeedback.elements.namedItem("rating").value),
      message:String(formFeedback.elements.namedItem("message").value||"").trim(),feedback_id:id
   });
   if(!data.recorded)throw Error("NO_STORAGE_RECEIPT");
   setText(out,"Feedback saved to your original case.");
   formFeedback.reset();trackEvent("connect.feedback_recorded","stored");
 }catch(error){setText(out,("Feedback not saved: ")+error.message);}
 finally{button.disabled=false}
});
document.getElementById("showConnectStatus").addEventListener("click",function(){tracking.requestSubmit();});
document.getElementById("copyConnectReference").addEventListener("click",async function(){
 var data="Noetfield Connect\nCase: "+receipt.intake_id+"\nPrivate request ID: "+receipt.request_id+
          "\nEmail: "+receipt.email+"\nStatus: https://www.noetfield.com/connect/#connectTracking";
 try{await navigator.clipboard.writeText(data);
   text("#resultNext","Private tracking details copied.");}
 catch{text("#resultNext","Please save the reference and email manually.");}
});
chooseFromLink();
})();
