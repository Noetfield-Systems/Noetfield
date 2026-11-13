"""Noetfield Onchain community: signed EVM wallet, durable XP, daily claims and qualified referrals.

This is a real PostgreSQL-backed participation ledger, NOT a token transfer,
custody system, investment waitlist approval, or a simulated in-browser balance.
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import re
import secrets
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

import asyncpg
from eth_account import Account
from eth_account.messages import encode_defunct
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict

router = APIRouter(prefix="/api/v1/onchain", tags=["onchain-community"])
_POOL: asyncpg.Pool | None = None
_LOCK = asyncio.Lock()
_WALLET = re.compile(r"^0x[a-fA-F0-9]{40}$")
_REF = re.compile(r"^[a-f0-9]{20}$")
_EMAIL = re.compile(r"^[^@\s]{1,110}@[^@\s]{1,200}\.[^@\s]{2,32}$")
_ALLOWED_ORIGINS = {"https://www.noetfield.com", "https://noetfield.com"}
_PROGRAM_ID = "noetfield-onchain-season-0"
_DAILY_BASE = 10
_REFERRAL_BONUS = 25

DDL = """
CREATE TABLE IF NOT EXISTS nf_onchain_members (
 wallet TEXT PRIMARY KEY,
 referral_code TEXT NOT NULL UNIQUE,
 referred_by TEXT REFERENCES nf_onchain_members(wallet),
 email TEXT,
 email_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
 first_joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 last_checkin DATE,
 checkin_streak INTEGER NOT NULL DEFAULT 0,
 leaderboard_opt_in BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE IF NOT EXISTS nf_onchain_nonces (
 nonce TEXT PRIMARY KEY,
 wallet TEXT NOT NULL,
 message TEXT NOT NULL,
 expires_at TIMESTAMPTZ NOT NULL,
 used_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS nf_onchain_nonces_expires_idx ON nf_onchain_nonces(expires_at);
CREATE TABLE IF NOT EXISTS nf_onchain_sessions (
 session_hash TEXT PRIMARY KEY,
 wallet TEXT NOT NULL REFERENCES nf_onchain_members(wallet) ON DELETE CASCADE,
 expires_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS nf_onchain_sessions_expires_idx ON nf_onchain_sessions(expires_at);
CREATE TABLE IF NOT EXISTS nf_onchain_checkins (
 wallet TEXT NOT NULL REFERENCES nf_onchain_members(wallet),
 day DATE NOT NULL,
 streak INTEGER NOT NULL,
 xp INTEGER NOT NULL,
 PRIMARY KEY(wallet,day)
);
CREATE TABLE IF NOT EXISTS nf_onchain_xp_ledger (
 id BIGSERIAL PRIMARY KEY,
 wallet TEXT NOT NULL REFERENCES nf_onchain_members(wallet),
 event_key TEXT NOT NULL UNIQUE,
 xp INTEGER NOT NULL CHECK (xp > 0 AND xp <= 100),
 reason TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS nf_onchain_xp_wallet_idx ON nf_onchain_xp_ledger(wallet);
CREATE TABLE IF NOT EXISTS nf_onchain_referral_qualifications (
 invitee_wallet TEXT PRIMARY KEY REFERENCES nf_onchain_members(wallet),
 inviter_wallet TEXT NOT NULL REFERENCES nf_onchain_members(wallet),
 awarded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

def wallet_address(value: str) -> str:
    if not _WALLET.fullmatch(value or ""):
        raise HTTPException(status_code=422, detail="Invalid EVM wallet address")
    return value.lower()


def daily_xp(streak: int) -> int:
    return _DAILY_BASE + 2 * min(max(streak - 1, 0), 7)


def valid_referral(value: str | None) -> bool:
    return bool(value and _REF.fullmatch(value))


def signed_message(wallet: str, nonce: str, issued_at: datetime, expires_at: datetime) -> str:
    # EIP-4361-compatible text wrapped with EIP-191 personal_sign.
    return (
        "www.noetfield.com wants you to sign in with your Ethereum account:\n"
        + wallet
        + "\n\nSign in to Noetfield Onchain to join the community and record "
        "your participation. Signing this message does not transfer funds."
        "\n\nURI: https://www.noetfield.com/onchain/"
        "\nVersion: 1\nChain ID: 8453\nNonce: " + nonce
        + "\nIssued At: " + issued_at.isoformat().replace("+00:00", "Z")
        + "\nExpiration Time: " + expires_at.isoformat().replace("+00:00", "Z")
    )


def check_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin and origin not in _ALLOWED_ORIGINS:
        raise HTTPException(status_code=403, detail="Unrecognized application origin")


async def pool() -> asyncpg.Pool:
    global _POOL
    if _POOL is not None and not _POOL._closed:
        return _POOL
    async with _LOCK:
        if _POOL is not None and not _POOL._closed:
            return _POOL
        dsn = (os.getenv("DATABASE_URL") or "").replace("postgresql+asyncpg://", "postgresql://")
        if not dsn:
            raise HTTPException(status_code=503, detail="Community database not configured")
        try:
            candidate = await asyncpg.create_pool(dsn, min_size=1, max_size=3, command_timeout=12)
            async with candidate.acquire() as conn:
                await conn.execute(DDL)
            _POOL = candidate
            return candidate
        except Exception:
            raise HTTPException(status_code=503, detail="Community database unavailable") from None


async def close_community_pool() -> None:
    global _POOL
    if _POOL is not None:
        await _POOL.close()
        _POOL = None


class ChallengeIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    wallet: str


class VerifyIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    wallet: str
    nonce: str = Field(min_length=16, max_length=100)
    signature: str = Field(min_length=130, max_length=132)
    ref: str | None = Field(default=None, max_length=32)


class WaitlistIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str | None = Field(default=None, max_length=254)
    email_opt_in: bool = False
    interest: str = Field(default="ecosystem", max_length=48)


class PreferencesIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    leaderboard_opt_in: bool


async def current_wallet(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Connect and sign with your wallet first")
    token = authorization[7:].strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{36,100}", token):
        raise HTTPException(status_code=401, detail="Invalid session")
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    async with (await pool()).acquire() as conn:
        row = await conn.fetchrow(
            "SELECT wallet FROM nf_onchain_sessions WHERE session_hash=$1 AND expires_at>now()",
            digest,
        )
    if not row:
        raise HTTPException(status_code=401, detail="Session expired. Sign again.")
    return row["wallet"]


async def member_state(conn: asyncpg.Connection, wallet: str) -> dict:
    row = await conn.fetchrow(
        """SELECT m.wallet,m.referral_code,m.email_opt_in,m.last_checkin,m.checkin_streak,
            m.leaderboard_opt_in,COALESCE(SUM(l.xp),0)::int AS xp
            FROM nf_onchain_members m LEFT JOIN nf_onchain_xp_ledger l ON l.wallet=m.wallet
            WHERE m.wallet=$1
            GROUP BY m.wallet""",
        wallet,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Community wallet not registered")
    last = row["last_checkin"]
    today = datetime.now(UTC).date()
    return {
        "wallet": wallet, "xp": row["xp"], "streak": row["checkin_streak"],
        "last_checkin": last.isoformat() if last else None,
        "claim_available": last != today,
        "referral_code": row["referral_code"],
        "referral_url": "https://www.noetfield.com/onchain/hub/?ref=" + row["referral_code"],
        "leaderboard_opt_in": row["leaderboard_opt_in"],
        "email_opt_in": row["email_opt_in"],
        "program": _PROGRAM_ID,
        "xp_is_token": False, "token_claim_open": False,
    }


@router.get("/status")
async def public_status() -> dict:
    db_ready = False
    try:
        async with (await pool()).acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_ready = True
    except Exception:
        pass
    return {
        "program": _PROGRAM_ID,
        "wallet_auth": "eip191_personal_sign",
        "chain_id": 8453,
        "daily_quest": {"status": "active" if db_ready else "unavailable", "reward": "server-verified XP",
                        "base_xp": _DAILY_BASE, "streak_bonus_cap": 14},
        "referrals": {"status": "active" if db_ready else "unavailable", "reward_xp": _REFERRAL_BONUS,
                      "qualification": "referred wallet signs in and completes first daily check-in"},
        "token": {"name": "Noetfield Ecosystem Token", "symbol": "NFIELD",
                  "design_stage": "draft", "issued": False, "contract": None,
                  "swap_enabled": False, "airdrop_onchain": False},
        "database_ready": db_ready, "no_funds_moved": True,
    }


@router.post("/challenge")
async def challenge(req: ChallengeIn, request: Request) -> dict:
    check_origin(request)
    wallet = wallet_address(req.wallet)
    nonce = secrets.token_hex(16)
    now = datetime.now(UTC)
    expiry = now + timedelta(minutes=5)
    message = signed_message(wallet, nonce, now, expiry)
    async with (await pool()).acquire() as conn:
        # Cleanup stale challenges; rate cap for repeated requests to one wallet.
        await conn.execute("DELETE FROM nf_onchain_nonces WHERE expires_at<now()-interval '10 minutes'")
        recent = await conn.fetchval(
            """SELECT count(*) FROM nf_onchain_nonces WHERE wallet=$1
               AND expires_at>now()-interval '4 minutes'""", wallet,
        )
        if recent >= 8:
            raise HTTPException(status_code=429, detail="Too many signature requests")
        await conn.execute(
            "INSERT INTO nf_onchain_nonces(nonce,wallet,message,expires_at) VALUES($1,$2,$3,$4)",
            nonce, wallet, message, expiry,
        )
    return {"nonce": nonce, "message": message, "expires_at": expiry.isoformat()}


@router.post("/verify")
async def verify(req: VerifyIn, request: Request) -> dict:
    check_origin(request)
    wallet = wallet_address(req.wallet)
    if not re.fullmatch(r"[a-f0-9]{32}", req.nonce):
        raise HTTPException(status_code=422, detail="Invalid signature challenge")
    async with (await pool()).acquire() as conn:
        row = await conn.fetchrow(
            "SELECT wallet,message FROM nf_onchain_nonces WHERE nonce=$1 AND used_at IS NULL AND expires_at>now()",
            req.nonce,
        )
        if not row or row["wallet"] != wallet:
            raise HTTPException(status_code=401, detail="Challenge expired or already used")
        try:
            recovered = Account.recover_message(encode_defunct(text=row["message"]), signature=req.signature)
        except Exception:
            raise HTTPException(status_code=401, detail="Wallet signature was not verified") from None
        if recovered.lower() != wallet:
            raise HTTPException(status_code=401, detail="Signature does not match wallet")
        async with conn.transaction():
            consumed = await conn.fetchval(
                """UPDATE nf_onchain_nonces SET used_at=now()
                   WHERE nonce=$1 AND used_at IS NULL AND expires_at>now() RETURNING nonce""",
                req.nonce,
            )
            if not consumed:
                raise HTTPException(status_code=409, detail="Signature challenge already used")
            code = secrets.token_hex(10)
            await conn.execute(
                """INSERT INTO nf_onchain_members(wallet,referral_code)
                   VALUES($1,$2) ON CONFLICT(wallet) DO UPDATE SET last_seen_at=now()""",
                wallet, code,
            )
            await conn.execute(
                """INSERT INTO nf_onchain_xp_ledger(wallet,event_key,xp,reason)
                   VALUES($1,$2,25,'wallet_verified') ON CONFLICT(event_key) DO NOTHING""",
                wallet, "wallet:" + wallet,
            )
            if valid_referral(req.ref):
                ref = await conn.fetchval(
                    "SELECT wallet FROM nf_onchain_members WHERE referral_code=$1",
                    req.ref,
                )
                if ref and ref != wallet:
                    await conn.execute(
                        """UPDATE nf_onchain_members SET referred_by=$1
                           WHERE wallet=$2 AND referred_by IS NULL""",
                        ref, wallet,
                    )
            session = secrets.token_urlsafe(32)
            await conn.execute(
                """INSERT INTO nf_onchain_sessions(session_hash,wallet,expires_at)
                   VALUES($1,$2,now()+interval '7 days')""",
                hashlib.sha256(session.encode("ascii")).hexdigest(), wallet,
            )
        data = await member_state(conn, wallet)
    return {"session": session, "expires_in_seconds": 604800, "member": data}


@router.get("/me")
async def me(authorization: Annotated[str | None, Header()] = None) -> dict:
    wallet = await current_wallet(authorization)
    async with (await pool()).acquire() as conn:
        return await member_state(conn, wallet)


@router.post("/daily-claim")
async def daily_claim(request: Request, authorization: Annotated[str | None, Header()] = None) -> dict:
    check_origin(request)
    wallet = await current_wallet(authorization)
    today = datetime.now(UTC).date()
    async with (await pool()).acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT last_checkin,checkin_streak,referred_by FROM nf_onchain_members WHERE wallet=$1 FOR UPDATE",
                wallet,
            )
            if not row:
                raise HTTPException(status_code=404, detail="Wallet not registered")
            if row["last_checkin"] == today:
                return {"ok": True, "already_claimed": True, "xp_awarded": 0,
                        "member": await member_state(conn, wallet)}
            previous = row["last_checkin"]
            streak = row["checkin_streak"] + 1 if previous == today - timedelta(days=1) else 1
            xp = daily_xp(streak)
            await conn.execute(
                "INSERT INTO nf_onchain_checkins(wallet,day,streak,xp) VALUES($1,$2,$3,$4)",
                wallet, today, streak, xp,
            )
            await conn.execute(
                """INSERT INTO nf_onchain_xp_ledger(wallet,event_key,xp,reason)
                   VALUES($1,$2,$3,'daily_checkin') ON CONFLICT(event_key) DO NOTHING""",
                wallet, "daily:" + wallet + ":" + today.isoformat(), xp,
            )
            await conn.execute(
                """UPDATE nf_onchain_members SET last_checkin=$2,checkin_streak=$3
                   WHERE wallet=$1""", wallet, today, streak,
            )
            referrer = row["referred_by"]
            if referrer and referrer != wallet:
                qualified = await conn.fetchval(
                    """INSERT INTO nf_onchain_referral_qualifications(invitee_wallet,inviter_wallet)
                       VALUES($1,$2) ON CONFLICT(invitee_wallet) DO NOTHING RETURNING invitee_wallet""",
                    wallet, referrer,
                )
                if qualified:
                    await conn.execute(
                        """INSERT INTO nf_onchain_xp_ledger(wallet,event_key,xp,reason)
                           VALUES($1,$2,$3,'qualified_referral') ON CONFLICT(event_key) DO NOTHING""",
                        referrer, "referral:" + wallet, _REFERRAL_BONUS,
                    )
            state = await member_state(conn, wallet)
        return {"ok": True, "already_claimed": False, "xp_awarded": xp, "member": state}


@router.post("/waitlist")
async def join_waitlist(
    req: WaitlistIn, request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    check_origin(request)
    wallet = await current_wallet(authorization)
    email = (req.email or "").strip().lower()
    if email and not _EMAIL.fullmatch(email):
        raise HTTPException(status_code=422, detail="Valid email required")
    if req.email_opt_in and not email:
        raise HTTPException(status_code=422, detail="Email required for updates")
    if req.interest not in {"ecosystem", "airdrop-design", "token-updates", "rwa", "ai-agent", "builder"}:
        raise HTTPException(status_code=422, detail="Unrecognized interest")
    async with (await pool()).acquire() as conn:
        await conn.execute(
            """UPDATE nf_onchain_members SET email=$2,email_opt_in=$3,
               last_seen_at=now() WHERE wallet=$1""",
            wallet, email or None, bool(req.email_opt_in),
        )
        # No point award for joining a token list, no token allocation reserved.
    return {"joined": True, "interest": req.interest,
            "email_updates": bool(req.email_opt_in),
            "token_reserved": False, "airdrop_entitlement": False}


@router.post("/preferences")
async def preferences(
    req: PreferencesIn, request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    check_origin(request)
    wallet = await current_wallet(authorization)
    async with (await pool()).acquire() as conn:
        await conn.execute(
            "UPDATE nf_onchain_members SET leaderboard_opt_in=$2 WHERE wallet=$1",
            wallet, bool(req.leaderboard_opt_in),
        )
    return {"ok": True, "leaderboard_opt_in": req.leaderboard_opt_in}


@router.get("/leaderboard")
async def leaderboard() -> dict:
    async with (await pool()).acquire() as conn:
        rows = await conn.fetch(
            """SELECT m.wallet,COALESCE(SUM(l.xp),0)::int AS xp
               FROM nf_onchain_members m
               LEFT JOIN nf_onchain_xp_ledger l ON l.wallet=m.wallet
               WHERE m.leaderboard_opt_in=TRUE
               GROUP BY m.wallet ORDER BY xp DESC,m.wallet LIMIT 25"""
        )
    return {"members": [
        {"wallet": r["wallet"][:6] + "…" + r["wallet"][-4:], "xp": r["xp"]}
        for r in rows
    ], "only_opted_in": True, "real_accounts_only": True}
