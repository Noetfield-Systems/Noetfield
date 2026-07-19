/** GET /api/runway/job-status?job_id=… — poll allowlisted Motor job result. */

const { readPublicJobStatus } = require("../_lib/runway-public-dispatch");

function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
  res.setHeader("Cache-Control", "no-store");
}

module.exports = async function handler(req, res) {
  cors(res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }
  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const jobId = (req.query && (req.query.job_id || req.query.jobId)) || "";
  const outcome = await readPublicJobStatus({ jobId, env: process.env });
  return res.status(outcome.httpStatus).json(outcome.body);
};
