/** Internal partner-onboarding audit cockpit. Requires X-Admin-Secret; reads the last
 *  committed receipt from scripts/nf_partner_onboarding_e2e_audit_v1.py — read-only,
 *  no checks run from the browser. */
(function () {
  "use strict";

  var STORAGE_KEY = "nf_admin_secret";

  function $(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function secret() {
    try {
      return localStorage.getItem(STORAGE_KEY) || "";
    } catch (_) {
      return "";
    }
  }

  function setSecret(value) {
    try {
      if (value) localStorage.setItem(STORAGE_KEY, value);
      else localStorage.removeItem(STORAGE_KEY);
    } catch (_) {}
  }

  function setStatus(message, kind) {
    var el = $("nfAdminStatus");
    if (!el) return;
    el.hidden = false;
    el.className = "nf-admin-status" + (kind ? " nf-admin-status--" + kind : "");
    el.textContent = message;
  }

  function metricCard(label, value, hint) {
    return (
      '<article class="nf-admin-card"><span>' +
      escapeHtml(label) +
      "</span><strong>" +
      escapeHtml(value) +
      "</strong><small>" +
      escapeHtml(hint || "") +
      "</small></article>"
    );
  }

  function badgeClass(state) {
    if (state === "available") return "nf-signal-badge--available";
    if (state === "orientation") return "nf-signal-badge--orientation";
    if (state === "fail") return "nf-signal-badge--fail";
    return "nf-signal-badge--na";
  }

  function badgeLabel(state) {
    if (state === "available") return "Ready";
    if (state === "orientation") return "Not verified";
    if (state === "fail") return "FAIL";
    return "N/A";
  }

  function checksGrid(checks) {
    return (
      '<section class="nf-trust-signals" aria-labelledby="pa-checks-title"><h2 id="pa-checks-title" style="font-size:1rem">Per-check status</h2>' +
      '<div class="nf-trust-signals-grid">' +
      (checks || [])
        .map(function (c) {
          return (
            '<div class="nf-trust-signal" title="' +
            escapeHtml(c.detail || "") +
            '"><span class="nf-trust-signal-label">' +
            escapeHtml(c.label) +
            '</span><span class="nf-signal-badge ' +
            badgeClass(c.state) +
            '">' +
            badgeLabel(c.state) +
            "</span></div>"
          );
        })
        .join("") +
      "</div></section>"
    );
  }

  function findingsTable(findings) {
    var rows = (findings || [])
      .map(function (f) {
        return (
          "<tr><td>" +
          escapeHtml(f.severity) +
          "</td><td>" +
          escapeHtml(f.check_id) +
          "</td><td>" +
          escapeHtml(f.summary) +
          "</td><td>" +
          (f.machine_safe ? "yes (" + escapeHtml(f.kaizen_recipe || "") + ")" : "no — human triage") +
          "</td></tr>"
        );
      })
      .join("");
    return (
      '<section class="nf-admin-panel"><h2>Findings</h2><div class="nf-admin-table-wrap"><table><thead><tr>' +
      "<th>Severity</th><th>Check</th><th>Summary</th><th>Kaizen auto-fix</th>" +
      "</tr></thead><tbody>" +
      (rows || '<tr><td colspan="4">No open findings on the latest run.</td></tr>') +
      "</tbody></table></div></section>"
    );
  }

  function render(receipt) {
    var root = $("nfAuditOutput");
    if (!root) return;
    root.innerHTML =
      '<section class="nf-admin-grid">' +
      metricCard("Score", (receipt.score == null ? "—" : receipt.score) + "/100", receipt.status || "") +
      metricCard("Critical", receipt.critical_count || 0, "block the funnel") +
      metricCard("High", receipt.high_count || 0, "degrade the funnel") +
      metricCard("Browser checks", receipt.browser_checks_ran ? "ran" : "skipped", "Playwright") +
      "</section>" +
      checksGrid(receipt.checks) +
      findingsTable(receipt.findings);
    $("nfGeneratedAt").textContent = receipt.generated_at || "";
  }

  function load() {
    var input = $("nfAdminSecret");
    var value = input ? input.value.trim() : "";
    if (!value) {
      setStatus("Enter the admin secret to load the latest audit receipt.", "err");
      return;
    }
    setSecret(value);
    setStatus("Loading latest audit receipt...", "");
    fetch("/api/admin/partner-onboarding-audit", {
      headers: { Accept: "application/json", "X-Admin-Secret": value },
      credentials: "omit",
    })
      .then(function (res) {
        return res.json().then(function (body) {
          if (!res.ok) {
            var err = new Error(body.detail || "Partner-onboarding audit API failed");
            err.status = res.status;
            throw err;
          }
          return body;
        });
      })
      .then(function (data) {
        render(data);
        setStatus("Loaded — run_id " + (data.run_id || "—"), "ok");
      })
      .catch(function (err) {
        setStatus((err.status ? "HTTP " + err.status + ": " : "") + err.message, "err");
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var input = $("nfAdminSecret");
    if (input) input.value = secret();
    var button = $("nfLoadAudit");
    if (button) button.addEventListener("click", load);
    var clear = $("nfClearSecret");
    if (clear) {
      clear.addEventListener("click", function () {
        setSecret("");
        if (input) input.value = "";
        setStatus("Admin secret cleared from this browser.", "");
      });
    }
    if (secret()) load();
  });
})();
