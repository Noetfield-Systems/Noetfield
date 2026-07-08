/* Noetfield cookie consent — essential storage + gated first-party analytics */
(function () {
  "use strict";

  var STORAGE_KEY = "noetfield_cookie_consent_v1";
  var OPEN_EVENT = "nf:open-cookie-preferences";
  var CONSENT_EVENT = "nf:cookie-consent";

  function readConsent() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (_) {
      return null;
    }
  }

  function writeConsent(analytics) {
    var row = {
      version: 1,
      essential: true,
      analytics: !!analytics,
      updatedAt: new Date().toISOString(),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(row));
    document.documentElement.dataset.analytics = row.analytics ? "granted" : "denied";
    document.dispatchEvent(new CustomEvent(CONSENT_EVENT, { detail: row }));
    return row;
  }

  function mountBanner() {
    if (document.getElementById("nfCookieBanner")) return;
    var root = document.createElement("div");
    root.id = "nfCookieBanner";
    root.className = "nf-cookie-banner";
    root.setAttribute("role", "dialog");
    root.setAttribute("aria-labelledby", "nfCookieTitle");
    root.setAttribute("aria-describedby", "nfCookieDesc");
    root.innerHTML =
      '<div class="nf-cookie-banner-inner">' +
      '<div><p id="nfCookieTitle" class="nf-cookie-title">Cookie preferences</p>' +
      '<p id="nfCookieDesc" class="nf-cookie-desc">We use essential storage to remember your choices. Optional analytics helps us improve noetfield.com — off until you opt in. <a href="/cookies/">Learn more</a></p></div>' +
      '<div class="nf-cookie-actions">' +
      '<button type="button" class="btn ghost" data-cookie-reject>Reject non-essential</button>' +
      '<button type="button" class="btn ghost" data-cookie-customize>Customize</button>' +
      '<button type="button" class="btn btn-primary" data-cookie-accept>Accept all</button>' +
      "</div></div>";
    document.body.appendChild(root);

    root.querySelector("[data-cookie-accept]").addEventListener("click", function () {
      writeConsent(true);
      hideBanner();
      hideModal();
    });
    root.querySelector("[data-cookie-reject]").addEventListener("click", function () {
      writeConsent(false);
      hideBanner();
      hideModal();
    });
    root.querySelector("[data-cookie-customize]").addEventListener("click", function () {
      showModal(readConsent());
    });
  }

  function mountModal() {
    if (document.getElementById("nfCookieModal")) return;
    var modal = document.createElement("div");
    modal.id = "nfCookieModal";
    modal.className = "nf-cookie-modal";
    modal.hidden = true;
    modal.innerHTML =
      '<div class="nf-cookie-modal-backdrop" data-cookie-backdrop></div>' +
      '<div class="nf-cookie-modal-panel" role="dialog" aria-modal="true" aria-labelledby="nfCookieModalTitle">' +
      '<h2 id="nfCookieModalTitle">Cookie preferences</h2>' +
      '<p class="nf-cookie-desc">Essential storage is required. Analytics sends first-party events to noetfield.com only when enabled.</p>' +
      '<div class="nf-cookie-option"><div class="nf-cookie-option-head"><strong>Essential</strong><span class="nf-cookie-pill">Always on</span></div>' +
      "<p>Stores your consent decision in this browser.</p></div>" +
      '<label class="nf-cookie-option nf-cookie-option--click"><div class="nf-cookie-option-head"><strong>Analytics</strong>' +
      '<input type="checkbox" id="nfCookieAnalytics" /></div>' +
      "<p>First-party page and CTA events via /api/analytics/event.</p></label>" +
      '<div class="nf-cookie-actions nf-cookie-actions--end">' +
      '<button type="button" class="btn ghost" data-cookie-cancel>Cancel</button>' +
      '<button type="button" class="btn btn-primary" data-cookie-save>Save preferences</button>' +
      "</div></div>";
    document.body.appendChild(modal);

    modal.querySelector("[data-cookie-backdrop]").addEventListener("click", hideModal);
    modal.querySelector("[data-cookie-cancel]").addEventListener("click", hideModal);
    modal.querySelector("[data-cookie-save]").addEventListener("click", function () {
      var analytics = !!document.getElementById("nfCookieAnalytics").checked;
      writeConsent(analytics);
      hideBanner();
      hideModal();
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") hideModal();
    });
  }

  function showBanner() {
    var banner = document.getElementById("nfCookieBanner");
    if (banner) banner.hidden = false;
  }

  function hideBanner() {
    var banner = document.getElementById("nfCookieBanner");
    if (banner) banner.hidden = true;
  }

  function showModal(consent) {
    var modal = document.getElementById("nfCookieModal");
    var box = document.getElementById("nfCookieAnalytics");
    if (box) box.checked = !!(consent && consent.analytics);
    if (modal) modal.hidden = false;
  }

  function hideModal() {
    var modal = document.getElementById("nfCookieModal");
    if (modal) modal.hidden = true;
  }

  function openPreferences() {
    mountBanner();
    mountModal();
    showModal(readConsent() || { analytics: false });
  }

  window.NFCookieConsent = {
    read: readConsent,
    write: writeConsent,
    openPreferences: openPreferences,
  };

  document.addEventListener(OPEN_EVENT, openPreferences);
  document.addEventListener("click", function (ev) {
    var btn = ev.target && ev.target.closest ? ev.target.closest("[data-cookie-manage]") : null;
    if (!btn) return;
    ev.preventDefault();
    openPreferences();
  });

  mountBanner();
  mountModal();
  var existing = readConsent();
  if (existing && typeof existing.essential === "boolean") {
    document.documentElement.dataset.analytics = existing.analytics ? "granted" : "denied";
    hideBanner();
  } else {
    showBanner();
  }
})();
