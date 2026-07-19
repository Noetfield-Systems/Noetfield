const { forwardPlatform } = require("../../_lib/product-job-proxy");

module.exports = async function handler(req, res) {
  const entitlementId = String(req.query.entitlement_id || req.query.entitlementId || "").trim();
  if (!entitlementId) {
    return res.status(400).json({ error: "ENTITLEMENT_ID_REQUIRED" });
  }
  return forwardPlatform(req, res, {
    method: "GET",
    path: `/api/product/entitlements/${encodeURIComponent(entitlementId)}`,
  });
};
