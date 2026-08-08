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

// api/_lib/research-trader-state.js
var require_research_trader_state = __commonJS({
  "api/_lib/research-trader-state.js"(exports, module) {
    var CYCLE_SCHEMA_PREFIX = "noetfield.ai-trader-research-cycle.";
    var CURRENT_MAX_AGE_S = 26 * 3600;
    var LATE_MAX_AGE_S = 72 * 3600;
    var FUTURE_TOLERANCE_MS = 15 * 60 * 1e3;
    function count(value) {
      const n = Number(value);
      return Number.isInteger(n) && n >= 0 ? n : null;
    }
    function money(value) {
      const n = Number(value);
      return Number.isFinite(n) && n >= 0 ? n : null;
    }
    function text(value) {
      return typeof value === "string" && value ? value : null;
    }
    function instant(value, nowMs) {
      if (typeof value !== "string" || !value) return null;
      const t = Date.parse(value);
      if (!Number.isFinite(t)) return null;
      if (t > nowMs + FUTURE_TOLERANCE_MS) return null;
      return { iso: value, ms: t };
    }
    function classify(ageSeconds) {
      if (ageSeconds === null || ageSeconds === void 0) return "unknown";
      if (ageSeconds <= CURRENT_MAX_AGE_S) return "current";
      if (ageSeconds <= LATE_MAX_AGE_S) return "late";
      return "stale";
    }
    function normalize(raw, nowMs) {
      if (!raw || typeof raw !== "object") {
        return { available: false, reason: "upstream_malformed" };
      }
      if (raw.storeAvailable !== true) {
        return { available: false, reason: "store_unavailable" };
      }
      const latest = raw.latest;
      if (!latest || typeof latest !== "object") {
        return { available: false, reason: "store_unavailable" };
      }
      if (typeof latest.schema !== "string" || latest.schema.indexOf(CYCLE_SCHEMA_PREFIX) !== 0) {
        return { available: false, reason: "upstream_malformed" };
      }
      const completed = instant(latest.completedAtIso, nowMs);
      if (!completed) {
        return { available: false, reason: "upstream_malformed" };
      }
      const stats = raw.stats && typeof raw.stats === "object" ? raw.stats : {};
      const totals = {
        cyclesRun: count(stats.cyclesRun),
        screenings: count(stats.symbolsScreened),
        // Deliberately not "plansWritten": the upstream counter includes cycles
        // where the model declined outright, so calling these "plans" would
        // overstate what the gate has actually refused.
        modelVerdicts: count(stats.plansWritten),
        clearedGate: count(stats.plansPassed),
        spendUsd: money(raw.totalSpendUsd)
      };
      const required = ["cyclesRun", "screenings", "modelVerdicts", "clearedGate", "spendUsd"];
      for (let i = 0; i < required.length; i += 1) {
        if (totals[required[i]] === null) {
          return { available: false, reason: "upstream_malformed" };
        }
      }
      if (totals.clearedGate > totals.modelVerdicts) {
        return { available: false, reason: "upstream_malformed" };
      }
      if (totals.cyclesRun > 0 && totals.screenings < totals.cyclesRun) {
        return { available: false, reason: "upstream_malformed" };
      }
      const reported = Number(stats.gatePassPct);
      const derived = totals.modelVerdicts > 0 ? totals.clearedGate / totals.modelVerdicts * 100 : null;
      totals.gatePassPct = derived !== null && Number.isFinite(reported) && Math.round(reported) === Math.round(derived) ? reported : null;
      const started = instant(latest.startedAtIso, nowMs);
      const cost = latest.cost && typeof latest.cost === "object" ? latest.cost : {};
      const ageSeconds = Math.round((nowMs - completed.ms) / 1e3);
      return {
        available: true,
        cycle: {
          proofRunId: text(latest.proofRunId),
          state: text(latest.state),
          mode: text(latest.mode),
          startedAtIso: started ? started.iso : null,
          completedAtIso: completed.iso,
          watchlistCount: Array.isArray(latest.watchlist) ? latest.watchlist.length : null,
          symbolsScreened: count(latest.screenedCount),
          costUsd: money(cost.totalUsd),
          costBasis: text(cost.basis)
        },
        totals,
        freshness: {
          ageSeconds,
          class: classify(ageSeconds),
          computedFrom: "completedAtIso"
        },
        note: text(typeof raw.error === "string" ? raw.error.trim() : null)
      };
    }
    module.exports = { normalize, classify, CURRENT_MAX_AGE_S, LATE_MAX_AGE_S };
  }
});

// api/research-trader/state.js
var require_state = __commonJS({
  "api/research-trader/state.js"(exports, module) {
    var { normalize, classify } = require_research_trader_state();
    var SCHEMA = "noetfield.research-trader-state.v1";
    var UPSTREAM_PATH = "/api/state.json";
    var DEFAULT_BASE = "https://noetfield-ai-trader.sina-kazemnezhad-ca.workers.dev";
    var FETCH_TIMEOUT_MS = 5e3;
    var FRESH_TTL_SECONDS = 300;
    var MAX_BODY_BYTES = 2 * 1024 * 1024;
    function cacheKey(req) {
      const host = String(req.headers && req.headers.host || "www.noetfield.com").replace(/[^\w.\-:]/g, "");
      return "https://" + host + "/__nf/research-trader-state-v1";
    }
    async function readCache(key) {
      try {
        if (typeof caches === "undefined" || !caches.default) return null;
        const hit = await caches.default.match(new Request(key, { method: "GET" }));
        return hit ? await hit.json() : null;
      } catch (err) {
        return null;
      }
    }
    async function writeCache(key, body) {
      try {
        if (typeof caches === "undefined" || !caches.default) return;
        await caches.default.put(
          new Request(key, { method: "GET" }),
          new Response(JSON.stringify(body), {
            headers: { "content-type": "application/json", "cache-control": "max-age=604800" }
          })
        );
      } catch (err) {
      }
    }
    function reclass(cached, nowMs) {
      const completed = Date.parse(cached.cycle && cached.cycle.completedAtIso);
      const ageSeconds = Number.isFinite(completed) ? Math.round((nowMs - completed) / 1e3) : null;
      return Object.assign({}, cached, {
        source: "edge-cache",
        freshness: {
          ageSeconds,
          class: classify(ageSeconds),
          computedFrom: "completedAtIso"
        }
      });
    }
    module.exports = async function handler2(req, res) {
      res.setHeader("Access-Control-Allow-Origin", "*");
      res.setHeader("Cache-Control", "no-store");
      if (req.method === "OPTIONS") {
        res.setHeader("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS");
        return res.status(204).end();
      }
      if (req.method !== "GET" && req.method !== "HEAD") {
        return res.status(405).json({ schema: SCHEMA, detail: "Method not allowed" });
      }
      const env = process.env || {};
      const base = String(env.AI_TRADER_BASE_URL || DEFAULT_BASE).replace(/\/+$/, "");
      const upstream = { base, path: UPSTREAM_PATH };
      const key = cacheKey(req);
      const nowMs = Date.now();
      try {
        const cached = await readCache(key);
        if (cached && cached.available === true && cached.observedAtIso) {
          const ageS = (nowMs - Date.parse(cached.observedAtIso)) / 1e3;
          if (ageS >= 0 && ageS < FRESH_TTL_SECONDS) {
            return res.status(200).json(reclass(cached, nowMs));
          }
        }
        let normalized;
        try {
          const upstreamRes = await fetch(base + UPSTREAM_PATH, {
            headers: { Accept: "application/json", "User-Agent": "noetfield-www-research-trader" },
            signal: AbortSignal.timeout(FETCH_TIMEOUT_MS)
          });
          const ctype = String(upstreamRes.headers.get("content-type") || "");
          const clen = Number(upstreamRes.headers.get("content-length") || 0);
          if (upstreamRes.ok && ctype.indexOf("json") >= 0 && !(clen > MAX_BODY_BYTES)) {
            const raw = await upstreamRes.json().catch(function() {
              return null;
            });
            normalized = normalize(raw, nowMs);
          } else {
            normalized = {
              available: false,
              reason: upstreamRes.ok ? "upstream_malformed" : "upstream_status"
            };
          }
        } catch (err) {
          normalized = { available: false, reason: "upstream_unreachable" };
        }
        if (normalized.available === true) {
          const body = Object.assign(
            {
              schema: SCHEMA,
              source: "upstream",
              observedAtIso: new Date(nowMs).toISOString(),
              upstream
            },
            normalized
          );
          await writeCache(key, body);
          return res.status(200).json(body);
        }
        if (cached && cached.available === true) {
          return res.status(200).json(reclass(cached, nowMs));
        }
        return res.status(503).json({
          schema: SCHEMA,
          available: false,
          reason: normalized.reason || "upstream_unreachable",
          observedAtIso: new Date(nowMs).toISOString(),
          upstream
        });
      } catch (err) {
        console.error("research_trader_state_failed", err && err.message ? err.message : err);
        return res.status(503).json({
          schema: SCHEMA,
          available: false,
          reason: "upstream_unreachable",
          observedAtIso: new Date(nowMs).toISOString(),
          upstream
        });
      }
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

// tmp/pages-function-entries/api__research-trader__state.js
var handlerModule = __toESM(require_state());
var handler = handlerModule.default || handlerModule;
var onRequest = (context) => runNodeHandler(handler, context);
export {
  onRequest
};
