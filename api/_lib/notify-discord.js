/** Intake ops notify — Discord webhook channel. Additive sink alongside Telegram. */

const { isTestIntake, testPipelineLabel } = require("./intake-test");

const DEDUP_TTL_MS = 24 * 60 * 60 * 1000;
const SEND_TIMEOUT_MS = 5000;
const COLOR_LEAD = 0xc9a962;
const COLOR_TEST = 0x6b7280;
const ALLOWED_WEBHOOK_HOSTS = new Set(["discord.com", "discordapp.com", "ptb.discord.com", "canary.discord.com"]);

const _notifiedIntakeIds = new Map();
const _notifiedRequestIds = new Map();

function webhookUrl() {
  return (process.env.DISCORD_OPS_WEBHOOK_URL || "").trim();
}

/** Only real Discord webhook endpoints — a mistyped env var must not become an outbound POST to an arbitrary host. */
function isValidWebhookUrl(raw) {
  if (!raw) return false;
  let parsed;
  try {
    parsed = new URL(raw);
  } catch (e) {
    return false;
  }
  if (parsed.protocol !== "https:") return false;
  if (!ALLOWED_WEBHOOK_HOSTS.has(parsed.hostname)) return false;
  return parsed.pathname.startsWith("/api/webhooks/");
}

function discordConfigured() {
  return isValidWebhookUrl(webhookUrl());
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

function clip(value, max) {
  const text = String(value == null ? "" : value).trim();
  if (!text) return "—";
  return text.length > max ? text.slice(0, max - 1) + "…" : text;
}

function formatIntakeEmbed(body, intakeId) {
  const isTest = isTestIntake(body);
  return {
    title: isTest ? "Test intake · " + clip(testPipelineLabel(body), 200) : "New intake",
    color: isTest ? COLOR_TEST : COLOR_LEAD,
    timestamp: new Date().toISOString(),
    fields: [
      { name: "Name", value: clip(body.contact_name, 1024), inline: true },
      { name: "Company", value: clip(body.organization, 1024), inline: true },
      { name: "Vector", value: clip(body.vector || "web-intake", 1024), inline: true },
      { name: "Message", value: clip(body.message, 1024), inline: false },
      { name: "Intake ID", value: clip(intakeId, 1024), inline: true },
      { name: "Request ID", value: clip(body.request_id, 1024), inline: true },
    ],
    footer: { text: "noetfield.com" },
  };
}

/**
 * Post an intake to the ops Discord channel. Never throws; a Discord outage
 * must not change what the intake endpoint returns to the visitor.
 */
async function sendIntakeDiscord(body, intakeId, options) {
  const opts = options || {};
  const url = webhookUrl();

  if (!isValidWebhookUrl(url)) {
    return { ok: false, configured: false, error: url ? "invalid_discord_webhook_url" : "missing_discord_webhook_url" };
  }

  const id = String(intakeId || "").trim();
  const requestId = String(body.request_id || "").trim().toUpperCase();
  const alreadyNotified =
    (id && (opts.deduped || wasIntakeNotified(id))) || (requestId && wasRequestNotified(requestId));

  if (alreadyNotified) {
    return {
      ok: true,
      configured: true,
      skipped: true,
      reason: opts.deduped ? "request_id_dedup" : "intake_id_dedup",
      discord_mode: "deduped",
    };
  }

  const result = await postWebhook(url, {
    username: "Noetfield Site",
    allowed_mentions: { parse: [] },
    embeds: [formatIntakeEmbed(body, intakeId)],
  });

  if (result.ok) {
    if (id) markIntakeNotified(id);
    if (requestId) markRequestNotified(requestId);
  }
  return result;
}

async function postWebhook(url, payload) {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(SEND_TIMEOUT_MS),
    });

    if (res.ok) {
      return { ok: true, configured: true, discord_mode: "sent" };
    }

    const detail = await res.text().catch(function () {
      return "";
    });
    console.error("intake_discord_failed", "http_" + res.status, detail.slice(0, 200));
    return { ok: false, configured: true, error: "http_" + res.status };
  } catch (err) {
    const message = err && err.message ? err.message : String(err);
    console.error("intake_discord_failed", message);
    return { ok: false, configured: true, error: message };
  }
}

function discordPathOk(result) {
  if (!result) return false;
  return Boolean(result.ok);
}

module.exports = {
  discordConfigured,
  isValidWebhookUrl,
  formatIntakeEmbed,
  sendIntakeDiscord,
  discordPathOk,
  wasIntakeNotified,
  markIntakeNotified,
  wasRequestNotified,
  markRequestNotified,
};
