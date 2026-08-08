/**
 * GET /api/research-trader/state — a same-origin, validated mirror of the
 * ai-trader public cycle feed.
 *
 * Why this exists: the upstream worker serves its state with no
 * Access-Control-Allow-Origin header, so a browser on www.noetfield.com cannot
 * read it directly. Mirroring it here also means /research-trader/ keeps
 * answering — and says why — when the agent itself is unreachable.
 *
 * The upstream URL comes from the environment only. No request input may
 * influence it; a `?base=` convenience parameter would turn this into a
 * same-origin open relay.
 */

const { normalize, classify } = require("../_lib/research-trader-state");

const SCHEMA = "noetfield.research-trader-state.v1";
const UPSTREAM_PATH = "/api/state.json";
const DEFAULT_BASE = "https://noetfield-ai-trader.sina-kazemnezhad-ca.workers.dev";

const FETCH_TIMEOUT_MS = 5000;
/** The cycle changes once a day, so five minutes of edge age is invisible. */
const FRESH_TTL_SECONDS = 300;
const MAX_BODY_BYTES = 2 * 1024 * 1024;

function cacheKey(req) {
  const host = String((req.headers && req.headers.host) || "www.noetfield.com")
    .replace(/[^\w.\-:]/g, "");
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
    // Long retention on purpose: this entry is the last-known-good used when
    // upstream is down. Every copy carries observedAtIso, so its age is always
    // visible and a stale reading can never pass as a current one.
    await caches.default.put(
      new Request(key, { method: "GET" }),
      new Response(JSON.stringify(body), {
        headers: { "content-type": "application/json", "cache-control": "max-age=604800" },
      })
    );
  } catch (err) {
    /* the cache is an optimisation, never a dependency */
  }
}

/** Re-date a cached payload against the current clock, so a cache hit never
    carries a frozen freshness verdict. */
function reclass(cached, nowMs) {
  const completed = Date.parse(cached.cycle && cached.cycle.completedAtIso);
  const ageSeconds = Number.isFinite(completed) ? Math.round((nowMs - completed) / 1000) : null;
  return Object.assign({}, cached, {
    source: "edge-cache",
    freshness: {
      ageSeconds: ageSeconds,
      class: classify(ageSeconds),
      computedFrom: "completedAtIso",
    },
  });
}

module.exports = async function handler(req, res) {
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
  const upstream = { base: base, path: UPSTREAM_PATH };
  const key = cacheKey(req);
  const nowMs = Date.now();

  // The Pages node-handler adapter has no error boundary, so an uncaught throw
  // here would leave the runtime to answer with an HTML 500. Everything stays
  // inside this try.
  try {
    const cached = await readCache(key);
    if (cached && cached.available === true && cached.observedAtIso) {
      const ageS = (nowMs - Date.parse(cached.observedAtIso)) / 1000;
      if (ageS >= 0 && ageS < FRESH_TTL_SECONDS) {
        return res.status(200).json(reclass(cached, nowMs));
      }
    }

    let normalized;
    try {
      const upstreamRes = await fetch(base + UPSTREAM_PATH, {
        headers: { Accept: "application/json", "User-Agent": "noetfield-www-research-trader" },
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
      });
      const ctype = String(upstreamRes.headers.get("content-type") || "");
      const clen = Number(upstreamRes.headers.get("content-length") || 0);
      if (upstreamRes.ok && ctype.indexOf("json") >= 0 && !(clen > MAX_BODY_BYTES)) {
        const raw = await upstreamRes.json().catch(function () { return null; });
        normalized = normalize(raw, nowMs);
      } else {
        normalized = {
          available: false,
          reason: upstreamRes.ok ? "upstream_malformed" : "upstream_status",
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
          upstream: upstream,
        },
        normalized
      );
      // Only validated payloads are cached. One malformed-but-200 response
      // written here would poison the last-known-good for a week.
      await writeCache(key, body);
      return res.status(200).json(body);
    }

    if (cached && cached.available === true) {
      return res.status(200).json(reclass(cached, nowMs));
    }

    // 503 rather than a 200 carrying "no data": a 200 that means nothing is
    // available is itself a small untruth, and it hides outages from probes.
    return res.status(503).json({
      schema: SCHEMA,
      available: false,
      reason: normalized.reason || "upstream_unreachable",
      observedAtIso: new Date(nowMs).toISOString(),
      upstream: upstream,
    });
  } catch (err) {
    console.error("research_trader_state_failed", err && err.message ? err.message : err);
    return res.status(503).json({
      schema: SCHEMA,
      available: false,
      reason: "upstream_unreachable",
      observedAtIso: new Date(nowMs).toISOString(),
      upstream: upstream,
    });
  }
};
