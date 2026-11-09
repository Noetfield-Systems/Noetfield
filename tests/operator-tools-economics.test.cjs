// Regression tests for public operator-tool economics.
// Run: node tests/operator-tools-economics.test.cjs
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "../assets/noetfield-tools.js"), "utf8");
const sandbox = {
  window: {},
  document: { readyState: "loading", addEventListener() {} },
  Intl, Number, Math, String, Object, Array, JSON,
};
vm.runInNewContext(source, sandbox);
const compute = sandbox.window.NF_TOOLS_MATH.compute;
function form(values) {
  return { elements: Object.fromEntries(Object.entries(values).map(([k, v]) =>
    [k, { value: String(v), checked: Boolean(v) }])) };
}

const attributableButMostlyUnexplained = compute("ai-spend", form({
  monthly: 4000, attributed: 20, teams: 3, named: "yes",
}));
assert.equal(attributableButMostlyUnexplained.kind, "act");
assert.match(attributableButMostlyUnexplained.headline, /20%/);
assert.match(attributableButMostlyUnexplained.body, /not proven waste/);

const mostlyAttributed = compute("ai-spend", form({
  monthly: 4000, attributed: 95, teams: 3, named: "yes",
}));
assert.equal(mostlyAttributed.kind, "leave");

const smallSingleTeam = compute("ai-spend", form({
  monthly: 800, attributed: 0, teams: 1, named: "no",
}));
assert.equal(smallSingleTeam.kind, "leave");

const largeCopilotUse = compute("copilot-seats", form({
  licensed: 200, used: 150, hours: 6, pay: "hourly", rate: 70, seat: 360,
}));
assert.equal(largeCopilotUse.kind, "look");
assert.equal(largeCopilotUse.cta, "acceptance");
assert.match(largeCopilotUse.amount, /estimated in-tool labor/);
assert.doesNotMatch(largeCopilotUse.amount, /ungoverned|waste/);
assert.match(largeCopilotUse.body, /cannot tell whether outputs were reviewed/);

const lowUnusedSeats = compute("copilot-seats", form({
  licensed: 12, used: 11, hours: 2, pay: "hourly", rate: 45, seat: 360,
}));
assert.equal(lowUnusedSeats.kind, "leave");
assert.match(lowUnusedSeats.extra, /not additional spend or savings/);

const acceptance = compute("who-accepted", form({
  deliverables: 20, signed: 0, minutes: 15,
  pay: "hourly", rate: 50, replay: "no",
}));
assert.match(acceptance.amount, /modeled unsigned-item rework/);
assert.match(acceptance.extra, /assumes every unsigned item/);

assert.doesNotMatch(source, /window\.parent\.postMessage/);
console.log("PASS operator-tools-economics: 7 trust/attribution assertions");
