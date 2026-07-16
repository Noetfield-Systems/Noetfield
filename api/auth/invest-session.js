/** POST /api/auth/invest-session — verify Supabase token, set protected bearer cookie. */

const SUPABASE_URL = "https://ldfruywifqnfpwsfgmdl.supabase.co";
const SUPABASE_ANON_KEY =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkZnJ1eXdpZnFuZnB3c2ZnbWRsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAwMzY3OTIsImV4cCI6MjA5NTYxMjc5Mn0.ETJQMWEO0eIgwDh9YSmtZ5C-jHGT31oXC1PdsUWR5RQ";

async function verifyAccessToken(token) {
  if (!token) return false;
  const res = await fetch(`${SUPABASE_URL}/auth/v1/user`, {
    headers: {
      Authorization: `Bearer ${token}`,
      apikey: SUPABASE_ANON_KEY,
    },
  });
  return res.ok;
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") {
    return res.status(405).json({ ok: false, error: "method_not_allowed" });
  }

  const token = req.body && req.body.access_token;
  if (!(await verifyAccessToken(token))) {
    return res.status(401).json({ ok: false, error: "unauthorized" });
  }

  res.setHeader(
    "Set-Cookie",
    `nf_invest_token=${encodeURIComponent(token)}; Path=/invest; HttpOnly; Secure; SameSite=Lax; Max-Age=3600`
  );
  return res.status(200).json({ ok: true });
};
