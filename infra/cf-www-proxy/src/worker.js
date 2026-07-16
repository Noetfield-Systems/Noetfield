const ORIGIN =
  (typeof ORIGIN_HOST !== "undefined" ? ORIGIN_HOST : null) ||
  "https://release-required.invalid";
const APEX_HOST = "noetfield.com";
const CANONICAL_HOST = "www.noetfield.com";
const STATUS_HOST = "status.noetfield.com";
const SHA_PATTERN = /^[0-9a-f]{40}$/;

function isImmutablePagesOrigin(value) {
  try {
    const url = new URL(value);
    const labels = url.hostname.split(".");
    return (
      url.protocol === "https:" &&
      labels.length === 4 &&
      labels[1] === "noetfield-www" &&
      labels[2] === "pages" &&
      labels[3] === "dev" &&
      !["main", "production", "www"].includes(labels[0])
    );
  } catch (_error) {
    return false;
  }
}

function edgeHeaders(releaseSha) {
  const headers = new Headers({
    "Cache-Control": "no-store, max-age=0, must-revalidate",
    "CDN-Cache-Control": "no-store",
    "Cloudflare-CDN-Cache-Control": "no-store",
    "X-Noetfield-Proxy": "cf-www-proxy",
  });
  if (SHA_PATTERN.test(releaseSha)) {
    headers.set("X-Noetfield-Release", releaseSha);
  }
  return headers;
}

function permanentRedirect(url, releaseSha) {
  const headers = edgeHeaders(releaseSha);
  headers.set("Location", url.toString());
  return new Response(null, { status: 308, headers });
}

function unavailable(releaseSha) {
  return new Response("Release origin is not configured", {
    status: 503,
    headers: edgeHeaders(releaseSha),
  });
}

export default {
  async fetch(request, env) {
    const origin = env.ORIGIN || ORIGIN;
    const releaseSha = String(env.RELEASE_SHA || "").trim().toLowerCase();
    const url = new URL(request.url);
    const apexHost = env.APEX_HOST || APEX_HOST;
    const canonicalHost = env.CANONICAL_HOST || CANONICAL_HOST;
    const statusHost = env.STATUS_HOST || STATUS_HOST;
    if (url.hostname === statusHost && url.pathname === "/") {
      url.protocol = "https:";
      url.hostname = canonicalHost;
      url.pathname = "/status/";
      url.port = "";
      return permanentRedirect(url, releaseSha);
    }
    if (url.hostname === apexHost) {
      url.protocol = "https:";
      url.hostname = canonicalHost;
      url.port = "";
      return permanentRedirect(url, releaseSha);
    }
    if (!SHA_PATTERN.test(releaseSha) || !isImmutablePagesOrigin(origin)) {
      return unavailable(releaseSha);
    }
    const originUrl = new URL(origin);
    const target = new URL(url.pathname + url.search, originUrl);
    const headers = new Headers(request.headers);
    headers.set("Host", originUrl.host);
    headers.set("X-Forwarded-Host", url.host);
    headers.set("X-Forwarded-Proto", url.protocol.replace(":", ""));
    const init = {
      method: request.method,
      headers,
      redirect: "manual",
    };
    if (request.method !== "GET" && request.method !== "HEAD") {
      init.body = request.body;
    }
    const res = await fetch(target, init);
    const out = new Response(res.body, res);
    out.headers.set("X-Noetfield-Proxy", "cf-www-proxy");
    out.headers.set("X-Noetfield-Release", releaseSha);
    if ((out.headers.get("Content-Type") || "").toLowerCase().includes("text/html")) {
      out.headers.set("Cache-Control", "no-store, max-age=0, must-revalidate");
      out.headers.set("CDN-Cache-Control", "no-store");
      out.headers.set("Cloudflare-CDN-Cache-Control", "no-store");
      out.headers.delete("Age");
    }
    return out;
  },
};
