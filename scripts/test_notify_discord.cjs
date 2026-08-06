#!/usr/bin/env node
/** Assert the Discord ops sink validates its webhook, dedupes, mutes mentions, and never throws. */

const assert = require("node:assert/strict");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const {
  discordConfigured,
  isValidWebhookUrl,
  formatIntakeEmbed,
  sendIntakeDiscord,
  discordPathOk,
} = require(path.join(root, "api/_lib/notify-discord"));

const WEBHOOK = "https://discord.com/api/webhooks/123/abc";

const leadBody = {
  organization: "Acme Corp",
  contact_name: "Buyer",
  contact_email: "buyer@example.com",
  message: "Interested in Trust Brief",
  request_id: "RID-2026-0613-BUYER",
  metadata: { form_id: "contact", topic: "trust-brief" },
};

const probeBody = {
  organization: "NF E2E Deploy Verify",
  contact_name: "NF E2E Bot",
  message: "Automated intake E2E health probe",
  request_id: "RID-E2E-TEST-PROBE",
  metadata: { form_id: "nf_intake_e2e", topic: "e2e", intake_kind: "test" },
};

// Webhook URL validation — a mistyped env var must never become an outbound POST elsewhere.
assert.equal(isValidWebhookUrl(WEBHOOK), true, "canonical webhook accepted");
assert.equal(isValidWebhookUrl("https://discordapp.com/api/webhooks/1/x"), true, "legacy host accepted");
assert.equal(isValidWebhookUrl("http://discord.com/api/webhooks/1/x"), false, "http rejected");
assert.equal(isValidWebhookUrl("https://evil.example.com/api/webhooks/1/x"), false, "foreign host rejected");
assert.equal(isValidWebhookUrl("https://discord.com/api/other/1/x"), false, "non-webhook path rejected");
assert.equal(isValidWebhookUrl("not a url"), false, "garbage rejected");
assert.equal(isValidWebhookUrl(""), false, "empty rejected");

const leadEmbed = formatIntakeEmbed(leadBody, "INT-LEAD1");
assert.equal(leadEmbed.title, "New intake", "lead embed titled as lead");
assert.equal(
  leadEmbed.fields.find(function (f) {
    return f.name === "Company";
  }).value,
  "Acme Corp",
);
const probeEmbed = formatIntakeEmbed(probeBody, "INT-PROBE1");
assert.match(probeEmbed.title, /^Test intake/, "probe embed marked as test");
assert.notEqual(probeEmbed.color, leadEmbed.color, "probe and lead are visually distinct");

// Long free-text stays inside Discord's 1024-char field limit.
const longEmbed = formatIntakeEmbed({ message: "x".repeat(5000) }, "INT-LONG");
const messageField = longEmbed.fields.find(function (f) {
  return f.name === "Message";
});
assert.ok(messageField.value.length <= 1024, "message field clipped to Discord limit");
assert.equal(
  formatIntakeEmbed({}, "INT-EMPTY").fields.find(function (f) {
    return f.name === "Name";
  }).value,
  "—",
  "missing values render as a dash, not empty",
);

(async function main() {
  const prevUrl = process.env.DISCORD_OPS_WEBHOOK_URL;
  const realFetch = global.fetch;

  // Unconfigured: reports cleanly instead of throwing or sending.
  delete process.env.DISCORD_OPS_WEBHOOK_URL;
  assert.equal(discordConfigured(), false, "unset webhook is not configured");
  const unset = await sendIntakeDiscord(leadBody, "INT-UNSET", {});
  assert.equal(unset.configured, false);
  assert.equal(unset.error, "missing_discord_webhook_url");
  assert.equal(discordPathOk(unset), false);

  process.env.DISCORD_OPS_WEBHOOK_URL = "https://evil.example.com/api/webhooks/1/x";
  const bad = await sendIntakeDiscord(leadBody, "INT-BAD", {});
  assert.equal(bad.error, "invalid_discord_webhook_url", "foreign host refused before any request");

  process.env.DISCORD_OPS_WEBHOOK_URL = WEBHOOK;
  assert.equal(discordConfigured(), true, "valid webhook is configured");

  const sent = [];
  global.fetch = async function (url, init) {
    sent.push({ url: url, payload: JSON.parse(init.body) });
    return { ok: true, status: 204, text: async () => "" };
  };

  const ok = await sendIntakeDiscord(leadBody, "INT-SEND1", {});
  assert.equal(ok.ok, true, "send succeeds");
  assert.equal(ok.discord_mode, "sent");
  assert.equal(discordPathOk(ok), true);
  assert.equal(sent.length, 1, "exactly one webhook call");
  assert.equal(sent[0].url, WEBHOOK);
  assert.deepEqual(sent[0].payload.allowed_mentions, { parse: [] }, "form text can never ping the server");
  assert.equal(sent[0].payload.embeds.length, 1);

  // Same intake twice: second call is suppressed.
  const repeat = await sendIntakeDiscord(leadBody, "INT-SEND1", {});
  assert.equal(repeat.skipped, true, "duplicate intake deduped");
  assert.equal(repeat.discord_mode, "deduped");
  assert.equal(sent.length, 1, "no second webhook call");

  // An upstream dedupe flag suppresses without a send.
  const upstream = await sendIntakeDiscord(
    { ...leadBody, request_id: "RID-FRESH-1" },
    "INT-FRESH-1",
    { deduped: true },
  );
  assert.equal(upstream.skipped, true, "upstream dedupe honoured");
  assert.equal(sent.length, 1);

  // Discord returning an error is reported, not thrown.
  global.fetch = async function () {
    return { ok: false, status: 429, text: async () => "rate limited" };
  };
  const rateLimited = await sendIntakeDiscord({ ...leadBody, request_id: "RID-429" }, "INT-429", {});
  assert.equal(rateLimited.ok, false);
  assert.equal(rateLimited.error, "http_429");
  assert.equal(rateLimited.configured, true);

  // A network failure is reported, not thrown — intake must still answer the visitor.
  global.fetch = async function () {
    throw new Error("network down");
  };
  const offline = await sendIntakeDiscord({ ...leadBody, request_id: "RID-OFFLINE" }, "INT-OFFLINE", {});
  assert.equal(offline.ok, false);
  assert.match(offline.error, /network down/);

  global.fetch = realFetch;
  if (prevUrl === undefined) delete process.env.DISCORD_OPS_WEBHOOK_URL;
  else process.env.DISCORD_OPS_WEBHOOK_URL = prevUrl;

  console.log("notify-discord smoke ok");
})().catch(function (err) {
  console.error(err);
  process.exit(1);
});
