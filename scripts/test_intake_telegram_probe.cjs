#!/usr/bin/env node
/** Assert probe intakes skip lead Telegram; customer leads use lead format. */

const assert = require("node:assert/strict");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const { isTestIntake } = require(path.join(root, "api/_lib/intake-test"));
const {
  formatIntakeTelegramText,
  sendIntakeTelegram,
  telegramPathOk,
  probeTelegramSkipped,
  wasRequestNotified,
  markRequestNotified,
} = require(path.join(root, "api/_lib/intake-telegram"));

const probeBody = {
  organization: "NF E2E Deploy Verify",
  contact_name: "NF E2E Bot",
  contact_email: "e2e@noetfield.com",
  message: "Automated intake E2E health probe",
  request_id: "RID-E2E-TEST-PROBE",
  metadata: { form_id: "nf_intake_e2e", topic: "e2e", intake_kind: "test" },
};

const leadBody = {
  organization: "Acme Corp",
  contact_name: "Buyer",
  contact_email: "buyer@example.com",
  message: "Interested in Trust Brief",
  request_id: "RID-2026-0613-BUYER",
  metadata: { form_id: "contact", topic: "trust-brief" },
};

assert.equal(isTestIntake(probeBody), true, "probe body detected");
assert.equal(isTestIntake(leadBody), false, "lead body not probe");

const leadText = formatIntakeTelegramText(leadBody, "INT-LEAD1");
assert.match(leadText, /^name: Buyer/m, "lead telegram uses lead format");
assert.doesNotMatch(leadText, /TEST/, "lead telegram is not health receipt");

(async function main() {
  const prevToken = process.env.TELEGRAM_NOETFIELD_OPS_BOT_TOKEN;
  process.env.TELEGRAM_NOETFIELD_OPS_BOT_TOKEN = "test-token";
  process.env.TELEGRAM_OPS_CHAT_ID = "12345";

  const probeResult = await sendIntakeTelegram(probeBody, "INT-PROBE1", {});
  assert.equal(probeResult.telegram_skipped_probe, true, "probe skips lead telegram");
  assert.equal(probeResult.telegram_mode, "receipt_only");
  assert.equal(telegramPathOk(probeResult), true, "probe path ok without send");
  assert.equal(probeTelegramSkipped(probeResult), true);

  const dedupeResult = await sendIntakeTelegram(probeBody, "INT-PROBE1", { deduped: true });
  assert.equal(dedupeResult.telegram_skipped_probe, true, "deduped probe still skipped");
  assert.match(dedupeResult.reason || "", /dedup/, "dedupe reason set");

  markRequestNotified("RID-E2E-DEDUP-TEST");
  assert.equal(wasRequestNotified("rid-e2e-dedup-test"), true, "request_id dedup case-insensitive");

  process.env.TELEGRAM_NOETFIELD_OPS_BOT_TOKEN = prevToken || "";
  console.log("test_intake_telegram_probe: PASS");
})().catch((err) => {
  console.error("test_intake_telegram_probe: FAIL", err.message || err);
  process.exit(1);
});
