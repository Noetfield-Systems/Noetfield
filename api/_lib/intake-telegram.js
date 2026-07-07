/** Intake ops notify — Telegram (@noetfield_ops_bot) primary channel for www submissions. */

const { isTestIntake, testPipelineLabel } = require("./intake-test");

const DEFAULT_CHAT_ID = "8635650894";
const DEDUP_TTL_MS = 24 * 60 * 60 * 1000;
const _notifiedIntakeIds = new Map();
const _notifiedRequestIds = new Map();

function telegramConfigured() {
  const token = (process.env.TELEGRAM_NOETFIELD_OPS_BOT_TOKEN || "").trim();
  const chatId = (process.env.TELEGRAM_OPS_CHAT_ID || DEFAULT_CHAT_ID).trim();
  return Boolean(token && chatId);
}

function pruneNotifiedDedup() {
  const now = Date.now();
  for (const [id, ts] of _notifiedIntakeIds) {
    if (now - ts > DEDUP_TTL_MS) _notifiedIntakeIds.delete(id);
  }
  for (const [id, ts] of _notifiedRequestIds) {
    if (now - ts > DEDUP_TTL_MS) _notifiedRequestIds.delete(id);
  }
}

function wasRequestNotified(requestId) {
  if (!requestId) return false;
  pruneNotifiedDedup();
  return _notifiedRequestIds.has(String(requestId).toUpperCase());
}

function markRequestNotified(requestId) {
  if (!requestId) return;
  pruneNotifiedDedup();
  _notifiedRequestIds.set(String(requestId).toUpperCase(), Date.now());
}

function wasIntakeNotified(intakeId) {
  if (!intakeId) return false;
  pruneNotifiedDedup();
  return _notifiedIntakeIds.has(intakeId);
}

function markIntakeNotified(intakeId) {
  if (!intakeId) return;
  pruneNotifiedDedup();
  _notifiedIntakeIds.set(intakeId, Date.now());
}

function formatIntakeTelegramText(body, intakeId) {
  const name = String(body.contact_name || "—").trim() || "—";
  const company = String(body.organization || "—").trim() || "—";
  const message = String(body.message || "").trim() || "—";
  const id = String(intakeId || "—").trim() || "—";
  return ["name: " + name, "company: " + company, "message: " + message, "intake ID: " + id].join("\n");
}

function formatHealthReceiptTelegram({
  pass,
  pipeline,
  intakeId,
  timestamp,
  founderActionRequired,
  receiptPath,
  supabaseReceiptId,
  reason,
}) {
  const lines = [
    "NF " + (pass ? "PASS" : "FAIL") + " · TEST",
    "pipeline: " + (pipeline || "test:intake"),
    "intake_id: " + (intakeId || "—"),
    "at: " + (timestamp || new Date().toISOString()),
    "founder_action: " + (founderActionRequired ? "yes" : "no"),
  ];
  if (receiptPath) lines.push("receipt: " + receiptPath);
  if (supabaseReceiptId) lines.push("supabase_receipt: " + supabaseReceiptId);
  if (reason) lines.push("reason: " + reason);
  return lines.join("\n");
}

function telegramPathOk(result) {
  if (!result) return false;
  if (result.telegram_skipped_probe) return true;
  if (result.ok && result.mode === "receipt_only") return true;
  return Boolean(result.ok);
}

function probeTelegramSkipped(result) {
  return Boolean(result && (result.telegram_skipped_probe || (result.skipped && result.intake_kind === "test")));
}

async function sendIntakeTelegram(body, intakeId, options) {
  const opts = options || {};
  const token = (process.env.TELEGRAM_NOETFIELD_OPS_BOT_TOKEN || "").trim();
  const chatId = (process.env.TELEGRAM_OPS_CHAT_ID || DEFAULT_CHAT_ID).trim();
  const configured = Boolean(token && chatId);
  const id = String(intakeId || "").trim();
  const requestId = String(body.request_id || "").trim().toUpperCase();

  if (!configured) {
    return { ok: false, configured: false, error: "missing_telegram_config" };
  }

  if (isTestIntake(body)) {
    const alreadyNotified =
      (id && (opts.deduped || wasIntakeNotified(id))) || (requestId && wasRequestNotified(requestId));
    if (alreadyNotified) {
      return {
        ok: true,
        configured: true,
        skipped: true,
        reason: opts.deduped ? "request_id_dedup" : "intake_id_dedup",
        intake_kind: "test",
        telegram_skipped_probe: true,
        telegram_mode: "receipt_only",
      };
    }

    if (!opts.probeFail) {
      if (requestId) markRequestNotified(requestId);
      return {
        ok: true,
        configured: true,
        skipped: true,
        intake_kind: "test",
        telegram_skipped_probe: true,
        telegram_mode: "receipt_only",
      };
    }

    const text = formatHealthReceiptTelegram({
      pass: false,
      pipeline: testPipelineLabel(body),
      intakeId: id,
      timestamp: opts.timestamp || new Date().toISOString(),
      founderActionRequired: true,
      receiptPath: opts.receiptPath || null,
      supabaseReceiptId: opts.supabaseReceiptId || null,
      reason: opts.reason || "probe_fail",
    });
    markIntakeNotified(id);
    if (requestId) markRequestNotified(requestId);
    return sendTelegramRaw(token, chatId, text);
  }

  const text = formatIntakeTelegramText(body, intakeId);
  const result = await sendTelegramRaw(token, chatId, text);
  if (result.ok && id) markIntakeNotified(id);
  if (result.ok && requestId) markRequestNotified(requestId);
  return result;
}

async function sendTelegramRaw(token, chatId, text) {
  const res = await fetch("https://api.telegram.org/bot" + token + "/sendMessage", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text: text.slice(0, 4096),
      disable_web_page_preview: true,
    }),
  });

  const payload = await res.json().catch(function () {
    return {};
  });
  if (res.ok && payload.ok) {
    return {
      ok: true,
      configured: true,
      message_id: payload.result && payload.result.message_id ? payload.result.message_id : null,
      telegram_mode: "sent",
    };
  }

  const err = payload.description || "http_" + res.status;
  console.error("intake_telegram_failed", err);
  return { ok: false, configured: true, error: err };
}

module.exports = {
  DEFAULT_CHAT_ID,
  telegramConfigured,
  formatIntakeTelegramText,
  formatHealthReceiptTelegram,
  sendIntakeTelegram,
  telegramPathOk,
  probeTelegramSkipped,
  wasIntakeNotified,
  markIntakeNotified,
  wasRequestNotified,
  markRequestNotified,
};
