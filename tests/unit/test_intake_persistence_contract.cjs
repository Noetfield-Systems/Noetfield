"use strict";
/** Contract tests: a notification fallback must never impersonate a stored intake. */
const test = require("node:test");
const assert = require("node:assert/strict");

const handlerPath = require.resolve("../../api/intake.js");
const dependencyPaths = {
  email: require.resolve("../../api/_lib/intake-email.js"),
  test: require.resolve("../../api/_lib/intake-test.js"),
  telegram: require.resolve("../../api/_lib/intake-telegram.js"),
  discord: require.resolve("../../api/_lib/notify-discord.js"),
};

function response() {
  return {
    code: null, body: null,
    setHeader() {},
    status(code) { this.code = code; return this; },
    json(data) { this.body = data; return this; },
    end() { return this; },
  };
}

async function invoke({ platformOk = false, platformData = {},
                        telegram = false, email = false }) {
  const previousFetch = global.fetch;
  const original = Object.fromEntries(
    Object.entries(dependencyPaths).map(([k, p]) => [k, require.cache[p]])
  );
  const originalHandler = require.cache[handlerPath];
  try {
    global.fetch = async () => ({
      ok: platformOk,
      json: async () => platformData,
    });
    const fake = {
      email: {
        CANONICAL: "operations@example.invalid",
        emailConfigured: () => true,
        opsBodyText: () => "Test",
        sendIntakeEmails: async () => ({ ops: email, ack: false }),
      },
      test: {
        isTestIntake: () => false,
        ensureTestMetadata: value => value,
      },
      telegram: {
        telegramConfigured: () => true,
        sendIntakeTelegram: async () => ({ ok: telegram }),
        telegramPathOk: value => Boolean(value.ok),
      },
      discord: {
        discordConfigured: () => false,
        sendIntakeDiscord: async () => ({ ok: false }),
        discordPathOk: () => false,
      },
    };
    for (const [key, modulePath] of Object.entries(dependencyPaths)) {
      require.cache[modulePath] = { id: modulePath, filename: modulePath,
                                    loaded: true, exports: fake[key] };
    }
    delete require.cache[handlerPath];
    const handler = require(handlerPath);
    const res = response();
    await handler({
      method: "POST",
      body: {
        vector: "work-with-us-contributor",
        contact_email: "human@example.invalid",
        request_id: "RID-EXISTING-1",
        message: "I can deliver testing and evidence.",
        metadata: { application_kind: "human",
                    project_id: "buildrelay", role: "qa",
                    evidence_url: "https://example.invalid/proof" },
      },
    }, res);
    return res;
  } finally {
    global.fetch = previousFetch;
    for (const [key, modulePath] of Object.entries(dependencyPaths)) {
      if (original[key]) require.cache[modulePath] = original[key];
      else delete require.cache[modulePath];
    }
    if (originalHandler) require.cache[handlerPath] = originalHandler;
    else delete require.cache[handlerPath];
  }
}

test("stored platform record is the only accepted intake ID", async () => {
  const r = await invoke({
    platformOk: true,
    platformData: { intake_id: "INT-ABC123456789", request_id: "RID-EXISTING-1",
                    deduped: true },
    telegram: false, email: false,
  });
  assert.equal(r.code, 200);
  assert.equal(r.body.intake_id, "INT-ABC123456789");
  assert.equal(r.body.intake_persisted, true);
  assert.equal(r.body.submission_state, "PERSISTED");
  assert.equal(r.body.record_provenance, "platform-api-persisted");
});

test("Telegram-only notification cannot create a phantom Company OS record", async () => {
  const r = await invoke({ telegram: true });
  assert.equal(r.code, 202);
  assert.equal(r.body.intake_persisted, false);
  assert.equal(r.body.submission_state, "NOTIFIED_NOT_PERSISTED");
  assert.ok(r.body.notification_reference);
  assert.equal(Object.hasOwn(r.body, "intake_id"), false);
});

test("email-only notification cannot create a phantom Company OS record", async () => {
  const r = await invoke({ email: true });
  assert.equal(r.code, 202);
  assert.equal(r.body.intake_persisted, false);
  assert.equal(r.body.email_delivered, true);
  assert.equal(Object.hasOwn(r.body, "intake_id"), false);
});

test("HTTP 200 from Platform without stored intake ID does not claim persistence", async () => {
  const r = await invoke({ platformOk: true, platformData: { status: "ok" },
                           telegram: true });
  assert.equal(r.code, 202);
  assert.equal(r.body.intake_persisted, false);
  assert.equal(Object.hasOwn(r.body, "intake_id"), false);
});

test("all delivery paths failing returns error without stored intake ID", async () => {
  const r = await invoke({});
  assert.equal(r.code, 502);
  assert.equal(r.body.intake_persisted, false);
  assert.equal(r.body.submission_state, "NOT_DELIVERED");
  assert.equal(Object.hasOwn(r.body, "intake_id"), false);
});
