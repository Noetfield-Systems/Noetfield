/* Corporate collaboration intake. Reuses the single NFIntakeCore POST contract. */
(function () {
 "use strict";
 var roles = ["founder","specialist","agent","startup","client","technology","strategic","investor"];
 var areaForRole={founder:"build-business",specialist:"workforce",agent:"workforce",startup:"build-business",client:"transform-operations",technology:"transform-operations",strategic:"portfolio",investor:"portfolio"};
 function qs(name){try{return new URLSearchParams(location.search).get(name)||""}catch(_){return ""}}
 function event(name,props){
   try{fetch("/api/analytics/event",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({event:name,source:"www-corporate-collaboration",page:location.pathname,properties:props||{}}),keepalive:true,credentials:"omit"}).catch(function(){})}catch(_){}
 }
 function init(){
  var form=document.getElementById("nfCorporateCollaborationForm");
  if(!form || !window.NFIntakeCore)return;
  var status=document.getElementById("nfCorporateCollaborationStatus");
  var role=form.elements.namedItem("role"),area=form.elements.namedItem("area"),buttons=document.querySelectorAll("[data-collab-role]");
  var pending=false;
  function selectRole(next,scroll){
   if(!roles.includes(next))return;
   role.value=next;
   if(!area.value)area.value=areaForRole[next];
   buttons.forEach(function(button){button.setAttribute("aria-pressed",String(button.getAttribute("data-collab-role")===next))});
   event("collaboration_role_selected",{role:next});
   if(scroll){form.scrollIntoView({behavior:window.matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"});role.focus({preventScroll:true})}
  }
  buttons.forEach(function(button){button.setAttribute("aria-pressed","false");button.addEventListener("click",function(){selectRole(button.getAttribute("data-collab-role"),true)})});
  role.addEventListener("change",function(){selectRole(role.value,false)});
  var pre=qs("role")||qs("participant");if(roles.includes(pre))selectRole(pre,false);
  event("collaboration_page_view",{entry:qs("utm_source")||"direct"});
  form.addEventListener("submit",function(e){
   e.preventDefault();
   if(pending||!form.reportValidity())return;
   var val=function(name){return String(form.elements.namedItem(name).value||"").trim()};
   var selected=val("role"),scope=val("area"),name=val("name"),email=val("email"),org=val("organization"),proposal=val("proposal"),evidence=val("evidence");
   if(!roles.includes(selected)||!form.elements.namedItem("consent").checked)return;
   var msg="Noetfield corporate collaboration request\nRole: "+selected+"\nArea: "+scope+"\nResponsible contact: "+name+" <"+email+">\nOrganization: "+org+"\nProposal: "+proposal+"\nPublic evidence URL: "+(evidence||"None")+"\nContact consent: yes";
   pending=true;event("collaboration_submit_started",{role:selected,area:scope});
   window.NFIntakeCore.submitAsync({
    organization:org,contact_name:name,contact_email:email,message:msg,vector:"work-with-us",sku:"general",
    metadata:{page:location.pathname,form_id:"nfCorporateCollaborationForm",program_lane:selected,role:selected,area:scope,evidence_url:evidence,consent:true,consent_purpose:"respond_to_corporate_collaboration_request",utm_source:qs("utm_source"),utm_medium:qs("utm_medium"),utm_campaign:qs("utm_campaign"),referral_code:qs("ref"),intake_status:"REVIEW_REQUESTED"},
    submitBtn:form.querySelector('button[type="submit"]'),statusEl:status,
    labels:{idle:"Send proposal",loading:"Recording request…",done:"Request recorded"},
    successCopy:{headline:"Your proposal was recorded",detail:"The existing Noetfield intake system returned a persisted reference. A responsible operator can assess the next step. This is not a contract or an automated work assignment."},
    errorCopy:{mailSubject:"Noetfield corporate collaboration: "+selected,mailBody:msg},
    onSuccess:function(data){event("collaboration_submit_persisted",{role:selected,area:scope,has_intake_id:!!data.intake_id})},
    onPending:function(){event("collaboration_submit_unpersisted",{role:selected,area:scope})},
    onError:function(){event("collaboration_submit_failed",{role:selected,area:scope})}
   }).then(function(data){if(data&&data.intake_persisted===false){pending=false;var submit=form.querySelector('button[type="submit"]');if(submit){submit.disabled=false;submit.textContent="Retry to save request"}}}).catch(function(){pending=false});
  });
 }
 if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();
