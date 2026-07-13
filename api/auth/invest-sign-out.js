/** POST /api/auth/invest-sign-out — clear nf_invest_auth cookie. */

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") {
    return res.status(405).json({ ok: false, error: "method_not_allowed" });
  }

  res.setHeader(
    "Set-Cookie",
    "nf_invest_auth=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0"
  );
  return res.status(200).json({ ok: true });
};
