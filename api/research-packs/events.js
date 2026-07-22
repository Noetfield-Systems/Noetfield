/** POST /api/research-packs/events — funnel events for Research packs. */

function cryptoRandomId(prefix) {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
  return `${prefix}${hex}`;
}

module.exports = async function handler(req, res) {
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
  const event_name = String(body.event_name || "").trim();
  if (!event_name) {
    return res.status(400).json({ error: "EVENT_NAME_REQUIRED" });
  }

  const event_id = cryptoRandomId("event_");
  const recorded_at = new Date().toISOString();
  const platformBase = String(
    process.env.PLATFORM_API_BASE || "https://platform.noetfield.com"
  ).replace(/\/$/, "");

  try {
    await fetch(platformBase + "/api/analytics/event", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "User-Agent": "noetfield-www-research-packs",
      },
      body: JSON.stringify({
        event_name: event_name.slice(0, 160),
        route: String(body.route || "/research-packs/").slice(0, 320),
        source: String(body.source || "research-packs-www").slice(0, 120),
        recipe_id: String(body.recipe_id || "").slice(0, 120),
        caller_site: String(body.caller_site || "noetfield.com").slice(0, 120),
        event_id,
        recorded_at,
      }),
    });
  } catch (err) {
    console.error("research_packs_event_forward_failed", err && err.message ? err.message : err);
  }

  return res.status(200).json({
    ok: true,
    event_id,
    next: { kind: "event_recorded", at: recorded_at },
  });
};
