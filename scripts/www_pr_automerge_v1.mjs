#!/usr/bin/env node
/**
 * Queue GitHub auto-merge on green Noetfield PRs.
 * Never squash-merges without --auto. The GitHub merge queue is the merger.
 */
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const BLOCKED_EXACT = new Set(["main", "master"]);
const BLOCKED_PREFIXES = ["factory/", "dependabot/"];
const ACTIVE_PREFIXES = ["repair/", "feat/", "fix/"];
const MUST_BE_GREEN_IF_PRESENT = [
  "repo-validate",
  "www-health",
  "backend-runtime",
  "platform-deploy-smoke",
];

export function isAutomergeLane(branch) {
  const name = String(branch || "").trim();
  if (!name) return false;
  if (BLOCKED_EXACT.has(name)) return false;
  if (BLOCKED_PREFIXES.some((prefix) => name.startsWith(prefix))) return false;
  return ACTIVE_PREFIXES.some((prefix) => name.startsWith(prefix));
}

export function rollupReady(checks) {
  const rows = Array.isArray(checks) ? checks : [];
  const named = new Map();
  for (const row of rows) {
    const name = String(row?.name || "");
    if (!MUST_BE_GREEN_IF_PRESENT.includes(name)) continue;
    named.set(name, row);
  }
  if (!named.has("repo-validate")) return "missing";
  for (const row of named.values()) {
    const status = String(row.status || "");
    const conclusion = String(row.conclusion || "");
    if (status && status !== "COMPLETED") return "pending";
    if (["FAILURE", "CANCELLED", "TIMED_OUT", "STARTUP_FAILURE"].includes(conclusion)) {
      return "red";
    }
    if (conclusion !== "SUCCESS") return "pending";
  }
  return "green";
}

function gh(args) {
  return execFileSync("gh", args, { encoding: "utf8", env: process.env }).trim();
}

function ghJson(args) {
  const out = gh(args);
  return out ? JSON.parse(out) : null;
}

function isEligiblePr(pr) {
  const n = pr.number;
  const branch = pr.headRefName || "";
  if (pr.isDraft) {
    console.log(`SKIP_DRAFT pr=${n}`);
    return false;
  }
  if (/do not merge|\bdraft\b|\[wip\]/i.test(pr.title || "")) {
    console.log(`SKIP_TITLE_BLOCKED pr=${n}`);
    return false;
  }
  if (!isAutomergeLane(branch)) {
    console.log(`SKIP_LANE pr=${n} branch=${branch}`);
    return false;
  }
  return true;
}

function queueAutoMerge(pr) {
  const n = pr.number;
  const branch = pr.headRefName;
  const viewed = ghJson([
    "pr",
    "view",
    String(n),
    "--json",
    "mergeable,autoMergeRequest,statusCheckRollup",
  ]);
  if (!viewed) {
    console.log(`SKIP_VIEW pr=${n}`);
    return false;
  }
  if (viewed.mergeable === "CONFLICTING") {
    console.log(`SKIP_CONFLICT pr=${n} branch=${branch}`);
    return false;
  }
  if (viewed.autoMergeRequest) {
    console.log(`ALREADY_QUEUED pr=${n}`);
    return false;
  }
  const ready = rollupReady(viewed.statusCheckRollup);
  if (ready !== "green") {
    console.log(`SKIP_CHECKS ready=${ready} pr=${n} branch=${branch}`);
    return false;
  }
  gh(["pr", "merge", String(n), "--squash", "--auto"]);
  console.log(`QUEUED_GITHUB_AUTOMERGE pr=${n} branch=${branch}`);
  return true;
}

function main() {
  const all =
    ghJson([
      "pr",
      "list",
      "--state",
      "open",
      "--base",
      "main",
      "--json",
      "number,headRefName,isDraft,title",
    ]) ?? [];
  const prs = all.filter((pr) => isEligiblePr(pr));
  if (!prs.length) {
    console.log("NO_OPEN_AUTOMERGE_PRS");
    return;
  }
  let queued = 0;
  for (const pr of prs) {
    if (queueAutoMerge(pr)) queued += 1;
  }
  console.log(`WWW_PR_AUTOMERGE_DONE queued=${queued} scanned=${prs.length}`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main();
}
