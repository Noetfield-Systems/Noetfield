"""Onchain community contract: wallet sign-in, bounded XP and public truth."""
from datetime import UTC, datetime, timedelta

from eth_account import Account
from eth_account.messages import encode_defunct
from fastapi import HTTPException

from noetfield_governance.onchain_community import daily_xp, signed_message, valid_referral, wallet_address


def test_eip191_message_signature_recovers_wallet() -> None:
    account = Account.create()
    now = datetime(2026, 11, 13, tzinfo=UTC)
    wallet = wallet_address(account.address)
    msg = signed_message(wallet, "e" * 32, now, now + timedelta(minutes=5))
    signed = Account.sign_message(encode_defunct(text=msg), account.key)
    assert Account.recover_message(encode_defunct(text=msg), signature=signed.signature).lower() == wallet
    assert "does not transfer funds" in msg
    assert "Nonce: " + "e" * 32 in msg
    assert "Chain ID: 8453" in msg
    assert "Expiration Time:" in msg


def test_signature_changes_when_nonce_changes() -> None:
    account = Account.create()
    at = datetime.now(UTC)
    one = signed_message(account.address.lower(), "a" * 32, at, at + timedelta(minutes=5))
    two = signed_message(account.address.lower(), "b" * 32, at, at + timedelta(minutes=5))
    signature = Account.sign_message(encode_defunct(text=one), account.key)
    assert Account.recover_message(encode_defunct(text=two), signature=signature.signature).lower() != account.address.lower()


def test_wallet_address_validation() -> None:
    assert wallet_address("0x" + "AB" * 20) == "0x" + "ab" * 20
    for invalid in ["", "1x" + "a" * 40, "0x" + "a" * 39, "0x" + "g" * 40]:
        try:
            wallet_address(invalid)
        except HTTPException as exc:
            assert exc.status_code == 422
        else:
            raise AssertionError("Invalid wallet accepted: " + invalid)


def test_daily_streak_rewards_are_capped() -> None:
    assert daily_xp(1) == 10
    assert daily_xp(2) == 12
    assert daily_xp(8) == 24
    assert daily_xp(100) == 24
    assert daily_xp(0) == 10


def test_referral_codes_require_exact_random_hex() -> None:
    assert valid_referral("d" * 20)
    assert not valid_referral("d" * 19)
    assert not valid_referral("z" * 20)
    assert not valid_referral(None)
