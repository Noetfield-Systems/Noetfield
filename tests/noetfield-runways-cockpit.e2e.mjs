import assert from "node:assert/strict";
import { createHash, createHmac } from "node:crypto";
import { createRequire } from "node:module";
import { createServer } from "node:http";
import { existsSync, readFileSync } from "node:fs";
import { extname, join } from "node:path";
import { chromium } from "playwright";

const require = createRequire(import.meta.url);
const handler = require("../api/runways/demo.js");
const root = process.cwd();
const liveBearer = "runways-e2e-bearer-credential";
const hmacSecret = "runways-e2e-hmac-secret-credential-0001";
const gatewayRequests = [];

function listen(server, port) {
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, "localhost", resolve);
  });
}

function close(server) {
  return new Promise((resolve) => server.close(resolve));
}

function responseFor(path, method) {
  const jobId = `rj_${"2".repeat(32)}`;
  if (path === "/v1/jobs/blueprint") return { blueprint_id: `bp_${"1".repeat(32)}`, status: "READY_FOR_APPROVAL" };
  if (path.endsWith("/approve")) return { job_id: jobId, status: "QUEUED" };
  if (path.endsWith("/events")) return { job_id: jobId, events: [{ event_type: "JOB_TERMINAL" }] };
  if (path.endsWith("/result")) return { job_id: jobId, status: "succeeded", artifacts: [{ artifact_id: "brief-pdf" }] };
  if (path.endsWith("/download")) return { job_id: jobId, artifact_id: "brief-pdf", download_path: `${path}?artifact_id=brief-pdf&token=signed` };
  if (path.endsWith("/acceptance") && method === "POST") return { job_id: jobId, acceptance: { state: "accepted" } };
  return { error: "stub_not_found" };
}

const gateway = createServer(async (request, response) => {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  const body = Buffer.concat(chunks);
  const timestamp = String(request.headers["x-noetfield-timestamp"] || "");
  const nonce = String(request.headers["x-noetfield-nonce"] || "");
  const authorization = String(request.headers.authorization || "");
  const match = /^NOETFIELD-HMAC ([A-Za-z0-9._-]+):([0-9a-f]{64})$/.exec(authorization);
  const pathname = new URL(request.url || "/", "http://gateway.local").pathname;
  const canonical = `${request.method}\n${pathname}\n${timestamp}\n${nonce}\n${createHash("sha256").update(body).digest("hex")}`;
  const expected = createHmac("sha256", hmacSecret).update(canonical).digest("hex");
  const authorized = match?.[1] === "noetfield-e2e" && match?.[2] === expected;
  gatewayRequests.push({ method: request.method, pathname, authorized, query: new URL(request.url || "/", "http://gateway.local").search });
  response.setHeader("content-type", "application/json");
  response.statusCode = authorized ? 200 : 401;
  response.end(JSON.stringify(authorized ? responseFor(pathname, request.method || "GET") : { error: "bad_hmac" }));
});

function invoke(body, authorization = "") {
  return new Promise((resolve, reject) => {
    const headers = {};
    const res = {
      statusCode: 200,
      setHeader(name, value) { headers[name] = value; return this; },
      status(code) { this.statusCode = code; return this; },
      json(value) { resolve({ status: this.statusCode, headers, body: value }); return this; },
      end(value) { resolve({ status: this.statusCode, headers, body: value }); return this; },
    };
    Promise.resolve(handler({ method: "POST", headers: { authorization }, body }, res)).catch(reject);
  });
}

function contentType(path) {
  return ({ ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".png": "image/png" })[extname(path)] || "application/octet-stream";
}

const site = createServer(async (request, response) => {
  const url = new URL(request.url || "/", "http://site.local");
  if (request.method === "POST" && url.pathname === "/api/runways/demo") {
    const chunks = [];
    for await (const chunk of request) chunks.push(chunk);
    const value = JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}");
    const result = await invoke(value, String(request.headers.authorization || ""));
    response.writeHead(result.status, { "content-type": "application/json", ...result.headers });
    response.end(JSON.stringify(result.body));
    return;
  }
  const relative = url.pathname === "/runways/" ? "runways/index.html" : url.pathname.replace(/^\//, "");
  const allowed = relative === "runways/index.html" || relative.startsWith("assets/") || relative === "noetfield-favicon-512.png";
  const file = join(root, relative);
  if (!allowed || !existsSync(file)) {
    response.writeHead(404);
    response.end("not found");
    return;
  }
  response.writeHead(200, { "content-type": contentType(file), "cache-control": "no-store" });
  response.end(readFileSync(file));
});

await listen(gateway, 4421);
process.env.RUNWAY_GATEWAY_BASE_URL = "http://localhost:4421";
process.env.RUNWAY_GATEWAY_KEY_ID = "noetfield-e2e";
process.env.RUNWAY_GATEWAY_HMAC_SECRET = hmacSecret;
process.env.RUNWAYS_DEMO_BEARER = liveBearer;

try {
  const denied = await invoke({ mode: "live", action: "blueprint", intake: {} });
  assert.equal(denied.status, 401);
  const blueprintId = `bp_${"1".repeat(32)}`;
  const jobId = `rj_${"2".repeat(32)}`;
  const auth = `Bearer ${liveBearer}`;
  const liveCalls = [
    { action: "blueprint", intake: { schema: "noetfield.job-intake.v0.1" } },
    { action: "approve", blueprint_id: blueprintId, intake: { schema: "noetfield.job-intake.v0.1" }, expires_at: "2030-01-01T00:00:00.000Z", approval_token: "a".repeat(64) },
    { action: "events", job_id: jobId },
    { action: "result", job_id: jobId },
    { action: "download", job_id: jobId, artifact_id: "brief-pdf" },
    { action: "acceptance", job_id: jobId, state: "accepted", reason: "qualified" },
  ];
  for (const body of liveCalls) {
    const result = await invoke({ mode: "live", ...body }, auth);
    assert.equal(result.status, 200, JSON.stringify(result.body));
  }
  assert.equal(gatewayRequests.length, liveCalls.length);
  assert(gatewayRequests.every((row) => row.authorized));
  assert(gatewayRequests.some((row) => row.pathname.endsWith("/download") && row.query.includes("artifact_id=brief-pdf")));

  await listen(site, 4422);
  const systemChrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
  const executablePath = process.env.NOETFIELD_E2E_CHROME_EXECUTABLE ?? (existsSync(systemChrome) ? systemChrome : undefined);
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const page = await browser.newPage();
    await page.route("https://fonts.googleapis.com/**", (route) => route.abort());
    await page.route("https://fonts.gstatic.com/**", (route) => route.abort());
    await page.goto("http://localhost:4422/runways/", { waitUntil: "domcontentloaded" });
    await page.getByRole("button", { name: "Generate blueprint" }).click();
    await page.getByText("Ready for approval").waitFor();
    await page.getByRole("button", { name: "Approve fixture build" }).click();
    await page.getByText("Fixture event ledger").waitFor();
    await page.getByRole("button", { name: "Inspect delivery receipt" }).click();
    await page.getByText("Qualified fixture").waitFor();
    await page.getByText("fixture-decision-brief.docx").waitFor();
    await page.getByText("fixture-decision-brief.pdf").waitFor();
  } finally {
    await browser.close();
  }
  console.log(JSON.stringify({
    verdict: "PASS",
    fixture_browser_phases: 4,
    live_proxy_calls: gatewayRequests.length,
    live_proxy_hmac_verified: true,
    public_mode: "SAFE_FIXTURE",
  }));
} finally {
  if (site.listening) await close(site);
  await close(gateway);
}
