/** GET /api/admin/partner-onboarding-audit — serves the last committed audit receipt.
 *  Batch/cron result, not a live proxy — no platform.noetfield.com dependency.
 *  Runs as a Cloudflare Pages Function (workerd, not Node) — no fs/disk access, so this
 *  fetches the receipt as a same-origin static asset instead of reading it off disk. */

const RECEIPT_PATH = "/admin/partner-onboarding/latest.json";

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

  const host = req.headers["host"] || "www.noetfield.com";
  const origin = `https://${host}`;

  try {
    const forwarded = await fetch(origin + RECEIPT_PATH, {
      headers: { Accept: "application/json" },
    });
    if (!forwarded.ok) {
      throw new Error(`receipt fetch HTTP ${forwarded.status}`);
    }
    const data = await forwarded.json();
    return res.status(200).json(data);
  } catch (err) {
    console.error("partner_onboarding_audit_receipt_read_failed", err && err.message ? err.message : err);
    return res.status(502).json({
      detail: "No audit receipt yet — nf-partner-onboarding-e2e-audit.yml has not run on this deploy.",
    });
  }
};
