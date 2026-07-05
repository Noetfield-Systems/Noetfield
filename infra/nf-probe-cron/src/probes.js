/** @typedef {{ ok: boolean, probe: string, status: string, reason?: string, receipt: Record<string, unknown> }} ProbeResult */

const PROBE_NAMES = ["uptime", "greeting", "drift", "intake_e2e"];

/**
 * @param {string} url
 * @param {RequestInit} [init]
 */
async function fetchJson(url, init = {}) {
  const res = await fetch(url, {
    ...init,
    headers: {
      Accept: "application/json",
      "User-Agent": "noetfield-probe-cron/1.0",
      ...(init.headers || {}),
    },
  });
  const text = await res.text();
  let body = {};
  try {
    body = text ? JSON.parse(text) : {};
  } catch {
    body = { detail: text.slice(0, 500) };
  }
  return { status: res.status, body };
}

/**
 * @param {Record<string, string>} env
 * @param {string} table
 * @param {Record<string, unknown>} row
 */
async function supabaseInsert(env, table, row) {
  const base = (env.SUPABASE_URL || "").replace(/\/$/, "");
  const key = env.SUPABASE_SERVICE_ROLE_KEY || "";
  if (!base || !key) {
    return { ok: false, error: "supabase_not_configured" };
  }
  const res = await fetch(`${base}/rest/v1/${table}`, {
    method: "POST",
    headers: {
      apikey: key,
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify(row),
  });
  if (!res.ok) {
    const detail = await res.text();
    return { ok: false, error: `supabase_${res.status}:${detail.slice(0, 200)}` };
  }
  return { ok: true };
}

/**
 * @param {Record<string, string>} env
 * @param {string} text
 */
async function sendTelegram(env, text) {
  const token = env.TELEGRAM_NOETFIELD_OPS_BOT_TOKEN || "";
  const chatId = env.TELEGRAM_OPS_CHAT_ID || "";
  if (!token || !chatId) {
    return { ok: false, error: "telegram_not_configured" };
  }
  const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text: text.slice(0, 4096),
      parse_mode: "HTML",
      disable_web_page_preview: true,
    }),
  });
  const body = await res.json().catch(() => ({}));
  return { ok: Boolean(body.ok), error: body.description };
}

/**
 * @param {Record<string, string>} env
 * @returns {Promise<ProbeResult>}
 */
export async function probeUptime(env) {
  const wwwBase = (env.WWW_BASE || "https://www.noetfield.com").replace(/\/$/, "");
  const platformBase = (env.PLATFORM_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  const receipt = { www: {}, platform: {} };

  const www = await fetchJson(`${wwwBase}/health`);
  receipt.www = { status: www.status, body: www.body };
  const platform = await fetchJson(`${platformBase}/api/public/chat/health`);
  receipt.platform = { status: platform.status, body: platform.body };

  const wwwOk = www.status === 200 && www.body && www.body.status === "ok";
  const platformOk = platform.status === 200;
  const ok = wwwOk && platformOk;
  return {
    ok,
    probe: "uptime",
    status: ok ? "pass" : "fail",
    reason: ok
      ? undefined
      : !wwwOk
        ? "www_health_failed"
        : "platform_health_failed",
    receipt,
  };
}

/**
 * @param {Record<string, string>} env
 * @returns {Promise<ProbeResult>}
 */
export async function probeGreeting(env) {
  const wwwBase = (env.WWW_BASE || "https://www.noetfield.com").replace(/\/$/, "");
  const platformBase = (env.PLATFORM_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  const expected = (env.GREETING_SSOT_HASH || "").trim();
  const receipt = { expected_hash: expected || null, platform_hash: null, www_hash: null };

  if (!expected) {
    return {
      ok: false,
      probe: "greeting",
      status: "error",
      reason: "greeting_ssot_hash_missing",
      receipt,
    };
  }

  const platform = await fetchJson(`${platformBase}/api/public/chat/health`);
  const greeting = platform.body && platform.body.greeting_ssot;
  if (greeting && typeof greeting === "object") {
    receipt.platform_hash = greeting.content_hash || null;
  }

  const asset = await fetch(`${wwwBase}/assets/nf-chat-greeting-ssot.js`, {
    headers: { "User-Agent": "noetfield-probe-cron/1.0" },
  });
  const assetText = await asset.text();
  const match = assetText.match(/sha256=([a-f0-9]{64})/);
  receipt.www_hash = match ? match[1] : null;

  const platformOk = receipt.platform_hash === expected;
  const wwwOk = receipt.www_hash === expected;
  const ok = platformOk && wwwOk && asset.status === 200;
  return {
    ok,
    probe: "greeting",
    status: ok ? "pass" : "fail",
    reason: ok
      ? undefined
      : !wwwOk
        ? "www_greeting_hash_mismatch"
        : "platform_greeting_hash_mismatch",
    receipt,
  };
}

/**
 * @param {Record<string, string>} env
 * @returns {Promise<ProbeResult>}
 */
export async function probeDrift(env) {
  const platformBase = (env.PLATFORM_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  const expectedSha = (env.EXPECTED_GIT_SHA || "").trim();
  const receipt = { expected_git_sha: expectedSha || null, live_git_sha: null };

  const platform = await fetchJson(`${platformBase}/api/public/chat/health`);
  receipt.live_git_sha = platform.body && platform.body.git_sha ? String(platform.body.git_sha) : null;

  if (!expectedSha) {
    return {
      ok: true,
      probe: "drift",
      status: "pass",
      reason: "expected_git_sha_not_configured",
      receipt,
    };
  }

  const live = receipt.live_git_sha || "";
  const ok = platform.status === 200 && (live === expectedSha || live.startsWith(expectedSha.slice(0, 12)));
  return {
    ok,
    probe: "drift",
    status: ok ? "pass" : "fail",
    reason: ok ? undefined : "platform_git_sha_drift",
    receipt,
  };
}

/**
 * @param {Record<string, string>} env
 * @returns {Promise<ProbeResult>}
 */
export async function probeIntakeE2e(env) {
  const wwwBase = (env.WWW_BASE || "https://www.noetfield.com").replace(/\/$/, "");
  const platformBase = (env.PLATFORM_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  const intakeUrl = `${wwwBase}/api/intake`;
  const requestId = `RID-PROBE-${Math.floor(Date.now() / 1000)}`;
  const body = {
    organization: "NF Probe Cron",
    contact_name: "NF Probe Bot",
    contact_email: "probe@noetfield.com",
    message: `Automated probe intake — ${new Date().toISOString()}. Ignore.`,
    request_id: requestId,
    sku: "general",
    vector: "contact",
    source: "api",
    metadata: { form_id: "nf_probe_cron", topic: "probe" },
  };
  const receipt = { request_id: requestId, submit: null, dedupe: null };

  const health = await fetchJson(`${platformBase}/api/intake/health`);
  if (health.status !== 200 || health.body.storage !== "postgres") {
    return {
      ok: false,
      probe: "intake_e2e",
      status: "fail",
      reason: "platform_storage_not_postgres",
      receipt: { ...receipt, health },
    };
  }

  const submit = await fetchJson(intakeUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  receipt.submit = { status: submit.status, body: submit.body };

  const intakeId = submit.body && submit.body.intake_id ? String(submit.body.intake_id) : "";
  const telegramOk = Boolean(submit.body && submit.body.telegram_delivered);
  if (submit.status < 200 || submit.status >= 300 || !intakeId) {
    return {
      ok: false,
      probe: "intake_e2e",
      status: "fail",
      reason: "intake_submit_failed",
      receipt,
    };
  }
  if (!telegramOk) {
    return {
      ok: false,
      probe: "intake_e2e",
      status: "fail",
      reason: "telegram_not_delivered",
      receipt,
    };
  }

  const dedupe = await fetchJson(intakeUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  receipt.dedupe = { status: dedupe.status, intake_id: dedupe.body && dedupe.body.intake_id };
  const dedupeOk =
    dedupe.status >= 200 &&
    dedupe.status < 300 &&
    String((dedupe.body && dedupe.body.intake_id) || "") === intakeId;

  return {
    ok: dedupeOk,
    probe: "intake_e2e",
    status: dedupeOk ? "pass" : "fail",
    reason: dedupeOk ? undefined : "db_dedupe_failed",
    receipt,
  };
}

/** @type {Record<string, (env: Record<string, string>) => Promise<ProbeResult>>} */
export const PROBES = {
  uptime: probeUptime,
  greeting: probeGreeting,
  drift: probeDrift,
  intake_e2e: probeIntakeE2e,
};

export { PROBE_NAMES };

/**
 * @param {Record<string, string>} env
 */
export async function runAllProbes(env) {
  const runId = crypto.randomUUID();
  const checkedAt = new Date().toISOString();
  const results = [];

  for (const name of PROBE_NAMES) {
    const fn = PROBES[name];
    let result;
    try {
      result = await fn(env);
    } catch (err) {
      result = {
        ok: false,
        probe: name,
        status: "error",
        reason: err && err.message ? err.message : "probe_error",
        receipt: {},
      };
    }

    await supabaseInsert(env, "probe_cron_receipts", {
      run_id: runId,
      probe_name: name,
      status: result.status,
      receipt: {
        ...result.receipt,
        ok: result.ok,
        reason: result.reason || null,
        pass_definition: name === "intake_e2e" ? "telegram_delivered_and_db_dedupe" : null,
        checked_at: checkedAt,
      },
      checked_at: checkedAt,
    });

    if (!result.ok && result.status !== "pass") {
      await supabaseInsert(env, "improvement_queue", {
        finding: result.reason || `${name}_failed`,
        source: `probe_cron:${name}`,
        expected_roi: name === "intake_e2e" ? "ops_intake_reliability" : "www_uptime_visibility",
        machine_safe: name === "drift" || name === "greeting",
        status: "open",
        metadata: { run_id: runId, receipt: result.receipt },
      });
    }

    results.push(result);
  }

  const failures = results.filter((r) => !r.ok);
  if (failures.length) {
    const lines = failures.map(
      (f) => `• <b>${f.probe}</b>: ${f.reason || f.status}`
    );
    await sendTelegram(
      env,
      `<b>Noetfield probe cron FAIL</b>\nrun_id: ${runId}\n` + lines.join("\n")
    );
  }

  return { runId, checkedAt, results, ok: failures.length === 0 };
}
