#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const source = fs.readFileSync(path.join(root, "functions/invest/[[path]].js"), "utf8");
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString("base64")}`;
const { onRequest } = await import(moduleUrl);

function assert(condition, message) {
  if (!condition) throw new Error(message);
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

let assetRequest = "";
const authorized = await run(
  new Request("https://www.noetfield.com/invest/", {
    headers: { Cookie: "nf_invest_auth=1" },
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
  assetRequest === "https://www.noetfield.com/invest/index.html",
  `authorized asset request ${assetRequest}`,
);
assert(
  authorized.headers.get("cache-control") === "private, no-store",
  `authorized cache-control ${authorized.headers.get("cache-control")}`,
);

const post = await run(
  new Request("https://www.noetfield.com/invest/", { method: "POST" }),
);
assert(post.status === 405, `non-read method status ${post.status}`);

console.log("test-invest-access-control: PASS");
