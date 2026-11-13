/** Shared Noetfield intake is the only submission backend; no parallel CRM. */
(function(){
 "use strict";
 function init(){
  var form=document.getElementById("nfContributorForm"),status=document.getElementById("nfContributorStatus");
  if(!form||!window.NFIntakeCore)return;
  var qs=new URLSearchParams(location.search),pre=qs.get("project")||"";
  var project=form.elements.namedItem("project_id");
  if(project&&Array.from(project.options).some(function(o){return o.value===pre}))project.value=pre;
  form.addEventListener("submit",function(ev){
   ev.preventDefault();
   if(!form.reportValidity())return;
   var v=function(name){return String(form.elements.namedItem(name).value||"").trim()};
   var kind=v("kind"),projectId=v("project_id"),name=v("name"),email=v("email"),role=v("role"),evidence=v("evidence_url"),notes=v("notes");
   if(!["human","agent","organization"].includes(kind))return;
   var message="Noetfield Portfolio — Contributor Application\nApplicant type: "+kind+"\nProject: "+projectId+"\nApplicant/agent: "+name+"\nResponsible operator: "+email+"\nProposed role: "+role+"\nEvidence URL: "+evidence+"\nProposed result: "+notes+"\nNo confidential materials supplied.\n";
   window.NFIntakeCore.submitAsync({
    organization:name,contact_name:kind==="agent"?"AI Agent — "+name:name,contact_email:email,message:message,
    vector:"work-with-us-contributor",sku:"general",
    metadata:{page:location.pathname,application_kind:kind,project_id:projectId,role:role,evidence_url:evidence,application_status:"APPLIED",consent_contact:form.elements.namedItem("consent").checked},
    submitBtn:form.querySelector('button[type="submit"]'),statusEl:status,
    labels:{idle:"Submit collaboration application",loading:"Submitting…",done:"Application recorded"},
    successCopy:{headline:"Application received",detail:"Your request ID is recorded in the existing Noetfield intake system. The relevant product operator can assess a scoped contribution; application alone does not grant tool access."},
    errorCopy:{mailSubject:"Portfolio contributor application — "+projectId,mailBody:message}
   }).catch(function(){});
  });
 }
 if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();
