"""Unit tests for pilot key store (in-memory)."""

from __future__ import annotations

import asyncio
from uuid import uuid4

from noetfield_governance.pilot_key_store import (
    InMemoryPilotKeyStore,
    generate_secret,
    hash_pilot_secret,
)


def test_hash_pilot_secret_is_sha256_of_pepper_plus_secret() -> None:
    assert hash_pilot_secret("secret", "pepper") == hash_pilot_secret("secret", "pepper")
    assert hash_pilot_secret("secret", "pepper") != hash_pilot_secret("secret", "other")
    assert len(hash_pilot_secret("x", "y")) == 64


def test_generate_secret_prefix() -> None:
    secret = generate_secret()
    assert secret.startswith("nf_pilot_")
    assert len(secret) > 20


def test_inmemory_create_lookup_list_revoke() -> None:
    async def run() -> None:
        store = InMemoryPilotKeyStore(pepper="test-pepper")
        secret, record = await store.create(
            label="Founder console",
            tenant_id=None,
            scopes=["workspace:admin", "governance:read"],
            created_by="test",
        )
        assert secret.startswith("nf_pilot_")
        assert record.key_prefix == secret[:16]
        assert await store.count_active() == 1

        found = await store.lookup_by_secret(secret)
        assert found is not None
        assert found.key_id == record.key_id
        assert found.label == "Founder console"

        assert await store.lookup_by_secret("wrong") is None

        active = await store.list_active()
        assert len(active) == 1
        assert active[0].key_id == record.key_id

        revoked = await store.revoke(record.key_id)
        assert revoked is not None
        assert revoked.revoked_at is not None
        assert await store.count_active() == 0
        assert await store.lookup_by_secret(secret) is None

        missing = await store.revoke(uuid4())
        assert missing is None

    asyncio.run(run())
