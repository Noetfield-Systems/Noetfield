var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __commonJS = (cb, mod) => function __require() {
  return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// api/_lib/intake-test.js
var require_intake_test = __commonJS({
  "api/_lib/intake-test.js"(exports, module) {
    var TEST_FORM_IDS = /* @__PURE__ */ new Set(["nf_intake_e2e", "nf_probe_cron"]);
    var TEST_TOPICS = /* @__PURE__ */ new Set(["e2e", "probe"]);
    var TEST_EMAILS = /* @__PURE__ */ new Set(["e2e@noetfield.com", "probe@noetfield.com"]);
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
      ensureTestMetadata
    };
  }
});

// api/_lib/intake-email.js
var require_intake_email = __commonJS({
  "api/_lib/intake-email.js"(exports, module) {
    var { isTestIntake } = require_intake_test();
    var CANONICAL = "operations@noetfield.com";
    function meta(body) {
      return body && typeof body.metadata === "object" && body.metadata ? body.metadata : {};
    }
    function intakeLabel(body) {
      const m = meta(body);
      const vector = String(body.vector || "").toLowerCase();
      const topic = String(m.topic || m.role || m.program_lane || "").toLowerCase();
      const sku = String(body.sku || "").toLowerCase();
      const formId = String(m.form_id || "").toLowerCase();
      if (vector.indexOf("sandbox") >= 0 || formId === "nfsandboxform" || formId === "nftrialaccountform") {
        return "Sandbox signup";
      }
      if (vector === "investor-diligence" || topic === "investor-diligence") {
        return "Investor diligence vault";
      }
      if (topic === "investor" || vector === "work-with-us" && topic === "investor") {
        return "Investor brief";
      }
      if (vector === "work-with-us" || ["connector", "facilitator", "co-partner", "partner"].indexOf(topic) >= 0) {
        return "Work with Noetfield application";
      }
      if (vector.indexOf("copilot") >= 0 || sku === "copilot" || topic === "pilot") {
        return "Governance Pack apply";
      }
      if (vector.indexOf("trust") >= 0 || sku === "trust_brief" || topic === "trust-brief") {
        return "Trust Brief Intake";
      }
      if (vector.indexOf("bank") >= 0 || sku === "bank_pilot" || topic === "bank-pilot") {
        return "Bank Pilot inquiry";
      }
      if (topic === "federal") return "Federal Brief";
      if (topic === "feedback") return "Site feedback";
      if (topic === "partner") return "Partner program";
      if (vector === "contact" && topic) return "Contact \u2014 " + topic;
      if (vector === "contact") return "Contact";
      return "Intake";
    }
    function metaLine(body) {
      const m = meta(body);
      const parts = [];
      const lane = m.program_lane || m.buyer_role || m.role || "";
      const topic = m.topic || "";
      if (lane) parts.push("lane/role: " + lane);
      if (topic && topic !== lane) parts.push("topic: " + topic);
      if (m.pilot_band) parts.push("pilot_band: " + m.pilot_band);
      if (m.engagement) parts.push("engagement: " + m.engagement);
      if (m.page) parts.push("page: " + m.page);
      if (m.form_id) parts.push("form: " + m.form_id);
      if (m.async) parts.push("async web submit");
      return parts.join(" \xB7 ");
    }
    function intakeSubject(body, intakeId) {
      const rid = body.request_id || intakeId;
      const label = intakeLabel(body);
      const vector = String(body.vector || "").trim();
      if (vector && label.indexOf("[vector:") < 0) {
        return "[vector:" + vector + "] Noetfield \u2014 " + label + " (" + rid + ")";
      }
      return "Noetfield \u2014 " + label + " (" + rid + ")";
    }
    function opsBodyText(body, intakeId) {
      const m = meta(body);
      const ctx = metaLine(body);
      const lines = [
        "New Noetfield intake \u2014 REPLY to this email to reach the submitter.",
        "",
        "Intake ID: " + intakeId,
        "RID: " + (body.request_id || "\u2014"),
        "Organization: " + (body.organization || "\u2014"),
        "Contact: " + (body.contact_name || "\u2014") + " <" + (body.contact_email || "\u2014") + ">",
        "SKU: " + (body.sku || "\u2014"),
        "Vector: " + (body.vector || "\u2014"),
        "Source: " + (body.source || "web")
      ];
      if (ctx) lines.push("Context: " + ctx);
      lines.push("", "Message:", String(body.message || "").trim(), "");
      return lines.join("\n");
    }
    function ackBody(body, intakeId) {
      const name = body.contact_name ? " " + body.contact_name : "";
      const rid = body.request_id || intakeId;
      return "Hi" + name + ",\n\nYour message was saved instantly. Operations at Noetfield will follow up within one business day.\n\nReference: " + rid + "\nIntake ID: " + intakeId + "\n\nReply to this email or write " + CANONICAL + " \u2014 include your Request ID in any follow-up.\n\n\u2014 Noetfield Operations\n" + CANONICAL + "\n";
    }
    async function sendResend({ from, to, subject, text, replyTo, requestId }) {
      const key = (process.env.RESEND_API_KEY || "").trim();
      if (!key) return { ok: false, error: "missing_api_key" };
      const payload = { from, to, subject, text };
      if (replyTo) payload.reply_to = replyTo;
      const rid = String(requestId || "").trim().toUpperCase();
      if (rid) payload.tags = [{ name: "request_id", value: rid }];
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + key
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) return { ok: true };
      const errBody = await res.text().catch(function() {
        return "";
      });
      console.error("resend_send_failed", res.status, errBody.slice(0, 500));
      return { ok: false, error: errBody.slice(0, 200) };
    }
    function emailConfigured() {
      return Boolean((process.env.RESEND_API_KEY || "").trim());
    }
    async function sendIntakeEmails(body, ids) {
      if (isTestIntake(body)) {
        return { ops: false, ack: false, configured: emailConfigured(), skipped: true, intake_kind: "test" };
      }
      const intakeId = ids.intakeId;
      const from = (process.env.INTAKE_EMAIL_FROM || "").trim() || "Noetfield Intake <notifications@noetfield.com>";
      const inbox = (process.env.INTAKE_EMAIL_TO || CANONICAL).trim();
      const autoAck = (process.env.INTAKE_AUTO_ACK_ENABLED || "true").toLowerCase() !== "false";
      if (!emailConfigured()) {
        return { ops: false, ack: false, configured: false };
      }
      if (!body.contact_email || String(body.contact_email).indexOf("@") < 1) {
        return { ops: false, ack: false, configured: true };
      }
      const opsResult = await sendResend({
        from,
        to: [inbox],
        subject: intakeSubject(body, intakeId),
        text: opsBodyText(body, intakeId),
        replyTo: body.contact_email,
        requestId: body.request_id || ids.rid || null
      });
      const ops = opsResult.ok;
      let ack = false;
      if (autoAck && ops) {
        const ackResult = await sendResend({
          from,
          to: [body.contact_email],
          subject: "Noetfield \u2014 message received (" + (body.request_id || intakeId) + ")",
          text: ackBody(body, intakeId),
          replyTo: CANONICAL,
          requestId: body.request_id || ids.rid || null
        });
        ack = ackResult.ok;
      }
      return { ops, ack, configured: true, resend_error: ops ? null : opsResult.error || null };
    }
    module.exports = {
      CANONICAL,
      emailConfigured,
      intakeLabel,
      intakeSubject,
      opsBodyText,
      sendIntakeEmails
    };
  }
});

// api/_lib/intake-telegram.js
var require_intake_telegram = __commonJS({
  "api/_lib/intake-telegram.js"(exports, module) {
    var { isTestIntake, testPipelineLabel } = require_intake_test();
    var DEFAULT_CHAT_ID = "8635650894";
    var DEDUP_TTL_MS = 24 * 60 * 60 * 1e3;
    var _notifiedIntakeIds = /* @__PURE__ */ new Map();
    var _notifiedRequestIds = /* @__PURE__ */ new Map();
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
      const name = String(body.contact_name || "\u2014").trim() || "\u2014";
      const company = String(body.organization || "\u2014").trim() || "\u2014";
      const message = String(body.message || "").trim() || "\u2014";
      const id = String(intakeId || "\u2014").trim() || "\u2014";
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
      reason
    }) {
      const lines = [
        "NF " + (pass ? "PASS" : "FAIL") + " \xB7 TEST",
        "pipeline: " + (pipeline || "test:intake"),
        "intake_id: " + (intakeId || "\u2014"),
        "at: " + (timestamp || (/* @__PURE__ */ new Date()).toISOString()),
        "founder_action: " + (founderActionRequired ? "yes" : "no")
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
      return Boolean(result && (result.telegram_skipped_probe || result.skipped && result.intake_kind === "test"));
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
        const alreadyNotified = id && (opts.deduped || wasIntakeNotified(id)) || requestId && wasRequestNotified(requestId);
        if (alreadyNotified) {
          return {
            ok: true,
            configured: true,
            skipped: true,
            reason: opts.deduped ? "request_id_dedup" : "intake_id_dedup",
            intake_kind: "test",
            telegram_skipped_probe: true,
            telegram_mode: "receipt_only"
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
            telegram_mode: "receipt_only"
          };
        }
        const text2 = formatHealthReceiptTelegram({
          pass: false,
          pipeline: testPipelineLabel(body),
          intakeId: id,
          timestamp: opts.timestamp || (/* @__PURE__ */ new Date()).toISOString(),
          founderActionRequired: true,
          receiptPath: opts.receiptPath || null,
          supabaseReceiptId: opts.supabaseReceiptId || null,
          reason: opts.reason || "probe_fail"
        });
        markIntakeNotified(id);
        if (requestId) markRequestNotified(requestId);
        return sendTelegramRaw(token, chatId, text2);
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
          disable_web_page_preview: true
        })
      });
      const payload = await res.json().catch(function() {
        return {};
      });
      if (res.ok && payload.ok) {
        return {
          ok: true,
          configured: true,
          message_id: payload.result && payload.result.message_id ? payload.result.message_id : null,
          telegram_mode: "sent"
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
      markRequestNotified
    };
  }
});

// api/intake.js
var require_intake = __commonJS({
  "api/intake.js"(exports, module) {
    var { CANONICAL, emailConfigured, sendIntakeEmails, opsBodyText } = require_intake_email();
    var { isTestIntake, ensureTestMetadata } = require_intake_test();
    var { sendIntakeTelegram, telegramConfigured, telegramPathOk } = require_intake_telegram();
    function randomIntakeId() {
      const hex = Array.from({ length: 12 }, function() {
        return Math.floor(Math.random() * 16).toString(16);
      }).join("");
      return "INT-" + hex.toUpperCase();
    }
    function cors(res) {
      res.setHeader("Access-Control-Allow-Origin", "*");
      res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
      res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
    }
    module.exports = async function handler2(req, res) {
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
          body: JSON.stringify(body)
        });
        platformData = await forward.json().catch(function() {
          return {};
        });
        platformOk = forward.ok;
      } catch (err) {
        console.error("platform_intake_forward_failed", err && err.message ? err.message : err);
      }
      const intakeId = platformData && platformData.intake_id || randomIntakeId();
      const deduped = Boolean(platformData && platformData.deduped);
      let telegramResult = { ok: false, configured: telegramConfigured() };
      try {
        telegramResult = await sendIntakeTelegram(body, intakeId, { deduped });
      } catch (err) {
        console.error("intake_telegram_failed", err && err.message ? err.message : err);
      }
      const telegramDelivered = telegramPathOk(telegramResult);
      const intakeKind = isTestIntake(body) ? "test" : "lead";
      const notifyExtras = {
        telegram_delivered: telegramDelivered,
        telegram_mode: telegramResult.telegram_mode || (telegramResult.ok ? "sent" : "none"),
        intake_kind: intakeKind,
        deduped
      };
      if (intakeKind === "test") {
        notifyExtras.telegram_skipped_probe = Boolean(telegramResult.telegram_skipped_probe);
        notifyExtras.intake_persisted = platformOk;
        notifyExtras.dedupe_checked = deduped;
      }
      let emailResult = { ops: false, ack: false, configured: emailConfigured() };
      try {
        emailResult = await sendIntakeEmails(body, { intakeId, rid: body.request_id || null });
      } catch (err) {
        console.error("intake_email_archive_failed", err && err.message ? err.message : err);
      }
      if (platformOk && platformData) {
        return res.status(200).json({
          ...platformData,
          ...notifyExtras,
          email_delivered: emailResult.ops,
          email_ack: emailResult.ack
        });
      }
      if (telegramDelivered) {
        return res.status(200).json({
          intake_id: intakeId,
          request_id: body.request_id || null,
          message: intakeKind === "test" ? "Test intake recorded \u2014 health receipt only" : "Intake recorded \u2014 operations notified on Telegram",
          ...notifyExtras,
          email_delivered: emailResult.ops,
          email_ack: emailResult.ack
        });
      }
      if (emailResult.ops) {
        return res.status(200).json({
          intake_id: intakeId,
          request_id: body.request_id || null,
          message: "Intake recorded \u2014 operations archive email sent",
          ...notifyExtras,
          telegram_delivered: false,
          email_delivered: true,
          email_ack: emailResult.ack
        });
      }
      const mailSubject = "[vector:" + (body.vector || "web-intake") + "] Noetfield \u2014 Intake fallback (" + intakeId + ")";
      const mailBody = opsBodyText(body, intakeId);
      return res.status(502).json({
        detail: "Intake unavailable \u2014 platform record failed and ops notify did not deliver. Use /contact/ or email operations@noetfield.com with your Request ID.",
        intake_id: intakeId,
        telegram_delivered: false,
        email_delivered: false,
        mailto: "mailto:" + CANONICAL + "?subject=" + encodeURIComponent(mailSubject) + "&body=" + encodeURIComponent(mailBody),
        www_email_configured: emailResult.configured,
        www_telegram_configured: telegramResult.configured
      });
    };
  }
});

// functions/_lib/pages-node-handler-adapter.js
function headersToObject(request) {
  const out = {};
  request.headers.forEach((value, key) => {
    out[key] = value;
  });
  return out;
}
function createRes() {
  let statusCode = 200;
  const headers = {};
  let settled = null;
  const res = {
    status(code) {
      statusCode = code;
      return res;
    },
    setHeader(key, value) {
      headers[key] = value;
      return res;
    },
    json(data) {
      headers["content-type"] = headers["content-type"] || "application/json;charset=UTF-8";
      settled = new Response(JSON.stringify(data), { status: statusCode, headers });
      return settled;
    },
    end(body) {
      settled = new Response(body == null ? null : String(body), { status: statusCode, headers });
      return settled;
    },
    _response() {
      return settled;
    }
  };
  return res;
}
async function readBody(request) {
  if (request.method === "GET" || request.method === "HEAD" || request.method === "OPTIONS") {
    return {};
  }
  const contentType = request.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      return await request.json();
    } catch (_) {
      return {};
    }
  }
  const text = await request.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch (_) {
    return { raw: text };
  }
}
function bindEnv(env) {
  const base = typeof process !== "undefined" && process.env ? { ...process.env } : {};
  for (const [key, value] of Object.entries(env || {})) {
    if (value != null) base[key] = String(value);
  }
  if (typeof process !== "undefined") {
    process.env = base;
  }
  return base;
}
function queryToObject(url) {
  const out = {};
  url.searchParams.forEach((value, key) => {
    out[key] = value;
  });
  return out;
}
async function runNodeHandler(handler2, context) {
  const { request, env } = context;
  bindEnv(env);
  const url = new URL(request.url);
  const req = {
    method: request.method,
    url: url.pathname + url.search,
    query: queryToObject(url),
    headers: headersToObject(request),
    body: await readBody(request)
  };
  const res = createRes();
  const result = await handler2(req, res);
  if (result instanceof Response) return result;
  const fromRes = res._response();
  if (fromRes instanceof Response) return fromRes;
  return new Response(JSON.stringify({ detail: "handler did not send a response" }), {
    status: 500,
    headers: { "content-type": "application/json" }
  });
}

// tmp/pages-function-entries/api__intake.js
var handlerModule = __toESM(require_intake());
var handler = handlerModule.default || handlerModule;
var onRequest = (context) => runNodeHandler(handler, context);
export {
  onRequest
};
