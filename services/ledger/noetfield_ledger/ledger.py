"""Append-only governance ledger foundation.

The repository interface is intentionally storage-agnostic. Concrete adapters
can persist to PostgreSQL/Supabase, a warehouse, or enterprise WORM storage
without changing event producers.
"""

from dataclasses import dataclass
from hashlib import sha256
import hmac
import json

from pydantic import SecretStr

from noetfield_types import GovernanceEvent


@dataclass(frozen=True)
class LedgerAppendResult:
    event_id: str
    integrity_hash: str
    persisted: bool


class LedgerRepository:
    """Append-only Trust Ledger boundary.

    This base implementation computes deterministic integrity hashes. The
    concrete database adapter should insert into `governance_events` and must
    never update or delete existing ledger records.
    """

    def __init__(self, integrity_secret: SecretStr) -> None:
        self._integrity_secret = integrity_secret.get_secret_value().encode("utf-8")

    def attach_integrity_hash(self, event: GovernanceEvent) -> GovernanceEvent:
        payload = event.model_dump(mode="json", exclude={"integrity_hash"})
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        digest = hmac.new(self._integrity_secret, canonical, sha256).hexdigest()
        return event.model_copy(update={"integrity_hash": digest})

    async def append(self, event: GovernanceEvent) -> LedgerAppendResult:
        sealed_event = self.attach_integrity_hash(event)
        return LedgerAppendResult(
            event_id=str(sealed_event.event_id),
            integrity_hash=sealed_event.integrity_hash or "",
            persisted=False,
        )
