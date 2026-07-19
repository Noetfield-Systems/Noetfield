/** Allowlisted public Motor dispatch from www.noetfield.com (staging by default). */

const { buildSignedHeaders } = require("./runway-hmac");

const DEFAULT_BASE =
  "https://noetfield-runway-runtime-api-staging.sina-kazemnezhad-ca.workers.dev";
const DEFAULT_KEY_ID = "staging-proof";

const PUBLIC_RECIPES = Object.freeze({
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
          evidence_urls: ["https://example.com/a"],
        },
        {
          vendor_id: "b",
          name: "Vendor B",
          scores: { security: 0.7, fit: 0.9 },
          evidence_urls: ["https://example.com/b"],
        },
      ],
    }),
  }),
});

function runtimeConfig(env) {
  const source = env || process.env || {};
  const secret = String(source.RUNWAY_RUNTIME_API_SECRET || "").trim();
  const baseUrl = String(source.RUNWAY_RUNTIME_BASE_URL || DEFAULT_BASE)
    .trim()
    .replace(/\/$/, "");
  const keyId = String(source.RUNWAY_RUNTIME_KEY_ID || DEFAULT_KEY_ID).trim();
  return { secret, baseUrl, keyId, configured: Boolean(secret && baseUrl && keyId) };
}

function listPublicRecipes() {
  return Object.values(PUBLIC_RECIPES).map((recipe) => ({
    recipe_id: recipe.recipe_id,
    runway_id: recipe.runway_id,
    recipe_version: recipe.recipe_version,
    label: recipe.label,
  }));
}

function resolveRecipe(recipeId) {
  const key = String(recipeId || "vendor-decision-brief").trim();
  return PUBLIC_RECIPES[key] || null;
}

function buildPublicIntake(recipe, idempotencyKey) {
  return {
    schema: "noetfield.job-intake.v0.1",
    tenant_id: "tenant-www-public-demo",
    entitlement_id: "ent-www-public-demo",
    runway_id: recipe.runway_id,
    recipe_id: recipe.recipe_id,
    recipe_version: recipe.recipe_version,
    idempotency_key: idempotencyKey,
    requested_at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    caller_site: "noetfield.com",
    budget_usd: 25,
    input: { goal: recipe.goal },
  };
}

function makeIdempotencyKey(recipeId) {
  const stamp = Date.now().toString(36);
  const rand = Math.random().toString(36).slice(2, 10);
  return `www-${recipeId.slice(0, 24)}-${stamp}-${rand}`.slice(0, 128);
}

async function signedFetch(config, method, path, payload) {
  const bodyBytes =
    payload == null
      ? new Uint8Array(0)
      : new TextEncoder().encode(JSON.stringify(payload));
  const headers = await buildSignedHeaders({
    secret: config.secret,
    keyId: config.keyId,
    method,
    path,
    bodyBytes,
  });
  const response = await fetch(`${config.baseUrl}${path}`, {
    method,
    headers,
    body: payload == null ? undefined : bodyBytes,
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
        recipes: listPublicRecipes(),
      },
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
        recipes: listPublicRecipes(),
      },
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
        detail: (result.json && (result.json.detail || result.json.error)) || "Motor rejected the job.",
        motor_status: result.status,
        intake_fallback: "/contact/?topic=enterprise-governance",
      },
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
      note: "Staging Motor dispatch. Paid customer delivery is not claimed.",
    },
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
        detail: "Live Motor dispatch is not configured on this surface yet.",
      },
    };
  }

  const id = String(jobId || "").trim();
  if (!/^[A-Za-z0-9._:-]{8,128}$/.test(id)) {
    return {
      ok: false,
      httpStatus: 400,
      body: { ok: false, code: "JOB_ID_INVALID", detail: "job_id is required." },
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
        environment: "staging",
      },
    };
  }
  if (result.status !== 200) {
    return {
      ok: false,
      httpStatus: result.status >= 400 && result.status < 600 ? result.status : 502,
      body: {
        ok: false,
        code: "MOTOR_STATUS_FAILED",
        detail: (result.json && (result.json.detail || result.json.error)) || "Could not read job status.",
        motor_status: result.status,
        job_id: id,
      },
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
      result: result.json,
    },
  };
}

module.exports = {
  PUBLIC_RECIPES,
  runtimeConfig,
  listPublicRecipes,
  resolveRecipe,
  buildPublicIntake,
  dispatchPublicJob,
  readPublicJobStatus,
};
