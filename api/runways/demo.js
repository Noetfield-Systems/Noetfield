const FIXTURE_BLUEPRINT = {
  schema: "noetfield.job-blueprint.v0.1",
  blueprint_id: "bp_00000000000000000000000000000001",
  runway_id: "research",
  recipe_id: "vendor-decision-brief",
  recipe_version: "0.1.0",
  status: "READY_FOR_APPROVAL",
  steps: [
    ["validate_intent", "Validate the decision contract", "deterministic"],
    ["score_options", "Score options against approved criteria", "deterministic"],
    ["synthesize_brief", "Synthesize the decision brief", "model backed"],
    ["verify_evidence", "Verify citations and unsupported claims", "deterministic"],
    ["render_artifacts", "Render DOCX and PDF artifacts", "tool backed"],
    ["deliver_receipt", "Deliver artifacts with a receipt", "deterministic"],
  ].map(function (step, index) {
    return {
      step_id: step[0],
      label: step[1],
      execution_class: step[2].replace(" ", "_"),
      acceptance: index === 5 ? "result and receipt available" : "stage contract passes",
    };
  }),
  cost: {
    currency: "USD",
    metered_model_cost_usd: null,
    external_tools_usd: null,
    deterministic_compute_usd: null,
    total_reconciled_machine_cost_usd: null,
    budget_cap_usd: 2,
  },
  estimate: { basis: "recipe_class", label: "minutes, not guaranteed" },
  expires_at: "fixture",
  approval_token: "fixture",
  evidence_class: "SAFE_FIXTURE",
};

const FIXTURE_EVENTS = [
  ["JOB_QUEUED", "Blueprint approved. Build queued."],
  ["JOB_LEASED", "Motor claimed an isolated job sandbox."],
  ["EXECUTION_SUBMITTED", "Draft artifacts produced."],
  ["VERIFICATION_CLAIMED", "Independent checks started."],
  ["JOB_TERMINAL", "Verifier qualified the fixture result."],
  ["RESULT_PERSISTED", "Artifacts and receipt recorded."],
].map(function (row, index) {
  return {
    sequence: index + 1,
    event_id: index + 1,
    event_type: row[0],
    occurred_at: new Date(Date.UTC(2026, 6, 19, 10, 0, index * 4)).toISOString(),
    payload: { human_label: row[1] },
  };
});

function bytes(text) {
  return new TextEncoder().encode(text);
}

async function sha256Hex(value) {
  const digest = await crypto.subtle.digest("SHA-256", value);
  return Array.from(new Uint8Array(digest)).map(function (part) {
    return part.toString(16).padStart(2, "0");
  }).join("");
}

async function hmacSha256Hex(secret, value) {
  const key = await crypto.subtle.importKey(
    "raw",
    bytes(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign("HMAC", key, bytes(value));
  return Array.from(new Uint8Array(signature)).map(function (part) {
    return part.toString(16).padStart(2, "0");
  }).join("");
}

async function gatewayFetch(method, path, body) {
  const base = String(process.env.RUNWAY_GATEWAY_BASE_URL || "").replace(/\/$/, "");
  const keyId = String(process.env.RUNWAY_GATEWAY_KEY_ID || "");
  const secret = String(process.env.RUNWAY_GATEWAY_HMAC_SECRET || "");
  if (!base || !keyId || secret.length < 32) throw new Error("live staging Gateway is not configured");
  const payload = body == null ? new Uint8Array() : bytes(JSON.stringify(body));
  const timestamp = new Date().toISOString();
  const nonce = crypto.randomUUID().replace(/-/g, "");
  const digest = await sha256Hex(payload);
  const canonical = [method, path, timestamp, nonce, digest].join("\n");
  const signature = await hmacSha256Hex(secret, canonical);
  const response = await fetch(base + path, {
    method,
    headers: {
      authorization: `NOETFIELD-HMAC ${keyId}:${signature}`,
      "x-noetfield-timestamp": timestamp,
      "x-noetfield-nonce": nonce,
      ...(body == null ? {} : { "content-type": "application/json" }),
    },
    ...(body == null ? {} : { body: JSON.stringify(body) }),
  });
  return { status: response.status, body: await response.json().catch(function () { return { error: "invalid_gateway_response" }; }) };
}

function liveAuthorized(req) {
  const expected = String(process.env.RUNWAYS_DEMO_BEARER || "");
  return expected.length >= 24 && String(req.headers.authorization || "") === `Bearer ${expected}`;
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  if (req.method !== "POST") return res.status(405).json({ error: "method_not_allowed" });

  const body = req.body && typeof req.body === "object" ? req.body : {};
  const action = String(body.action || "");
  const mode = body.mode === "live" ? "live" : "fixture";

  if (mode === "fixture") {
    if (action === "blueprint") return res.status(200).json(FIXTURE_BLUEPRINT);
    if (action === "approve") {
      return res.status(202).json({
        job_id: "rj_d0000000000000000000000000000000",
        status: "SUCCEEDED",
        approved: true,
        evidence_class: "SAFE_FIXTURE",
      });
    }
    if (action === "events") {
      return res.status(200).json({
        schema: "noetfield.runtime-event-list.v0.1",
        job_id: "rj_d0000000000000000000000000000000",
        events: FIXTURE_EVENTS,
        evidence_class: "SAFE_FIXTURE",
      });
    }
    if (action === "result") {
      return res.status(200).json({
        schema: "noetfield.job-result.v0.1",
        job_id: "rj_d0000000000000000000000000000000",
        status: "succeeded",
        artifacts: [
          { artifact_id: "decision-brief-docx", filename: "fixture-decision-brief.docx", content_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" },
          { artifact_id: "decision-brief-pdf", filename: "fixture-decision-brief.pdf", content_type: "application/pdf" },
        ],
        acceptance: { state: "pending" },
        cost: {
          metered_model_cost_usd: null,
          total_reconciled_machine_cost_usd: null,
          note: "Fixture costs are not live measurements.",
        },
        receipt_ref: "fixture://noetfield-runways/guided-cockpit-v1",
        evidence_class: "SAFE_FIXTURE",
      });
    }
    return res.status(400).json({ error: "unsupported_fixture_action" });
  }

  if (!liveAuthorized(req)) return res.status(401).json({ error: "live_demo_auth_required" });
  const allowed = new Set(["blueprint", "approve", "events", "result"]);
  if (!allowed.has(action)) return res.status(400).json({ error: "unsupported_live_action" });

  let response;
  if (action === "blueprint") {
    response = await gatewayFetch("POST", "/v1/jobs/blueprint", body.intake);
  } else if (action === "approve") {
    if (!/^bp_[0-9a-f]{32}$/.test(String(body.blueprint_id || ""))) return res.status(400).json({ error: "invalid_blueprint_id" });
    response = await gatewayFetch("POST", `/v1/jobs/${body.blueprint_id}/approve`, {
      intake: body.intake,
      expires_at: body.expires_at,
      approval_token: body.approval_token,
    });
  } else {
    if (!/^rj_[0-9a-f]{32}$/.test(String(body.job_id || ""))) return res.status(400).json({ error: "invalid_job_id" });
    response = await gatewayFetch("GET", `/v1/jobs/${body.job_id}/${action}`, null);
  }
  return res.status(response.status).json(response.body);
};
