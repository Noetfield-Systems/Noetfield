/* Operator-only Google OAuth handoff. No operator key is sent to Google or JS storage. */
(function () {
  "use strict";
  const status = document.getElementById("operator-bridge-status");
  const targetOrigin = "https://platform.noetfield.com";
  const returnPath = "/auth/operator-bridge/";
  function update(message) { if (status) status.textContent = message; }
  function bounded(action, name) {
    let handle;
    return Promise.race([
      Promise.resolve().then(action),
      new Promise((_, reject) => {
        handle = setTimeout(() => reject(new Error(name + " timed out. Check your connection and try again.")), 18000);
      }),
    ]).finally(() => clearTimeout(handle));
  }
  if (!window.opener || window.opener.closed) {
    update("Open Google sign-in from Corporate CRM. This window is not connected to your workspace.");
    return;
  }
  (async function () {
    try {
      if (!window.NoetfieldInvestAuth) throw new Error("Google authentication script did not load.");
      update("Contacting Noetfield's Google identity provider…");
      const sb = await bounded(() => window.NoetfieldInvestAuth.getClient(), "Google client initialization");
      const row = await bounded(() => sb.auth.getSession(), "Session lookup");
      if (row.error) throw row.error;
      const session = row.data && row.data.session;
      if (session && session.access_token) {
        update("Google identity verified. Returning to your CRM…");
        window.opener.postMessage(
          {type:"noetfield.operator.google.v1",access_token:session.access_token}, targetOrigin
        );
        setTimeout(() => window.close(), 350);
        return;
      }
      if (location.hostname !== "www.noetfield.com") {
        update("Continuing on the canonical Noetfield sign-in domain…");
        location.replace("https://www.noetfield.com" + returnPath);
        return;
      }
      sessionStorage.setItem("nf-operator-sso-return", returnPath);
      update("Redirecting to Google sign-in…");
      const signIn = await bounded(() => sb.auth.signInWithOAuth({
        provider:"google",
        options:{redirectTo:"https://www.noetfield.com/auth/callback/"},
      }), "Google sign-in");
      if (signIn.error) throw signIn.error;
    } catch (err) {
      update("Unable to connect Google: " + String(err && err.message || err) + ". Close this window and try again.");
    }
  })();
})();
