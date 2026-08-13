import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { isAutomergeLane, rollupReady } from "./www_pr_automerge_v1.mjs";

const root = dirname(fileURLToPath(import.meta.url));
const workflow = readFileSync(
  join(root, "../.github/workflows/www-pr-automerge.yml"),
  "utf8",
);
const script = readFileSync(join(root, "www_pr_automerge_v1.mjs"), "utf8");

test("lane allows feat fix repair and blocks main and bots", () => {
  assert.equal(isAutomergeLane("feat/www-pr-github-automerge"), true);
  assert.equal(isAutomergeLane("fix/www-health"), true);
  assert.equal(isAutomergeLane("repair/ci"), true);
  assert.equal(isAutomergeLane("main"), false);
  assert.equal(isAutomergeLane("chore/docs"), false);
  assert.equal(isAutomergeLane("dependabot/npm_and_yarn/foo"), false);
});

test("rollup waits for required checks and ignores missing optional ones", () => {
  assert.equal(rollupReady([]), "missing");
  assert.equal(
    rollupReady([{ name: "repo-validate", status: "COMPLETED", conclusion: "SUCCESS" }]),
    "green",
  );
  assert.equal(
    rollupReady([
      { name: "repo-validate", status: "COMPLETED", conclusion: "SUCCESS" },
      { name: "www-health", status: "IN_PROGRESS", conclusion: null },
    ]),
    "pending",
  );
  assert.equal(
    rollupReady([
      { name: "repo-validate", status: "COMPLETED", conclusion: "SUCCESS" },
      { name: "www-health", status: "COMPLETED", conclusion: "FAILURE" },
    ]),
    "red",
  );
});

test("workflow and script never squash-merge without GitHub --auto", () => {
  assert.match(script, /"--squash", "--auto"/);
  assert.equal((script.match(/"merge"/g) || []).length, 1);
  assert.doesNotMatch(script, /--delete-branch/);
  assert.doesNotMatch(workflow, /gh pr merge/);
});
