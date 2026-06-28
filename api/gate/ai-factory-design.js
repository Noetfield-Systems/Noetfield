const { buildFactoryReceipt, validateGateRequest } = require("../_lib/ai-factory-core");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method !== "POST") return res.status(405).json({ detail: "Method not allowed" });

  const payload = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
  const errors = validateGateRequest(payload);
  if (errors.length) return res.status(400).json({ status: "failed", errors });

  return res.status(202).json(buildFactoryReceipt(payload));
};
