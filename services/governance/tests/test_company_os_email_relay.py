"""Contract test for the private Noetfield Digital email relay (network mocked)."""
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from noetfield_governance.company_os_email_relay import router


def test_company_os_email_requires_token_and_returns_real_provider_receipt(monkeypatch):
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    monkeypatch.setenv("COMPANY_OS_EMAIL_RELAY_TOKEN", "a" * 60)
    monkeypatch.setenv("RESEND_API_KEY", "re_test_fixture")
    message = {
        "kind": "requested_proposal",
        "to": "buyer@example.com",
        "subject": "Your requested service proposal",
        "text": "A specific proposal is ready at the private link in this message.",
        "idempotency_key": "notification12345678901234567890",
    }
    assert client.post("/api/internal/company-os/notify", json=message).status_code == 401
    assert client.post("/api/internal/company-os/notify", json=message,
                       headers={"Authorization": "Bearer wrong"}).status_code == 401
    calls = []

    class Response:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *unused):
            return False
        def read(self, size):
            return json.dumps({"id": "resend_real_receipt_fixture"}).encode()

    def fake_urlopen(req, timeout):
        assert req.full_url == "https://api.resend.com/emails"
        assert req.headers["Authorization"] == "Bearer re_test_fixture"
        payload = json.loads(req.data)
        assert payload["to"] == ["buyer@example.com"]
        assert payload["from"] == "Noetfield Digital <notifications@noetfield.com>"
        calls.append(payload)
        return Response()

    monkeypatch.setattr("noetfield_governance.company_os_email_relay.urllib.request.urlopen", fake_urlopen)
    response = client.post("/api/internal/company-os/notify", json=message,
                           headers={"Authorization": "Bearer " + ("a" * 60)})
    assert response.status_code == 200, response.text
    assert response.json()["id"] == "resend_real_receipt_fixture"
    assert len(calls) == 1
    bad = dict(message, to="invalid address")
    assert client.post("/api/internal/company-os/notify", json=bad,
                       headers={"Authorization": "Bearer " + ("a" * 60)}).status_code == 422
