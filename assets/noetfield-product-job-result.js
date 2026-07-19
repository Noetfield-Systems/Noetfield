/** Minimal client for research product job status/result/download/acceptance (HOLD — no production deploy). */

(function () {
  function qs(name) {
    return new URLSearchParams(location.search).get(name) || "";
  }

  function api(path, options) {
    return fetch(path, Object.assign({ headers: { Accept: "application/json" } }, options || {})).then(function (res) {
      return res.json().then(function (body) {
        return { ok: res.ok, status: res.status, body: body };
      });
    });
  }

  function render(el, lines) {
    el.innerHTML = lines.map(function (line) {
      return "<p>" + line + "</p>";
    }).join("");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var statusEl = document.getElementById("nfProductJobStatus");
    var actionsEl = document.getElementById("nfProductJobActions");
    if (!statusEl) return;

    var entitlementId = qs("entitlement_id");
    var jobId = qs("job_id");
    var sessionId = qs("session_id");

    function showStatus(lines) {
      render(statusEl, lines);
    }

    function loadEntitlement() {
      if (!entitlementId) {
        showStatus(["Missing entitlement_id.", "Complete Stripe checkout first."]);
        return;
      }
      api("/api/product/entitlements/status?entitlement_id=" + encodeURIComponent(entitlementId))
        .then(function (res) {
          if (!res.ok) {
            showStatus(["Entitlement lookup failed (" + res.status + ").", JSON.stringify(res.body)]);
            return;
          }
          var body = res.body;
          jobId = body.outbox && body.outbox.job_id ? body.outbox.job_id : jobId;
          showStatus([
            "Entitlement: " + body.entitlement_id,
            "Recipe: " + body.recipe_id + " · runway " + body.runway_id,
            "Status: " + body.status,
            "Outbox: " + (body.outbox ? body.outbox.status : "none"),
            jobId ? "Job: " + jobId : "Job not submitted yet.",
          ]);
          if (!jobId && body.status === "active") {
            actionsEl.hidden = false;
          } else if (jobId) {
            pollJob(jobId);
          }
        })
        .catch(function (err) {
          showStatus(["Entitlement request failed.", String(err)]);
        });
    }

    function pollJob(id) {
      api("/api/product/jobs/status?job_id=" + encodeURIComponent(id)).then(function (res) {
        var lines = ["Job: " + id, "Gateway status: " + (res.body.status || res.status)];
        if (res.ok) {
          lines.push("State: " + (res.body.status || "unknown"));
        } else {
          lines.push("Detail: " + JSON.stringify(res.body));
        }
        showStatus(lines);
        if (res.ok && String(res.body.status || "").toUpperCase() === "SUCCEEDED") {
          actionsEl.hidden = false;
          document.getElementById("nfLoadResultBtn").hidden = false;
          document.getElementById("nfAcceptBtn").hidden = false;
          document.getElementById("nfRejectBtn").hidden = false;
        }
      });
    }

    document.getElementById("nfSubmitJobBtn")?.addEventListener("click", function () {
      if (!entitlementId) return;
      var goal = {
        summary: "Customer purchased research product via noetfield.com",
        checkout_session_id: sessionId || undefined,
      };
      api("/api/product/jobs/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          entitlement_id: entitlementId,
          idempotency_key: "nf-www-" + (sessionId || entitlementId),
          goal: goal,
        }),
      }).then(function (res) {
        if (!res.ok) {
          showStatus(["Submit failed (" + res.status + ").", JSON.stringify(res.body)]);
          return;
        }
        jobId = res.body.job_id;
        var next = new URL(location.href);
        next.searchParams.set("job_id", jobId);
        history.replaceState({}, "", next);
        pollJob(jobId);
      });
    });

    document.getElementById("nfLoadResultBtn")?.addEventListener("click", function () {
      if (!jobId) return;
      api("/api/product/jobs/result?job_id=" + encodeURIComponent(jobId)).then(function (res) {
        showStatus([
          "Job: " + jobId,
          "Result status: " + (res.body.status || res.status),
          "Artifacts: " + JSON.stringify(res.body.artifacts || []),
        ]);
      });
    });

    function postAcceptance(state) {
      if (!jobId) return;
      api("/api/product/jobs/acceptance?job_id=" + encodeURIComponent(jobId), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state: state }),
      }).then(function (res) {
        showStatus(["Acceptance " + state + ": " + JSON.stringify(res.body)]);
      });
    }

    document.getElementById("nfAcceptBtn")?.addEventListener("click", function () {
      postAcceptance("accepted");
    });
    document.getElementById("nfRejectBtn")?.addEventListener("click", function () {
      postAcceptance("rejected");
    });

    loadEntitlement();
  });
})();
