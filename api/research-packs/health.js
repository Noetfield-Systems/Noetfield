/** GET /api/research-packs/health — Research packs buy-surface liveness. */

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
  return res.status(200).json({
    ok: true,
    service: "noetfield-research-packs",
    surface: "www",
    catalog_version: "runway-commercial-catalog.v1",
    canonical_url: "https://www.noetfield.com/research-packs/",
  });
};
