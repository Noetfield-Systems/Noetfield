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

// api/_lib/runway-hmac.js
var require_runway_hmac = __commonJS({
  "api/_lib/runway-hmac.js"(exports, module) {
    function toHex(buffer) {
      return Array.from(new Uint8Array(buffer), (b) => b.toString(16).padStart(2, "0")).join("");
    }
    function utf8(text) {
      return new TextEncoder().encode(text);
    }
    async function sha256Hex(bytes) {
      const digest = await crypto.subtle.digest("SHA-256", bytes);
      return toHex(digest);
    }
    async function hmacSha256Hex(secret, message) {
      const key = await crypto.subtle.importKey(
        "raw",
        utf8(secret),
        { name: "HMAC", hash: "SHA-256" },
        false,
        ["sign"]
      );
      const sig = await crypto.subtle.sign("HMAC", key, utf8(message));
      return toHex(sig);
    }
    function randomNonceHex() {
      const bytes = new Uint8Array(16);
      crypto.getRandomValues(bytes);
      return toHex(bytes);
    }
    async function signRequest(secret, method, path, timestamp, nonce, bodyBytes) {
      const bodyHash = await sha256Hex(bodyBytes);
      const canonical = `${method.toUpperCase()}
${path}
${timestamp}
${nonce}
${bodyHash}`;
      return hmacSha256Hex(secret, canonical);
    }
    async function buildSignedHeaders({ secret, keyId, method, path, bodyBytes }) {
      const timestamp = (/* @__PURE__ */ new Date()).toISOString().replace(/\.\d{3}Z$/, "Z");
      const nonce = randomNonceHex();
      const signature = await signRequest(secret, method, path, timestamp, nonce, bodyBytes);
      return {
        authorization: `NOETFIELD-HMAC ${keyId}:${signature}`,
        "x-noetfield-timestamp": timestamp,
        "x-noetfield-nonce": nonce,
        "content-type": "application/json",
        accept: "application/json",
        "user-agent": "Noetfield-WWW-Runway-Dispatch/1.0"
      };
    }
    module.exports = { sha256Hex, signRequest, buildSignedHeaders };
  }
});

// api/_lib/runway-public-dispatch.js
var require_runway_public_dispatch = __commonJS({
  "api/_lib/runway-public-dispatch.js"(exports, module) {
    var { buildSignedHeaders } = require_runway_hmac();
    var DEFAULT_BASE = "https://noetfield-runway-runtime-api-staging.sina-kazemnezhad-ca.workers.dev";
    var DEFAULT_KEY_ID = "staging-proof";
    var PUBLIC_RECIPES = Object.freeze({
      "vendor-decision-brief": Object.freeze({
        runway_id: "research",
        recipe_id: "vendor-decision-brief",
        recipe_version: "0.1.0",
        label: "Vendor Decision Brief",
        goal: Object.freeze({
          question: "Which vendor best fits a bounded document-automation scope?",
          scope: "Document automation (public demo)",
          criteria: ["security", "fit"],
          weights: { security: 0.6, fit: 0.4 },
          options: [
            {
              vendor_id: "a",
              name: "Vendor A",
              scores: { security: 0.9, fit: 0.8 },
              evidence_urls: ["https://example.com/a"]
            },
            {
              vendor_id: "b",
              name: "Vendor B",
              scores: { security: 0.7, fit: 0.9 },
              evidence_urls: ["https://example.com/b"]
            }
          ]
        })
      })
    });
    function runtimeConfig(env) {
      const source = env || process.env || {};
      const secret = String(source.RUNWAY_RUNTIME_API_SECRET || "").trim();
      const baseUrl = String(source.RUNWAY_RUNTIME_BASE_URL || DEFAULT_BASE).trim().replace(/\/$/, "");
      const keyId = String(source.RUNWAY_RUNTIME_KEY_ID || DEFAULT_KEY_ID).trim();
      return { secret, baseUrl, keyId, configured: Boolean(secret && baseUrl && keyId) };
    }
    function listPublicRecipes() {
      return Object.values(PUBLIC_RECIPES).map((recipe) => ({
        recipe_id: recipe.recipe_id,
        runway_id: recipe.runway_id,
        recipe_version: recipe.recipe_version,
        label: recipe.label
      }));
    }
    function resolveRecipe(recipeId) {
      const key = String(recipeId || "vendor-decision-brief").trim();
      return PUBLIC_RECIPES[key] || null;
    }
    function buildPublicIntake(recipe, idempotencyKey) {
      return {
        schema: "noetfield.job-intake.v0.1",
        // Staging Motor entitlements are pinned in runway-cloud-runtime wrangler.jsonc.
        tenant_id: "tenant-staging-proof",
        entitlement_id: "ent-staging-proof",
        runway_id: recipe.runway_id,
        recipe_id: recipe.recipe_id,
        recipe_version: recipe.recipe_version,
        idempotency_key: idempotencyKey,
        requested_at: (/* @__PURE__ */ new Date()).toISOString().replace(/\.\d{3}Z$/, "Z"),
        caller_site: "noetfield.com",
        budget_usd: 25,
        input: { goal: recipe.goal }
      };
    }
    function makeIdempotencyKey(recipeId) {
      const stamp = Date.now().toString(36);
      const rand = Math.random().toString(36).slice(2, 10);
      return `www-${recipeId.slice(0, 24)}-${stamp}-${rand}`.slice(0, 128);
    }
    async function signedFetch(config, method, path, payload) {
      const bodyBytes = payload == null ? new Uint8Array(0) : new TextEncoder().encode(JSON.stringify(payload));
      const headers = await buildSignedHeaders({
        secret: config.secret,
        keyId: config.keyId,
        method,
        path,
        bodyBytes
      });
      const response = await fetch(`${config.baseUrl}${path}`, {
        method,
        headers,
        body: payload == null ? void 0 : bodyBytes
      });
      const text = await response.text();
      let json = null;
      try {
        json = text ? JSON.parse(text) : null;
      } catch (_) {
        json = { raw: text.slice(0, 500) };
      }
      return { status: response.status, json, text };
    }
    async function dispatchPublicJob({ recipeId, env } = {}) {
      const config = runtimeConfig(env);
      if (!config.configured) {
        return {
          ok: false,
          httpStatus: 503,
          body: {
            ok: false,
            code: "MOTOR_DISPATCH_UNCONFIGURED",
            detail: "Live Motor dispatch is not configured on this surface yet.",
            intake_fallback: "/contact/?topic=enterprise-governance",
            recipes: listPublicRecipes()
          }
        };
      }
      const recipe = resolveRecipe(recipeId);
      if (!recipe) {
        return {
          ok: false,
          httpStatus: 400,
          body: {
            ok: false,
            code: "RECIPE_NOT_ALLOWLISTED",
            detail: "Only allowlisted public demo recipes may be dispatched from www.",
            recipes: listPublicRecipes()
          }
        };
      }
      const intake = buildPublicIntake(recipe, makeIdempotencyKey(recipe.recipe_id));
      const result = await signedFetch(config, "POST", "/v1/jobs", intake);
      if (result.status !== 200 && result.status !== 202) {
        return {
          ok: false,
          httpStatus: result.status >= 400 && result.status < 600 ? result.status : 502,
          body: {
            ok: false,
            code: "MOTOR_DISPATCH_FAILED",
            detail: result.json && (result.json.detail || result.json.error) || "Motor rejected the job.",
            motor_status: result.status,
            intake_fallback: "/contact/?topic=enterprise-governance"
          }
        };
      }
      const jobId = result.json && result.json.job_id;
      return {
        ok: true,
        httpStatus: 202,
        body: {
          ok: true,
          environment: "staging",
          recipe_id: recipe.recipe_id,
          runway_id: recipe.runway_id,
          recipe_version: recipe.recipe_version,
          label: recipe.label,
          job_id: jobId,
          status_path: jobId ? `/api/runway/job-status?job_id=${encodeURIComponent(jobId)}` : null,
          note: "Staging Motor dispatch. Paid customer delivery is not claimed."
        }
      };
    }
    async function readPublicJobStatus({ jobId, env } = {}) {
      const config = runtimeConfig(env);
      if (!config.configured) {
        return {
          ok: false,
          httpStatus: 503,
          body: {
            ok: false,
            code: "MOTOR_DISPATCH_UNCONFIGURED",
            detail: "Live Motor dispatch is not configured on this surface yet."
          }
        };
      }
      const id = String(jobId || "").trim();
      if (!/^[A-Za-z0-9._:-]{8,128}$/.test(id)) {
        return {
          ok: false,
          httpStatus: 400,
          body: { ok: false, code: "JOB_ID_INVALID", detail: "job_id is required." }
        };
      }
      const result = await signedFetch(config, "GET", `/v1/jobs/${encodeURIComponent(id)}/result`, null);
      if (result.status === 409) {
        return {
          ok: true,
          httpStatus: 202,
          body: {
            ok: true,
            job_id: id,
            status: "running",
            environment: "staging"
          }
        };
      }
      if (result.status !== 200) {
        return {
          ok: false,
          httpStatus: result.status >= 400 && result.status < 600 ? result.status : 502,
          body: {
            ok: false,
            code: "MOTOR_STATUS_FAILED",
            detail: result.json && (result.json.detail || result.json.error) || "Could not read job status.",
            motor_status: result.status,
            job_id: id
          }
        };
      }
      return {
        ok: true,
        httpStatus: 200,
        body: {
          ok: true,
          job_id: id,
          environment: "staging",
          status: result.json.status || "unknown",
          result: result.json
        }
      };
    }
    module.exports = {
      PUBLIC_RECIPES,
      runtimeConfig,
      listPublicRecipes,
      resolveRecipe,
      buildPublicIntake,
      dispatchPublicJob,
      readPublicJobStatus
    };
  }
});

// api/runway/jobs.js
var require_jobs = __commonJS({
  "api/runway/jobs.js"(exports, module) {
    var { dispatchPublicJob, listPublicRecipes } = require_runway_public_dispatch();
    function cors(res) {
      res.setHeader("Access-Control-Allow-Origin", "*");
      res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
      res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
      res.setHeader("Cache-Control", "no-store");
    }
    module.exports = async function handler2(req, res) {
      cors(res);
      if (req.method === "OPTIONS") {
        return res.status(204).end();
      }
      if (req.method === "GET") {
        return res.status(200).json({
          ok: true,
          service: "noetfield-www-runway-dispatch",
          recipes: listPublicRecipes(),
          intake_fallback: "/contact/?topic=enterprise-governance"
        });
      }
      if (req.method !== "POST") {
        return res.status(405).json({ detail: "Method not allowed" });
      }
      const body = req.body && typeof req.body === "object" ? req.body : {};
      const outcome = await dispatchPublicJob({
        recipeId: body.recipe_id || body.recipeId,
        env: process.env
      });
      return res.status(outcome.httpStatus).json(outcome.body);
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

// tmp/pages-function-entries/api__runway__jobs.js
var handlerModule = __toESM(require_jobs());
var handler = handlerModule.default || handlerModule;
var onRequest = (context) => runNodeHandler(handler, context);
export {
  onRequest
};
