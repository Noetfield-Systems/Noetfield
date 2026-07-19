#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const source = fs.readFileSync(path.join(root, "infra/cf-www-proxy/src/worker.js"), "utf8");
const wrangler = fs.readFileSync(path.join(root, "infra/cf-www-proxy/wrangler.toml"), "utf8");
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString("base64")}`;
const worker = (await import(moduleUrl)).default;
const releaseSha = "626b9b68512b6c474f759bff134ca251b053960d";
const immutableOrigin = "https://a1b2c3d4.noetfield-www.pages.dev";

const apex = await worker.fetch(
  new Request("https://noetfield.com/about/?nf_rel_002=1"),
  { RELEASE_SHA: releaseSha },
);
if (apex.status !== 308) throw new Error(`apex status ${apex.status}`);
if (apex.headers.get("location") !== "https://www.noetfield.com/about/?nf_rel_002=1") {
  throw new Error(`apex location ${apex.headers.get("location")}`);
}
if (apex.headers.get("cache-control") !== "no-store, max-age=0, must-revalidate") {
  throw new Error(`apex cache policy ${apex.headers.get("cache-control")}`);
}

if (!wrangler.includes('pattern = "status.noetfield.com/*"')) {
  throw new Error("missing status worker route");
}
if (!wrangler.includes('STATUS_HOST = "status.noetfield.com"')) {
  throw new Error("missing status host binding");
}
const status = await worker.fetch(
  new Request("https://status.noetfield.com/?incident=1"),
  { RELEASE_SHA: releaseSha },
);
if (status.status !== 308) throw new Error(`status subdomain status ${status.status}`);
if (status.headers.get("location") !== "https://www.noetfield.com/status/?incident=1") {
  throw new Error(`status subdomain location ${status.headers.get("location")}`);
}

const originalFetch = globalThis.fetch;
let fetchedUrl = "";
globalThis.fetch = async (request) => {
  fetchedUrl = String(request);
  return new Response("<!doctype html><title>Current release</title>", {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "public, max-age=604800",
      Age: "300",
    },
  });
};
try {
  const response = await worker.fetch(
    new Request("https://www.noetfield.com/proof/?nf_rel_002=1"),
    { ORIGIN: immutableOrigin, RELEASE_SHA: releaseSha },
  );
  if (response.status !== 200) throw new Error(`proxy status ${response.status}`);
  if (fetchedUrl !== `${immutableOrigin}/proof/?nf_rel_002=1`) {
    throw new Error(`proxy target ${fetchedUrl}`);
  }
  if (response.headers.get("x-noetfield-proxy") !== "cf-www-proxy") {
    throw new Error("missing proxy identity header");
  }
  if (response.headers.get("x-noetfield-release") !== releaseSha) {
    throw new Error("missing exact release identity header");
  }
  if (response.headers.get("cache-control") !== "no-store, max-age=0, must-revalidate") {
    throw new Error(`html cache policy ${response.headers.get("cache-control")}`);
  }
  if (response.headers.get("cdn-cache-control") !== "no-store") {
    throw new Error("missing CDN no-store policy");
  }
  if (response.headers.get("cloudflare-cdn-cache-control") !== "no-store") {
    throw new Error("missing Cloudflare CDN no-store policy");
  }
  if (response.headers.has("age")) {
    throw new Error("stale origin age leaked through HTML response");
  }
} finally {
  globalThis.fetch = originalFetch;
}

const missingRelease = await worker.fetch(
  new Request("https://www.noetfield.com/"),
  { ORIGIN: immutableOrigin },
);
if (missingRelease.status !== 503) {
  throw new Error(`missing release must fail closed, received ${missingRelease.status}`);
}

const mutableAlias = await worker.fetch(
  new Request("https://www.noetfield.com/"),
  { ORIGIN: "https://noetfield-www.pages.dev", RELEASE_SHA: releaseSha },
);
if (mutableAlias.status !== 503) {
  throw new Error(`mutable Pages alias must fail closed, received ${mutableAlias.status}`);
}

if (wrangler.includes('ORIGIN = "https://noetfield-www.pages.dev"')) {
  throw new Error("wrangler config must not default to the mutable Pages alias");
}
if (!wrangler.includes('RELEASE_SHA = "UNSET"')) {
  throw new Error("wrangler config missing fail-closed release placeholder");
}

console.log("test-cf-www-proxy: PASS");
