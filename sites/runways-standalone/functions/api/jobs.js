/**
 * Standalone Pages Function — allowlisted Motor dispatch (Web Crypto HMAC).
 * POST /api/jobs  ·  GET /api/jobs/status?job_id=
 */

const DEFAULT_BASE =
  "https://noetfield-runway-runtime-api-staging.sina-kazemnezhad-ca.workers.dev";
const DEFAULT_KEY_ID = "staging-proof";

const RECIPE = {
  runway_id: "research",
  recipe_id: "vendor-decision-brief",
  recipe_version: "0.1.0",
  goal: {
    question: "Which vendor best fits a bounded document-automation scope?",
    scope: "Document automation (public demo)",
    criteria: ["security", "fit"],
    weights: { security: 0.6, fit: 0.4 },
    options: [
      { vendor_id: "a", name: "Vendor A", scores: { security: 0.9, fit: 0.8 }, evidence_urls: ["https://example.com/a"] },
      { vendor_id: "b", name: "Vendor B", scores: { security: 0.7, fit: 0.9 }, evidence_urls: ["https://example.com/b"] },
    ],
  },
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "access-control-allow-origin": "*",
    },
  });
}

function toHex(buf) {
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function sha256Hex(bytes) {
  return toHex(await crypto.subtle.digest("SHA-256", bytes));
}

async function hmacHex(secret, message) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  return toHex(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message)));
}

async function signedFetch(env, method, path, payload) {
  const secret = String(env.RUNWAY_RUNTIME_API_SECRET || "").trim();
  const baseUrl = String(env.RUNWAY_RUNTIME_BASE_URL || DEFAULT_BASE).replace(/\/$/, "");
  const keyId = String(env.RUNWAY_RUNTIME_KEY_ID || DEFAULT_KEY_ID).trim();
  if (!secret) {
    return { status: 503, body: { ok: false, code: "MOTOR_DISPATCH_UNCONFIGURED", detail: "RUNWAY_RUNTIME_API_SECRET missing on this Pages project." } };
  }
  const bodyBytes = payload == null ? new Uint8Array(0) : new TextEncoder().encode(JSON.stringify(payload));
  const timestamp = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const nonce = toHex(crypto.getRandomValues(new Uint8Array(16)));
  const canonical = `${method}\n${path}\n${timestamp}\n${nonce}\n${await sha256Hex(bodyBytes)}`;
  const signature = await hmacHex(secret, canonical);
  const res = await fetch(`${baseUrl}${path}`, {
    method,
    headers: {
      authorization: `NOETFIELD-HMAC ${keyId}:${signature}`,
      "x-noetfield-timestamp": timestamp,
      "x-noetfield-nonce": nonce,
      "content-type": "application/json",
      accept: "application/json",
      "user-agent": "Noetfield-Runways-Standalone/1.0",
    },
    body: payload == null ? undefined : bodyBytes,
  });
  const text = await res.text();
  let parsed = null;
  try {
    parsed = text ? JSON.parse(text) : null;
  } catch {
    parsed = { raw: text.slice(0, 400) };
  }
  return { status: res.status, body: parsed };
}

function buildIntake() {
  const stamp = Date.now().toString(36);
  const rand = Math.random().toString(36).slice(2, 10);
  return {
    schema: "noetfield.job-intake.v0.1",
    tenant_id: "tenant-staging-proof",
    entitlement_id: "ent-staging-proof",
    runway_id: RECIPE.runway_id,
    recipe_id: RECIPE.recipe_id,
    recipe_version: RECIPE.recipe_version,
    idempotency_key: `standalone-${stamp}-${rand}`.slice(0, 128),
    requested_at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    caller_site: "noetfield.com",
    budget_usd: 25,
    input: { goal: RECIPE.goal },
  };
}

export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "GET, POST, OPTIONS",
        "access-control-allow-headers": "Content-Type, Accept",
      },
    });
  }

  if (url.pathname.endsWith("/status") || url.searchParams.has("job_id") && url.pathname.includes("status")) {
    if (request.method !== "GET") return json({ detail: "Method not allowed" }, 405);
    const jobId = url.searchParams.get("job_id") || "";
    if (!/^[A-Za-z0-9._:-]{8,128}$/.test(jobId)) {
      return json({ ok: false, code: "JOB_ID_INVALID", detail: "job_id required" }, 400);
    }
    const result = await signedFetch(env, "GET", `/v1/jobs/${encodeURIComponent(jobId)}/result`, null);
    if (result.status === 409) {
      return json({ ok: true, job_id: jobId, status: "running", environment: "staging" }, 202);
    }
    if (result.status !== 200) {
      return json(
        {
          ok: false,
          code: "MOTOR_STATUS_FAILED",
          detail: (result.body && (result.body.detail || result.body.error)) || "status failed",
          motor_status: result.status,
        },
        result.status >= 400 && result.status < 600 ? result.status : 502
      );
    }
    return json({
      ok: true,
      job_id: jobId,
      environment: "staging",
      status: result.body.status || "unknown",
      result: result.body,
    });
  }

  if (request.method === "GET") {
    return json({
      ok: true,
      service: "noetfield-runways-standalone",
      recipe_id: RECIPE.recipe_id,
      intake_fallback: "https://www.noetfield.com/contact/?topic=enterprise-governance",
    });
  }

  if (request.method !== "POST") return json({ detail: "Method not allowed" }, 405);

  const result = await signedFetch(env, "POST", "/v1/jobs", buildIntake());
  if (result.status !== 200 && result.status !== 202) {
    return json(
      {
        ok: false,
        code: "MOTOR_DISPATCH_FAILED",
        detail: (result.body && (result.body.detail || result.body.error)) || "Motor rejected job",
        motor_status: result.status,
        intake_fallback: "https://www.noetfield.com/contact/?topic=enterprise-governance",
      },
      result.status >= 400 && result.status < 600 ? result.status : 502
    );
  }

  const jobId = result.body && result.body.job_id;
  return json(
    {
      ok: true,
      environment: "staging",
      recipe_id: RECIPE.recipe_id,
      job_id: jobId,
      status_path: jobId ? `/api/jobs/status?job_id=${encodeURIComponent(jobId)}` : null,
      note: "Standalone product surface · staging Motor · paid delivery not claimed",
    },
    202
  );
}
