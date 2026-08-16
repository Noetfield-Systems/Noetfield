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

/** App / auth / private routes must stay out of Google/Bing/GEO. */
const FORCE_NOINDEX_PREFIXES = [
  "/deterministic-api/workspace",
  "/deterministic-api/signin",
  "/auth/",
  "/admin/",
  "/invest/",
  "/gate/",
  "/banner/",
  "/factory/",
];

function forceNoindex(pathname) {
  const path = pathname.endsWith("/") && pathname.length > 1 ? pathname.slice(0, -1) : pathname;
  return FORCE_NOINDEX_PREFIXES.some(
    (prefix) => path === prefix.replace(/\/$/, "") || path.startsWith(prefix),
  );
}

const PUBLIC_SECURITY_HEADERS = {
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
  "X-Frame-Options": "DENY",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
};

const WWW_HTML_CSP =
  "default-src 'self'; base-uri 'self'; frame-ancestors 'none'; form-action 'self' https:; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; script-src 'self'; connect-src 'self' https://www.noetfield.com https://noetfield.com https://platform.noetfield.com https://api.noetfield.com https://scan.noetfield.com; upgrade-insecure-requests";

function applyPublicSecurityHeaders(headers, { html = false } = {}) {
  for (const [key, value] of Object.entries(PUBLIC_SECURITY_HEADERS)) {
    headers.set(key, value);
  }
  if (html) {
    headers.set("Content-Security-Policy", WWW_HTML_CSP);
    headers.delete("Access-Control-Allow-Origin");
    headers.delete("Access-Control-Allow-Credentials");
    headers.delete("Access-Control-Allow-Methods");
    headers.delete("Access-Control-Allow-Headers");
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
  applyPublicSecurityHeaders(headers);
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
    // Strip provider-side preview noindex so public marketing pages can rank.
    // Keep explicit noindex only on private/app routes.
    if (forceNoindex(url.pathname)) {
      out.headers.set("X-Robots-Tag", "noindex, nofollow");
    } else {
      out.headers.delete("X-Robots-Tag");
    }
    if ((out.headers.get("Content-Type") || "").toLowerCase().includes("text/html")) {
      out.headers.set("Cache-Control", "no-store, max-age=0, must-revalidate");
      out.headers.set("CDN-Cache-Control", "no-store");
      out.headers.set("Cloudflare-CDN-Cache-Control", "no-store");
      out.headers.delete("Age");
      applyPublicSecurityHeaders(out.headers, { html: true });
    }
    return out;
  },
};
