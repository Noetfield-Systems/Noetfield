/** POST /api/runway/jobs — public allowlisted Motor dispatch (HMAC via server secrets). */
/* secret-bind: redeploy after Pages RUNWAY_RUNTIME_API_SECRET sync */

const { dispatchPublicJob, listPublicRecipes } = require("../_lib/runway-public-dispatch");

function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
  res.setHeader("Cache-Control", "no-store");
}

module.exports = async function handler(req, res) {
  cors(res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method === "GET") {
    return res.status(200).json({
      ok: true,
      service: "noetfield-www-runway-dispatch",
      recipes: listPublicRecipes(),
      intake_fallback: "/contact/?topic=enterprise-governance",
    });
  }

  if (req.method !== "POST") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const body = req.body && typeof req.body === "object" ? req.body : {};
  const outcome = await dispatchPublicJob({
    recipeId: body.recipe_id || body.recipeId,
    goal: body.goal || null,
    env: process.env,
  });
  return res.status(outcome.httpStatus).json(outcome.body);
};
