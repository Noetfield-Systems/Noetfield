/* CSP-compliant Noetfield Google sign-in and callback startup. */
(function () {
  "use strict";
  function start() {
    const auth=window.NoetfieldInvestAuth;
    if (!auth) {
      const status=document.getElementById("nf-auth-callback-status") || document.getElementById("nf-auth-status");
      if (status) status.textContent="The authentication client could not load. Reload this page.";
      return;
    }
    if (document.getElementById("nf-auth-callback-status")) {
      auth.bootCallbackPage();
    } else if (document.getElementById("nf-auth-signin-form")) {
      auth.bootSignInPage();
    }
  }
  if (document.readyState==="loading") document.addEventListener("DOMContentLoaded",start,{once:true});
  else start();
})();
