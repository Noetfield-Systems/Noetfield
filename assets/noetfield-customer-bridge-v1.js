/* OAuth customer identity handoff: only verified Supabase bearer, no operator privilege. */
(function(){
"use strict";
const status=document.getElementById("customer-bridge-status");
const returnPath="/auth/customer-bridge/";
const origin="https://platform.noetfield.com";
function show(msg){if(status)status.textContent=msg}
if(!window.opener||window.opener.closed){show("Open this Google sign-in from your Noetfield customer portal.");return}
(async()=>{
try{
if(!window.NoetfieldInvestAuth)throw Error("Authentication client could not load.");
const sb=await window.NoetfieldInvestAuth.getClient();
const {data,error}=await sb.auth.getSession();
if(error)throw error;
const session=data?.session;
if(session?.access_token){
 window.opener.postMessage({type:"noetfield.customer.google.v1",access_token:session.access_token},origin);
 show("Identity returned to your customer portal.");
 setTimeout(()=>window.close(),350);
 return;
}
if(location.hostname!=="www.noetfield.com"){
 location.replace("https://www.noetfield.com"+returnPath);return;
}
sessionStorage.setItem("nf-customer-sso-return",returnPath);
show("Opening Google sign-in…");
const result=await sb.auth.signInWithOAuth({provider:"google",options:{
redirectTo:"https://www.noetfield.com/auth/callback/" }});
if(result.error)throw result.error;
}catch(err){show("Sign-in was not completed: "+String(err?.message||err)+". Close this window and retry.")}
})();
})();