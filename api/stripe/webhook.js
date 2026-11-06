/**
 * Stripe webhook receiver for Noetfield's own commercial sales.
 *
 * Cloudflare Pages Functions bundles this file from api/stripe/webhook.js.
 * This endpoint verifies the raw Stripe-Signature header and sends internal
 * operations notifications only. It does not grant entitlements, issue refunds,
 * move funds, or collect card data.
 */

const EVENT_TTL_MS = 30 * 24 * 60 * 60 * 1000;
const PROCESSING_LEASE_MS = 5 * 60 * 1000;
const processedEvents = new Map();

const PAYMENT_LINK_SKUS = {
  plink_1UYgwvPzg8bUp343POMzC1Ln: "Trust_Brief",
  plink_1UYgwxPzg8bUp343dHbEYpDL: "Copilot_Readiness_Pack",
  plink_1UYheSL4BR0lqapB7tejJ6TQ: "Trust_Brief",
  plink_1UYheSL4BR0lqapBbfTzgwuL: "Copilot_Readiness_Pack",
};

const SUPPORTED_EVENTS = new Set([
  "checkout.session.completed",
  "checkout.session.async_payment_succeeded",
  "checkout.session.async_payment_failed",
  "invoice.finalized",
  "invoice.paid",
  "invoice.payment_failed",
  "invoice.payment_action_required",
  "invoice.voided",
  "invoice.marked_uncollectible",
  "charge.refunded",
  "charge.dispute.created",
  "charge.dispute.closed",
  "charge.dispute.funds_withdrawn",
  "charge.dispute.funds_reinstated",
  "refund.created",
  "refund.failed",
  "radar.early_fraud_warning.created",
]);

function hex(bytes) {
  return Array.from(new Uint8Array(bytes), (value) => value.toString(16).padStart(2, "0")).join("");
}

function safeEqualHex(left, right) {
  if (typeof left !== "string" || typeof right !== "string" || left.length !== right.length) {
    return false;
  }
  let mismatch = 0;
  for (let index = 0; index < left.length; index += 1) {
    mismatch |= left.charCodeAt(index) ^ right.charCodeAt(index);
  }
  return mismatch === 0;
}

function parseSignatureHeader(header) {
  const result = { timestamp: null, signatures: [] };
  for (const item of String(header || "").split(",")) {
    const separator = item.indexOf("=");
    if (separator < 1) continue;
    const key = item.slice(0, separator).trim();
    const value = item.slice(separator + 1).trim();
    if (key === "t" && /^\d+$/.test(value)) result.timestamp = Number(value);
    if (key === "v1" && /^[a-f0-9]{64}$/i.test(value)) result.signatures.push(value.toLowerCase());
  }
  return result;
}

async function stripeSignatureMatches(rawBody, header, secret, nowMs) {
  if (typeof rawBody !== "string" || !rawBody || !secret) return false;
  const parsed = parseSignatureHeader(header);
  if (!parsed.timestamp || parsed.signatures.length === 0) return false;

  const nowSeconds = Math.floor((nowMs == null ? Date.now() : nowMs) / 1000);
  if (Math.abs(nowSeconds - parsed.timestamp) > 300) return false;

  const encoder = new TextEncoder();
  const key = await globalThis.crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signedPayload = String(parsed.timestamp) + "." + rawBody;
  const digest = await globalThis.crypto.subtle.sign("HMAC", key, encoder.encode(signedPayload));
  const expected = hex(digest);
  return parsed.signatures.some((candidate) => safeEqualHex(candidate, expected));
}

async function verifyStripeSignature(rawBody, header, requestEnv, eventLivemode, nowMs) {
  const env = requestEnv || {};
  const candidates = [
    { secret: env.STRIPE_WEBHOOK_SECRET_TEST, livemode: false },
    { secret: env.STRIPE_WEBHOOK_SECRET_LIVE, livemode: true },
  ].filter((item) => typeof item.secret === "string" && item.secret.trim());

  const fallback = String(env.STRIPE_WEBHOOK_SECRET || "").trim();
  if (candidates.length === 0 && fallback) {
    candidates.push({ secret: fallback, livemode: null });
  }

  for (const candidate of candidates) {
    if (candidate.livemode !== null && typeof eventLivemode === "boolean" &&
        candidate.livemode !== eventLivemode) {
      continue;
    }
    if (await stripeSignatureMatches(rawBody, header, candidate.secret, nowMs)) {
      return candidate.livemode === null ? "unspecified" : (candidate.livemode ? "live" : "test");
    }
  }
  return null;
}

function money(amount, currency) {
  if (amount === null || amount === undefined || amount === "") return "amount not supplied";
  const numeric = Number(amount);
  if (!Number.isFinite(numeric)) return String(amount) + " " + String(currency || "").toUpperCase();
  return (numeric / 100).toFixed(2) + " " + String(currency || "").toUpperCase();
}

function parseRelevantEvent(event) {
  if (!event || typeof event !== "object" || !SUPPORTED_EVENTS.has(event.type)) return null;
  const object = event.data && event.data.object && typeof event.data.object === "object"
    ? event.data.object
    : {};

  if (event.type.indexOf("checkout.session.") === 0) {
    const paymentStatus = String(object.payment_status || "");
    const isAsyncFailure = event.type === "checkout.session.async_payment_failed";
    if (!isAsyncFailure && paymentStatus !== "paid" && paymentStatus !== "no_payment_required") {
      return null;
    }
    const paymentLink = String(object.payment_link || "");
    const metadata = object.metadata && typeof object.metadata === "object" ? object.metadata : {};
    const sku = String(metadata.gtm_sku || metadata.sku || PAYMENT_LINK_SKUS[paymentLink] || "commercial_license");
    const customerDetails = object.customer_details && typeof object.customer_details === "object"
      ? object.customer_details
      : {};
    return {
      kind: isAsyncFailure ? "payment_failure" : "checkout",
      eventType: event.type,
      eventId: String(event.id || ""),
      livemode: Boolean(event.livemode),
      objectId: String(object.id || ""),
      sku,
      customerId: String(object.customer || ""),
      customerEmail: String(customerDetails.email || object.customer_email || ""),
      amount: money(object.amount_total, object.currency),
      paymentLink,
      paymentStatus: isAsyncFailure ? "failed" : paymentStatus,
      failureMessage: String(object.last_payment_error?.message || object.status || ""),
    };
  }

  if (event.type.indexOf("invoice.") === 0) {
    const customerDetails = object.customer_details && typeof object.customer_details === "object"
      ? object.customer_details
      : {};
    const metadata = object.metadata && typeof object.metadata === "object" ? object.metadata : {};
    const isPaid = event.type === "invoice.paid";
    const amount = isPaid ? object.amount_paid : object.amount_due;
    return {
      kind: "invoice",
      eventType: event.type,
      eventId: String(event.id || ""),
      livemode: Boolean(event.livemode),
      objectId: String(object.id || ""),
      invoiceNumber: String(object.number || ""),
      status: String(object.status || ""),
      sku: String(metadata.gtm_sku || metadata.sku || ""),
      customerId: String(object.customer || ""),
      customerEmail: String(customerDetails.email || object.customer_email || ""),
      amount: money(amount, object.currency),
      hostedInvoiceUrl: String(object.hosted_invoice_url || ""),
    };
  }

  const metadata = object.metadata && typeof object.metadata === "object" ? object.metadata : {};
  const customer = String(object.customer || "");
  const paymentIntent = String(object.payment_intent || object.payment_intent_id || "");
  const amount = object.amount_refunded ?? object.amount ?? object.amount_disputed ?? object.amount;
  const currency = String(object.currency || "usd").toUpperCase();
  const isDispute = event.type.indexOf("charge.dispute.") === 0;
  const isFraudWarning = event.type === "radar.early_fraud_warning.created";
  const isChargeRefunded = event.type === "charge.refunded";
  const riskType = isFraudWarning ? "early_fraud_warning" : (isDispute ? "dispute" : "refund");
  return {
    kind: "risk",
    riskType,
    eventType: event.type,
    eventId: String(event.id || ""),
    livemode: Boolean(event.livemode),
    objectId: String(object.id || ""),
    customerId: customer,
    customerEmail: "",
    sku: String(metadata.gtm_sku || metadata.sku || ""),
    amount: money(amount, currency),
    status: String(object.status || (isChargeRefunded ? "refunded" : "")),
    paymentIntent,
    chargeId: String(object.charge || (isChargeRefunded ? object.id : "")),
    reason: String(object.reason || object.fraud_type || object.failure_reason || ""),
    actionable: object.actionable === undefined ? "" : String(Boolean(object.actionable)),
    evidenceDueBy: object.evidence_details?.due_by ? String(object.evidence_details.due_by) : "",
  };
}

function claimLocalEvent(eventId) {
  const now = Date.now();
  for (const [key, value] of processedEvents.entries()) {
    if (now - value.updatedAt > EVENT_TTL_MS) processedEvents.delete(key);
  }
  const existing = processedEvents.get(eventId);
  if (existing && existing.status === "processed") return "duplicate";
  if (existing && existing.status === "processing" && now - existing.updatedAt < PROCESSING_LEASE_MS) {
    return "processing";
  }
  processedEvents.set(eventId, { status: "processing", updatedAt: now });
  return "reserved";
}

function markLocalEvent(eventId, status) {
  processedEvents.set(eventId, { status, updatedAt: Date.now() });
}

async function claimEvent(eventId, requestEnv, livemode) {
  const kv = requestEnv && requestEnv.STRIPE_WEBHOOK_EVENTS;
  if (kv && typeof kv.get === "function" && typeof kv.put === "function") {
    const key = "stripe-event:" + eventId;
    const existingRaw = await kv.get(key);
    if (existingRaw) {
      let existing = null;
      try { existing = JSON.parse(existingRaw); } catch (_) {}
      if (existing && existing.status === "processed") return "duplicate";
      if (existing && existing.status === "processing" &&
          Date.now() - Number(existing.updatedAt || 0) < PROCESSING_LEASE_MS) {
        return "processing";
      }
    }
    await kv.put(key, JSON.stringify({ status: "processing", updatedAt: Date.now() }), {
      expirationTtl: 60 * 60 * 24 * 30,
    });
    return "reserved-kv";
  }
  if (livemode === true) {
    throw new Error("durable STRIPE_WEBHOOK_EVENTS binding is required for live events");
  }
  return claimLocalEvent(eventId);
}

async function markEvent(eventId, status, requestEnv) {
  const kv = requestEnv && requestEnv.STRIPE_WEBHOOK_EVENTS;
  const value = { status, updatedAt: Date.now() };
  if (kv && typeof kv.put === "function") {
    await kv.put("stripe-event:" + eventId, JSON.stringify(value), {
      expirationTtl: 60 * 60 * 24 * 30,
    });
    return;
  }
  markLocalEvent(eventId, status);
}

function notificationText(details) {
  const eventKind = details.kind === "checkout"
    ? "PAYMENT"
    : (details.kind === "payment_failure" ? "PAYMENT FAILURE" : (details.kind === "invoice" ? "INVOICE" : "RISK"));
  const lines = [
    "NOETFIELD · STRIPE " + eventKind,
    "",
    "event: " + details.eventType,
    "event_id: " + details.eventId,
    "mode: " + (details.livemode ? "LIVE" : "TEST"),
    "object_id: " + details.objectId,
    "sku: " + (details.sku || "not tagged"),
    "customer: " + (details.customerEmail || details.customerId || "not supplied"),
    "amount: " + details.amount,
  ];
  if (details.kind === "checkout" || details.kind === "payment_failure") {
    lines.push("payment_status: " + details.paymentStatus);
    if (details.paymentLink) lines.push("payment_link_id: " + details.paymentLink);
    if (details.failureMessage) lines.push("failure: " + details.failureMessage);
  } else if (details.kind === "invoice") {
    lines.push("invoice_number: " + (details.invoiceNumber || "not assigned"));
    lines.push("invoice_status: " + (details.status || "unknown"));
    if (details.hostedInvoiceUrl) lines.push("hosted_invoice_url: " + details.hostedInvoiceUrl);
  } else if (details.kind === "risk") {
    lines.push("risk_type: " + details.riskType);
    lines.push("status: " + (details.status || "not supplied"));
    if (details.paymentIntent) lines.push("payment_intent: " + details.paymentIntent);
    if (details.chargeId) lines.push("charge: " + details.chargeId);
    if (details.reason) lines.push("reason: " + details.reason);
    if (details.actionable) lines.push("actionable: " + details.actionable);
    if (details.evidenceDueBy) lines.push("evidence_due_by: " + details.evidenceDueBy);
  }
  lines.push("", "Internal operations notice only. Reconcile against Stripe Dashboard before changing customer access or accounting records.");
  return lines.join("\n");
}

async function sendOpsEmail(text, eventId) {
  const apiKey = String(process.env.RESEND_API_KEY || "").trim();
  if (!apiKey) return false;
  const from = String(process.env.INTAKE_EMAIL_FROM || "Noetfield Stripe <notifications@noetfield.com>").trim();
  const to = String(process.env.INTAKE_EMAIL_TO || "operations@noetfield.com").trim();
  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + apiKey,
    },
    body: JSON.stringify({
      from,
      to: [to],
      subject: "Noetfield Stripe event · " + eventId,
      text,
    }),
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    console.error("stripe_ops_email_failed status=" + response.status + " detail=" + detail.slice(0, 200));
    return false;
  }
  return true;
}

async function sendOpsTelegram(text) {
  const token = String(process.env.TELEGRAM_NOETFIELD_OPS_BOT_TOKEN || "").trim();
  const chatId = String(process.env.TELEGRAM_OPS_CHAT_ID || "8635650894").trim();
  if (!token || !chatId) return false;
  const response = await fetch("https://api.telegram.org/bot" + token + "/sendMessage", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text: text.slice(0, 4096),
      disable_web_page_preview: true,
    }),
  });
  const result = await response.json().catch(() => ({}));
  return Boolean(response.ok && result.ok);
}

async function handleStripeWebhook(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "METHOD_NOT_ALLOWED" });
  }
  const rawBody = typeof req.rawBody === "string" ? req.rawBody : "";
  if (!rawBody || rawBody.length > 512000) {
    return res.status(400).json({ error: "INVALID_RAW_BODY" });
  }

  let event;
  try {
    event = JSON.parse(rawBody);
  } catch (_) {
    return res.status(400).json({ error: "INVALID_JSON" });
  }

  const eventId = String(event.id || "").trim();
  if (!eventId) return res.status(400).json({ error: "EVENT_ID_REQUIRED" });

  const verifiedMode = await verifyStripeSignature(
    rawBody,
    req.headers && req.headers["stripe-signature"],
    req.env || {},
    typeof event.livemode === "boolean" ? event.livemode : undefined
  );
  if (!verifiedMode) return res.status(400).json({ error: "INVALID_SIGNATURE" });

  const details = parseRelevantEvent(event);
  if (!details) {
    return res.status(200).json({ ok: true, handled: false, event_id: eventId });
  }

  let claim;
  try {
    claim = await claimEvent(eventId, req.env || {}, Boolean(event.livemode));
  } catch (error) {
    console.error("stripe_event_store_unavailable type=" + (error && error.name ? error.name : "Error"));
    return res.status(503).json({ error: "EVENT_STORE_UNAVAILABLE" });
  }
  if (claim === "duplicate") {
    return res.status(200).json({ ok: true, duplicate: true, event_id: eventId });
  }
  if (claim === "processing") {
    return res.status(503).json({ error: "EVENT_ALREADY_PROCESSING", event_id: eventId });
  }

  const text = notificationText(details);
  try {
    const results = await Promise.all([
      sendOpsEmail(text, eventId).catch(() => false),
      sendOpsTelegram(text).catch(() => false),
    ]);
    if (!results.some(Boolean)) {
      await markEvent(eventId, "failed", req.env || {});
      return res.status(503).json({ error: "OPS_NOTIFICATION_UNAVAILABLE", event_id: eventId });
    }
    await markEvent(eventId, "processed", req.env || {});
    return res.status(200).json({
      ok: true,
      handled: true,
      event_id: eventId,
      mode: verifiedMode,
      email_notified: results[0],
      telegram_notified: results[1],
    });
  } catch (error) {
    await markEvent(eventId, "failed", req.env || {}).catch(() => {});
    console.error("stripe_webhook_processing_failed type=" + (error && error.name ? error.name : "Error"));
    return res.status(503).json({ error: "WEBHOOK_PROCESSING_FAILED", event_id: eventId });
  }
}

module.exports = handleStripeWebhook;
module.exports.parseSignatureHeader = parseSignatureHeader;
module.exports.stripeSignatureMatches = stripeSignatureMatches;
module.exports.verifyStripeSignature = verifyStripeSignature;
module.exports.parseRelevantEvent = parseRelevantEvent;
module.exports.claimLocalEvent = claimLocalEvent;
module.exports.markLocalEvent = markLocalEvent;
module.exports.claimEvent = claimEvent;
module.exports.notificationText = notificationText;
