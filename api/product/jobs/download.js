const { forwardPlatform } = require("../../_lib/product-job-proxy");

module.exports = async function handler(req, res) {
  const jobId = String(req.query.jobId || req.query.job_id || "").trim();
  const artifactId = String(req.query.artifact_id || req.query.artifactId || "").trim();
  if (!jobId) {
    return res.status(400).json({ error: "JOB_ID_REQUIRED" });
  }
  const query = artifactId ? `?artifact_id=${encodeURIComponent(artifactId)}` : "";
  return forwardPlatform(req, res, {
    method: "GET",
    path: `/api/product/jobs/${encodeURIComponent(jobId)}/download${query}`,
  });
};
