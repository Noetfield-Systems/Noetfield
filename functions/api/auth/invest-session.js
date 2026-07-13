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

function investCookieHeaders() {
  return {
    "Set-Cookie":
      "nf_invest_auth=1; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=604800",
    "Cache-Control": "no-store",
  };
}

export async function onRequestPost(context) {
  let body;
  try {
    body = await context.request.json();
  } catch {
    return new Response(JSON.stringify({ ok: false, error: "invalid_json" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const token = body && body.access_token;
  if (!(await verifyAccessToken(token))) {
    return new Response(JSON.stringify({ ok: false, error: "unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
    });
  }

  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      ...investCookieHeaders(),
    },
  });
}

export async function onRequest() {
  return new Response(JSON.stringify({ ok: false, error: "method_not_allowed" }), {
    status: 405,
    headers: { "Content-Type": "application/json" },
  });
}
