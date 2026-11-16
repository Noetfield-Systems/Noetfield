/** POST /api/public/chat — proxies platform chat; GET returns greeting SSOT. */

const CANONICAL_INTAKE = "operations@noetfield.com";
const EXECUTIVE_OVERVIEW_REPLY =
  "Noetfield Systems builds intelligent infrastructure for real businesses. " +
  "Founders can explore the AI Software Builder to shape software projects. Businesses can commission AI workflow automation through Company OS, including a scoped lead-to-follow-up pilot. " +
  "Asset owners and capital professionals can explore Real-World Capital: readiness assessment, rights and workflow mapping, and scoped digital-asset technology services. " +
  "Builders and commercial partners can propose collaborations, while anyone interested in the products can join the free founding community. " +
  "Start with a product, tell us the business problem, or share a concrete opportunity; technical evidence is available separately.";

const EXECUTIVE_OVERVIEW_CITATIONS = [
  "/",
  "/company-os/",
  "/real-world-capital/",
  "/work-with-us/",
  "/community/",
  "/connect/",
];

function executiveOverviewReply(provider) {
  return {
    reply: EXECUTIVE_OVERVIEW_REPLY,
    provider,
    citations: EXECUTIVE_OVERVIEW_CITATIONS,
    intake_email: CANONICAL_INTAKE,
  };
}

function isExecutiveOverview(message) {
  const text = String(message || "").toLowerCase();
  return (
    text === "executive overview" ||
    text.includes("help me understand noetfield") ||
    text.includes("what is noetfield") ||
    text.includes("what does noetfield do")
  );
}

function isStaleInfrastructureReply(reply) {
  const text = String(reply || "").toLowerCase();
  return (
    text.includes("noetfield produces the audit trail a regulated copilot rollout") ||
    text.includes("noetfield provides governance execution infrastructure") ||
    (text.includes("record a compliance log") && text.includes("allow or deny decisions")) ||
    (text.includes("our offerings include the trust brief") && text.includes("support compliance and risk management"))
  );
}

function isInternalSourceLeakReply(reply) {
  const text = String(reply || "").toLowerCase();
  return (
    text.includes("offerings_locked") ||
    text.includes("product_brief") ||
    text.includes("positioning.md") ||
    text.includes("faq.md") ||
    text.includes("gel-runtime.md") ||
    text.includes("knowledge/") ||
    text.includes("docs/") ||
    text.includes("source:")
  );
}

function publicGuidanceReply(provider) {
  return {
    reply:
      "Tell us your goal and we can point you to the right place: software projects through the AI Software Builder, AI Business Operations through Company OS, or Real-World Capital for asset and digital-capital workflows. " +
      "For a business project use /connect/; for collaboration use /work-with-us/; for free product and community updates use /community/. " +
      "Specialized Copilot governance services have their own scope and intake pages.",
    provider,
    citations: ["/", "/company-os/", "/real-world-capital/", "/connect/", "/work-with-us/", "/community/"],
    intake_email: CANONICAL_INTAKE,
  };
}

function routeOnlyFallback() {
  return {
    reply:
      "I’m having trouble reaching the live assistant right now. " +
      "Explore the AI Software Builder, business automation at /company-os/, or asset services at /real-world-capital/. For a project or partnership, use /connect/ or email " +
      CANONICAL_INTAKE +
      ".",
    citations: ["/", "/company-os/", "/real-world-capital/", "/connect/"],
  };
}

function localGreetingPayload() {
  try {
    const data = require("../_lib/greeting-ssot.json");
    const greeting = String(data.greeting || "").trim();
    const citations = Array.isArray(data.citations) ? data.citations : [];
    return {
      greeting,
      citations,
      content_hash: String(data.content_hash || ""),
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

async function serveGreeting(res, platformBase) {
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
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");

  if (req.method === "GET") {
    return serveGreeting(res, platformBase);
  }

  if (req.method !== "POST") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const body = req.body && typeof req.body === "object" ? req.body : {};
  const message = String(body.message || "").trim();
  if (!message) {
    return res.status(400).json({ detail: "message is required" });
  }
  if (message.length > 2000) {
    return res.status(400).json({ detail: "message too long" });
  }
  if (isExecutiveOverview(message)) {
    return res.status(200).json(executiveOverviewReply("www-controlled-executive-overview"));
  }

  try {
    const r = await fetch(platformBase + "/api/public/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ message: message, session_id: body.session_id || null }),
    });
    if (r.ok) {
      const data = await r.json().catch(function () {
        return null;
      });
      if (data && data.reply) {
        if (isStaleInfrastructureReply(data.reply)) {
          return res.status(200).json(executiveOverviewReply("www-stale-platform-guard"));
        }
        if (isInternalSourceLeakReply(data.reply)) {
          return res.status(200).json(publicGuidanceReply("www-source-leak-guard"));
        }
        return res.status(200).json(data);
      }
    }
  } catch (_) {
    /* fall through to www-local */
  }

  const picked = routeOnlyFallback();
  return res.status(200).json({
    reply: picked.reply,
    provider: "www-routing-fallback",
    citations: picked.citations,
    intake_email: CANONICAL_INTAKE,
  });
};
