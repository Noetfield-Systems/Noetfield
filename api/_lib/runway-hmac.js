/** HMAC request signing for Noetfield Runway Cloud Runtime. */

const { createHmac, createHash, randomBytes } = require("node:crypto");

function sha256Hex(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function signRequest(secret, method, path, timestamp, nonce, bodyBytes) {
  const canonical = `${method.toUpperCase()}\n${path}\n${timestamp}\n${nonce}\n${sha256Hex(bodyBytes)}`;
  return createHmac("sha256", secret).update(canonical).digest("hex");
}

function buildSignedHeaders({ secret, keyId, method, path, bodyBytes }) {
  const timestamp = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const nonce = randomBytes(16).toString("hex");
  const signature = signRequest(secret, method, path, timestamp, nonce, bodyBytes);
  return {
    authorization: `NOETFIELD-HMAC ${keyId}:${signature}`,
    "x-noetfield-timestamp": timestamp,
    "x-noetfield-nonce": nonce,
    "content-type": "application/json",
    accept: "application/json",
    "user-agent": "Noetfield-WWW-Runway-Dispatch/1.0",
  };
}

module.exports = { sha256Hex, signRequest, buildSignedHeaders };
