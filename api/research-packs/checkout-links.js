/** GET /api/research-packs/checkout-links — optional Stripe Payment Links. */

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "OPTIONS") {
    res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
    return res.status(204).end();
  }
  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }
  const env = process.env || {};
  const runtimeBase = String(
    env.RUNWAY_RUNTIME_BASE_URL ||
      "https://noetfield-runway-runtime-api-staging.sina-kazemnezhad-ca.workers.dev"
  ).replace(/\/+$/, "");
  const workspacePath = String(env.WORKSPACE_PATH || "/v1/sourceb/workspace");
  return res.status(200).json({
    schema: "noetfield.runway-checkout-links.v0.1",
    links: {
      "vendor-decision-brief": env.STRIPE_PAYMENT_LINK_DECISION_BRIEF || null,
      "spreadsheet-kpi-pack": env.STRIPE_PAYMENT_LINK_KPI_PACK || null,
      "rfp-response-pack": env.STRIPE_PAYMENT_LINK_RFP_PACK || null,
    },
    workspace_url: runtimeBase + workspacePath,
    note: "When Stripe Payment Links are bound as Pages secrets, Buy CTAs open them. Until then, /api/research-packs/leads captures purchase intent.",
  });
};
