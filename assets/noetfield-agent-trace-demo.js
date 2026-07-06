/** Interactive agent trace — stepper clicks populate ADK-style event rows (copilot/demo). */
(function () {
  "use strict";

  var STEPPER_ID = "nf26-demoStepper";
  var TRACE_ID = "nf26-eventTrace";
  var RING_ID = "nf26-progressRing";

  var EVENTS = [
    { time: "T+0ms", name: "Policy load", detail: "Copilot Acceptable Use v3.2 loaded from tenant SSOT.", badge: "signal" },
    { time: "T+42ms", name: "POST /evaluate", detail: "Pre-execution policy check on Copilot rollout intent.", badge: "inspect" },
    { time: "T+88ms", name: "Confidence score", detail: "0.72 — route: conditional (human review required).", badge: "score" },
    { time: "T+120ms", name: "Workflow: pending_review", detail: "Human-in-the-loop: named approver must sign before export.", badge: "HITL" },
    { time: "T+180ms", name: "TLE draft", detail: "Signed entry prepared — metadata-only M365 evidence index.", badge: "record" },
    { time: "T+210ms", name: "Export gate", detail: "Board PDF + procurement ZIP fail closed if tampered.", badge: "export" },
  ];

  var SLICES = [1, 2, 3, 5, 6];
  var PCTS = [25, 50, 75, 90, 100];

  function rowHtml(event, active) {
    var cls = "nf26-eventRow" + (active ? " active" : "");
    var badgeCls = "nf26-eventBadge" + (event.badge === "HITL" ? " ok" : "");
    return (
      '<div class="' +
      cls +
      '"><div class="nf26-eventTime">' +
      event.time +
      '</div><div><div class="nf26-eventName">' +
      event.name +
      '</div><div class="nf26-eventDetail">' +
      event.detail +
      '</div></div><span class="' +
      badgeCls +
      '">' +
      event.badge +
      "</span></div>"
    );
  }

  function render(stepIdx, trace, tabs, ring) {
    var end = SLICES[stepIdx] || EVENTS.length;
    var html = "";
    for (var i = 0; i < end; i += 1) {
      html += rowHtml(EVENTS[i], i === end - 1);
    }
    trace.innerHTML = html;

    tabs.forEach(function (tab, i) {
      if (i === stepIdx) {
        tab.setAttribute("aria-current", "step");
        tab.classList.add("is-active");
      } else {
        tab.removeAttribute("aria-current");
        tab.classList.remove("is-active");
      }
    });

    if (ring) {
      ring.style.setProperty("--pct", String(PCTS[stepIdx] || 25));
    }
  }

  function init() {
    var stepper = document.getElementById(STEPPER_ID);
    var trace = document.getElementById(TRACE_ID);
    if (!stepper || !trace) {
      return;
    }

    var ring = document.getElementById(RING_ID);
    var tabs = stepper.querySelectorAll("[data-step]");
    if (!tabs.length) {
      tabs = stepper.querySelectorAll(".nf-demo-stepper__step, .nf26-demoStep");
    }

    tabs.forEach(function (tab, idx) {
      var step = tab.getAttribute("data-step");
      if (step === null || step === "") {
        tab.setAttribute("data-step", String(idx));
      }
      tab.setAttribute("role", tab.getAttribute("role") || "tab");
      tab.setAttribute("tabindex", "0");
      var activate = function () {
        render(parseInt(tab.getAttribute("data-step"), 10), trace, tabs, ring);
      };
      tab.addEventListener("click", activate);
      tab.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          activate();
        }
      });
    });

    render(0, trace, tabs, ring);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
