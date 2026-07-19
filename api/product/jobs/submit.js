const { forwardPlatform } = require("../../_lib/product-job-proxy");

module.exports = async function handler(req, res) {
  return forwardPlatform(req, res, {
    method: "POST",
    path: "/api/product/jobs/submit",
    body: req.body || {},
  });
};
