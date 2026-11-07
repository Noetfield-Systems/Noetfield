const test = require("node:test");
const assert = require("node:assert/strict");
const {
  intakeLabel,
  intakeSubject,
  opsBodyText,
} = require("../../api/_lib/intake-email");
const { isTestIntake } = require("../../api/_lib/intake-test");

const body = {
  organization: "Example Systems Ltd.",
  contact_name: "Buyer",
  contact_email: "buyer@example.com",
  message: "API latency has risen and worker operations are multiplying.",
  request_id: "RID-COI-REGRESSION-001",
  sku: "intelligence-diagnostic",
  vector: "intelligence-diagnostic",
  source: "web",
  metadata: {
    form_id: "coiIntakeForm",
    topic: "continuous-optimization-intelligence",
    engagement: "Diagnostic Sprint — CAD $2,500–$5,000",
    target_context: "Cloud infrastructure and runtime",
    page: "/intelligence/continuous-optimization/",
    async: true,
  },
};

test("optimization lead is clearly classified for operations", () => {
  assert.equal(intakeLabel(body), "Continuous Optimization Intelligence enquiry");
  assert.match(intakeSubject(body, "INT-ABC123"), /Continuous Optimization Intelligence enquiry/);
  assert.match(intakeSubject(body, "INT-ABC123"), /RID-COI-REGRESSION-001/);
});

test("operations notification includes engagement and system context", () => {
  const text = opsBodyText(body, "INT-ABC123");
  assert.match(text, /Diagnostic Sprint/);
  assert.match(text, /Cloud infrastructure and runtime/);
  assert.match(text, /continuous-optimization-intelligence/);
  assert.match(text, /API latency has risen/);
});

test("normal optimization leads are not classified as automated test probes", () => {
  assert.equal(isTestIntake(body), false);
});
