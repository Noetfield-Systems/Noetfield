(function () {
  "use strict";

  var form = document.getElementById("rw-demo-form");
  if (!form) return;

  var state = { blueprint: null, jobId: null };
  var error = document.getElementById("rw-demo-error");

  function setError(message) {
    if (!error) return;
    error.textContent = message || "";
    error.hidden = !message;
  }

  function setPhase(number) {
    document.querySelectorAll("[data-demo-phase]").forEach(function (panel) {
      panel.hidden = panel.getAttribute("data-demo-phase") !== String(number);
    });
    document.querySelectorAll("[data-demo-phase-indicator]").forEach(function (item) {
      item.classList.toggle("is-active", Number(item.getAttribute("data-demo-phase-indicator")) <= number);
    });
    setError("");
  }

  async function call(action) {
    var response = await fetch("/api/runways/demo", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ action: action, mode: "fixture" }),
    });
    var body = await response.json().catch(function () { return { error: "invalid_demo_response" }; });
    if (!response.ok) throw new Error(body.error || "Demo request failed");
    return body;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var submit = form.querySelector('button[type="submit"]');
    if (submit) submit.disabled = true;
    void call("blueprint").then(function (blueprint) {
      state.blueprint = blueprint;
      document.getElementById("rw-demo-blueprint-id").textContent = blueprint.blueprint_id;
      document.getElementById("rw-demo-budget").textContent =
        blueprint.cost.budget_cap_usd == null ? "Not set" : "$" + Number(blueprint.cost.budget_cap_usd).toFixed(2);
      var steps = document.getElementById("rw-demo-steps");
      steps.replaceChildren();
      blueprint.steps.forEach(function (step, index) {
        var item = document.createElement("li");
        var number = document.createElement("span");
        var content = document.createElement("div");
        var title = document.createElement("strong");
        var detail = document.createElement("small");
        number.textContent = String(index + 1);
        title.textContent = step.label;
        detail.textContent = step.execution_class.replaceAll("_", " ") + " · " + step.acceptance;
        content.append(title, detail);
        item.append(number, content);
        steps.append(item);
      });
      setPhase(2);
    }).catch(function (caught) {
      setError(caught.message || "Could not compile fixture blueprint.");
    }).finally(function () {
      if (submit) submit.disabled = false;
    });
  });

  document.getElementById("rw-demo-edit").addEventListener("click", function () {
    setPhase(1);
  });

  document.getElementById("rw-demo-approve").addEventListener("click", function (event) {
    var button = event.currentTarget;
    button.disabled = true;
    void call("approve").then(function (approved) {
      state.jobId = approved.job_id;
      document.getElementById("rw-demo-job-id").textContent = approved.job_id;
      return call("events");
    }).then(function (eventList) {
      var list = document.getElementById("rw-demo-events");
      list.replaceChildren();
      eventList.events.forEach(function (runtimeEvent) {
        var item = document.createElement("li");
        var check = document.createElement("span");
        var time = document.createElement("time");
        var label = document.createElement("strong");
        check.textContent = "✓";
        time.textContent = new Date(runtimeEvent.occurred_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
        label.textContent = runtimeEvent.payload.human_label || runtimeEvent.event_type;
        item.append(check, time, label);
        list.append(item);
      });
      setPhase(3);
    }).catch(function (caught) {
      setError(caught.message || "Could not approve fixture.");
    }).finally(function () {
      button.disabled = false;
    });
  });

  document.getElementById("rw-demo-result").addEventListener("click", function (event) {
    var button = event.currentTarget;
    button.disabled = true;
    void call("result").then(function (result) {
      var artifacts = document.getElementById("rw-demo-artifacts");
      artifacts.replaceChildren();
      result.artifacts.forEach(function (artifact) {
        var card = document.createElement("article");
        var title = document.createElement("strong");
        var type = document.createElement("small");
        title.textContent = artifact.filename || artifact.artifact_id;
        type.textContent = artifact.content_type;
        card.append(title, type);
        artifacts.append(card);
      });
      setPhase(4);
    }).catch(function (caught) {
      setError(caught.message || "Could not read fixture receipt.");
    }).finally(function () {
      button.disabled = false;
    });
  });
})();
