(function () {
  var dispatchBtn = document.getElementById("rw-dispatch-btn");
  var statusEl = document.getElementById("rw-console-status");
  var jobEl = document.getElementById("rw-console-job");
  var noteEl = document.getElementById("rw-console-note");
  var modeEl = document.getElementById("rw-console-mode");

  function setStatus(text, kind) {
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.className = "nf-rw-status" + (kind ? " nf-rw-status--" + kind : "");
  }

  async function pollStatus(jobId, attempt) {
    var res = await fetch("/api/jobs/status?job_id=" + encodeURIComponent(jobId), {
      headers: { Accept: "application/json" },
    });
    var data = await res.json().catch(function () {
      return {};
    });
    if (res.status === 202 || data.status === "running") {
      setStatus("Running", "amber");
      if (attempt < 40) {
        window.setTimeout(function () {
          pollStatus(jobId, attempt + 1);
        }, 2000);
      } else {
        setStatus("Timed out", "failed");
        if (dispatchBtn) dispatchBtn.disabled = false;
      }
      return;
    }
    if (!res.ok || data.ok === false) {
      setStatus("Failed check", "failed");
      if (noteEl) noteEl.textContent = data.detail || "Could not read staging job status.";
      if (dispatchBtn) dispatchBtn.disabled = false;
      return;
    }
    var terminal = String(data.status || "").toLowerCase();
    setStatus(
      terminal === "succeeded" || terminal === "qualified" ? "Qualified" : terminal || "Complete",
      terminal.indexOf("fail") >= 0 ? "failed" : "qualified"
    );
    if (noteEl) {
      noteEl.textContent =
        "Staging job " + jobId + " finished with status " + (data.status || "unknown") + ".";
    }
    if (dispatchBtn) dispatchBtn.disabled = false;
  }

  if (!dispatchBtn) return;
  dispatchBtn.addEventListener("click", async function () {
    dispatchBtn.disabled = true;
    setStatus("Dispatching", "amber");
    if (modeEl) modeEl.textContent = "Staging · live";
    if (jobEl) jobEl.textContent = "Submitting signed POST /v1/jobs…";
    try {
      var res = await fetch("/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ recipe_id: "vendor-decision-brief" }),
      });
      var data = await res.json().catch(function () {
        return {};
      });
      if (!res.ok || !data.job_id) {
        setStatus("Unavailable", "failed");
        if (jobEl) jobEl.textContent = "Dispatch blocked";
        if (noteEl) {
          noteEl.textContent =
            (data.detail || "Live Motor dispatch unavailable.") +
            " Use enterprise intake for a managed engagement.";
        }
        dispatchBtn.disabled = false;
        return;
      }
      if (jobEl) jobEl.textContent = data.job_id;
      setStatus("Queued", "amber");
      pollStatus(data.job_id, 0);
    } catch (_err) {
      setStatus("Unavailable", "failed");
      if (noteEl) noteEl.textContent = "Network error reaching dispatch proxy.";
      dispatchBtn.disabled = false;
    }
  });
})();
