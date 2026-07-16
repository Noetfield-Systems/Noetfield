const SUPABASE_URL = "https://ldfruywifqnfpwsfgmdl.supabase.co";
const SUPABASE_ANON_KEY =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkZnJ1eXdpZnFuZnB3c2ZnbWRsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAwMzY3OTIsImV4cCI6MjA5NTYxMjc5Mn0.ETJQMWEO0eIgwDh9YSmtZ5C-jHGT31oXC1PdsUWR5RQ";

function investToken(request) {
  const cookie = request.headers.get("Cookie") || "";
  for (const part of cookie.split(";")) {
    const [rawName, ...rawValue] = part.trim().split("=");
    if (rawName !== "nf_invest_token") continue;
    try {
      return decodeURIComponent(rawValue.join("="));
    } catch (_) {
      return null;
    }
  }
  return null;
}

async function verifyAccessToken(token, env) {
  if (!token) return false;
  const origin = String(env?.SUPABASE_URL || SUPABASE_URL).replace(/\/$/, "");
  const anonKey = env?.SUPABASE_ANON_KEY || SUPABASE_ANON_KEY;
  try {
    const response = await fetch(`${origin}/auth/v1/user`, {
      headers: {
        Authorization: `Bearer ${token}`,
        apikey: anonKey,
      },
    });
    return response.ok;
  } catch (_) {
    return false;
  }
}

function publicOrigin(request) {
  const forwarded = request.headers.get("X-Forwarded-Host");
  const forwardedHost = forwarded ? forwarded.split(",")[0].trim().split(":")[0] : "";
  if (forwardedHost.endsWith("noetfield.com")) {
    return `https://${forwardedHost}`;
  }
  const host = (request.headers.get("Host") || "").split(":")[0];
  if (host.endsWith("noetfield.com")) {
    return `https://${host}`;
  }
  return "https://www.noetfield.com";
}

function redirectSignIn(request) {
  const url = new URL(request.url);
  const signIn = new URL("/auth/sign-in/", publicOrigin(request));
  signIn.searchParams.set("next", url.pathname + url.search);
  return new Response(null, {
    status: 302,
    headers: { Location: signIn.toString(), "Cache-Control": "no-store" },
  });
}

export async function onRequest(context) {
  const { request, env } = context;

  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response("Method not allowed", { status: 405 });
  }

  const token = investToken(request);
  if (!(await verifyAccessToken(token, env))) {
    return redirectSignIn(request);
  }

  const pathname = new URL(request.url).pathname;
  const assetPath = pathname.endsWith("/") ? pathname + "index.html" : pathname + "/index.html";

  if (env.ASSETS && env.ASSETS.fetch) {
    const assetUrl = new URL(assetPath, request.url);
    const asset = await env.ASSETS.fetch(assetUrl);
    if (asset && asset.ok) {
      const headers = new Headers(asset.headers);
      headers.set("Cache-Control", "private, no-store");
      return new Response(asset.body, { status: asset.status, headers });
    }
  }

  return redirectSignIn(request);
}
