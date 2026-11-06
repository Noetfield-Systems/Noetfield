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
        payment_link: "plink_1TjyvtJ03eJkL57J1vb6kOU8",
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
