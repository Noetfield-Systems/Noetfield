const { buildStatusPreview } = require("../_lib/ai-factory-core");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method !== "GET") return res.status(405).json({ detail: "Method not allowed" });
  const requestId = req.query && req.query.request_id;
  if (!requestId) {
    return res.status(400).json({ status: "failed", errors: [{ field: "request_id", code: "required", message: "request_id is required" }] });
  }
  return res.status(200).json(buildStatusPreview(requestId));
};
