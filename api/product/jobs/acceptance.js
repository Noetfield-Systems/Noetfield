const { forwardPlatform } = require("../../_lib/product-job-proxy");

module.exports = async function handler(req, res) {
  const jobId = String(req.query.jobId || req.query.job_id || "").trim();
  if (!jobId) {
    return res.status(400).json({ error: "JOB_ID_REQUIRED" });
  }
  return forwardPlatform(req, res, {
    method: "POST",
    path: `/api/product/jobs/${encodeURIComponent(jobId)}/acceptance`,
    body: req.body || {},
  });
};
