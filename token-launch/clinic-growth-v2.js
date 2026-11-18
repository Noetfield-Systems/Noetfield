/* Token Launch Clinic v2: client-side, deterministic free launch fit brief + package selection.
 * Not a tokenomics recommendation, legal classification, onchain deployment, payment or audit.
 * Reuses the exact first-party Noetfield form and corporate CRM source; creates no second lead database.
 */
(function(){
"use strict";
var offerButtons=Array.prototype.slice.call(document.querySelectorAll("[data-clinic-offer]"));
var offerMap={
 blueprint:"Launch Blueprint",
 contracts:"Contracts & Claims",
 launch:"Launch App & Community",
 rwa:"RWA Technical Sprint"
};
var planPaths={
 startup:{
  title:"Startup / protocol launch brief",
  steps:["Describe the product action that genuinely uses the token.","Draft token utility, supply assumptions and allocation/vesting design.","Specify contract permissions, supported chain and test coverage.","Plan first-use onboarding, eligibility, claim and launch pages.","Define independent verification, release milestones and operating ownership."]
 },
 community:{
  title:"Community economy launch brief",
  steps:["Define member value beyond a token or simple points.","Map real contributions, referral eligibility and abuse prevention.","Separate offchain XP from any future onchain distribution.","Prototype member sign-up, quests, claims and moderation flows.","Measure meaningful engagement and return visits before expansion."]
 },
 business:{
  title:"Business tokenization launch brief",
  steps:["Name the real operating workflow the token would improve.","Identify customers, rights, counterparties and service obligations.","Evaluate whether a token improves on a traditional account or ledger.","Plan integration with existing app, records and payments.","Specify the smallest deployable service and success metrics."]
 },
 rwa:{
  title:"Real-world asset readiness brief",
  steps:["Identify the asset, controller, issuing party and jurisdiction.","Map title, economic rights, transfer terms and servicing records.","Classify issuer and authorization needs for the actual transaction.","Define permissioning, smart-contract controls and record reconciliation.","Scope the separate RWA readiness assessment and technical next steps."]
 }
};
var selectedOffer="";
var brief="";
var form=document.getElementById("nfTokenLaunchIntake");
var chosen=document.getElementById("clinic-selected-offer");
function currentTrack(){
 var select=document.getElementById("clinic-type");
 return select?({"startup-token-launch":"startup","community-token-launch":"community","business-tokenization":"business","rwa-tokenization":"rwa"}[select.value]||"startup"):"startup";
}
function field(id){var el=document.getElementById(id);return el?el.value:"";}
function text(id,value){var el=document.getElementById(id);if(el)el.textContent=value;}
function chooseOffer(id,scroll){
 if(!Object.prototype.hasOwnProperty.call(offerMap,id))return;
 selectedOffer=id;
 offerButtons.forEach(function(b){var hit=b.dataset.clinicOffer===id;b.setAttribute("aria-pressed",String(hit));var card=b.closest(".offer-card");if(card)card.classList.toggle("is-selected",hit)});
 if(chosen){chosen.textContent="Selected service: "+offerMap[id]+". Your request will be scoped before any payment.";chosen.classList.add("is-visible");}
 if(id==="rwa"){var select=document.getElementById("clinic-type");if(select){select.value="rwa-tokenization";select.dispatchEvent(new Event("change",{bubbles:true}));}}
 if(scroll){document.getElementById("request").scrollIntoView({behavior:window.matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"});}
}
offerButtons.forEach(function(b){b.setAttribute("aria-pressed","false");b.addEventListener("click",function(){chooseOffer(b.dataset.clinicOffer,true)})});
var generate=document.getElementById("clinic-generate-brief");
function buildBrief(){
 var track=currentTrack(),info=planPaths[track]||planPaths.startup;
 var stage=field("clinic-fit-stage")||"unspecified";
 var timing=field("clinic-fit-timing")||"unspecified";
 var focus=field("clinic-fit-focus")||"unspecified";
 var steps=info.steps.slice();
 if(focus==="community"){steps[3]="Plan qualified referrals, access and community user onboarding.";}
 if(focus==="product"){steps[3]="Build and test a first useful app flow before campaign spending.";}
 if(focus==="rwa"){steps[0]="Identify the asset, owner/issuer, actual economic rights and operating workflow.";}
 var intro="Project: "+info.title+" | Stage: "+stage+" | Target: "+timing+" | Primary need: "+focus+".";
 brief=intro+"\n"+steps.map(function(step,index){return (index+1)+". "+step;}).join("\n");
 text("clinic-brief-heading",info.title);
 text("clinic-brief-summary",intro);
 var list=document.getElementById("clinic-brief-steps");
 if(list){list.replaceChildren();steps.forEach(function(step){var li=document.createElement("li");li.textContent=step;list.appendChild(li)})}
 text("clinic-brief-status","A planning preview for your project. Not a final quote, suitability assessment or deployed token.");
 var result=document.getElementById("clinic-brief-result");
 if(result)result.setAttribute("data-generated","true");
 return brief;
}
if(generate)generate.addEventListener("click",buildBrief);
var copy=document.getElementById("clinic-copy-brief");
if(copy)copy.addEventListener("click",function(){
 var value=brief||buildBrief();
 if(navigator.clipboard&&window.isSecureContext){
 navigator.clipboard.writeText(value).then(function(){text("clinic-brief-status","Copied. You can edit this planning brief before using it.");}).catch(function(){text("clinic-brief-status","Clipboard unavailable. Use the Add to project request action to keep your brief.");});
 }else{text("clinic-brief-status","Clipboard unavailable. Use Add to project request to keep the brief.");}
});
var use=document.getElementById("clinic-use-brief");
if(use)use.addEventListener("click",function(){
 var generated=brief||buildBrief();
 var note=form&&form.querySelector('textarea[name="notes"]');
 if(note&&!note.dataset.clinicBriefAdded){var previous=note.value.trim();note.value=(previous?previous+"\n\n":"")+"Launch Fit Brief (illustrative):\n"+generated;note.value=note.value.slice(0,5000);note.dataset.clinicBriefAdded="true";}
 text("clinic-brief-status","Brief added to the project request. Review the details before submitting.");
 if(form)form.scrollIntoView({behavior:window.matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"});
});
var select=document.getElementById("clinic-type");
if(select)select.addEventListener("change",function(){brief="";text("clinic-brief-status","Your project type changed. Generate an updated brief.");});
if(form)form.addEventListener("submit",function(){
 var hidden=document.getElementById("clinic-context");if(!hidden)return;
 var p=new URLSearchParams(window.location.search);
 hidden.value+=(selectedOffer?"; requested_package="+selectedOffer:"; requested_package=unselected");
 hidden.value+="; utm_medium="+(p.get("utm_medium")||"").slice(0,60)+"; utm_content="+(p.get("utm_content")||"").slice(0,80);
 if(brief)hidden.value+="; fit_brief_generated=yes";
},true);
})();
