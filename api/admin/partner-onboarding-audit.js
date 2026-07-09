/** GET /api/admin/partner-onboarding-audit — serves the last committed audit receipt.
 *  Batch/cron result, not a live proxy — no platform.noetfield.com dependency. */

const fs = require("fs");
const path = require("path");

const RECEIPT_PATH = path.join(
  process.cwd(),
  "reports",
  "agent-auto",
  "partner-onboarding-audit",
  "latest.json"
);

function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Accept, X-Admin-Secret");
}

module.exports = async function handler(req, res) {
  cors(res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }
  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const adminSecret = req.headers["x-admin-secret"] || "";
  if (!adminSecret) {
    return res.status(401).json({ detail: "X-Admin-Secret required" });
  }

  try {
    const raw = fs.readFileSync(RECEIPT_PATH, "utf8");
    const data = JSON.parse(raw);
    return res.status(200).json(data);
  } catch (err) {
    console.error("partner_onboarding_audit_receipt_read_failed", err && err.message ? err.message : err);
    return res.status(502).json({
      detail: "No audit receipt yet — nf-partner-onboarding-e2e-audit.yml has not run on this deploy.",
    });
  }
};
