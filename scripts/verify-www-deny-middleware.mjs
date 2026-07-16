#!/usr/bin/env node
import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const denylistPath = path.join(root, "governance/PUBLIC_OUTPUT_DENYLIST.json");
const routesPath = path.join(root, "governance/www-pages-routes.json");
const middlewarePath = path.join(root, "functions/_middleware.js");
const artifactAllowlistPath = path.join(root, "governance/www-public-artifact-v1.json");
const artifactManifestPath = path.join(
  root,
  "tmp/nf-rel-002/public-artifact-manifest.json",
);
const distPath = path.join(root, "www-pages-dist");
const reportPath = path.join(root, "reports/recovery/NF-REL-002-denylist-matrix.json");

const denylist = JSON.parse(fs.readFileSync(denylistPath, "utf8"));
const routes = JSON.parse(fs.readFileSync(routesPath, "utf8"));
const artifactAllowlist = JSON.parse(fs.readFileSync(artifactAllowlistPath, "utf8"));
const artifactManifest = JSON.parse(fs.readFileSync(artifactManifestPath, "utf8"));
const source = fs.readFileSync(middlewarePath, "utf8");
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString("base64")}`;
const { onRequest } = await import(moduleUrl);

function sha256File(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function artifactFiles() {
  const rows = [];
  function walk(directory, prefix = "") {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
      if (entry.isDirectory()) walk(path.join(directory, entry.name), rel);
      else if (entry.isFile()) rows.push(rel);
    }
  }
  walk(distPath);
  return rows.sort();
}

function artifactTarget(pathname) {
  const decoded = decodeURIComponent(pathname);
  if (decoded === "/") return path.join(distPath, "index.html");
  const rel = decoded.replace(/^\/+/, "");
  if (decoded.endsWith("/")) return path.join(distPath, rel, "index.html");
  const direct = path.join(distPath, rel);
  if (fs.existsSync(direct) && fs.statSync(direct).isFile()) return direct;
  return path.join(distPath, rel, "index.html");
}

async function artifactFetch(request) {
  const pathname = new URL(request.url || request).pathname;
  const target = artifactTarget(pathname);
  if (!target.startsWith(`${distPath}${path.sep}`) || !fs.existsSync(target)) {
    return new Response("not found", { status: 404 });
  }
  return new Response(fs.readFileSync(target), {
    status: 200,
    headers: {
      "content-type": target.endsWith(".html")
        ? "text/html; charset=utf-8"
        : "application/octet-stream",
    },
  });
}

function materializeRoute(sourcePath) {
  if (sourcePath.endsWith("/:path*")) {
    return `${sourcePath.slice(0, -7)}/__nf_rel_002_probe__/artifact.txt`;
  }
  return sourcePath;
}

function middlewareRule(pathname) {
  if (denylist.exact_paths.includes(pathname)) return `EXACT:${pathname}`;
  const prefixes = denylist.prefix_paths
    .filter((prefix) => pathname === prefix.slice(0, -1) || pathname.startsWith(prefix))
    .sort((a, b) => b.length - a.length);
  if (prefixes.length) return `PREFIX:${prefixes[0]}`;
  if (pathname === "/governance/") return "PUBLIC_EXCEPTION:/governance/";
  if (pathname === "/services/") return "PASSTHROUGH;STATIC_ARTIFACT_ABSENCE:/services/";
  if (!fs.existsSync(artifactTarget(pathname))) {
    return `STATIC_ARTIFACT_ABSENCE:${pathname}`;
  }
  return "NONE";
}

const requested = new Map();
function add(pathname, expectedStatus, origin) {
  const existing = requested.get(pathname);
  if (!existing) {
    requested.set(pathname, { pathname, expectedStatus, origins: [origin] });
    return;
  }
  if (existing.expectedStatus !== expectedStatus) {
    throw new Error(`conflicting expected status for ${pathname}`);
  }
  if (!existing.origins.includes(origin)) existing.origins.push(origin);
}

for (const route of routes.redirects || []) {
  if (Number(route.statusCode) === 404) {
    add(materializeRoute(String(route.source)), 404, `former_redirect:${route.source}`);
  }
}
for (const exact of denylist.exact_paths || []) {
  add(exact, 404, `denylist_exact:${exact}`);
}
for (const prefix of denylist.prefix_paths || []) {
  add(prefix, 404, `denylist_prefix_root:${prefix}`);
  add(`${prefix}__nf_rel_002_probe__/artifact.txt`, 404, `denylist_prefix_nested:${prefix}`);
}

const mandatoryAbsenceProbes = [
  "/AGENTS.md",
  "/README.md",
  "/repo-policy.json",
  "/Makefile",
  "/PRODUCT_BRIEF.md",
  "/FOUNDER_CANON.md",
  "/.claude/launch.json",
  "/.cursor/README.md",
  "/.agents/skills/cloudflare/SKILL.md",
  "/docs/README.md",
  "/docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md",
  "/scripts/build-www-pages-dist.sh",
  "/tests/unit/test_investor_diligence_lane.py",
  "/reports/recovery/NF-REL-002.md",
  "/packages/schemas/tle-v1.schema.json",
  "/config/gate-ai-factory-design.json",
  "/assets/noetfield-platform-auth-config-v1.json",
  "/api/auth/invest-session.js",
  "/functions/invest/[[path]].js",
  "/docs/README.md.bak.1783081948",
  "/.DS_Store",
  "/.env",
  "/archive.zip",
  "/temporary.tmp",
];
for (const pathname of mandatoryAbsenceProbes) {
  add(pathname, 404, `mandatory_artifact_absence:${pathname}`);
}

const actualArtifactFiles = artifactFiles();
const expectedArtifactFiles = [...artifactAllowlist.static_files].sort();
const unexpectedArtifactFiles = actualArtifactFiles.filter(
  (rel) => !expectedArtifactFiles.includes(rel),
);
for (const rel of unexpectedArtifactFiles) {
  add(`/${rel}`, 404, `unexpected_artifact_path:${rel}`);
}

// The public governance product hub is intentional; sensitive governance files
// and internal subtrees remain exact/prefix denied above.
add("/governance/", 200, "intentional_public_governance_hub");
// There is no public directory index at /services/. Named public product pages
// remain available while all former internal service prefixes stay denied above.
add("/services/", 404, "no_public_services_directory_index");

const rows = [];
for (const item of [...requested.values()].sort((a, b) => a.pathname.localeCompare(b.pathname))) {
  const response = await onRequest({
    request: new Request(`https://www.noetfield.com${item.pathname}?nf_rel_002=deny`),
    env: {
      ASSETS: {
        fetch: artifactFetch,
      },
    },
    next: async (request) => artifactFetch(request || new Request(
      `https://www.noetfield.com${item.pathname}?nf_rel_002=deny`,
    )),
  });
  const rule = middlewareRule(item.pathname);
  const passed = response.status === item.expectedStatus &&
    (item.expectedStatus !== 404 || rule !== "NONE");
  rows.push({
    requested_protected_path: item.pathname,
    expected_status: item.expectedStatus,
    actual_status: response.status,
    middleware_rule_responsible: rule,
    source_coverage: item.origins.sort(),
    result: passed ? "PASS" : "FAIL",
  });
}

const failed = rows.filter((row) => row.result === "FAIL");
const report = {
  schema: "nf-rel-002-pages-deny-middleware-matrix-v1",
  baseline_sha: "e83aff92764c916362767f1dcb616bc3ece9535f",
  generated_middleware: "functions/_middleware.js",
  generated_middleware_sha256: sha256File(middlewarePath),
  exact_artifact_manifest: "tmp/nf-rel-002/public-artifact-manifest.json",
  exact_artifact_manifest_sha256: sha256File(artifactManifestPath),
  exact_artifact_manifest_schema: artifactManifest.schema,
  artifact_static_file_count: actualArtifactFiles.length,
  unexpected_artifact_paths: unexpectedArtifactFiles,
  query_string_tested: "?nf_rel_002=deny",
  public_exceptions: [
    {
      path: "/governance/",
      reason: "Intentional public governance product hub; sensitive governance files and internal subtrees remain denied.",
    },
  ],
  artifact_absence_checks: [
    {
      path: "/services/",
      reason: "No directory index is shipped; named public service product routes remain preserved.",
    },
  ],
  summary: {
    total: rows.length,
    passed: rows.length - failed.length,
    failed: failed.length,
  },
  rows,
};

fs.mkdirSync(path.dirname(reportPath), { recursive: true });
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);

if (failed.length) {
  for (const row of failed) {
    console.error(
      `FAIL ${row.requested_protected_path}: expected=${row.expected_status} actual=${row.actual_status} rule=${row.middleware_rule_responsible}`,
    );
  }
  process.exit(1);
}

console.log(`verify-www-deny-middleware: PASS (${rows.length}/${rows.length})`);
console.log(`matrix: ${path.relative(root, reportPath)}`);
