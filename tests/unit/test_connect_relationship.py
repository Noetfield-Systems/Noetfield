"""Noetfield Connect graph and canonical invitation contracts.

Synthetic fixtures never represent customers, accepted introductions or cash.
"""
from __future__ import annotations
import asyncio
import json
import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from noetfield_governance.connect_relationship import project_relationship
from noetfield_governance.opportunity_desk import triage_connect_record
from noetfield_governance.postgres_intake_store import PostgresIntakeStore


def row(intake_id, email, venture="noetfield", kind="people", name="A Person", **extra):
    return {
        "intake_id": intake_id,
        "contact_email": email,
        "contact_name": name,
        "organization": extra.get("org", "Organization"),
        "created_at": "2026-11-12T15:30:00+00:00",
        "metadata": {
            "form_id": "nfConnectWizard", "intake_kind": "lead",
            "initiative": venture, "topic": kind,
            "proposal_title": extra.get("title", "Collaboration"),
            "participant_role": extra.get("role", "advisor"),
            "offering": "Intro to buyers", "requesting": "Product demo",
            "consent_contact": True,
        },
        "qualification_json": extra.get("qualification_json", {}),
    }


def test_multiple_opportunities_one_claim_identity_without_cross_venture_export():
    rows = [
        row("INT-ABCDEF100001", "someone@example.invalid", title="Sales intro"),
        row("INT-ABCDEF100002", "SOMEONE@example.invalid", venture="buildrelay",
            kind="partnership", role="founder", title="Founder initiative"),
        row("INT-ABCDEF100003", "another@example.invalid", venture="trustfield"),
        {**row("INT-ABCDEF100004", "someone@example.invalid"), "metadata":
            {"form_id": "nfConnectWizard", "intake_kind": "test"}},
    ]
    result = project_relationship(rows, "INT-ABCDEF100001")
    assert result["opportunity_count"] == 2
    assert result["ventures"] == ["buildrelay", "noetfield"]
    assert len([n for n in result["nodes"] if n["type"] == "person_claim"]) == 1
    assert len([n for n in result["nodes"] if n["type"] == "opportunity"]) == 2
    assert result["canonical_crm_sync"] == "NOT_CONNECTED"
    assert result["cross_venture_export"] is False
    assert result["verified_cash_collected"] is None
    assert all(e["provenance"] in {"INT-ABCDEF100001", "INT-ABCDEF100002"}
               for e in result["edges"])
    assert not project_relationship(rows,"INT-MISSING")


def test_projection_does_not_publish_bearer_token_hash():
    rec = row("INT-ABCDEF100001","someone@example.invalid", qualification_json={
        "connect_ops": {
            "revision": 2,
            "interactions": [{"kind": "followup_planned", "body": "Ask about timing"}],
            "invitations": [{"id":"inv_aabbccddeeff0011","state":"PREPARED_NOT_SENT",
                             "token_hash":"hidden-secret-hash","scope":"trial"}],
        }
    })
    projected = triage_connect_record(rec)
    assert projected["offer"] == "Intro to buyers"
    assert projected["ask"] == "Product demo"
    assert projected["participant_role"] == "advisor"
    assert projected["consent_contact"] is True
    assert len(projected["invitations"]) == 1
    assert "token_hash" not in projected["invitations"][0]
    assert projected["cash_collected"] is None
    assert projected["execution_status"] == "NOT_DISPATCHED"


@pytest.mark.skipif(not os.getenv("CONNECT_TEST_POSTGRES_URL"), reason="Disposable PostgreSQL required")
def test_real_postgres_invitation_acceptance_and_revision_conflicts():
    import asyncpg
    async def run():
        import uuid
        url = os.environ["CONNECT_TEST_POSTGRES_URL"]
        database = await asyncpg.connect(url)
        case = "INT-" + uuid.uuid4().hex[:12].upper()
        email = "invite-test-" + uuid.uuid4().hex[:12] + "@example.invalid"
        try:
            await database.execute("CREATE SCHEMA IF NOT EXISTS noetfield")
            await database.execute("""CREATE TABLE IF NOT EXISTS noetfield.public_intakes (
                intake_id text PRIMARY KEY,
                metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
                qualification_json jsonb
            )""")
            await database.execute("ALTER TABLE noetfield.public_intakes ADD COLUMN IF NOT EXISTS contact_email text")
            await database.execute("""INSERT INTO noetfield.public_intakes
                (intake_id,metadata,contact_email,qualification_json)
                VALUES ($1,$2::jsonb,$3,$4::jsonb)""",
                case,json.dumps({"form_id":"nfConnectWizard","intake_kind":"lead"}),email,
                json.dumps({"tier":"human_review"}))
        finally:
            await database.close()
        store = PostgresIntakeStore(url)
        try:
            created = await store.create_connect_invitation(
                intake_id=case,expected_revision=0,scope="trial",
                message="Would you consider a scoped research deliverable with a human owner?",
                request_id="invreq_" + uuid.uuid4().hex,
            )
            assert created and created["state"] == "PREPARED_NOT_SENT"
            assert created["created"] is True
            token = created["share_token"]
            assert len(token) >= 32
            with pytest.raises(ValueError,match="OPPORTUNITY_VERSION_CONFLICT"):
                await store.append_connect_activity(
                    intake_id=case,expected_revision=0,
                    action="followup_planned",body="Wrong revision"
                )
            saved = await store.append_connect_activity(
                intake_id=case,expected_revision=1,
                action="draft_prepared",body="An internal email draft, not sent",
            )
            assert saved["revision"] == 2
            with pytest.raises(ValueError,match="INVITATION_RECIPIENT_MISMATCH"):
                await store.respond_connect_invitation(
                    intake_id=case,invitation_id=created["invitation_id"],
                    token=token,email="different@example.invalid",decision="accept"
                )
            with pytest.raises(ValueError,match="INVITATION_TOKEN_INVALID"):
                await store.respond_connect_invitation(
                    intake_id=case,invitation_id=created["invitation_id"],
                    token="a"*40,email=email,decision="accept",
                )
            response = await store.respond_connect_invitation(
                intake_id=case,invitation_id=created["invitation_id"],
                token=token,email=email.upper(),decision="accept",
            )
            assert response == {
                "state":"ACCEPTED_BY_TOKEN_HOLDER",
                "created":True,"identity_verified":False,
                "external_action_executed":False,"confirmed_meeting":False,
                "scoped_authority_granted":False,
            }
            repeated = await store.respond_connect_invitation(
                intake_id=case,invitation_id=created["invitation_id"],
                token=token,email=email,decision="accept",
            )
            assert repeated["created"] is False
            with pytest.raises(ValueError,match="INVITATION_DECISION_CONFLICT"):
                await store.respond_connect_invitation(
                    intake_id=case,invitation_id=created["invitation_id"],
                    token=token,email=email,decision="decline",
                )
            # A normal case-stage update must preserve the new interactions/invitations.
            state = await store.update_connect_state(
                intake_id=case,expected_revision=3,
                stage="QUALIFYING",owner="Founder",next_action="Human confirms consent",
                due_date="2026-11-19",note="Review token-holder interest",
            )
            assert state["revision"]==4
            assert len(state["invitations"])==1
            assert len(state["interactions"])==1
            assert "token_hash" in state["invitations"][0]  # server-side only; projection redacts
            # Real Postgres outcome report is evidence-backed and replay-safe,
            # but deliberately cannot create an independent verification receipt.
            outcome_rid="outcome_ci_" + uuid.uuid4().hex
            with pytest.raises(ValueError,match="CONNECT_OUTCOME_EVIDENCE_REQUIRED"):
                await store.record_connect_outcome(
                    intake_id=case,expected_revision=4,request_id=outcome_rid,
                    outcome_type="trial",evidence_url="http://not-secure.invalid",
                    note="A documented trial began with an assigned operator",
                )
            reported=await store.record_connect_outcome(
                intake_id=case,expected_revision=4,request_id=outcome_rid,
                outcome_type="trial",
                evidence_url="https://example.invalid/trial/receipt",
                note="A trial was reported from the referenced evidence",
            )
            assert reported["created"] is True
            assert reported["revision"] == 5
            assert reported["reported_outcome"]["independently_verified"] is False
            assert reported["reported_outcome"]["cash_collected"] is None
            replay=await store.record_connect_outcome(
                intake_id=case,expected_revision=4,request_id=outcome_rid,
                outcome_type="trial",
                evidence_url="https://example.invalid/trial/receipt",
                note="A trial was reported from the referenced evidence",
            )
            assert replay["created"] is False
            assert replay["revision"] == 5
            with pytest.raises(ValueError,match="OPPORTUNITY_VERSION_CONFLICT"):
                await store.record_connect_outcome(
                    intake_id=case,expected_revision=4,
                    request_id="outcome_retry_"+uuid.uuid4().hex,
                    outcome_type="meeting",
                    evidence_url="https://example.invalid/another-receipt",
                    note="A meeting took place according to the operator",
                )

        finally:
            await store.close()
    asyncio.run(run())


def test_api_access_and_source_readback_contracts():
    from noetfield_governance import api as gov
    async def run():
        old = gov.settings.admin_dashboard_secret
        gov.settings.admin_dashboard_secret = SecretStr("testing-founder-secret")
        try:
            with patch("noetfield_governance.intake_repository.list_connect_page",
                       new_callable=AsyncMock) as list_page, \
                 patch("noetfield_governance.intake_repository.list_connect_by_intake",
                       new_callable=AsyncMock) as list_people, \
                 patch("noetfield_governance.intake_repository.append_connect_activity",
                       new_callable=AsyncMock) as activity:
                rec=row("INT-ABCDEF100001","person@example.invalid")
                list_page.return_value={"records":[rec],"total":1,"offset":0,"limit":50}
                list_people.return_value=[rec]
                activity.return_value={
                    "revision":1,"interaction":{"kind":"draft_prepared"},
                    "interactions_count":1,
                }
                async with AsyncClient(transport=ASGITransport(app=gov.app),
                                       base_url="http://test") as client:
                    unauthorized=await client.get("/api/opportunities/desk/page")
                    assert unauthorized.status_code==403
                    auth={"X-Admin-Secret":"testing-founder-secret"}
                    listing=await client.get("/api/opportunities/desk/page",headers=auth)
                    assert listing.status_code==200,listing.text
                    assert listing.json()["total"]==1
                    graph=await client.get("/api/opportunities/desk/INT-ABCDEF100001/relationship",
                                           headers=auth)
                    assert graph.status_code==200
                    assert graph.json()["opportunity_count"]==1
                    update=await client.post(
                        "/api/opportunities/desk/INT-ABCDEF100001/activity",
                        headers=auth,
                        json={"expected_revision":0,"action":"draft_prepared",
                              "body":"A draft prepared for review, not sent."})
                    assert update.status_code==200,update.text
                    assert update.json()["actual_external_action"] is False
                activity.assert_awaited_once()
        finally:
            gov.settings.admin_dashboard_secret = old
    asyncio.run(run())


@pytest.mark.skipif(not os.getenv("CONNECT_TEST_POSTGRES_URL"), reason="Disposable PostgreSQL required")
def test_consent_scoped_provider_invitation_delivery_ledger_is_real_and_replay_safe():
    import uuid
    async def run():
        url=os.environ["CONNECT_TEST_POSTGRES_URL"]
        iid="INT-"+uuid.uuid4().hex[:12].upper()
        rid="RID-CNX-"+uuid.uuid4().hex[:16].upper()
        db=await __import__("asyncpg").connect(url)
        try:
            await db.execute("CREATE SCHEMA IF NOT EXISTS noetfield")
            await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.public_intakes (
                intake_id text PRIMARY KEY,
                metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
                qualification_json jsonb
            )""")
            for statement in (
                "ALTER TABLE noetfield.public_intakes ADD COLUMN IF NOT EXISTS request_id text",
                "ALTER TABLE noetfield.public_intakes ADD COLUMN IF NOT EXISTS contact_name text",
                "ALTER TABLE noetfield.public_intakes ADD COLUMN IF NOT EXISTS contact_email text",
            ):
                await db.execute(statement)
            await db.execute("""INSERT INTO noetfield.public_intakes
                (intake_id,request_id,contact_name,contact_email,metadata,qualification_json)
                VALUES($1,$2,$3,$4,$5::jsonb,$6::jsonb)""",
                iid,rid,"Applicant","applicant@example.invalid",
                json.dumps({"form_id":"nfConnectWizard","intake_kind":"lead",
                            "consent_contact":True}),
                json.dumps({"tier":"human_review"}))
        finally:
            await db.close()
        store=PostgresIntakeStore(url)
        try:
            source=await store.get_connect_delivery_source(intake_id=iid)
            assert source["contact_consent"] is True
            assert source["contact_email"]=="applicant@example.invalid"
            prepared=await store.create_connect_invitation(
                intake_id=iid,expected_revision=0,scope="trial",
                message="A proposed bounded trial with a specific engineering deliverable",
                request_id="send_req_"+uuid.uuid4().hex)
            assert prepared["created"] is True
            token=prepared["share_token"]
            claim=await store.claim_connect_invitation_send(
                intake_id=iid,invitation_id=prepared["invitation_id"],token=token)
            assert claim["claimed"] is True
            assert claim["state"]=="SEND_ATTEMPTED_UNCONFIRMED"
            with pytest.raises(ValueError,match="INVITATION_ALREADY_ATTEMPTED"):
                await store.claim_connect_invitation_send(
                    intake_id=iid,invitation_id=prepared["invitation_id"],token=token)
            ack=await store.finish_connect_invitation_send(
                intake_id=iid,invitation_id=prepared["invitation_id"],
                provider_accepted=True,provider_message_id="resend_fixture_012345")
            assert ack["provider_accepted"] is True
            assert ack["state"]=="SENT_PROVIDER_ACCEPTED"
            assert ack["recipient_delivery_verified"] is False
            with pytest.raises(ValueError,match="INVITATION_SEND_STATE_CONFLICT"):
                await store.finish_connect_invitation_send(
                    intake_id=iid,invitation_id=prepared["invitation_id"],
                    provider_accepted=True,provider_message_id="second_id")
            rows=await store.list_connect_by_intake(intake_id=iid)
            projected=triage_connect_record(next(x for x in rows if x["intake_id"]==iid))
            assert projected["invitations"][0]["state"]=="SENT_PROVIDER_ACCEPTED"
            assert projected["invitations"][0]["provider_message_id"]=="resend_fixture_012345"
            assert "token_hash" not in projected["invitations"][0]
            assert projected["execution_status"]=="NOT_DISPATCHED"
            assert projected["cash_collected"] is None
        finally:
            await store.close()
            db=await __import__("asyncpg").connect(url)
            try:
                await db.execute("DELETE FROM noetfield.public_intakes WHERE intake_id=$1",iid)
            finally:
                await db.close()
    asyncio.run(run())
