/* Noetfield Connect v3 progressive experience. Existing NFIntakeCore remains the sole intake writer. */
(function(){"use strict";
var form=document.getElementById("connectWizard");
if(!form)return;
var params=new URLSearchParams(location.search),fa=(params.get("lang")||"").toLowerCase()==="fa";
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
   if(hero)hero.innerHTML=fa?"از مهارت شما تا <em>همکاری واقعی.</em>":"Your expertise deserves <em>a real next step.</em>";
   text(".hero .lede",fa?
     "برای یک همکاری واقعی به ما پیام داده‌اید؟ مهارت‌ها، نمونه‌کار و یک ایده عملی را در چند قدم ثبت کنید. مسیر شما گم نمی‌شود؛ رسید و امکان پیگیری دریافت می‌کنید.":
     "You reached out on LinkedIn. Share your expertise, work samples and one concrete contribution. Your message becomes a real, trackable review case—not another lost inbox conversation.");
   text("#heroTruth",fa?
     "بدون ساخت حساب · ثبت مستقیم · امکان پیگیری خصوصی":
     "No signup · Direct application · Private case tracking");
   var button=document.querySelector('.heroactions a.primary');
   if(button)button.textContent=fa?"ثبت پیشنهاد همکاری ↗":"Share what you can build ↗";
   var tile=document.querySelector('.tile[data-choose="people"]');
   if(tile){tile.querySelector("b").textContent=fa?"توسعه‌دهنده و همکار حرفه‌ای":"Builders & independent talent";
      tile.querySelector("p").textContent=fa?
      "برای پروژه واقعی، همکاری فنی، AI یا نقش مؤسسیتی پیشنهاد بدهید.":
      "Propose an actionable first contribution, scoped project, or founding collaboration.";}
 }
 showConditional();
}
function translateExtras(){
 if(!fa)return;
 var items={
 "#heroTruth":"یک معرفی روشن · بدون حساب کاربری · رسید و پیگیری خصوصی",
 ".network-head span":"از معرفی تا نتیجه",
 ".network-node:nth-of-type(2) b":"مسیر مناسب را پیدا کنید",
 ".network-node:nth-of-type(2) small":"مهارت و نقش خود را مشخص کنید.",
 ".network-node:nth-of-type(3) b":"پیشنهاد قابل اجرا ثبت کنید",
 ".network-node:nth-of-type(3) small":"توانایی، نمونه‌کار و یک اقدام مشخص.",
 ".network-node:nth-of-type(4) b":"بررسی و ارجاع",
 ".network-node:nth-of-type(4) small":"پرونده واقعی با اقدام بعدی و صف بررسی.",
 ".network-node:nth-of-type(5) b":"نتیجه را پیگیری کنید",
 ".network-node:nth-of-type(5) small":"مشاهده وضعیت و ثبت بازخورد روی همان پرونده.",
 ".network-foot span:last-child":"بدون استخدام، قرارداد یا نتیجه ساختگی.",
 "#peopleQualifiers h3":"چه مهارت‌هایی دارید و چه زمانی آماده‌اید؟",
 "#growthQualifiers h3":"با هم به چه مخاطبانی می‌توانیم برسیم؟",
 "#capitalQualifiers h3":"زمینه سرمایه‌گذاری یا معرفی چیست؟",
 "#businessQualifiers h3":"نتیجه مطلوب پایلوت چیست؟",
 "#connectResult h3":"معرفی شما به‌صورت واقعی ثبت شد.",
 "#connectResult > p":"این یک درخواست بررسی است، نه پیشنهاد شغلی، جلسه قطعی یا قرارداد.",
 "#connectTracking > h3":"قبلاً درخواست خود را ثبت کرده‌اید؟",
 "#connectTracking > p:not(.eyebrow)":"با کد پیگیری خصوصی و ایمیل ثبت‌شده، وضعیت بررسی را مشاهده کنید و نظر بدهید.",
 "#connectFeedback h3":"نظر شما درباره تجربه همکاری",
 "#connectFeedback .primary":"ثبت بازخورد ↗",
 "#participantTrack .primary":"بررسی وضعیت ↗",
 "#copyConnectReference":"کپی اطلاعات پیگیری",
 "#showConnectStatus":"مشاهده وضعیت پرونده",
 };
 Object.keys(items).forEach(function(sel){text(sel,items[sel]);});
 var labels={
 skillStack:"مهارت‌ها و ابزارهای اصلی *",availability:"زمان در دسترس",
 workModel:"نوع همکاری ترجیحی",portfolioUrl:"نمونه کار، GitHub یا وب‌سایت",
 audience:"مخاطبان، مشتریان یا شبکه توزیع",growthModel:"مدل همکاری تجاری",
 capitalContext:"اطلاعات سرمایه‌گذاری",businessConstraints:"بودجه، مهلت یا محدودیت",
 linkedinURL:"لینک پروفایل LinkedIn (اختیاری)"
 };
 Object.keys(labels).forEach(function(name){
   var el=form.elements.namedItem(name);
   if(!el)return;
   var label=el.closest("label.field");
   if(label&&label.firstChild&&label.firstChild.nodeType===3)label.firstChild.textContent=labels[name]+"\n";
 });
 var context=document.getElementById("sourceContextLabel");
 if(context&&context.firstChild&&context.firstChild.nodeType===3)
   context.firstChild.textContent="زمینه گفت‌وگوی قبلی (اختیاری)\\n";
 var tc=document.querySelector(".journey-consent span");
 if(tc)tc.textContent="اختیاری: اجازه ثبت رویدادهای مراحل ویزارد در آنالیتیکس داخلی برای بهبود تجربه؛ بدون پیکسل تبلیغاتی.";
 var fields=tracking.querySelectorAll("label.field");
 if(fields[0]&&fields[0].firstChild)fields[0].firstChild.textContent="کد خصوصی پیگیری\n";
 if(fields[1]&&fields[1].firstChild)fields[1].firstChild.textContent="ایمیل ثبت‌شده\n";
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
 var labels=fa?{
 NEW:"دریافت‌شده",QUALIFYING:"در حال ارزیابی",ROUTED:"در مسیر بررسی تخصصی",ENGAGED:"گفت‌وگوی فعال",
 NEGOTIATING:"بررسی شرایط",PILOT:"مرحله پایلوت",WON:"تبدیل‌شده (ثبت داخلی)",
 LOST:"بسته‌شده",ARCHIVED:"آرشیوشده"
 }:{NEW:"Received",QUALIFYING:"Under review",ROUTED:"Specialist review",
 ENGAGED:"Engaged",NEGOTIATING:"Terms review",PILOT:"Pilot stage",
 WON:"Internally marked won",LOST:"Closed",ARCHIVED:"Archived"};
 return labels[stage]||stage;
}
tracking.addEventListener("submit",async function(event){
 event.preventDefault();var rid=String(tracking.elements.namedItem("request_id").value||"").trim();
 var email=String(tracking.elements.namedItem("email").value||"").trim();
 var target=document.getElementById("participantTrackOutput");
 if(!tracking.reportValidity())return;
 var button=tracking.querySelector('button[type="submit"]');button.disabled=true;
 setText(target,fa?"در حال بررسی داده‌های ثبت‌شده…":"Reading the saved case…");
 try{
   var data=await api("/api/connect/participant/status",{request_id:rid,email:email});
   if(!data.found||!data.intake_id)throw Error("SOURCE_RECORD_UNAVAILABLE");
   receipt={request_id:rid,email:email,intake_id:data.intake_id};
   setText(target,(fa?"پرونده: ":"Case: ")+data.intake_id+"\n"+
      (fa?"مرحله: ":"Stage: ")+statusLabels(data.stage)+"\n"+
      (fa?"ثبت اولیه: ":"Received: ")+String(data.created_at||"").slice(0,10)+"\n"+
      (fa?"یادداشت: هیچ تأیید مستقل اجرای کار وجود ندارد.":data.detail));
   document.getElementById("connectFeedback").hidden=false;
   trackEvent("connect.status_checked","verified_source_read");
 }catch(error){
   setText(target,(fa?"پرونده پیدا نشد یا سرویس در دسترس نیست: ":"Reference not found or unavailable: ")+error.message);
   document.getElementById("connectFeedback").hidden=true;
 }finally{button.disabled=false}
});
document.getElementById("participantFeedback").addEventListener("submit",async function(event){
 event.preventDefault();var formFeedback=event.currentTarget;
 if(!formFeedback.reportValidity()||!receipt.request_id||!receipt.email)return;
 var button=formFeedback.querySelector('button[type="submit"]'),out=document.getElementById("participantFeedbackOutput");
 button.disabled=true;setText(out,fa?"در حال ثبت بازخورد…":"Saving feedback to your case…");
 var id=(window.crypto&&window.crypto.randomUUID)?window.crypto.randomUUID().replace(/-/g,""):"fback"+Date.now().toString(36)+"00000000";
 try{
   var data=await api("/api/connect/participant/feedback",{
      request_id:receipt.request_id,email:receipt.email,
      rating:Number(formFeedback.elements.namedItem("rating").value),
      message:String(formFeedback.elements.namedItem("message").value||"").trim(),feedback_id:id
   });
   if(!data.recorded)throw Error("NO_STORAGE_RECEIPT");
   setText(out,fa?"بازخورد شما روی همین پرونده ثبت شد.":"Feedback saved to your original case.");
   formFeedback.reset();trackEvent("connect.feedback_recorded","stored");
 }catch(error){setText(out,(fa?"ثبت بازخورد ناموفق بود: ":"Feedback not saved: ")+error.message);}
 finally{button.disabled=false}
});
document.getElementById("showConnectStatus").addEventListener("click",function(){tracking.requestSubmit();});
document.getElementById("copyConnectReference").addEventListener("click",async function(){
 var data="Noetfield Connect\nCase: "+receipt.intake_id+"\nPrivate request ID: "+receipt.request_id+
          "\nEmail: "+receipt.email+"\nStatus: https://www.noetfield.com/connect/#connectTracking";
 try{await navigator.clipboard.writeText(data);
   text("#resultNext",fa?"اطلاعات خصوصی کپی شد.":"Private tracking details copied.");}
 catch{text("#resultNext",fa?"لطفاً شناسه و ایمیل را یادداشت کنید.":"Please save the reference and email manually.");}
});
chooseFromLink();translateExtras();
})();
