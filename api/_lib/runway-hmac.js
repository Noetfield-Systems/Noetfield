/** HMAC request signing for Noetfield Runway Cloud Runtime (Web Crypto — Workers-safe). */

function toHex(buffer) {
  return Array.from(new Uint8Array(buffer), (b) => b.toString(16).padStart(2, "0")).join("");
}

function utf8(text) {
  return new TextEncoder().encode(text);
}

async function sha256Hex(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return toHex(digest);
}

async function hmacSha256Hex(secret, message) {
  const key = await crypto.subtle.importKey(
    "raw",
    utf8(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, utf8(message));
  return toHex(sig);
}

function randomNonceHex() {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return toHex(bytes);
}

async function signRequest(secret, method, path, timestamp, nonce, bodyBytes) {
  const bodyHash = await sha256Hex(bodyBytes);
  const canonical = `${method.toUpperCase()}\n${path}\n${timestamp}\n${nonce}\n${bodyHash}`;
  return hmacSha256Hex(secret, canonical);
}

async function buildSignedHeaders({ secret, keyId, method, path, bodyBytes }) {
  const timestamp = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const nonce = randomNonceHex();
  const signature = await signRequest(secret, method, path, timestamp, nonce, bodyBytes);
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
