#!/usr/bin/env python3
"""Public read/nonce-only Noetfield Onchain smoke. Never creates members, XP, or funds."""
from __future__ import annotations

import json
import secrets
import urllib.error
import urllib.request

BASE = "https://platform.noetfield.com/api/v1/onchain"
ORIGIN = "https://www.noetfield.com"


def call(path: str, method: str = "GET", payload: dict | None = None) -> tuple[int, dict, dict]:
    headers = {"Accept": "application/json", "Origin": ORIGIN}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            body = res.read().decode("utf-8")
            return res.status, json.loads(body) if body else {}, dict(res.headers)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8") or "{}"), dict(e.headers)


def main() -> None:
    status, data, cors = call("/status")
    assert status == 200, ("status http", status, data)
    assert data.get("database_ready") is True, "Production PostgreSQL participation tables unavailable"
    assert data.get("daily_quest", {}).get("status") == "active", "Daily XP not active"
    assert data.get("token", {}).get("issued") is False, "Do not treat token as minted without verified contract"
    assert {k.lower(): v for k, v in cors.items()}.get("access-control-allow-origin") == ORIGIN, "Official website CORS missing"
    wallet = "0x" + secrets.token_hex(20)
    code, challenge, headers = call("/challenge", "POST", {"wallet": wallet})
    assert code == 200, (code, challenge)
    assert challenge.get("nonce"), "Nonce was not created in production"
    assert "www.noetfield.com wants you to sign in" in challenge.get("message", "")
    assert "Chain ID: 8453" in challenge.get("message", "")
    assert "does not transfer funds" in challenge.get("message", "")
    assert {k.lower(): v for k, v in headers.items()}.get("access-control-allow-origin") == ORIGIN
    invalid_sig = "0x" + "00" * 65
    rejected, response, _ = call("/verify", "POST", {
        "wallet": wallet, "nonce": challenge["nonce"], "signature": invalid_sig
    })
    assert rejected == 401, ("Invalid signature unexpectedly accepted", rejected, response)
    print("PASS onchain live: Postgres status, EIP-191 challenge, official CORS and invalid signature rejected. No member, XP or money created.")


if __name__ == "__main__":
    main()
