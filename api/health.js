/** GET /api/health — lightweight www liveness (production E2E). */

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cache-Control", "no-store, max-age=0, must-revalidate");
  res.setHeader("CDN-Cache-Control", "no-store");
  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }
  const runtimeSha = String(
    process.env.CF_PAGES_COMMIT_SHA || process.env.NF_WWW_RELEASE_SHA || ""
  )
    .trim()
    .toLowerCase();
  return res.status(200).json({
    status: "ok",
    service: "noetfield-www",
    surface: "institutional",
    git_sha: /^[0-9a-f]{40}$/.test(runtimeSha) ? runtimeSha : "unavailable",
  });
};
