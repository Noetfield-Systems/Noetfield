const test = require("node:test");
const assert = require("node:assert/strict");
const { createHmac, webcrypto } = require("node:crypto");

globalThis.crypto = webcrypto;

const webhook = require("../../api/stripe/webhook.js");

function signatureHeader(secret, payload, timestamp) {
  const signed = String(timestamp) + "." + payload;
  const signature = createHmac("sha256", secret).update(signed, "utf8").digest("hex");
  return "t=" + timestamp + ",v1=" + signature;
}

test("accepts a valid Stripe signature for the matching test-mode secret", async () => {
  const secret = "whsec_test_secret";
  const payload = JSON.stringify({
    id: "evt_test_1",
    type: "checkout.session.completed",
    livemode: false,
    data: { object: { id: "cs_test_1", payment_status: "paid" } },
  });
  const timestamp = 1_800_000_000;
  const header = signatureHeader(secret, payload, timestamp);
  const mode = await webhook.verifyStripeSignature(
    payload,
    header,
    { STRIPE_WEBHOOK_SECRET_TEST: secret, STRIPE_WEBHOOK_SECRET_LIVE: "whsec_live_secret" },
    false,
    timestamp * 1000
  );
  assert.equal(mode, "test");
});

test("rejects a signature from a different mode", async () => {
  const secret = "whsec_live_secret";
  const payload = JSON.stringify({ id: "evt_live_1", livemode: true });
  const timestamp = 1_800_000_000;
  const header = signatureHeader(secret, payload, timestamp);
  const mode = await webhook.verifyStripeSignature(
    payload,
    header,
    { STRIPE_WEBHOOK_SECRET_TEST: "whsec_test_secret", STRIPE_WEBHOOK_SECRET_LIVE: secret },
    false,
    timestamp * 1000
  );
  assert.equal(mode, null);
});

test("rejects stale signatures", async () => {
  const secret = "whsec_test_secret";
  const payload = '{"id":"evt_old"}';
  const timestamp = 1_800_000_000;
  const header = signatureHeader(secret, payload, timestamp);
  const ok = await webhook.stripeSignatureMatches(
    payload,
    header,
    secret,
    (timestamp + 301) * 1000
  );
  assert.equal(ok, false);
});

test("parses paid Checkout sessions and maps known Payment Links to catalog SKUs", () => {
  const parsed = webhook.parseRelevantEvent({
    id: "evt_checkout",
    type: "checkout.session.completed",
    livemode: false,
    data: {
      object: {
        id: "cs_test_1",
        payment_status: "paid",
        payment_link: "plink_1UYheSL4BR0lqapB7tejJ6TQ",
        customer: "cus_test_1",
        customer_details: { email: "buyer@example.com" },
        amount_total: 1000000,
        currency: "usd",
      },
    },
  });
  assert.equal(parsed.kind, "checkout");
  assert.equal(parsed.sku, "Trust_Brief");
  assert.equal(parsed.amount, "10000.00 USD");
  assert.equal(parsed.customerEmail, "buyer@example.com");
});

test("does not process an unpaid Checkout session", () => {
  const parsed = webhook.parseRelevantEvent({
    id: "evt_checkout_unpaid",
    type: "checkout.session.completed",
    livemode: false,
    data: { object: { id: "cs_unpaid", payment_status: "unpaid" } },
  });
  assert.equal(parsed, null);
});

test("parses invoice lifecycle events without treating invoice finalization as payment", () => {
  const parsed = webhook.parseRelevantEvent({
    id: "evt_invoice_paid",
    type: "invoice.paid",
    livemode: false,
    data: {
      object: {
        id: "in_test_1",
        number: "NOE-0001",
        customer: "cus_test_1",
        customer_email: "ap@example.com",
        amount_due: 200000,
        amount_paid: 200000,
        currency: "usd",
        status: "paid",
        hosted_invoice_url: "https://invoice.stripe.test/i/test",
      },
    },
  });
  assert.equal(parsed.kind, "invoice");
  assert.equal(parsed.eventType, "invoice.paid");
  assert.equal(parsed.amount, "2000.00 USD");
  assert.equal(parsed.invoiceNumber, "NOE-0001");
});

test("suppresses repeated event IDs within one Pages isolate", () => {
  assert.equal(webhook.claimLocalEvent("evt_dedupe_test"), "reserved");
  assert.equal(webhook.claimLocalEvent("evt_dedupe_test"), "processing");
  webhook.markLocalEvent("evt_dedupe_test", "processed");
  assert.equal(webhook.claimLocalEvent("evt_dedupe_test"), "duplicate");
});

test("notifies operations when a delayed Checkout payment fails", () => {
  const parsed = webhook.parseRelevantEvent({
    id: "evt_async_failed",
    type: "checkout.session.async_payment_failed",
    livemode: true,
    data: {
      object: {
        id: "cs_live_failed",
        payment_status: "unpaid",
        payment_link: "plink_1UYheSL4BR0lqapBbfTzgwuL",
        customer: "cus_live_1",
        customer_details: { email: "buyer@example.com" },
        amount_total: 200000,
        currency: "usd",
        status: "complete",
      },
    },
  });
  assert.equal(parsed.kind, "payment_failure");
  assert.equal(parsed.sku, "Copilot_Readiness_Pack");
  assert.equal(parsed.paymentStatus, "failed");
  assert.equal(parsed.amount, "2000.00 USD");
});

test("parses a charge refund as a risk event", () => {
  const parsed = webhook.parseRelevantEvent({
    id: "evt_refunded",
    type: "charge.refunded",
    livemode: true,
    data: {
      object: {
        id: "ch_1",
        amount: 1000000,
        amount_refunded: 1000000,
        currency: "usd",
        customer: "cus_1",
        payment_intent: "pi_1",
        refunded: true,
      },
    },
  });
  assert.equal(parsed.kind, "risk");
  assert.equal(parsed.riskType, "refund");
  assert.equal(parsed.amount, "10000.00 USD");
  assert.equal(parsed.paymentIntent, "pi_1");
});

test("parses a dispute event without automatically contesting it", () => {
  const parsed = webhook.parseRelevantEvent({
    id: "evt_dispute",
    type: "charge.dispute.created",
    livemode: true,
    data: {
      object: {
        id: "dp_1",
        charge: "ch_1",
        payment_intent: "pi_1",
        amount: 1000000,
        currency: "usd",
        reason: "fraudulent",
        status: "needs_response",
        evidence_details: { due_by: 1800000000 },
      },
    },
  });
  assert.equal(parsed.kind, "risk");
  assert.equal(parsed.riskType, "dispute");
  assert.equal(parsed.status, "needs_response");
  assert.equal(parsed.reason, "fraudulent");
  assert.equal(parsed.evidenceDueBy, "1800000000");
});

test("live events fail closed without a durable Cloudflare KV binding", async () => {
  await assert.rejects(
    webhook.claimEvent("evt_live_dedupe", {}, true),
    /durable STRIPE_WEBHOOK_EVENTS binding is required/
  );
});

test("risk notification includes the event type and dispute evidence deadline", () => {
  const text = webhook.notificationText({
    kind: "risk",
    riskType: "dispute",
    eventType: "charge.dispute.created",
    eventId: "evt_dispute",
    livemode: true,
    objectId: "dp_1",
    sku: "Trust_Brief",
    customerEmail: "",
    customerId: "cus_1",
    amount: "10000.00 USD",
    status: "needs_response",
    paymentIntent: "pi_1",
    chargeId: "ch_1",
    reason: "fraudulent",
    actionable: "",
    evidenceDueBy: "1800000000",
  });
  assert.match(text, /STRIPE RISK/);
  assert.match(text, /charge\.dispute\.created/);
  assert.match(text, /evidence_due_by: 1800000000/);
});

test("does not accept the legacy mode-agnostic webhook secret", async () => {
  const secret = "whsec_legacy";
  const payload = JSON.stringify({ id: "evt_legacy", livemode: true });
  const timestamp = 1_800_000_000;
  const header = signatureHeader(secret, payload, timestamp);
  const mode = await webhook.verifyStripeSignature(
    payload,
    header,
    { STRIPE_WEBHOOK_SECRET: secret },
    true,
    timestamp * 1000
  );
  assert.equal(mode, null);
});

test("rejects events that omit livemode instead of trying both secrets", async () => {
  const secret = "whsec_test_secret";
  const payload = JSON.stringify({ id: "evt_no_mode" });
  const timestamp = 1_800_000_000;
  const header = signatureHeader(secret, payload, timestamp);
  const mode = await webhook.verifyStripeSignature(
    payload,
    header,
    { STRIPE_WEBHOOK_SECRET_TEST: secret, STRIPE_WEBHOOK_SECRET_LIVE: "whsec_live_secret" },
    undefined,
    timestamp * 1000
  );
  assert.equal(mode, null);
});
