"""Provider-independent communication policy. Only native trusted adapters
may supply identity, contact, relationship and authorization facts.
No model-generated verification or implicit default sender.
"""
from __future__ import annotations
from dataclasses import dataclass
import re

VERSION = "2.1"
INTENTS = frozenset("commercial technical research partnership community customer_support investment corporate personal intellectual operational legal financial".split())
EMAIL = re.compile(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+")
RANK = {"native": 1, "specialist": 2, "representative": 3, "fallback": 4}

class CommunicationRejected(ValueError):
    pass

@dataclass(frozen=True)
class Identity:
    address: str
    entity: str
    venture: str
    intents: frozenset[str]
    kind: str
    reply_to: str
    verified: bool
    available: bool
    authority_ref: str

@dataclass(frozen=True)
class Relationship:
    venture: str
    entity: str
    recipient: str
    contact_ref: str
    crm: str
    owner: str
    next_action: str
    thread_sender: str = ""
    suppressed: bool = False
    action_attempted: bool = False
    context_checked: bool = False

def resolve(*, venture: str, entity: str, intent: str, relationship: Relationship,
            identities: tuple[Identity, ...], authority_ref: str) -> Identity:
    if intent not in INTENTS or not authority_ref:
        raise CommunicationRejected("AUTHORITY_OR_INTENT_MISSING")
    if (relationship.venture, relationship.entity) != (venture, entity):
        raise CommunicationRejected("RELATIONSHIP_SCOPE_MISMATCH")
    if not all((relationship.contact_ref, relationship.crm, relationship.owner,
                relationship.next_action)) or not relationship.context_checked:
        raise CommunicationRejected("RELATIONSHIP_CONTEXT_MISSING")
    if not EMAIL.fullmatch(relationship.recipient):
        raise CommunicationRejected("RECIPIENT_NOT_VERIFIED")
    if relationship.suppressed or relationship.action_attempted:
        raise CommunicationRejected("SUPPRESSED_OR_DUPLICATE")
    eligible = [x for x in identities if x.venture == venture and x.entity == entity
                and intent in x.intents and x.kind in RANK and x.verified
                and x.available and x.authority_ref and EMAIL.fullmatch(x.address)
                and EMAIL.fullmatch(x.reply_to)]
    if not eligible:
        raise CommunicationRejected("NO_AUTHORIZED_SENDER")
    return min(eligible, key=lambda x: (0 if x.address == relationship.thread_sender
                                        else RANK[x.kind], x.address))

def enforce_envelope(*, identity: Identity, sender: str, recipient: str,
                     reply_to: str, relationship: Relationship) -> None:
    if not identity.verified or not identity.available or not identity.authority_ref:
        raise CommunicationRejected("SENDER_NOT_AUTHORIZED")
    if (identity.venture, identity.entity) != (relationship.venture, relationship.entity):
        raise CommunicationRejected("RELATIONSHIP_SCOPE_MISMATCH")
    if (sender, recipient, reply_to) != (identity.address, relationship.recipient, identity.reply_to):
        raise CommunicationRejected("ENVELOPE_MISMATCH")

def corporate_sender(mailbox: str, authorized_addresses: tuple[str, ...] = ("operations@noetfield.com",)) -> str:
    """Existing Noetfield corporate route: explicit canonical mailbox only.
    Alternative identities require a native authorized provider adapter, not
    an arbitrary GMAIL_MAILBOX override. SMTP acceptance is not delivery.
    """
    if mailbox not in authorized_addresses or not EMAIL.fullmatch(mailbox) or not mailbox.endswith("@noetfield.com"):
        raise CommunicationRejected("CORPORATE_SENDER_IDENTITY_MISMATCH")
    return mailbox
