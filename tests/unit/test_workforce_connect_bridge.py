"""Noetfield Platform -> existing WorkforceOS scoped source projection tests.

No public lead, real candidate or external payment is created by these tests.
"""
import io
import json
from unittest.mock import patch

from noetfield_governance.intake_store import IntakeRecord
from noetfield_governance.workforce_connect_bridge import eligible, deliver


def record(vector="external-opportunities", metadata=None):
    return IntakeRecord(
        intake_id="INT-ABCDEF123456", request_id="RID-CNX-ABCDEF123456",
        organization="Independent", contact_name="CI Example",
        contact_email="ci@example.org", message="I propose a scoped project with tests.",
        sku="general", vector=vector, source="web", metadata=metadata or {},
        created_at="2026-11-13T00:00:00+00:00",
    )


class AcceptedResponse:
    status = 200

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return json.dumps(self.payload).encode("utf-8")


def test_people_consent_and_independent_venture_boundaries():
    assert not eligible(record(metadata={"category": "business", "consent_contact": True}))
    assert not eligible(record(metadata={"category": "people", "consent_contact": False}))
    assert not eligible(record(metadata={"category": "people", "consent_contact": True,
                                         "initiative": "trustfield"}))
    assert eligible(record(metadata={"category": "people", "consent_contact": True,
                                     "initiative": "noetfield"}))
    assert not eligible(record(vector="contact", metadata={"category": "people",
                                                            "consent_contact": True}))
    assert eligible(record(vector="work-with-us-contributor",
                           metadata={"application_kind": "agent",
                                     "consent_contact": True}))


def test_authenticated_source_sync_validates_upstream_ack_and_retains_source_id():
    item = record(metadata={"category": "people", "consent_contact": True,
                            "initiative": "workforce", "lead_source": "linkedin"})
    ack = AcceptedResponse({"accepted": True, "source_intake_id": item.intake_id,
                            "case_id": "opp_nf_1234567890abcdef12345678",
                            "deduped": False})
    with patch.dict("os.environ", {
        "WORKFORCE_CONNECT_BRIDGE_URL": "https://workforce.example.org",
        "WORKFORCE_CONNECT_BRIDGE_KEY": "x" * 48,
    }):
        with patch("noetfield_governance.workforce_connect_bridge.urlopen",
                   return_value=ack) as post:
            outcome = deliver(item)
        assert outcome["delivered"] is True
        assert outcome["source_intake_id"] == item.intake_id
        request = post.call_args.args[0]
        assert request.get_method() == "POST"
        assert request.full_url.endswith("/api/integrations/noetfield-connect")
        assert request.get_header("X-noetfield-bridge-key") == "x" * 48
        sent = json.loads(request.data)
        assert sent["source_intake_id"] == item.intake_id
        assert sent["contact_email"] == item.contact_email


def test_bad_ack_does_not_claim_delivery():
    item = record(metadata={"category": "people", "consent_contact": True})
    ack = AcceptedResponse({"accepted": True, "source_intake_id": "INT-WRONG1234",
                            "case_id": "opp_nf_1234567890abcdef12345678"})
    with patch.dict("os.environ", {
        "WORKFORCE_CONNECT_BRIDGE_URL": "https://workforce.example.org",
        "WORKFORCE_CONNECT_BRIDGE_KEY": "x" * 48,
    }):
        with patch("noetfield_governance.workforce_connect_bridge.urlopen",
                   return_value=ack), patch("noetfield_governance.workforce_connect_bridge.time.sleep"):
            outcome = deliver(item)
    assert outcome["delivered"] is False


def test_unconfigured_bridge_does_not_attempt_a_network_call():
    item = record(metadata={"category": "people", "consent_contact": True})
    with patch.dict("os.environ", {
        "WORKFORCE_CONNECT_BRIDGE_URL": "",
        "WORKFORCE_CONNECT_BRIDGE_KEY": "",
    }):
        with patch("noetfield_governance.workforce_connect_bridge.urlopen") as post:
            outcome = deliver(item)
            post.assert_not_called()
    assert outcome["eligible"] is True
    assert outcome["delivered"] is False
    assert outcome["error"] == "BRIDGE_NOT_CONFIGURED"
