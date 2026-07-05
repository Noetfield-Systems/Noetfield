/** GET /api/public/chat/greeting — platform proxy; disk SSOT fallback on www. */

const fs = require("fs");
const path = require("path");

function localGreetingPayload() {
  try {
    const file = path.join(process.cwd(), "data/chatbot/public-chat-greeting.json");
    const data = JSON.parse(fs.readFileSync(file, "utf8"));
    return {
      greeting: String(data.greeting || "").trim(),
      citations: Array.isArray(data.citations) ? data.citations : [],
      source: "www-disk-ssot",
    };
  } catch (_) {
    return {
      greeting: "Hi — what are you working on?",
      citations: ["/pricing/"],
      source: "www-minimal-fallback",
    };
  }
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  try {
    const r = await fetch(platformBase + "/api/public/chat/greeting", {
      headers: { Accept: "application/json" },
    });
    if (r.ok) {
      const body = await r.json().catch(function () {
        return {};
      });
      if (body && body.greeting) {
        return res.status(200).json({
          ok: true,
          mode: "platform-proxy",
          platform_base: platformBase,
          ...body,
        });
      }
    }
  } catch (_) {
    /* www-local spine */
  }

  return res.status(200).json({
    ok: true,
    mode: "www-disk-ssot",
    ...localGreetingPayload(),
  });
};
