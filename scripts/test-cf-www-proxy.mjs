#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const source = fs.readFileSync(path.join(root, "infra/cf-www-proxy/src/worker.js"), "utf8");
const wrangler = fs.readFileSync(path.join(root, "infra/cf-www-proxy/wrangler.toml"), "utf8");
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString("base64")}`;
const worker = (await import(moduleUrl)).default;

const apex = await worker.fetch(new Request("https://noetfield.com/about/?nf_rel_002=1"), {});
if (apex.status !== 308) throw new Error(`apex status ${apex.status}`);
if (apex.headers.get("location") !== "https://www.noetfield.com/about/?nf_rel_002=1") {
  throw new Error(`apex location ${apex.headers.get("location")}`);
}

if (!wrangler.includes('pattern = "status.noetfield.com/*"')) {
  throw new Error("missing status worker route");
}
if (!wrangler.includes('STATUS_HOST = "status.noetfield.com"')) {
  throw new Error("missing status host binding");
}
const status = await worker.fetch(
  new Request("https://status.noetfield.com/?incident=1"),
  {},
);
if (status.status !== 308) throw new Error(`status subdomain status ${status.status}`);
if (status.headers.get("location") !== "https://www.noetfield.com/status/?incident=1") {
  throw new Error(`status subdomain location ${status.headers.get("location")}`);
}

const originalFetch = globalThis.fetch;
let fetchedUrl = "";
globalThis.fetch = async (request) => {
  fetchedUrl = String(request);
  return new Response("origin", { status: 200 });
};
try {
  const response = await worker.fetch(
    new Request("https://www.noetfield.com/proof/?nf_rel_002=1"),
    { ORIGIN: "https://noetfield-www.pages.dev" },
  );
  if (response.status !== 200) throw new Error(`proxy status ${response.status}`);
  if (fetchedUrl !== "https://noetfield-www.pages.dev/proof/?nf_rel_002=1") {
    throw new Error(`proxy target ${fetchedUrl}`);
  }
  if (response.headers.get("x-noetfield-proxy") !== "cf-www-proxy") {
    throw new Error("missing proxy identity header");
  }
} finally {
  globalThis.fetch = originalFetch;
}

console.log("test-cf-www-proxy: PASS");
