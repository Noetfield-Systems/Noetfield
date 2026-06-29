/** Deterministic pre-execution evaluate (mirrors governance-console governance_engine.py). */

function generateRid() {
  const hex = () => Math.floor(Math.random() * 16).toString(16);
  const block = () =>
    Array.from({ length: 8 }, hex).join("").toUpperCase();
  const suffix = Array.from({ length: 8 }, hex).join("").toUpperCase();
  return "RID-" + block() + "-" + suffix;
}

function riskSeverity(riskScore) {
  if (riskScore >= 70) return "High";
  if (riskScore >= 40) return "Medium";
  return "Low";
}

function confidenceFromRisk(riskScore) {
  return Math.round((100 - Math.min(100, Math.max(0, riskScore))) / 100 * 100) / 100;
}

function buildConfidenceFactors(action, riskScore, reasons) {
  const description =
    (action || "").trim().slice(0, 120) ||
    (reasons[0] ? reasons[0].slice(0, 120) : "Governance evaluation risk");
  const riskSummary = [
    {
      id: "RISK-" + String(riskScore).padStart(3, "0"),
      description,
      severity: riskSeverity(riskScore),
    },
  ];
  const governanceValue = confidenceFromRisk(riskScore);
  return {
    risk_summary: riskSummary,
    confidence_factors: [
      { factor: "governance_risk", weight: governanceValue, value: governanceValue },
      { factor: "risk_summary", weight: 0, value: riskSummary },
    ],
  };
}

function parsePolicyVersion(meta) {
  const raw = meta.policy_version || meta.policyVersion || "3.1";
  const n = parseFloat(String(raw).replace(/^v/i, ""));
  return Number.isFinite(n) ? n : 3.1;
}

function evaluateIntent({ actor, action, context, metadata }) {
  const reasons = [];
  const conditions = [];
  const reasonCodes = [];
  let score = 8;

  const actorClean = (actor || "").trim();
  const actionClean = (action || "").trim().toLowerCase();
  const contextClean = (context || "").trim().toLowerCase();
  const meta = metadata && typeof metadata === "object" ? metadata : {};

  if (meta.stale === true || meta.re_brief_required === true) {
    return {
      error: "re_brief_required",
      status: 409,
      detail: "Evaluation context invalidated by SSOT change — re-brief required before evaluate.",
      rid: generateRid(),
      policy_version: parsePolicyVersion(meta),
    };
  }

  const policyVersion = parsePolicyVersion(meta);

  if (!actorClean) {
    return {
      decision: "deny",
      risk_score: 100,
      reason: ["Actor is required for any governed action."],
      conditions: ["Provide a non-empty actor identifier."],
      rid: generateRid(),
      policy_version: policyVersion,
    };
  }

  const riskTier = String(meta.risk_tier || meta.riskTier || "standard").toLowerCase();
  if (riskTier === "medium") {
    score += 14;
    reasonCodes.push("risk_tier_medium");
  } else if (riskTier === "high") {
    score += 28;
    reasonCodes.push("risk_tier_high");
  } else if (riskTier === "critical") {
    score += 42;
    reasonCodes.push("risk_tier_critical");
  }

  if (contextClean.includes("unknown") || contextClean.includes("unverified")) {
    score += 12;
    reasons.push("Context contains unverified or unknown signals.");
    reasonCodes.push("unverified_context");
  }

  if (contextClean.length < 12) {
    score += 15;
    reasons.push("Context is minimal — insufficient operational detail for STP.");
    reasonCodes.push("minimal_context");
  }

  if (meta.high_risk === true) {
    score += 20;
    reasons.push("Metadata flagged high_risk=true.");
    reasonCodes.push("high_risk_flag");
  }

  if (meta.pii_exposure === true) {
    score += 15;
    reasons.push("Metadata flagged personal or sensitive data exposure.");
    conditions.push("Human review required before Copilot or agent execution.");
    reasonCodes.push("sensitive_data_exposure");
  }

  if (meta.sensitive_data === true || meta.sensitivity === "high") {
    score += 14;
    reasons.push("Sensitive information is in scope for the evaluate.");
    conditions.push("Attach Purview labels, DLP status, and evidence owner before approval.");
    reasonCodes.push("sensitive_information_scope");
  }

  if (meta.broad_sharing === true || meta.oversharing === true) {
    score += 24;
    reasons.push("Potential oversharing could make restricted content visible through AI search or grounding.");
    conditions.push("Run access review and restrict broad SharePoint links before production rollout.");
    reasonCodes.push("oversharing_risk");
  }

  if (meta.external_users === true || contextClean.includes("external guest")) {
    score += 14;
    reasons.push("External-user access changes the approval boundary.");
    conditions.push("Confirm Entra access review and named business owner.");
    reasonCodes.push("external_access_boundary");
  }

  if (meta.prompt_dlp_gap === true || meta.dlp_gap === true) {
    score += 18;
    reasons.push("Prompt or content DLP coverage is incomplete.");
    conditions.push("Close DLP gap or keep the workflow in review mode.");
    reasonCodes.push("dlp_gap");
  }

  if (meta.agentic_tool_access === "write" || meta.write_access === true) {
    score += 24;
    reasons.push("Agentic workflow has write-capable tool access.");
    conditions.push("Require human checkpoint, tool allowlist, and kill-switch owner.");
    reasonCodes.push("agentic_write_access");
  }

  if (meta.irreversible_action === true) {
    score += 20;
    reasons.push("Requested action has irreversible or hard-to-reverse operational impact.");
    conditions.push("Escalate to named approver before execution.");
    reasonCodes.push("irreversible_action");
  }

  if (meta.evidence_ready === false) {
    score += 14;
    reasons.push("Evidence package is incomplete.");
    conditions.push("Attach policy version, evidence index, and approver chain.");
    reasonCodes.push("evidence_incomplete");
  }

  if (meta.ai_act_transparency === "missing") {
    score += 16;
    reasons.push("AI transparency or disclosure evidence is missing.");
    conditions.push("Map Article 50-style disclosure and generated-content labeling before launch.");
    reasonCodes.push("transparency_gap");
  }

  if (meta.gpai_vendor_status === "unverified") {
    score += 14;
    reasons.push("GPAI/vendor compliance evidence is unverified.");
    conditions.push("Request model/version transparency and vendor flow-down evidence.");
    reasonCodes.push("vendor_gpai_unverified");
  }

  if (meta.model_risk_owner === false || meta.model_risk_owner === "missing") {
    score += 12;
    reasons.push("No named model-risk or governance owner is attached.");
    conditions.push("Assign accountable owner before board or production use.");
    reasonCodes.push("owner_missing");
  }

  if (policyVersion >= 3.2) {
    if (contextClean.includes("production") && contextClean.includes("guest")) {
      score += 30;
      reasons.push(
        "Policy v3.2 blocks guest access in production Copilot scope — stale briefing detected."
      );
      conditions.push("Re-brief against Copilot Acceptable Use v3.2 before rollout.");
      reasonCodes.push("policy_v32_guest_access");
    }
    if (actionClean.includes("copilot_rollout") && contextClean.includes("production")) {
      score += 10;
      reasons.push("Production Copilot rollout requires v3.2 evidence index and approver chain.");
      reasonCodes.push("production_copilot_scope");
    }
  }

  score = Math.min(100, Math.max(0, score));

  let decision;
  if (score >= 70) {
    decision = "deny";
    if (!reasons.length) reasons.push("Risk score exceeds deny threshold.");
    conditions.push("Remediate policy gaps before retrying evaluate.");
  } else if (score >= 40) {
    decision = "review";
    if (!reasons.length) reasons.push("Risk score requires human review.");
    conditions.push("Route to compliance owner with RID attached.");
  } else {
    decision = "allow";
    reasons.push("Intent within default policy tolerance for shadow evaluation.");
    conditions.push(
      "External systems may proceed only under your institution's execution authority."
    );
  }

  const conf = buildConfidenceFactors(action, score, reasons);
  return {
    decision,
    risk_score: score,
    risk_level: riskSeverity(score),
    confidence_score: confidenceFromRisk(score),
    reason: reasons,
    reason_codes: reasonCodes,
    conditions,
    rid: generateRid(),
    policy_version: policyVersion,
    tenant_id: meta.tenant_id || "demo-tenant",
    scenario: meta.scenario || null,
    product_lane: meta.product_lane || null,
    ...conf,
  };
}

function applySsotChange({ fromVersion, toVersion, pending }) {
  const from = parseFloat(String(fromVersion || "3.1").replace(/^v/i, "")) || 3.1;
  const to = parseFloat(String(toVersion || "3.2").replace(/^v/i, "")) || 3.2;
  const list = Array.isArray(pending) ? pending : [];
  const invalidated = [];
  const reBriefQueue = [];

  list.forEach(function (item) {
    const pv = parseFloat(String(item.policy_version || item.policyVersion || "3.1").replace(/^v/i, "")) || 3.1;
    if (pv < to) {
      invalidated.push({
        rid: item.rid,
        action: item.action,
        prior_policy_version: String(pv),
        status: "invalidated",
        reason: "SSOT_CHANGED — policy v" + to + " supersedes v" + from,
      });
      reBriefQueue.push({
        rid: item.rid,
        action: item.action,
        required_policy_version: String(to),
        briefing_status: "queued",
        reason: "Re-brief required against Copilot Acceptable Use v" + to,
      });
    }
  });

  return {
    event: "SSOT_CHANGED",
    from_version: String(from),
    to_version: String(to),
    occurred_at: new Date().toISOString(),
    policy_id: "copilot-acceptable-use",
    invalidated_count: invalidated.length,
    invalidated,
    re_brief_queue: reBriefQueue,
    middleware_note:
      "Agency agents POST /api/demo/ssot-change then /api/demo/evaluate — Noetfield is gate + ledger, not the agent.",
  };
}

function buildTleReceipt(evalResult, scenario) {
  const score =
    typeof evalResult.confidence_score === "number"
      ? evalResult.confidence_score.toFixed(2)
      : typeof evalResult.risk_score === "number"
      ? confidenceFromRisk(evalResult.risk_score).toFixed(2)
      : scenario.score || "0.82";
  return {
    tle_id: "TLE-" + (evalResult.rid || "DEMO").slice(-12).toUpperCase(),
    decision: evalResult.decision || scenario.decision,
    confidence_score: score,
    rid: evalResult.rid,
    evidence_index: scenario.evidence || "purview · entra · audit",
    export_integrity: "PASS · fail closed on tamper",
    policy_version: evalResult.policy_version || "3.2",
  };
}

function buildBoardSnippet(evalResult, ssotEvent) {
  return {
    title: "Copilot Governance — board digest (demo excerpt)",
    generated_at: new Date().toISOString(),
    executive_summary:
      "Policy v" +
      (ssotEvent ? ssotEvent.to_version : "3.2") +
      " published; " +
      (ssotEvent ? ssotEvent.invalidated_count : 0) +
      " stale evaluations invalidated; fresh evaluate → " +
      (evalResult.decision || "review") +
      " with signed receipt.",
    bullets: [
      "SSOT change triggers automatic context invalidation (governance latency fix).",
      "Re-brief queue routes agency agents through middleware evaluate API.",
      "Board PDF exports TLE + evidence index — no payment rails or execution.",
    ],
    decision: evalResult.decision,
    confidence_score:
      typeof evalResult.risk_score === "number"
        ? (1 - evalResult.risk_score / 100).toFixed(2)
        : null,
  };
}

module.exports = {
  evaluateIntent,
  applySsotChange,
  buildTleReceipt,
  buildBoardSnippet,
  generateRid,
};
