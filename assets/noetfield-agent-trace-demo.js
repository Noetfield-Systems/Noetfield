/** Institutional nf26 demo — stepper, event trace, HITL panel, TLE preview, progress ring. */
(function () {
  "use strict";

  var STEPPER_ID = "nf26-demoStepper";
  var TRACE_ID = "nf26-eventTrace";
  var RING_ID = "nf26-progressRing";

  var EVENTS = [
    { time: "T+0ms", name: "POST /evaluate", detail: "Pre-execution policy check on Copilot operational intent.", badge: "signal" },
    { time: "T+42ms", name: "Policy router", detail: "Purview label gap + Entra CA posture surfaced for reviewer.", badge: "inspect" },
    { time: "T+88ms", name: "Confidence score", detail: "0.72 — route: conditional (human review required).", badge: "score" },
    { time: "T+120ms", name: "Workflow: pending_review", detail: "Approver chain: CISO delegate · RID threaded.", badge: "HITL" },
    { time: "T+180ms", name: "TLE draft", detail: "Signed entry prepared — metadata-only M365 evidence index.", badge: "record" },
    { time: "T+210ms", name: "Export gate", detail: "Board PDF + procurement ZIP fail closed if tampered.", badge: "export" },
  ];

  var SLICES = [1, 2, 3, 4, 5, 6];
  var PCTS = [20, 40, 60, 80, 100];
  var HITL = [
    "Signal ingested. Policy rules evaluate metadata-only M365 connectors.",
    "Confidence 0.72 — automatic allow blocked; review queue opened.",
    "Human-in-the-loop: <strong>named approver</strong> must sign before TLE is valid for board export.",
    "Approver signed — TLE v1 YAML sealed with evidence index.",
    "Export bundle ready — board PDF + procurement ZIP with integrity verify path.",
  ];
  var TLE = [
    "tle_id: tle_demo_001\ndecision: evaluating\nconfidence: —\napprover: —",
    "tle_id: tle_demo_001\ndecision: conditional\nconfidence: 0.72\napprover: pending",
    "tle_id: tle_demo_001\ndecision: conditional\nconfidence: 0.72\napprover: pending — CISO delegate",
    "tle_id: tle_demo_001\ndecision: approved\nconfidence: 0.72\napprover: jchen@institution.example",
    "tle_id: tle_demo_001\ndecision: exported\nconfidence: 0.72\nexport: board_pdf + procurement_zip",
  ];
  var TITLES = [
    "Session: Evaluate started",
    "Session: Confidence scored",
    "Session: Human gate active",
    "Session: TLE recorded",
    "Session: Export ready",
  ];

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

  function render(stepIdx, trace, tabs, ring, hitlCopy, tlePre, pctEl, titleEl, subEl, ach) {
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
      ring.style.setProperty("--pct", String(PCTS[stepIdx] || 20));
    }
    if (pctEl) {
      pctEl.textContent = String(PCTS[stepIdx] || 20) + "%";
    }
    if (hitlCopy && HITL[stepIdx]) {
      hitlCopy.innerHTML = HITL[stepIdx];
    }
    if (tlePre && TLE[stepIdx]) {
      tlePre.textContent = TLE[stepIdx];
    }
    if (titleEl && TITLES[stepIdx]) {
      titleEl.textContent = TITLES[stepIdx];
    }
    if (ach && subEl) {
      if (stepIdx >= 4) {
        ach.classList.add("show");
        subEl.textContent =
          "Achievement unlocked — start sandbox or apply for Copilot Readiness Pack.";
      } else {
        ach.classList.remove("show");
        subEl.textContent =
          "Complete all 5 steps to unlock export achievement — then start sandbox or apply for pilot.";
      }
    }
  }

  function init() {
    var stepper = document.getElementById(STEPPER_ID);
    var trace = document.getElementById(TRACE_ID);
    if (!stepper || !trace) {
      return;
    }

    var ring = document.getElementById(RING_ID);
    var hitlCopy = document.getElementById("nf26-hitlCopy");
    var tlePre = document.getElementById("nf26-tlePreview");
    var pctEl = document.getElementById("nf26-progressPct");
    var titleEl = document.getElementById("nf26-progressTitle");
    var subEl = document.getElementById("nf26-progressSub");
    var ach = document.getElementById("nf26-achievement");

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
        render(
          parseInt(tab.getAttribute("data-step"), 10),
          trace,
          tabs,
          ring,
          hitlCopy,
          tlePre,
          pctEl,
          titleEl,
          subEl,
          ach,
        );
      };
      tab.addEventListener("click", activate);
      tab.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          activate();
        }
      });
    });

    render(0, trace, tabs, ring, hitlCopy, tlePre, pctEl, titleEl, subEl, ach);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
