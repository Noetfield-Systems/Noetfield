#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const denylistPath = path.join(root, "governance/PUBLIC_OUTPUT_DENYLIST.json");
const routesPath = path.join(root, "governance/www-pages-routes.json");
const middlewarePath = path.join(root, "functions/_middleware.js");
const reportPath = path.join(root, "reports/recovery/NF-REL-002-denylist-matrix.json");

const denylist = JSON.parse(fs.readFileSync(denylistPath, "utf8"));
const routes = JSON.parse(fs.readFileSync(routesPath, "utf8"));
const source = fs.readFileSync(middlewarePath, "utf8");
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString("base64")}`;
const { onRequest } = await import(moduleUrl);

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
        fetch: async () => new Response("not found", {
          status: 200,
          headers: { "content-type": "text/html; charset=utf-8" },
        }),
      },
    },
    next: async () => new Response(
      item.pathname === "/services/" ? "not found" : "public asset",
      { status: item.pathname === "/services/" ? 404 : 200 },
    ),
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
