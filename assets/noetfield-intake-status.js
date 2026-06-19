/** Status + /next/ — live intake health + ops go-live next steps */
(function () {
  "use strict";

  function badge(label, state) {
    var cls = "nf-signal-badge nf-signal-badge--" + state;
    var text =
      state === "available" ? "Ready" : state === "orientation" ? "Partial" : "Pending";
    return (
      '<div class="nf-trust-signal"><span class="nf-trust-signal-label">' +
      label +
      '</span><span class="' +
      cls +
      '">' +
      text +
      "</span></div>"
    );
  }

  function opsNextSteps(ready) {
    var inboxNote =
      "<p><strong>Google Workspace inbox active.</strong> <code>operations@noetfield.com</code> receives direct email — reply from Gmail/Outlook in the same thread.</p>";
    if (ready) {
      return (
        '<aside class="nf-callout nf-callout--urgency" style="margin-top:16px">' +
        inboxNote +
        "<p><strong>Form delivery live.</strong> Every form notifies operations@noetfield.com · Reply-To = submitter · auto-ack enabled.</p>" +
        "</aside>"
      );
    }
    return (
      '<aside class="nf-callout nf-callout--urgency" style="margin-top:16px">' +
      inboxNote +
      "<p><strong>Next step — wire form delivery:</strong> Add <code>RESEND_API_KEY</code> on Vercel <code>web</code> → redeploy → verify here. " +
      "Until then, use <code>mailto:</code> fallbacks on intake forms or email operations@ directly. " +
      '<a href="/next/#next-ops">Full ops checklist →</a></p>' +
      "</aside>"
    );
  }

  function render(host, h) {
    if (!host || !h) return;
    var www = h.www_email_configured === true;
    var platform = h.platform_intake_enabled === true;
    var enabled = h.enabled === true;
    var mode = h.delivery_mode || "unconfigured";

    host.innerHTML =
      badge("Google Workspace inbox", "available") +
      badge("Form intake API", enabled ? "available" : "orientation") +
      badge("WWW form delivery (Resend)", www ? "available" : "orientation") +
      badge("Platform intake store", platform ? "available" : "orientation") +
      badge("Auto-ack to submitter", h.auto_ack_enabled ? "available" : "na") +
      '<p class="nf-section-lead" style="margin-top:12px">Delivery mode: <code>' +
      mode +
      "</code> · Inbox: <code>" +
      (h.intake_email || "operations@noetfield.com") +
      "</code></p>" +
      opsNextSteps(www || enabled);
  }

  function initHost(host) {
    if (!host || !window.NFIntakeCore) return;
    host.innerHTML =
      badge("Google Workspace inbox", "available") +
      badge("Form intake API", "orientation") +
      badge("WWW form delivery (Resend)", "orientation") +
      badge("Platform intake store", "orientation") +
      badge("Auto-ack to submitter", "orientation");
    window.NFIntakeCore.checkHealth().then(function (h) {
      render(host, h);
    });
  }

  function init() {
    document.querySelectorAll("[data-intake-health-host]").forEach(initHost);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
