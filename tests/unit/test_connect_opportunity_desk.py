"""Noetfield Connect advisory triage and private API tests."""
import asyncio
from datetime import date
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from noetfield_governance import api as governance_api
from noetfield_governance.api import app
from noetfield_governance.opportunity_desk import triage_connect_record


def sample(kind="business"):
    return {
        "intake_id": "INT-ABCDEF123456",
        "request_id": "RID-CNX-1234567890",
        "created_at": "2026-11-12T00:00:00+00:00",
        "contact_name": "Example Person",
        "contact_email": "person@example.invalid",
        "organization": "Example Organization",
        "source": "web",
        "metadata": {
            "form_id": "nfConnectWizard",
            "topic": kind,
            "initiative": "noetfield",
            "proposal_title": "Pilot proposal",
            "proposal_url": "https://example.invalid/proposal",
            "deadline": "2026-11-15",
            "lead_source": "linkedin",
        },
    }


def test_connect_projection_routes_and_no_fake_outcomes():
    result = triage_connect_record(sample(), today=date(2026, 11, 12))
    assert result["priority_score"] == 85
    assert result["suggested_owner_role"] == "Sales owner"
    assert result["days_remaining"] == 3
    assert result["stage"] == "NEW"
    assert result["assignment_status"] == "ADVISORY_ONLY"
    assert result["execution_status"] == "NOT_DISPATCHED"
    assert result["cash_collected"] is None
    assert triage_connect_record({"metadata": {"form_id": "other"}}) is None
    assert triage_connect_record(sample("events"))["suggested_owner_role"] == "Partnerships owner"
    synthetic = sample("business")
    synthetic["metadata"]["intake_kind"] = "test"
    assert triage_connect_record(synthetic) is None


def test_connect_desk_requires_admin_and_filters_nonconnect():
    async def run():
        old = governance_api.settings.admin_dashboard_secret
        try:
            with patch("noetfield_governance.intake_repository.list_recent",
                       new_callable=AsyncMock) as recent:
                recent.return_value = [sample(), {"metadata": {"form_id": "other"}}]
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    governance_api.settings.admin_dashboard_secret = SecretStr("")
                    assert (await client.get("/api/opportunities/desk")).status_code == 503
                    governance_api.settings.admin_dashboard_secret = SecretStr("desk-test-secret")
                    assert (await client.get("/api/opportunities/desk")).status_code == 403
                    assert (await client.get("/api/opportunities/desk",
                               headers={"X-Admin-Secret": "wrong"})).status_code == 403
                    response = await client.get("/api/opportunities/desk",
                                headers={"X-Admin-Secret": "desk-test-secret"})
                assert response.status_code == 200
                body = response.json()
                assert body["count"] == 1
                assert body["mode"] == "HUMAN_TRACKING_NO_AUTO_EXECUTION"
                assert body["opportunities"][0]["source"] == "linkedin"
                recent.assert_awaited_once()
        finally:
            governance_api.settings.admin_dashboard_secret = old
    asyncio.run(run())


def test_operator_state_survives_projection_and_public_metadata_cannot_spoof_it():
    user_record = sample("capital")
    user_record["metadata"]["connect_ops"] = {"stage": "WON", "owner": "Fraudulent public owner"}
    projected = triage_connect_record(user_record, today=date(2026, 11, 12))
    assert projected["stage"] == "NEW"
    assert projected["owner"] is None
    user_record["qualification_json"] = {"tier": "review", "connect_ops": {
        "stage": "QUALIFYING", "owner": "Founder", "next_action": "Verify terms",
        "due_date": "2026-11-17", "note": "Requested supporting material",
        "revision": 2, "history": [{"revision": 1}, {"revision": 2}],
        "updated_at": "2026-11-12T21:00:00+00:00",
    }}
    updated = triage_connect_record(user_record, today=date(2026, 11, 12))
    assert updated["stage"] == "QUALIFYING"
    assert updated["owner"] == "Founder"
    assert updated["revision"] == 2
    assert len(updated["activity"]) == 2
    assert updated["assignment_status"] == "HUMAN_ASSIGNED"
    assert updated["cash_collected"] is None


def test_authenticated_edit_updates_existing_intake_not_a_new_crm():
    async def run():
        old = governance_api.settings.admin_dashboard_secret
        try:
            governance_api.settings.admin_dashboard_secret = SecretStr("edit-test-secret")
            with patch("noetfield_governance.intake_repository.update_connect_opportunity",
                       new_callable=AsyncMock) as save:
                save.return_value = {"revision": 1, "stage": "QUALIFYING",
                                     "owner": "Founder", "next_action": "Request deck"}
                body = {"expected_revision": 0, "stage": "QUALIFYING",
                        "owner": "Founder", "next_action": "Request deck",
                        "due_date": "2026-11-20", "note": ""}
                async with AsyncClient(transport=ASGITransport(app=app),
                                       base_url="http://test") as client:
                    unauthorized = await client.patch("/api/opportunities/desk/INT-ABCDEF123456", json=body)
                    assert unauthorized.status_code == 403
                    good = await client.patch("/api/opportunities/desk/INT-ABCDEF123456",
                        json=body, headers={"X-Admin-Secret": "edit-test-secret"})
                    assert good.status_code == 200, good.text
                    assert good.json()["persisted"] is True
                    assert good.json()["external_action_executed"] is False
                    assert save.await_args.kwargs["expected_revision"] == 0
                    assert save.await_args.kwargs["due_date"] == "2026-11-20"
                    won = {**body, "stage": "WON"}
                    assert (await client.patch("/api/opportunities/desk/INT-ABCDEF123456",
                         json=won, headers={"X-Admin-Secret": "edit-test-secret"})).status_code == 422
                    save.side_effect = ValueError("OPPORTUNITY_VERSION_CONFLICT")
                    conflict = await client.patch("/api/opportunities/desk/INT-ABCDEF123456",
                         json=body, headers={"X-Admin-Secret": "edit-test-secret"})
                    assert conflict.status_code == 409
                    save.side_effect = None
                    save.return_value = None
                    missing = await client.patch("/api/opportunities/desk/INT-ABCDEF123456",
                         json=body, headers={"X-Admin-Secret": "edit-test-secret"})
                    assert missing.status_code == 404
        finally:
            governance_api.settings.admin_dashboard_secret = old
    asyncio.run(run())




def test_workforce_handoff_requires_saved_operator_decision_and_verified_remote_ack():
    async def run():
        original = governance_api.settings.admin_dashboard_secret
        governance_api.settings.admin_dashboard_secret = SecretStr("operator-bridge-test")
        record = sample("people")
        record["metadata"]["consent_contact"] = True
        record["qualification_json"] = {"connect_ops": {
            "owner": "Named operator", "next_action": "Review and propose a scoped trial",
            "due_date": "2026-11-19", "revision": 1,
        }}
        proof = {"connected": True, "found": True,
                 "case": {"source_intake_id": record["intake_id"],
                          "case_id": "opp_nf_" + "a" * 24,
                          "owner": "Named operator", "stage": "qualifying"}}
        with patch.object(governance_api, "_require_workforce_source",
                          new_callable=AsyncMock) as source_check, \\
             patch("noetfield_governance.intake_repository.list_connect_by_intake",
                   new_callable=AsyncMock) as source_rows, \\
             patch.object(governance_api, "readback_connect_workforce",
                          return_value=proof), \\
             patch.object(governance_api, "handoff_connect_workforce",
                          return_value={**proof, "accepted": True, "deduped": False}) as dispatch:
            source_rows.return_value = [record]
            request = {"request_id": "canonical_operator_case_0001",
                       "owner": "Named operator",
                       "next_action": "Review and propose a scoped trial",
                       "due_date": "2026-11-19",
                       "match_quality": "medium"}
            async with AsyncClient(transport=ASGITransport(app=app),
                                   base_url="http://test") as client:
                path = "/api/opportunities/desk/" + record["intake_id"] + "/workforce/handoff"
                unauth = await client.post(path, json=request)
                assert unauth.status_code == 403
                wrong_owner = await client.post(path, json={**request, "owner": "Unknown"},
                       headers={"X-Admin-Secret": "operator-bridge-test"})
                assert wrong_owner.status_code == 409
                actual = await client.post(path, json=request,
                          headers={"X-Admin-Secret": "operator-bridge-test"})
                assert actual.status_code == 200, actual.text
                assert actual.json()["operator_owner_recorded"] is True
                assert actual.json()["agent_executed"] is False
                assert actual.json()["independently_verified_by_platform"] is False
                status = await client.get(
                    "/api/opportunities/desk/" + record["intake_id"] + "/workforce/status",
                    headers={"X-Admin-Secret": "operator-bridge-test"})
                assert status.status_code == 200, status.text
                assert status.json()["case"]["case_id"] == proof["case"]["case_id"]
                assert dispatch.call_count == 1
                assert dispatch.call_args.kwargs["next_action"] == request["next_action"]
            source_check.assert_awaited()
        governance_api.settings.admin_dashboard_secret = original
    asyncio.run(run())

def test_public_ui_shell_contains_no_private_records_or_keys():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app),
                               base_url="http://test") as client:
            response = await client.get("/api/opportunities/desk/app")
        assert response.status_code == 200
        assert "Opportunity Desk." in response.text
        assert "X-Desk-CSRF" in response.text
        assert "X-Admin-Secret" not in response.text
        assert "Remember this device for 7 days" in response.text
        assert "private@example.test" not in response.text
        assert "localStorage" not in response.text
    asyncio.run(run())
