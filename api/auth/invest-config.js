/** GET /api/auth/invest-config — browser-safe Supabase auth configuration. */

const DEFAULT_SUPABASE_URL = "https://ldfruywifqnfpwsfgmdl.supabase.co";
const DEFAULT_SUPABASE_ANON_KEY =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkZnJ1eXdpZnFuZnB3c2ZnbWRsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAwMzY3OTIsImV4cCI6MjA5NTYxMjc5Mn0.ETJQMWEO0eIgwDh9YSmtZ5C-jHGT31oXC1PdsUWR5RQ";

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "private, no-store");
  res.setHeader("X-Robots-Tag", "noindex, nofollow");
  if (req.method !== "GET") {
    return res.status(405).json({ ok: false, error: "method_not_allowed" });
  }

  return res.status(200).json({
    schema: "noetfield-invest-browser-auth-config-v1",
    configured: true,
    supabase_url: process.env.SUPABASE_URL || DEFAULT_SUPABASE_URL,
    supabase_anon_key: process.env.SUPABASE_ANON_KEY || DEFAULT_SUPABASE_ANON_KEY,
  });
};
