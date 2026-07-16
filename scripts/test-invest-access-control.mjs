#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const source = fs.readFileSync(path.join(root, "functions/invest/[[path]].js"), "utf8");
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString("base64")}`;
const { onRequest } = await import(moduleUrl);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const require = createRequire(import.meta.url);
const sessionHandler = require(path.join(root, "api/auth/invest-session.js"));

function responseRecorder() {
  const state = { status: 200, headers: {}, body: null };
  const res = {
    setHeader(name, value) {
      state.headers[String(name).toLowerCase()] = value;
      return res;
    },
    status(code) {
      state.status = code;
      return res;
    },
    json(body) {
      state.body = body;
      return state;
    },
  };
  return { res, state };
}

async function run(request, env = {}) {
  return onRequest({
    request,
    env,
    next: async () => new Response("unexpected pass-through", { status: 200 }),
  });
}

const unauthenticated = await run(
  new Request("https://www.noetfield.com/invest/?nf_rel_002=1"),
);
assert(unauthenticated.status === 302, `unauthenticated status ${unauthenticated.status}`);
assert(
  unauthenticated.headers.get("location") ===
    "https://www.noetfield.com/auth/sign-in/?next=%2Finvest%2F%3Fnf_rel_002%3D1",
  `unauthenticated location ${unauthenticated.headers.get("location")}`,
);

const lookalikeCookie = await run(
  new Request("https://www.noetfield.com/invest/", {
    headers: { Cookie: "nf_invest_auth=10" },
  }),
);
assert(lookalikeCookie.status === 302, `lookalike-cookie status ${lookalikeCookie.status}`);

const originalFetch = globalThis.fetch;
let sessionVerification = null;
globalThis.fetch = async (request, init = {}) => {
  sessionVerification = { url: String(request), headers: new Headers(init.headers) };
  return new Response(JSON.stringify({ id: "investor-user" }), { status: 200 });
};
const session = responseRecorder();
await sessionHandler(
  { method: "POST", body: { access_token: "verified.supabase.token" } },
  session.res,
);
assert(session.state.status === 200, `session endpoint status ${session.state.status}`);
assert(
  session.state.headers["set-cookie"] ===
    "nf_invest_token=verified.supabase.token; Path=/invest; HttpOnly; Secure; SameSite=Lax; Max-Age=3600",
  `session cookie ${session.state.headers["set-cookie"]}`,
);
assert(
  sessionVerification?.headers.get("authorization") === "Bearer verified.supabase.token",
  "session endpoint did not verify the supplied bearer token",
);

let assetRequest = "";
let routeVerification = null;
globalThis.fetch = async (request, init = {}) => {
  routeVerification = { url: String(request), headers: new Headers(init.headers) };
  return new Response(JSON.stringify({ id: "investor-user" }), { status: 200 });
};
const authorized = await run(
  new Request("https://www.noetfield.com/invest/", {
    headers: { Cookie: "nf_invest_token=verified.supabase.token" },
  }),
  {
    ASSETS: {
      fetch: async (request) => {
        assetRequest = String(request);
        return new Response("private investor material", {
          status: 200,
          headers: { "content-type": "text/html" },
        });
      },
    },
  },
);
assert(authorized.status === 200, `authorized status ${authorized.status}`);
assert(
  routeVerification?.headers.get("authorization") === "Bearer verified.supabase.token",
  "protected route did not reverify the bearer token",
);
assert(
  assetRequest === "https://www.noetfield.com/invest/index.html",
  `authorized asset request ${assetRequest}`,
);
assert(
  authorized.headers.get("cache-control") === "private, no-store",
  `authorized cache-control ${authorized.headers.get("cache-control")}`,
);

globalThis.fetch = async () => new Response("unauthorized", { status: 401 });
const rejectedToken = await run(
  new Request("https://www.noetfield.com/invest/", {
    headers: { Cookie: "nf_invest_token=forged.token" },
  }),
);
assert(rejectedToken.status === 302, `forged-token status ${rejectedToken.status}`);

const post = await run(
  new Request("https://www.noetfield.com/invest/", { method: "POST" }),
);
assert(post.status === 405, `non-read method status ${post.status}`);

globalThis.fetch = originalFetch;

console.log("test-invest-access-control: PASS");
