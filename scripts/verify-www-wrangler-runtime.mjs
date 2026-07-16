#!/usr/bin/env node
/** Probe the exact static artifact and generated Functions through Wrangler Pages. */

import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const dist = path.join(root, "www-pages-dist");
const matrixPath = path.join(root, "reports/recovery/NF-REL-002-denylist-matrix.json");
const runtimeReportPath = path.join(
  root,
  "tmp/nf-rel-002/wrangler-runtime-probes.json",
);
const port = Number(process.env.NF_WRANGLER_TEST_PORT || "8797");
const base = `http://127.0.0.1:${port}`;
const runtimeTimeoutMs = Number(process.env.NF_WRANGLER_RUNTIME_TIMEOUT_MS || "120000");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(fs.existsSync(dist), "missing www-pages-dist; build the exact artifact first");
assert(fs.existsSync(matrixPath), "missing deny matrix; verify exact middleware first");

const matrix = JSON.parse(fs.readFileSync(matrixPath, "utf8"));
const wranglerArgs = [
  "--yes",
  "wrangler@4",
  "pages",
  "dev",
  "www-pages-dist",
  "--ip",
  "127.0.0.1",
  "--port",
  String(port),
  "--compatibility-date",
  "2025-04-01",
  "--compatibility-flags",
  "nodejs_compat",
];

const child = spawn("npx", wranglerArgs, {
  cwd: root,
  env: { ...process.env, NO_COLOR: "1" },
  // npx may retain Wrangler as a child process on Linux. A dedicated process
  // group lets the verifier stop the complete runtime tree deterministically.
  detached: process.platform !== "win32",
  stdio: ["ignore", "pipe", "pipe"],
});
let logs = "";
child.stdout.on("data", (chunk) => {
  logs += String(chunk);
});
child.stderr.on("data", (chunk) => {
  logs += String(chunk);
});

async function waitUntilReady() {
  const deadline = Date.now() + 45000;
  while (Date.now() < deadline) {
    if (child.exitCode !== null) {
      throw new Error(`Wrangler exited before readiness (code=${child.exitCode})\n${logs}`);
    }
    try {
      const response = await fetch(`${base}/api/health`, {
        headers: { Host: "www.noetfield.com" },
        signal: AbortSignal.timeout(2000),
      });
      if (response.status === 200) return;
    } catch (_) {
      // Wrangler is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error(`Wrangler did not become ready\n${logs}`);
}

async function probe(pathname, expectedStatus, rule) {
  const join = pathname.includes("?") ? "&" : "?";
  const response = await fetch(`${base}${pathname}${join}nf_rel_002=wrangler`, {
    redirect: "manual",
    headers: { Host: "www.noetfield.com" },
    signal: AbortSignal.timeout(5000),
  });
  return {
    requested_path: pathname,
    expected_status: expectedStatus,
    actual_status: response.status,
    rule,
    result: response.status === expectedStatus ? "PASS" : "FAIL",
  };
}

const rows = [];
let failure = null;
let runtimeTimer;

function childIsRunning() {
  return child.exitCode === null && child.signalCode === null;
}

function signalRuntimeTree(signal) {
  if (!childIsRunning()) return;
  try {
    if (process.platform !== "win32" && child.pid) {
      process.kill(-child.pid, signal);
    } else {
      child.kill(signal);
    }
  } catch (error) {
    if (error?.code !== "ESRCH") throw error;
  }
}

async function stopRuntimeTree() {
  signalRuntimeTree("SIGTERM");
  await Promise.race([
    new Promise((resolve) => {
      if (!childIsRunning()) return resolve();
      child.once("exit", resolve);
    }),
    new Promise((resolve) => setTimeout(resolve, 3000)),
  ]);
  if (childIsRunning()) {
    signalRuntimeTree("SIGKILL");
    await Promise.race([
      new Promise((resolve) => child.once("exit", resolve)),
      new Promise((resolve) => setTimeout(resolve, 1000)),
    ]);
  }
  child.stdout.destroy();
  child.stderr.destroy();
}

async function runProbes() {
  await waitUntilReady();
  for (const row of matrix.rows) {
    rows.push(
      await probe(
        row.requested_protected_path,
        row.expected_status,
        row.middleware_rule_responsible,
      ),
    );
  }
  for (const pathname of [
    "/",
    "/about/",
    "/investors/",
    "/proof/",
    "/enterprise/",
    "/motors/",
    "/noetfield-favicon-512.png",
  ]) {
    rows.push(await probe(pathname, 200, "REQUIRED_PUBLIC_ARTIFACT"));
  }
  rows.push(await probe("/invest/", 302, "INVEST_ACCESS_CONTROL"));
  rows.push(await probe("/api/auth/invest-config", 200, "INVEST_RUNTIME_CONFIG"));
}

try {
  const deadline = new Promise((_, reject) => {
    runtimeTimer = setTimeout(
      () => reject(new Error(`Wrangler probe deadline exceeded (${runtimeTimeoutMs}ms)`)),
      runtimeTimeoutMs,
    );
  });
  await Promise.race([runProbes(), deadline]);
} catch (error) {
  failure = String(error?.stack || error);
} finally {
  clearTimeout(runtimeTimer);
  await stopRuntimeTree();
}

const failed = rows.filter((row) => row.result === "FAIL");
const report = {
  schema: "nf-rel-002-wrangler-runtime-probes-v1",
  runtime: "wrangler@4 pages dev",
  exact_artifact_manifest_sha256: matrix.exact_artifact_manifest_sha256,
  unexpected_artifact_probe_count: matrix.unexpected_artifact_paths.length,
  summary: {
    total: rows.length,
    passed: rows.length - failed.length,
    failed: failed.length + (failure ? 1 : 0),
  },
  startup_failure: failure,
  rows,
};
fs.writeFileSync(runtimeReportPath, `${JSON.stringify(report, null, 2)}\n`);

if (failure || failed.length) {
  if (failure) console.error(failure);
  for (const row of failed) {
    console.error(
      `FAIL ${row.requested_path}: expected=${row.expected_status} actual=${row.actual_status}`,
    );
  }
  process.exit(1);
}

console.log(
  `verify-www-wrangler-runtime: PASS (${rows.length}/${rows.length}, unexpected artifact probes=${matrix.unexpected_artifact_paths.length})`,
);
console.log(`runtime matrix: ${path.relative(root, runtimeReportPath)}`);
