/** Shared helpers for noetfield.com product job gateway proxy routes. */

function platformBase() {
  return (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
}

function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
}

async function forwardPlatform(req, res, { method, path, body }) {
  cors(res);
  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }
  if (req.method !== method) {
    return res.status(405).json({ detail: "Method not allowed" });
  }
  const url = platformBase() + path;
  const init = {
    method,
    headers: { Accept: "application/json" },
  };
  if (body !== undefined) {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(body);
  }
  try {
    const upstream = await fetch(url, init);
    const payload = await upstream.json().catch(function () {
      return { detail: "invalid upstream json" };
    });
    return res.status(upstream.status).json(payload);
  } catch (err) {
    return res.status(502).json({
      error: "PLATFORM_UNREACHABLE",
      detail: err && err.message ? err.message : String(err),
    });
  }
}

module.exports = {
  platformBase,
  cors,
  forwardPlatform,
};
