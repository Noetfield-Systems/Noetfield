/* Noetfield commercial intake: no client-side secret, consent-first, fail closed. */
(() => {
  "use strict";
  const form=document.getElementById("nfCommercialForm");
  if(!form)return;
  const status=form.querySelector("[data-status]");
  const btn=form.querySelector("[data-submit]");
  let requestId="nfcom-"+crypto.randomUUID();
  let completed=false;
  const setStatus=(message,hasError)=>{
    status.textContent=message;
    if(hasError)status.setAttribute("data-error","");
    else status.removeAttribute("data-error");
  };
  document.querySelectorAll("[data-interest]").forEach(link=>link.addEventListener("click",()=>{
    const intent=form.elements.namedItem("intent");
    if(intent)intent.value=link.getAttribute("data-interest")||"pilot";
  }));
  form.addEventListener("submit",async event=>{
    event.preventDefault();
    if(completed||btn.disabled)return;
    if(!form.reportValidity())return;
    const data=new FormData(form);
    const payload={
      name:String(data.get("name")||"").trim(),
      email:String(data.get("email")||"").trim(),
      company:String(data.get("company")||"").trim(),
      role:String(data.get("role")||"").trim(),
      audience:String(data.get("audience")||"other"),
      intent:String(data.get("intent")||"other"),
      urgency:String(data.get("urgency")||"exploring"),
      problem:String(data.get("problem")||"").trim(),
      consent:data.get("consent")==="on",
      ai_consent:data.get("ai_consent")==="on",
      website:String(data.get("website")||""),
      idempotency_key:requestId
    };
    if(!payload.consent){setStatus("Consent is required before submission.",true);return}
    btn.disabled=true;
    btn.textContent="Submitting securely…";
    setStatus("Submitting to Company OS…",false);
    try{
      const response=await fetch("/api/company-os-intake",{
        method:"POST",credentials:"same-origin",
        headers:{"Content-Type":"application/json","Accept":"application/json"},
        cache:"no-store",body:JSON.stringify(payload)
      });
      const result=await response.json().catch(()=>({}));
      if(response.status!==202||result.accepted!==true||!result.reference)
        throw new Error(result.error||"Unable to confirm this request.");
      completed=true;
      btn.textContent="Request recorded";
      setStatus("Your request is recorded for internal review. Reference: "+result.reference+". No automatic offer or outreach has been sent.",false);
      form.querySelectorAll("input,textarea,select").forEach(field=>field.disabled=true);
    }catch(err){
      btn.disabled=false;
      btn.textContent="Request review ↗";
      setStatus((err&&err.message?err.message:"Submission unavailable.")+" Alternatively, use the contact page.",true);
    }
  });
})();
