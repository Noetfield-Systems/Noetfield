/** POST /api/research-packs/leads — record purchase intent + hand off to workspace/Stripe. */

const { sendIntakeTelegram } = require("../_lib/intake-telegram");

function cryptoRandomId(prefix) {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
  return `${prefix}${hex}`;
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "OPTIONS") {
    res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "content-type");
    return res.status(204).end();
  }
  if (req.method !== "POST") {
    return res.status(405).json({ error: "METHOD_NOT_ALLOWED" });
  }

  const body = req.body && typeof req.body === "object" ? req.body : {};
  const email = String(body.email || "")
    .trim()
    .toLowerCase();
  if (!email || !email.includes("@") || email.length > 320) {
    return res.status(400).json({ error: "EMAIL_REQUIRED" });
  }

  const recipe_id = String(body.recipe_id || "vendor-decision-brief").trim();
  const lead_id = cryptoRandomId("lead_");
  const recorded_at = new Date().toISOString();
  const record = {
    schema: "noetfield.runway-commercial-lead.v0.1",
    lead_id,
    recorded_at,
    email,
    name: String(body.name || "").slice(0, 200),
    organization: String(body.organization || "").slice(0, 200),
    recipe_id,
    caller_site: String(body.caller_site || "noetfield.com").slice(0, 80),
    note: String(body.note || "").slice(0, 2000),
    source: String(body.source || "research-packs-www").slice(0, 80),
  };

  const env = process.env || {};
  try {
    await sendIntakeTelegram(
      {
        contact_name: record.name || email,
        organization: record.organization || "—",
        message: `Research packs lead · ${recipe_id} · ${email}${record.note ? " · " + record.note : ""}`,
        contact_email: email,
        request_id: lead_id,
        metadata: {
          topic: "research-packs",
          form_id: "nf_research_packs",
          recipe_id,
          lead_id,
          caller_site: record.caller_site,
        },
      },
      lead_id
    );
  } catch (err) {
    console.error("research_packs_lead_telegram_failed", err && err.message ? err.message : err);
  }

  const payment =
    recipe_id === "spreadsheet-kpi-pack"
      ? env.STRIPE_PAYMENT_LINK_KPI_PACK
      : recipe_id === "rfp-response-pack"
        ? env.STRIPE_PAYMENT_LINK_RFP_PACK
        : env.STRIPE_PAYMENT_LINK_DECISION_BRIEF;

  const runtimeBase = String(
    env.RUNWAY_RUNTIME_BASE_URL ||
      "https://noetfield-runway-runtime-api-staging.sina-kazemnezhad-ca.workers.dev"
  ).replace(/\/+$/, "");
  const workspacePath = String(env.WORKSPACE_PATH || "/v1/sourceb/workspace");

  return res.status(200).json({
    ok: true,
    lead_id,
    recorded_at,
    next: payment
      ? { kind: "stripe_payment_link", url: payment }
      : {
          kind: "workspace",
          url: runtimeBase + workspacePath,
          message:
            "Purchase intent recorded. Open the delivery workspace after entitlement is activated.",
        },
  });
};
