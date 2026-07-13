function hasInvestCookie(request) {
  const cookie = request.headers.get("Cookie") || "";
  return /(?:^|;\s*)nf_invest_auth=1(?:;|$)/.test(cookie);
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
  return Response.redirect(signIn.toString(), 302);
}

export async function onRequest(context) {
  const { request, env } = context;

  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response("Method not allowed", { status: 405 });
  }

  if (!hasInvestCookie(request)) {
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
