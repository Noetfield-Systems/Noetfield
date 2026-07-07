/** Detect probe/E2E test intakes — never treat as customer leads. */

const TEST_FORM_IDS = new Set(["nf_intake_e2e", "nf_probe_cron"]);
const TEST_TOPICS = new Set(["e2e", "probe"]);
const TEST_EMAILS = new Set(["e2e@noetfield.com", "probe@noetfield.com"]);

function meta(body) {
  return body && typeof body.metadata === "object" && body.metadata ? body.metadata : {};
}

function isTestIntake(body) {
  if (!body || typeof body !== "object") return false;
  const m = meta(body);
  if (m.intake_kind === "test") return true;
  const formId = String(m.form_id || "").toLowerCase();
  if (TEST_FORM_IDS.has(formId)) return true;
  const topic = String(m.topic || "").toLowerCase();
  if (TEST_TOPICS.has(topic)) return true;
  const email = String(body.contact_email || "").trim().toLowerCase();
  if (TEST_EMAILS.has(email)) return true;
  const rid = String(body.request_id || "").toUpperCase();
  if (/^RID-(E2E|PROBE)-/.test(rid)) return true;
  return false;
}

function testPipelineLabel(body) {
  const m = meta(body);
  if (m.pipeline) return String(m.pipeline);
  const formId = String(m.form_id || "").toLowerCase();
  if (formId === "nf_probe_cron") return "probe_cron:intake_e2e";
  if (formId === "nf_intake_e2e") return "nf_intake_e2e:deploy_verify";
  if (m.topic === "probe") return "probe:intake";
  if (m.topic === "e2e") return "e2e:intake";
  return "test:intake";
}

function ensureTestMetadata(body) {
  if (!isTestIntake(body)) return body;
  const m = { ...meta(body), intake_kind: "test" };
  if (!m.pipeline) m.pipeline = testPipelineLabel(body);
  return { ...body, metadata: m };
}

module.exports = {
  isTestIntake,
  testPipelineLabel,
  ensureTestMetadata,
};
