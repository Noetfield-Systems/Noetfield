/** Governance Playground v23 — persona entry, evaluate-on-submit, event trace + TLE receipt. */
(function () {
  "use strict";

  var PANEL_ID = "nfLiveProofHero";
  var ROWS = [
    "tle_id",
    "decision",
    "confidence_score",
    "risk_score",
    "risk_level",
    "rid",
    "evidence_index",
    "policy_version",
    "export_integrity",
  ];

  var LANE_LABELS = {
    all: "All products",
    copilot: "Copilot Pack",
    trust_brief: "Trust Brief",
    bank: "Bank Pilot",
    automation: "AI automation",
    specialist: "Governance specialist",
    investor: "VC diligence",
    partner: "Partner shadow",
  };

  var PERSONAS = {
    copilot: { label: "Copilot owner", lanes: ["copilot", "specialist", "automation", "bank"] },
    trust_brief: { label: "GRC / Trust Brief", lanes: ["trust_brief", "bank"] },
    diligence: { label: "VC & Partner", lanes: ["investor", "partner"] },
  };

  var SCENARIO_CATALOG = [
    {
      key: "copilot_rollout",
      lane: "copilot",
      label: "Copilot rollout · overshared SharePoint",
      action: "copilot_rollout",
      actor: "security-team",
      context:
        "Production M365 Copilot rollout with overshared SharePoint sites, sensitive board files, and incomplete access review",
      decision: "deny",
      score: "0.18",
      evidence: "purview dspm · sharepoint oversharing · entra access review",
      metadata: {
        policy_version: "3.2",
        risk_tier: "critical",
        sensitive_data: true,
        broad_sharing: true,
        evidence_ready: false,
      },
    },
    {
      key: "copilot_generation",
      lane: "copilot",
      label: "Copilot session · content generation",
      action: "copilot_content_generation",
      actor: "knowledge-worker",
      context:
        "M365 Copilot prompt asks for classified workspace summary; sensitivity labels exist but prompt DLP coverage is incomplete",
      decision: "review",
      score: "0.42",
      evidence: "purview labels · prompt dlp · audit",
      metadata: { risk_tier: "high", pii_exposure: true, prompt_dlp_gap: true, evidence_ready: true },
    },
    {
      key: "guest_access",
      lane: "copilot",
      label: "Guest access · external sharing",
      action: "guest_sharing",
      actor: "collaboration-lead",
      context:
        "External guest access requested for Copilot-enabled production SharePoint before Entra access review closes",
      decision: "deny",
      score: "0.25",
      evidence: "entra · sharepoint · access review",
      metadata: {
        policy_version: "3.2",
        risk_tier: "high",
        external_users: true,
        broad_sharing: true,
        evidence_ready: false,
      },
    },
    {
      key: "trust_brief_scope",
      lane: "trust_brief",
      label: "Trust Brief · AI policy scope change",
      action: "ai_policy_update",
      actor: "grc-lead",
      context:
        "Six-week Trust Brief updates AI acceptable-use policy before Copilot scale; owner and board evidence are attached",
      decision: "review",
      score: "0.64",
      evidence: "policy · risk · board",
      metadata: { risk_tier: "medium", evidence_ready: true, model_risk_owner: true },
    },
    {
      key: "vendor_ai_tool",
      lane: "trust_brief",
      label: "Vendor AI tool · onboarding",
      action: "vendor_ai_intake",
      actor: "procurement",
      context:
        "Third-party AI SaaS onboarding in June 2026; GPAI model version and vendor flow-down evidence are not yet verified",
      decision: "review",
      score: "0.52",
      evidence: "vendor · gpai evidence · procurement",
      metadata: { risk_tier: "medium", gpai_vendor_status: "unverified", evidence_ready: false },
    },
    {
      key: "bank_board_report",
      lane: "bank",
      label: "Bank Pilot · board report publish",
      action: "publish_board_report",
      actor: "frfi-governance",
      context:
        "FRFI shadow mode board artifact publish with named model-risk owner and complete evidence package",
      decision: "allow",
      score: "0.78",
      evidence: "shadow · model risk · board audit",
      metadata: { risk_tier: "low", evidence_ready: true, model_risk_owner: true },
    },
    {
      key: "bank_shadow_evaluate",
      lane: "bank",
      label: "Bank Pilot · shadow evaluate",
      action: "shadow_policy_evaluate",
      actor: "model-risk",
      context:
        "Read-only policy evaluate for regulated institution agentic AI use case; audit lineage export only",
      decision: "allow",
      score: "0.82",
      evidence: "shadow · lineage · audit",
      metadata: { risk_tier: "low", evidence_ready: true, model_risk_owner: true },
    },
    {
      key: "agentic_workflow",
      lane: "automation",
      label: "Agentic workflow · policy-bound",
      action: "agentic_workflow_run",
      actor: "automation-owner",
      context:
        "Agentic workflow can investigate, draft, and update internal case records; human checkpoint and kill-switch owner required",
      decision: "review",
      score: "0.34",
      evidence: "tool allowlist · checkpoint · rid",
      metadata: { risk_tier: "high", agentic_tool_access: "write", evidence_ready: false },
    },
    {
      key: "specialist_investigate",
      lane: "specialist",
      label: "Governance specialist · investigate gaps",
      action: "investigate_purview_gaps",
      actor: "governance-specialist",
      context:
        "Specialist investigates Purview label, DLP, oversharing, and Entra conditional-access gaps before Copilot sign-off",
      decision: "review",
      score: "0.48",
      evidence: "purview · entra · specialist",
      metadata: { risk_tier: "medium", prompt_dlp_gap: true, evidence_ready: true },
    },
    {
      key: "vc_shadow_evaluate",
      lane: "investor",
      label: "VC diligence · shadow evaluate target",
      action: "shadow_target_governance",
      actor: "vc-associate",
      context:
        "Pre-term-sheet diligence: target claims enterprise Copilot governance but cannot produce signed evaluate receipts",
      decision: "review",
      score: "0.44",
      evidence: "shadow · tle · diligence",
      metadata: { risk_tier: "high", evidence_ready: false, model_risk_owner: "missing" },
    },
    {
      key: "vc_portfolio_scan",
      lane: "investor",
      label: "VC diligence · portfolio Copilot scan",
      action: "portfolio_copilot_risk_scan",
      actor: "operating-partner",
      context:
        "Fund-level June 2026 scan: B2B portfolio company has Copilot licenses, broad sharing, and no board-ready receipt trail",
      decision: "review",
      score: "0.36",
      evidence: "portfolio · shadow · lp report",
      metadata: { risk_tier: "high", broad_sharing: true, evidence_ready: false },
    },
    {
      key: "partner_claims_intake",
      lane: "partner",
      label: "Partner shadow · regulated claim intake",
      action: "regulated_claim_intake",
      actor: "partner-pilot",
      context:
        "Partner submits regulated AI claim for shadow governance review; supporting evidence and owner are incomplete",
      decision: "review",
      score: "0.54",
      evidence: "partner signal · policy · owner",
      metadata: { risk_tier: "medium", evidence_ready: false, model_risk_owner: "missing" },
    },
    {
      key: "partner_agent_handoff",
      lane: "partner",
      label: "Partner shadow · agent handoff",
      action: "partner_agent_handoff",
      actor: "partner-pilot",
      context:
        "External partner agent asks for write access into customer workflow before tool allowlist and approval chain are attached",
      decision: "deny",
      score: "0.20",
      evidence: "partner signal · tool access · approval chain",
      metadata: {
        risk_tier: "critical",
        agentic_tool_access: "write",
        irreversible_action: true,
        evidence_ready: false,
      },
    },
  ];

  var SCENARIOS = {};
  var SCENARIO_LABELS = {};
  SCENARIO_CATALOG.forEach(function (s) {
    SCENARIOS[s.key] = s;
    SCENARIO_LABELS[s.key] = s.label;
  });

  var activePersona = "copilot";
  var activeLane = "all";
  var hasEvaluated = false;
  var lastEvaluateData = null;

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function personaLanes() {
    var p = PERSONAS[activePersona];
    return p ? p.lanes : ["copilot"];
  }

  function scenarioKeysForLane(lane) {
    var allowed = personaLanes();
    return SCENARIO_CATALOG.filter(function (s) {
      if (allowed.indexOf(s.lane) < 0) return false;
      return lane === "all" || s.lane === lane;
    }).map(function (s) {
      return s.key;
    });
  }

  function scenarioOfTheDayKey() {
    var keys = scenarioKeysForLane(activeLane);
    if (!keys.length) keys = scenarioKeysForLane("all");
    var day = new Date().getDay();
    return keys[day % keys.length];
  }

  function rebuildScenarioSelect(form, preferredKey) {
    var select = qs('[name="scenario"]', form);
    if (!select) return;
    var keys = scenarioKeysForLane(activeLane);
    var current = preferredKey || select.value;
    select.innerHTML = "";
    var groups = {};
    SCENARIO_CATALOG.forEach(function (s) {
      if (keys.indexOf(s.key) < 0) return;
      if (!groups[s.lane]) groups[s.lane] = [];
      groups[s.lane].push(s);
    });
    Object.keys(groups).forEach(function (lane) {
      var og = document.createElement("optgroup");
      og.label = LANE_LABELS[lane] || lane;
      groups[lane].forEach(function (s) {
        var opt = document.createElement("option");
        opt.value = s.key;
        opt.textContent = s.label;
        og.appendChild(opt);
      });
      select.appendChild(og);
    });
    if (current && keys.indexOf(current) >= 0) select.value = current;
    else if (keys.length) select.value = keys[0];
  }

  function applyScenarioOfTheDay(form) {
    var key = scenarioOfTheDayKey();
    rebuildScenarioSelect(form, key);
    applyScenario(form);
    var banner = document.getElementById("nfScenarioOfDay");
    if (banner) {
      var item = SCENARIOS[key];
      banner.innerHTML =
        '<strong>Scenario of the day:</strong> ' +
        (SCENARIO_LABELS[key] || key) +
        (item && item.lane
          ? ' · <span class="nf-scenario-of-day__lane">' + (LANE_LABELS[item.lane] || item.lane) + "</span>"
          : "") +
        ' — <span class="nf-scenario-of-day__hint">Press Evaluate intent to run trace + receipt</span>';
    }
  }

  function activeScenario(form) {
    var key = (qs('[name="scenario"]', form) || {}).value || "copilot_rollout";
    return SCENARIOS[key] || SCENARIOS.copilot_rollout;
  }

  function applyScenario(form) {
    var s = activeScenario(form);
    var actor = qs('[name="actor"]', form);
    var action = qs('[name="action"]', form);
    var context = qs('[name="context"]', form);
    if (actor) actor.value = s.actor;
    if (action) action.value = s.action;
    if (context) context.value = s.context;
  }

  function renderScenarioDeck(root, form) {
    var host = qs("#nfScenarioDeck", root);
    if (!host) return;
    var selected = activeScenario(form);
    var keys = scenarioKeysForLane(activeLane).slice(0, 6);
    host.innerHTML = keys
      .map(function (key) {
        var s = SCENARIOS[key];
        if (!s) return "";
        var active = selected && selected.key === s.key;
        return (
          '<button type="button" class="nf-scenario-card nf-scenario-card--neutral' +
          (active ? " is-active" : "") +
          '" data-scenario-card="' +
          s.key +
          '">' +
          '<span class="nf-scenario-card__lane">' +
          (LANE_LABELS[s.lane] || s.lane) +
          "</span>" +
          "<strong>" +
          s.label +
          "</strong>" +
          '<span class="nf-scenario-card__meta">Run evaluate to see decision</span>' +
          "</button>"
        );
      })
      .join("");
    host.querySelectorAll("[data-scenario-card]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var select = qs('[name="scenario"]', form);
        if (select) select.value = btn.getAttribute("data-scenario-card");
        applyScenario(form);
        renderScenarioDeck(root, form);
        resetProofPanel(root, false);
      });
    });
  }

  function idleReceiptHtml() {
    return (
      '<div class="nf-artifact-panel nf-live-proof-receipt nf-live-proof-receipt--idle">' +
      '<div class="nf-artifact-panel-chrome">' +
      '<span class="nf-artifact-panel-dots" aria-hidden="true"><i></i><i></i><i></i></span>' +
      '<span class="nf-artifact-panel-file">tle-receipt.yaml</span>' +
      '<span class="nf-artifact-panel-badge nf-live-proof-badge" id="nfLpReceiptBadge">Pending</span>' +
      "</div>" +
      '<aside class="nf-receipt-mock nf-receipt-mock--idle" aria-label="Trust Ledger Entry receipt">' +
      '<p class="nf-live-proof-idle-msg">Choose a scenario and press <strong>Evaluate intent</strong> to generate a tamper-evident scorecard.</p>' +
      '<dl class="nf-receipt-mock-body nf-live-proof-skeleton">' +
      ROWS.map(function (k) {
        return (
          '<div class="nf-receipt-row"><dt>' +
          k +
          '</dt><dd class="nf-live-proof-val nf-live-proof-val--idle">—</dd></div>'
        );
      }).join("") +
      "</dl>" +
      '<p class="nf-receipt-mock-footer nf-live-proof-footer">Sandbox · same evaluate semantics as <code>POST /evaluate</code></p>' +
      "</aside></div>"
    );
  }

  function skeletonReceipt(container) {
    container.innerHTML =
      '<div class="nf-artifact-panel nf-live-proof-receipt" aria-busy="true">' +
      '<div class="nf-artifact-panel-chrome">' +
      '<span class="nf-artifact-panel-dots" aria-hidden="true"><i></i><i></i><i></i></span>' +
      '<span class="nf-artifact-panel-file">tle-receipt.yaml</span>' +
      '<span class="nf-artifact-panel-badge nf-live-proof-badge" id="nfLpReceiptBadge">Evaluating…</span>' +
      "</div>" +
      '<aside class="nf-receipt-mock" aria-label="Trust Ledger Entry receipt">' +
      '<dl class="nf-receipt-mock-body nf-live-proof-skeleton">' +
      ROWS.map(function (k) {
        return (
          '<div class="nf-receipt-row nf-live-proof-row" data-key="' +
          k +
          '"><dt>' +
          k +
          '</dt><dd class="nf-live-proof-val"><span class="nf-skel-line"></span></dd></div>'
        );
      }).join("") +
      "</dl>" +
      '<p class="nf-receipt-mock-footer nf-live-proof-footer">Running policy scan…</p>' +
      "</aside></div>";
  }

  function showTracePanel(root) {
    var panel = qs("#nfLpTracePanel", root);
    if (!panel) return;
    panel.hidden = false;
    panel.classList.remove("is-idle");
  }

  function hideTracePanel(root) {
    var panel = qs("#nfLpTracePanel", root);
    if (!panel) return;
    panel.hidden = true;
    panel.classList.add("is-idle");
    var trace = qs("#nfLpEventTrace", root);
    if (trace) trace.innerHTML = "";
    var why = qs("#nfLpWhy", root);
    if (why) {
      why.hidden = true;
      why.innerHTML = "";
    }
    var hitl = qs("#nfLpHitl", root);
    if (hitl) {
      hitl.hidden = true;
      hitl.innerHTML = "";
    }
    var badge = qs("#nfLpTraceBadge", root);
    if (badge) badge.textContent = "Pending";
  }

  function resetProofPanel(root, fullIdle) {
    hasEvaluated = false;
    lastEvaluateData = null;
    var receiptHost = qs("#nfLiveProofReceipt", root);
    hideTracePanel(root);
    var phases = qs("#nfLiveProofRunPhases", root);
    if (phases) phases.hidden = true;
    if (receiptHost && fullIdle !== false) receiptHost.innerHTML = idleReceiptHtml();
  }

  function animateRow(row, value, isOk) {
    if (!row) return;
    var dd = row.querySelector(".nf-live-proof-val") || row.querySelector("dd");
    if (!dd) return;
    dd.innerHTML = "";
    dd.classList.remove("nf-skel-line", "nf-live-proof-val--idle");
    dd.classList.remove("nf-receipt-ok", "nf-receipt-review", "nf-receipt-deny");
    if (isOk) dd.classList.add("nf-receipt-ok");
    if (value === "review") dd.classList.add("nf-receipt-review");
    if (value === "deny") dd.classList.add("nf-receipt-deny");
    dd.textContent = value;
    row.classList.add("nf-live-proof-row--in");
  }

  function confidenceFromRisk(riskScore, fallback) {
    if (typeof riskScore === "number") {
      return (1 - Math.min(1, Math.max(0, riskScore / 100))).toFixed(2);
    }
    return fallback || "0.82";
  }

  function riskSeverity(riskScore) {
    if (riskScore >= 70) return "High";
    if (riskScore >= 40) return "Medium";
    return "Low";
  }

  function scenarioRid(scenario) {
    var seed = (scenario.key || "local") + "|" + (scenario.lane || "www");
    var hash = 0;
    for (var i = 0; i < seed.length; i += 1) {
      hash = ((hash << 5) - hash + seed.charCodeAt(i)) | 0;
    }
    return "RID-MAC-" + Math.abs(hash).toString(16).toUpperCase().padStart(8, "0");
  }

  function addRisk(score, amount, reason, code, reasons, codes, conditions, condition) {
    if (reason) reasons.push(reason);
    if (code) codes.push(code);
    if (condition) conditions.push(condition);
    return score + amount;
  }

  function localEvaluateIntent(actor, action, context, scenario) {
    var meta = (scenario && scenario.metadata) || {};
    var text = String(context || "").toLowerCase();
    var actionText = String(action || "").toLowerCase();
    var reasons = [];
    var codes = [];
    var conditions = [];
    var score = 8;
    var tier = String(meta.risk_tier || "standard").toLowerCase();

    if (!String(actor || "").trim()) {
      return {
        decision: "deny",
        risk_score: 100,
        risk_level: "High",
        confidence_score: 0,
        reason: ["Actor is required for any governed action."],
        reason_codes: ["actor_missing"],
        conditions: ["Provide a named actor before evaluate."],
        rid: scenarioRid(scenario),
        policy_version: meta.policy_version || "3.2",
      };
    }

    if (tier === "medium")
      score = addRisk(score, 14, "Medium-risk governance lane selected.", "risk_tier_medium", reasons, codes, conditions);
    if (tier === "high")
      score = addRisk(score, 28, "High-risk governance lane selected.", "risk_tier_high", reasons, codes, conditions);
    if (tier === "critical")
      score = addRisk(score, 42, "Critical governance lane selected.", "risk_tier_critical", reasons, codes, conditions);
    if (text.indexOf("unverified") >= 0 || text.indexOf("unknown") >= 0)
      score = addRisk(score, 12, "Unverified evidence appears in the scenario.", "unverified_context", reasons, codes, conditions);
    if (meta.sensitive_data || meta.sensitivity === "high")
      score = addRisk(
        score,
        14,
        "Sensitive information is in scope.",
        "sensitive_information_scope",
        reasons,
        codes,
        conditions,
        "Attach labels, DLP status, and evidence owner."
      );
    if (meta.pii_exposure)
      score = addRisk(
        score,
        15,
        "Personal or sensitive data exposure is possible.",
        "sensitive_data_exposure",
        reasons,
        codes,
        conditions,
        "Route through human review before AI execution."
      );
    if (meta.broad_sharing || meta.oversharing)
      score = addRisk(
        score,
        24,
        "Overshared content could be surfaced by AI grounding.",
        "oversharing_risk",
        reasons,
        codes,
        conditions,
        "Run access review and restrict broad sharing links."
      );
    if (meta.external_users || text.indexOf("external guest") >= 0)
      score = addRisk(
        score,
        14,
        "External-user access changes the approval boundary.",
        "external_access_boundary",
        reasons,
        codes,
        conditions,
        "Confirm Entra access review and business owner."
      );
    if (meta.prompt_dlp_gap || meta.dlp_gap)
      score = addRisk(
        score,
        18,
        "Prompt/content DLP coverage is incomplete.",
        "dlp_gap",
        reasons,
        codes,
        conditions,
        "Close DLP coverage before approval."
      );
    if (meta.agentic_tool_access === "write" || meta.write_access)
      score = addRisk(
        score,
        24,
        "Agent has write-capable tool access.",
        "agentic_write_access",
        reasons,
        codes,
        conditions,
        "Require human checkpoint, allowlist, and kill-switch owner."
      );
    if (meta.irreversible_action)
      score = addRisk(
        score,
        20,
        "Action has irreversible operational impact.",
        "irreversible_action",
        reasons,
        codes,
        conditions,
        "Escalate to named approver."
      );
    if (meta.evidence_ready === false)
      score = addRisk(
        score,
        14,
        "Evidence package is incomplete.",
        "evidence_incomplete",
        reasons,
        codes,
        conditions,
        "Attach policy version, evidence index, and approver chain."
      );
    if (meta.ai_act_transparency === "missing")
      score = addRisk(
        score,
        16,
        "AI transparency/disclosure evidence is missing.",
        "transparency_gap",
        reasons,
        codes,
        conditions,
        "Map disclosure and generated-content labeling before launch."
      );
    if (meta.gpai_vendor_status === "unverified")
      score = addRisk(
        score,
        14,
        "GPAI/vendor compliance evidence is unverified.",
        "vendor_gpai_unverified",
        reasons,
        codes,
        conditions,
        "Request model/version transparency and vendor flow-down evidence."
      );
    if (meta.model_risk_owner === false || meta.model_risk_owner === "missing")
      score = addRisk(
        score,
        12,
        "No named model-risk owner is attached.",
        "owner_missing",
        reasons,
        codes,
        conditions,
        "Assign an accountable owner before board or production use."
      );
    if (
      String(meta.policy_version || "") === "3.2" &&
      actionText.indexOf("copilot_rollout") >= 0 &&
      text.indexOf("production") >= 0
    )
      score = addRisk(
        score,
        10,
        "Production Copilot rollout needs v3.2 evidence and approver chain.",
        "production_copilot_scope",
        reasons,
        codes,
        conditions
      );

    score = Math.min(100, Math.max(0, score));
    var decision = score >= 70 ? "deny" : score >= 40 ? "review" : "allow";
    if (!reasons.length) reasons.push("Intent is within the current sandbox governance tolerance.");
    if (!conditions.length) conditions.push("Record the TLE and continue under sandbox controls.");
    if (decision === "deny") conditions.push("Remediate policy gaps before retrying evaluate.");
    if (decision === "review") conditions.push("Attach RID to named human review.");

    return {
      decision: decision,
      risk_score: score,
      risk_level: riskSeverity(score),
      confidence_score: Number(confidenceFromRisk(score)),
      reason: reasons,
      reason_codes: codes,
      conditions: conditions,
      rid: scenarioRid(scenario),
      policy_version: meta.policy_version || "3.2",
      product_lane: scenario.lane,
      scenario: scenario.key,
    };
  }

  function traceEventsFor(data, scenario) {
    var decision = (data && data.decision) || scenario.decision || "review";
    var conf =
      typeof data.confidence_score === "number"
        ? data.confidence_score.toFixed(2)
        : scenario.score || "0.72";
    return [
      {
        time: "T+0ms",
        name: "POST /evaluate",
        detail: "Pre-execution policy check on operational intent.",
        badge: "signal",
      },
      {
        time: "T+48ms",
        name: "Policy router",
        detail: "Purview · Entra · evidence index surfaced for " + (scenario.lane || "sandbox") + " lane.",
        badge: "inspect",
      },
      {
        time: "T+96ms",
        name: "Confidence score",
        detail: conf + " — route: " + decision + (decision === "allow" ? "" : " (human gate may apply)"),
        badge: "score",
      },
      {
        time: "T+140ms",
        name: "Workflow gate",
        detail:
          decision === "deny"
            ? "Automatic deny — remediation required before retry."
            : decision === "review"
              ? "Pending review — named approver required."
              : "Allow path — TLE draft prepared.",
        badge: decision === "review" || decision === "deny" ? "HITL" : "record",
      },
      {
        time: "T+190ms",
        name: "TLE draft",
        detail: "Trust Ledger Entry YAML sealed with metadata-only evidence index.",
        badge: "record",
      },
      {
        time: "T+220ms",
        name: "Export gate",
        detail: "Board PDF + procurement ZIP fail closed on tamper.",
        badge: "export",
      },
    ];
  }

  function traceRowHtml(event, active) {
    var cls = "nf-lp-eventRow" + (active ? " active" : "");
    var badgeCls = "nf-lp-eventBadge" + (event.badge === "HITL" ? " hitl" : "");
    return (
      '<div class="' +
      cls +
      '"><div class="nf-lp-eventTime">' +
      event.time +
      '</div><div><div class="nf-lp-eventName">' +
      event.name +
      '</div><div class="nf-lp-eventDetail">' +
      event.detail +
      '</div></div><span class="' +
      badgeCls +
      '">' +
      event.badge +
      "</span></div>"
    );
  }

  function runTraceAnimation(root, events, onDone) {
    var trace = qs("#nfLpEventTrace", root);
    var badge = qs("#nfLpTraceBadge", root);
    if (!trace) {
      if (onDone) onDone();
      return;
    }
    if (badge) badge.textContent = "Running";
    trace.innerHTML = "";
    var idx = 0;
    function tick() {
      if (idx >= events.length) {
        if (badge) badge.textContent = "Verified";
        if (onDone) onDone();
        return;
      }
      var html = "";
      for (var i = 0; i <= idx; i += 1) html += traceRowHtml(events[i], i === idx);
      trace.innerHTML = html;
      idx += 1;
      setTimeout(tick, 130);
    }
    tick();
  }

  function setRunPhase(root, phase) {
    var host = qs("#nfLiveProofRunPhases", root);
    if (!host) return;
    host.hidden = false;
    var order = { intent: 0, policy: 1, tle: 2 };
    var current = order[phase] || 0;
    host.querySelectorAll("[data-run-phase]").forEach(function (el) {
      var p = el.getAttribute("data-run-phase");
      var idx = order[p] || 0;
      el.classList.toggle("is-active", p === phase);
      el.classList.toggle("is-done", idx < current);
    });
  }

  function renderWhyChips(root, data) {
    var why = qs("#nfLpWhy", root);
    if (!why) return;
    var codes = (data && data.reason_codes) || [];
    if (!codes.length) {
      why.hidden = true;
      return;
    }
    var labels = {
      oversharing_risk: "Purview · oversharing",
      dlp_gap: "DLP gap",
      agentic_write_access: "Tool write access",
      evidence_incomplete: "Evidence gap",
      owner_missing: "Owner missing",
      production_copilot_scope: "Production scope",
      vendor_gpai_unverified: "Vendor GPAI",
      external_access_boundary: "External access",
    };
    why.hidden = false;
    why.innerHTML =
      "<p class=\"nf-lp-why-label\">Signal chips</p>" +
      codes
        .slice(0, 5)
        .map(function (c) {
          return '<span class="nf-lp-why-chip">' + (labels[c] || c.replace(/_/g, " ")) + "</span>";
        })
        .join("");
  }

  function renderHitl(root, data, scenario, onApprove) {
    var hitl = qs("#nfLpHitl", root);
    if (!hitl) return;
    var decision = (data && data.decision) || "review";
    if (decision === "allow") {
      hitl.hidden = true;
      return;
    }
    hitl.hidden = false;
    hitl.innerHTML =
      '<p class="nf-lp-hitl-title">Human-in-the-loop</p>' +
      "<p>" +
      (decision === "deny"
        ? "Deny recorded — simulate approver acknowledgment before export links unlock."
        : "Review required — named approver must sign before board export.") +
      '</p><button type="button" class="btn btn-secondary nf-lp-hitl-btn" id="nfLpHitlBtn">Simulate approver sign-off</button>';
    var btn = qs("#nfLpHitlBtn", hitl);
    if (btn) {
      btn.addEventListener("click", function () {
        btn.disabled = true;
        btn.textContent = "Signed · CISO delegate";
        hitl.classList.add("is-approved");
        if (onApprove) onApprove();
      });
    }
  }

  function compactList(items, fallback) {
    if (!Array.isArray(items) || !items.length) return fallback || "";
    return items.slice(0, 2).join(" · ");
  }

  function receiptMap(data, rid, scenario) {
    var score =
      typeof data.confidence_score === "number"
        ? data.confidence_score.toFixed(2)
        : confidenceFromRisk(data.risk_score, scenario.score);
    var decision = data.decision || scenario.decision;
    var riskScore = typeof data.risk_score === "number" ? String(data.risk_score) : "sample";
    return {
      tle_id: "TLE-015DCFB8B953",
      decision: decision,
      confidence_score: score,
      risk_score: riskScore,
      risk_level: data.risk_level || (decision === "deny" ? "High" : decision === "review" ? "Medium" : "Low"),
      rid: rid,
      evidence_index: scenario.evidence || "purview · entra · audit",
      policy_version: String(data.policy_version || (scenario.metadata && scenario.metadata.policy_version) || "3.2"),
      export_integrity: "PASS · fail closed on tamper",
    };
  }

  function paintReceipt(container, map, data, scenario, exportUnlocked) {
    var panel = container.querySelector(".nf-live-proof-receipt");
    if (!panel) return;
    panel.classList.remove("nf-live-proof-receipt--idle");
    panel.setAttribute("aria-busy", "false");
    var badge = container.querySelector(".nf-live-proof-badge") || qs("#nfLpReceiptBadge", container);
    if (badge) badge.textContent = "Verified";
    ROWS.forEach(function (key, i) {
      setTimeout(function () {
        animateRow(
          panel.querySelector('[data-key="' + key + '"]'),
          map[key],
          key === "export_integrity"
        );
      }, 80 * i);
    });
    var foot = container.querySelector(".nf-live-proof-footer");
    if (foot) {
      var reason = compactList(data.reason, "Evaluate completed against current scenario metadata.");
      var condition = compactList(data.conditions, "Record the decision with RID lineage.");
      var exportLinks = exportUnlocked
        ? ' <a href="/trust-ledger/sample-report/">Download TLE YAML</a> · <a href="/copilot/procurement/">Procurement pack</a>'
        : ' <em class="nf-lp-export-locked">Export links unlock after approver sign-off</em>';
      foot.innerHTML =
        "<strong>Why:</strong> " +
        reason +
        " <br><strong>Next:</strong> " +
        condition +
        exportLinks +
        ' <br><a href="/result/' +
        encodeURIComponent(map.rid) +
        '">Open full result</a> · <a href="/start/?sandbox=1">Continue in sandbox</a>';
    }
  }

  function renderReceipt(container, data, rid, scenario, exportUnlocked) {
    skeletonReceipt(container);
    paintReceipt(container, receiptMap(data, rid, scenario), data, scenario, exportUnlocked);
  }

  function fetchEvaluate(actor, action, context, scenario) {
    return fetch("/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        actor: actor,
        action: action,
        context: context,
        metadata: Object.assign({}, scenario.metadata || {}, {
          source: "live-proof-hero",
          scenario: scenario.key,
          product_lane: scenario.lane,
        }),
      }),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          data.http_status = res.status;
          if (!res.ok && data.error !== "re_brief_required") throw new Error("HTTP " + res.status);
          return data;
        });
      })
      .then(function (data) {
        if (!data.rid) data.rid = scenarioRid(scenario);
        if (data.error === "re_brief_required") {
          data.decision = "review";
          data.risk_score = 62;
          data.risk_level = "Medium";
          data.confidence_score = 0.38;
          data.reason = [data.detail || "Evaluation context invalidated by SSOT change."];
          data.conditions = ["Re-brief against current policy version before evaluate."];
        }
        return data;
      })
      .catch(function () {
        return localEvaluateIntent(actor, action, context, scenario);
      });
  }

  function bindPersonas(root, form) {
    root.querySelectorAll("[data-live-proof-persona]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        activePersona = btn.getAttribute("data-live-proof-persona") || "copilot";
        activeLane = "all";
        root.querySelectorAll("[data-live-proof-persona]").forEach(function (b) {
          var on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        root.querySelectorAll("[data-live-proof-lane]").forEach(function (b) {
          b.classList.remove("is-active");
          b.setAttribute("aria-pressed", "false");
        });
        applyScenarioOfTheDay(form);
        renderScenarioDeck(root, form);
        resetProofPanel(root, true);
      });
    });
  }

  function bindLaneFilters(root, form) {
    root.querySelectorAll("[data-live-proof-lane]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        activeLane = btn.getAttribute("data-live-proof-lane") || "all";
        root.querySelectorAll("[data-live-proof-lane]").forEach(function (b) {
          var on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        applyScenarioOfTheDay(form);
        renderScenarioDeck(root, form);
        resetProofPanel(root, true);
      });
    });
  }

  function bindForm(root) {
    var form = qs("#nfLiveProofForm", root);
    if (!form) return;
    var receiptHost = qs("#nfLiveProofReceipt", root);
    var scenarioSelect = qs('[name="scenario"]', form);

    try {
      var sp = new URLSearchParams(window.location.search);
      var laneParam = sp.get("lane");
      if (laneParam === "investor" || laneParam === "partner") activePersona = "diligence";
      else if (laneParam === "trust_brief" || laneParam === "bank") activePersona = "trust_brief";
      else if (laneParam && LANE_LABELS[laneParam]) {
        activeLane = laneParam;
        if (["investor", "partner"].indexOf(laneParam) >= 0) activePersona = "diligence";
        else if (["trust_brief", "bank"].indexOf(laneParam) >= 0) activePersona = "trust_brief";
        else activePersona = "copilot";
        root.querySelectorAll("[data-live-proof-persona]").forEach(function (b) {
          var p = b.getAttribute("data-live-proof-persona");
          var on = p === activePersona;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        root.querySelectorAll("[data-live-proof-lane]").forEach(function (b) {
          var on = b.getAttribute("data-live-proof-lane") === laneParam;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
      }
    } catch (_) {}

    bindPersonas(root, form);
    bindLaneFilters(root, form);
    applyScenarioOfTheDay(form);
    renderScenarioDeck(root, form);
    resetProofPanel(root, true);

    if (scenarioSelect) {
      scenarioSelect.addEventListener("change", function () {
        applyScenario(form);
        renderScenarioDeck(root, form);
        resetProofPanel(root, true);
      });
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var scenario = activeScenario(form);
      var actor = (qs('[name="actor"]', form) || {}).value || scenario.actor;
      var action = (qs('[name="action"]', form) || {}).value || scenario.action;
      var context = (qs('[name="context"]', form) || {}).value || scenario.context;
      var btn = qs("#nfLiveProofSubmit", form) || qs('button[type="submit"]', form);
      if (btn) {
        btn.disabled = true;
        btn.textContent = "Evaluating…";
      }

      resetProofPanel(root, false);
      skeletonReceipt(receiptHost);
      showTracePanel(root);
      setRunPhase(root, "intent");

      var evaluatePromise = fetchEvaluate(actor, action, context, scenario);

      setTimeout(function () {
        setRunPhase(root, "policy");
      }, 280);

      evaluatePromise.then(function (data) {
        lastEvaluateData = data;
        hasEvaluated = true;
        var events = traceEventsFor(data, scenario);
        setRunPhase(root, "tle");
        runTraceAnimation(root, events, function () {
          var exportUnlocked = data.decision === "allow";
          renderWhyChips(root, data);
          renderHitl(root, data, scenario, function () {
            paintReceipt(receiptHost, receiptMap(data, data.rid, scenario), data, scenario, true);
          });
          renderReceipt(receiptHost, data, data.rid, scenario, exportUnlocked);
          if (window.noetfieldSandbox && window.noetfieldSandbox.incrementEvaluate) {
            window.noetfieldSandbox.incrementEvaluate();
          }
          if (btn) {
            btn.disabled = false;
            btn.textContent = "Evaluate intent";
          }
          var phases = qs("#nfLiveProofRunPhases", root);
          if (phases) {
            setTimeout(function () {
              phases.hidden = true;
            }, 1400);
          }
        });
      });

      evaluatePromise.catch(function () {
        if (btn) {
          btn.disabled = false;
          btn.textContent = "Evaluate intent";
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.getElementById(PANEL_ID);
    if (!root) return;
    bindForm(root);
  });
})();
