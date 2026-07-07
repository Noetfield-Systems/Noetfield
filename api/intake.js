/** POST /api/intake — platform DB (source of truth) + Telegram ops + Resend archive. */

const { CANONICAL, emailConfigured, sendIntakeEmails, opsBodyText } = require("./_lib/intake-email");
const { isTestIntake, ensureTestMetadata } = require("./_lib/intake-test");
const { sendIntakeTelegram, telegramConfigured, telegramPathOk } = require("./_lib/intake-telegram");

function randomIntakeId() {
  const hex = Array.from({ length: 12 }, function () {
    return Math.floor(Math.random() * 16).toString(16);
  }).join("");
  return "INT-" + hex.toUpperCase();
}

function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
}

module.exports = async function handler(req, res) {
  cors(res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }
  if (req.method !== "POST") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const body = ensureTestMetadata(req.body || {});
  const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  let platformData = null;
  let platformOk = false;

  try {
    const forward = await fetch(platformBase + "/api/intake", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    });
    platformData = await forward.json().catch(function () {
      return {};
    });
    platformOk = forward.ok;
  } catch (err) {
    console.error("platform_intake_forward_failed", err && err.message ? err.message : err);
  }

  const intakeId = (platformData && platformData.intake_id) || randomIntakeId();

  const deduped = Boolean(platformData && platformData.deduped);
  let telegramResult = { ok: false, configured: telegramConfigured() };
  try {
    telegramResult = await sendIntakeTelegram(body, intakeId, { deduped: deduped });
  } catch (err) {
    console.error("intake_telegram_failed", err && err.message ? err.message : err);
  }

  const telegramDelivered = telegramPathOk(telegramResult);
  const intakeKind = isTestIntake(body) ? "test" : "lead";
  const notifyExtras = {
    telegram_delivered: telegramDelivered,
    telegram_mode: telegramResult.telegram_mode || (telegramResult.ok ? "sent" : "none"),
    intake_kind: intakeKind,
    deduped: deduped,
  };
  if (intakeKind === "test") {
    notifyExtras.telegram_skipped_probe = Boolean(telegramResult.telegram_skipped_probe);
    notifyExtras.intake_persisted = platformOk;
    notifyExtras.dedupe_checked = deduped;
  }

  let emailResult = { ops: false, ack: false, configured: emailConfigured() };
  try {
    emailResult = await sendIntakeEmails(body, { intakeId: intakeId, rid: body.request_id || null });
  } catch (err) {
    console.error("intake_email_archive_failed", err && err.message ? err.message : err);
  }

  if (platformOk && platformData) {
    return res.status(200).json({
      ...platformData,
      ...notifyExtras,
      email_delivered: emailResult.ops,
      email_ack: emailResult.ack,
    });
  }

  if (telegramDelivered) {
    return res.status(200).json({
      intake_id: intakeId,
      request_id: body.request_id || null,
      message:
        intakeKind === "test"
          ? "Test intake recorded — health receipt only"
          : "Intake recorded — operations notified on Telegram",
      ...notifyExtras,
      email_delivered: emailResult.ops,
      email_ack: emailResult.ack,
    });
  }

  if (emailResult.ops) {
    return res.status(200).json({
      intake_id: intakeId,
      request_id: body.request_id || null,
      message: "Intake recorded — operations archive email sent",
      ...notifyExtras,
      telegram_delivered: false,
      email_delivered: true,
      email_ack: emailResult.ack,
    });
  }

  const mailSubject =
    "[vector:" + (body.vector || "web-intake") + "] Noetfield — Intake fallback (" + intakeId + ")";
  const mailBody = opsBodyText(body, intakeId);

  return res.status(502).json({
    detail:
      "Intake unavailable — platform record failed and ops notify did not deliver. Use /contact/ or email operations@noetfield.com with your Request ID.",
    intake_id: intakeId,
    telegram_delivered: false,
    email_delivered: false,
    mailto: "mailto:" + CANONICAL + "?subject=" + encodeURIComponent(mailSubject) + "&body=" + encodeURIComponent(mailBody),
    www_email_configured: emailResult.configured,
    www_telegram_configured: telegramResult.configured,
  });
};
