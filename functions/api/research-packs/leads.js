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

// api/research-packs/leads.js
var require_leads = __commonJS({
  "api/research-packs/leads.js"(exports, module) {
    var { sendIntakeTelegram } = require_intake_telegram();
    function cryptoRandomId(prefix) {
      const bytes = new Uint8Array(16);
      crypto.getRandomValues(bytes);
      const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
      return `${prefix}${hex}`;
    }
    module.exports = async function handler2(req, res) {
      res.setHeader("Access-Control-Allow-Origin", "*");
      res.setHeader("Cache-Control", "no-store");
      if (req.method === "OPTIONS") {
        res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
        res.setHeader("Access-Control-Allow-Headers", "content-type");
        return res.status(204).end();
      }
      if (req.method !== "POST") {
        return res.status(405).json({ error: "METHOD_NOT_ALLOWED" });
      }
      const body = req.body && typeof req.body === "object" ? req.body : {};
      const email = String(body.email || "").trim().toLowerCase();
      if (!email || !email.includes("@") || email.length > 320) {
        return res.status(400).json({ error: "EMAIL_REQUIRED" });
      }
      const recipe_id = String(body.recipe_id || "vendor-decision-brief").trim();
      const lead_id = cryptoRandomId("lead_");
      const recorded_at = (/* @__PURE__ */ new Date()).toISOString();
      const record = {
        schema: "noetfield.runway-commercial-lead.v0.1",
        lead_id,
        recorded_at,
        email,
        name: String(body.name || "").slice(0, 200),
        organization: String(body.organization || "").slice(0, 200),
        recipe_id,
        caller_site: String(body.caller_site || "noetfield.com").slice(0, 80),
        note: String(body.note || "").slice(0, 2e3),
        source: String(body.source || "research-packs-www").slice(0, 80)
      };
      const env = process.env || {};
      try {
        await sendIntakeTelegram(
          {
            contact_name: record.name || email,
            organization: record.organization || "\u2014",
            message: `Research packs lead \xB7 ${recipe_id} \xB7 ${email}${record.note ? " \xB7 " + record.note : ""}`,
            contact_email: email,
            request_id: lead_id,
            metadata: {
              topic: "research-packs",
              form_id: "nf_research_packs",
              recipe_id,
              lead_id,
              caller_site: record.caller_site
            }
          },
          lead_id
        );
      } catch (err) {
        console.error("research_packs_lead_telegram_failed", err && err.message ? err.message : err);
      }
      const payment = recipe_id === "spreadsheet-kpi-pack" ? env.STRIPE_PAYMENT_LINK_KPI_PACK : recipe_id === "rfp-response-pack" ? env.STRIPE_PAYMENT_LINK_RFP_PACK : env.STRIPE_PAYMENT_LINK_DECISION_BRIEF;
      const runtimeBase = String(
        env.RUNWAY_RUNTIME_BASE_URL || "https://noetfield-runway-runtime-api-staging.sina-kazemnezhad-ca.workers.dev"
      ).replace(/\/+$/, "");
      const workspacePath = String(env.WORKSPACE_PATH || "/v1/sourceb/workspace");
      return res.status(200).json({
        ok: true,
        lead_id,
        recorded_at,
        next: payment ? { kind: "stripe_payment_link", url: payment } : {
          kind: "workspace",
          url: runtimeBase + workspacePath,
          message: "Purchase intent recorded. Open the delivery workspace after entitlement is activated."
        }
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

// tmp/pages-function-entries/api__research-packs__leads.js
var handlerModule = __toESM(require_leads());
var handler = handlerModule.default || handlerModule;
var onRequest = (context) => runNodeHandler(handler, context);
export {
  onRequest
};
