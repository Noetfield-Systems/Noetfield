const config = require("../noetfield-ai-factory-lanes.json");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method !== "GET") return res.status(405).json({ detail: "Method not allowed" });
  return res.status(200).json(config);
};
