"""PostgreSQL-backed public intake store."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import asyncpg

from noetfield_governance.intake_store import IntakeRecord


class PostgresIntakeStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._database_url)

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def record(
        self,
        *,
        organization: str,
        contact_email: str,
        message: str,
        request_id: str | None = None,
        contact_name: str | None = None,
        sku: str = "trust_brief",
        vector: str = "web-intake",
        source: str = "api",
        metadata: dict[str, Any] | None = None,
        qualification_json: dict[str, Any] | None = None,
    ) -> IntakeRecord:
        await self.connect()
        assert self._pool is not None

        if request_id:
            existing = await self.get_by_request_id(request_id)
            if existing is not None:
                return existing

        rec = IntakeRecord(
            intake_id="INT-" + uuid.uuid4().hex[:12].upper(),
            created_at=datetime.now(UTC).isoformat(),
            request_id=request_id,
            organization=organization.strip(),
            contact_name=(contact_name or "").strip() or None,
            contact_email=contact_email.strip().lower(),
            sku=sku,
            vector=vector,
            source=source,
            message=message.strip(),
            metadata=metadata or {},
            qualification_json=qualification_json,
        )

        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.public_intakes (
                  intake_id, request_id, organization, contact_name,
                  contact_email, sku, vector, source, message, metadata,
                  qualification_json
                )
                values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10::jsonb, $11::jsonb)
                """,
                rec.intake_id,
                rec.request_id,
                rec.organization,
                rec.contact_name,
                rec.contact_email,
                rec.sku,
                rec.vector,
                rec.source,
                rec.message,
                json.dumps(rec.metadata, default=str),
                json.dumps(rec.qualification_json, default=str)
                if rec.qualification_json is not None
                else None,
            )
        return rec

    async def get_by_request_id(self, request_id: str) -> IntakeRecord | None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                select intake_id, created_at, request_id, organization, contact_name,
                       contact_email, sku, vector, source, message, metadata,
                       qualification_json,
                       email_archive_status, email_archive_updated_at, email_archive_detail
                from noetfield.public_intakes
                where request_id = $1
                limit 1
                """,
                request_id.upper(),
            )
        if row is None:
            return None
        return _row_to_record(row)

    async def public_connect_participant_status(
        self, *, request_id: str, email: str,
    ) -> dict[str, Any] | None:
        """Read only participant-safe source-backed status. No CRM notes or owner data."""
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """SELECT intake_id,created_at,contact_email,metadata,qualification_json
                   FROM noetfield.public_intakes WHERE request_id=$1""",
                request_id.strip().upper(),
            )
        if row is None or row["contact_email"].lower() != email.strip().lower():
            return None
        metadata = row["metadata"] or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        if metadata.get("form_id") != "nfConnectWizard" or metadata.get("intake_kind") == "test":
            return None
        qualification = row["qualification_json"] or {}
        if isinstance(qualification, str):
            qualification = json.loads(qualification)
        ops = qualification.get("connect_ops") or {}
        stage = str(ops.get("stage") or "NEW").upper()
        allowed = {"NEW","QUALIFYING","ROUTED","ENGAGED","NEGOTIATING","PILOT",
                   "WON","LOST","ARCHIVED"}
        if stage not in allowed:
            stage = "NEW"
        descriptions = {
            "NEW": "Received in Noetfield Connect. Review pending.",
            "QUALIFYING": "Your proposal is being reviewed for relevance and fit.",
            "ROUTED": "The opportunity has entered an internal review route.",
            "ENGAGED": "A collaboration conversation is recorded as active.",
            "NEGOTIATING": "Terms are under review; no agreement is implied.",
            "PILOT": "Pilot-stage activity is recorded; delivery is not independently verified.",
            "WON": "The internal record is marked won; confirm any agreement directly.",
            "LOST": "This opportunity is marked closed without conversion.",
            "ARCHIVED": "The opportunity has been archived.",
        }
        return {
            "found": True, "intake_id": row["intake_id"],
            "stage": stage, "detail": descriptions[stage],
            "created_at": row["created_at"].isoformat() if hasattr(row["created_at"],"isoformat") else str(row["created_at"]),
            "updated_at": ops.get("updated_at"),
            "independently_verified": False,
            "receipt_type": "SOURCE_BACKED_PARTICIPANT_STATUS",
        }

    async def append_public_connect_feedback(
        self, *, request_id: str, email: str, rating: int,
        message: str, feedback_id: str,
    ) -> dict[str, Any] | None:
        """Append feedback to the SAME Connect record; never mint a new lead."""
        if not 1 <= rating <= 5 or not 5 <= len(message.strip()) <= 1200:
            raise ValueError("FEEDBACK_INVALID")
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow(
                    """SELECT intake_id,contact_email,metadata,qualification_json
                       FROM noetfield.public_intakes
                       WHERE request_id=$1 FOR UPDATE""",
                    request_id.strip().upper(),
                )
                if row is None or row["contact_email"].lower() != email.strip().lower():
                    return None
                metadata = row["metadata"] or {}
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                if metadata.get("form_id") != "nfConnectWizard" or metadata.get("intake_kind") == "test":
                    return None
                qualification = row["qualification_json"] or {}
                if isinstance(qualification, str):
                    qualification = json.loads(qualification)
                ops = dict(qualification.get("connect_ops") or {})
                interactions = list(ops.get("interactions") or [])
                for item in interactions:
                    if item.get("feedback_id") == feedback_id:
                        return {"recorded": True,"deduped": True,
                                "intake_id": row["intake_id"], "feedback_id":feedback_id}
                public_feedback = [item for item in interactions
                                   if item.get("actor") == "submitter_token_holder"
                                   and item.get("kind") == "human_feedback"]
                if len(public_feedback) >= 5:
                    raise ValueError("FEEDBACK_LIMIT_REACHED")
                event = {
                    "id": "act_" + uuid.uuid4().hex[:16],
                    "feedback_id": feedback_id,
                    "kind": "human_feedback",
                    "body": "Applicant feedback (" + str(rating) + "/5): " + message.strip(),
                    "actor": "submitter_token_holder",
                    "state": "SOURCE_REPORTED_NOT_INDEPENDENTLY_VERIFIED",
                    "evidence_url": "",
                    "created_at": datetime.now(UTC).isoformat(),
                }
                ops["interactions"] = interactions[-99:] + [event]
                ops["revision"] = int(ops.get("revision") or 0) + 1
                ops["updated_at"] = event["created_at"]
                await connection.execute(
                    """UPDATE noetfield.public_intakes SET qualification_json=jsonb_set(
                        COALESCE(qualification_json,'{}'::jsonb),
                        '{connect_ops}', $2::jsonb,true)
                       WHERE intake_id=$1""",
                    row["intake_id"], json.dumps(ops),
                )
                return {"recorded": True,"deduped":False,
                        "intake_id": row["intake_id"],"feedback_id":feedback_id}

    async def update_email_archive_status(
        self,
        *,
        request_id: str,
        status: str,
        detail: str | None = None,
    ) -> dict[str, Any] | None:
        await self.connect()
        assert self._pool is not None
        rid = request_id.strip().upper()
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                update noetfield.public_intakes
                set email_archive_status = $2,
                    email_archive_updated_at = now(),
                    email_archive_detail = $3
                where request_id = $1
                returning intake_id, created_at, request_id, organization, contact_name,
                          contact_email, sku, vector, source, message, metadata,
                          qualification_json,
                          email_archive_status, email_archive_updated_at, email_archive_detail
                """,
                rid,
                status,
                detail,
            )
        if row is None:
            return None
        return _row_to_dict(row)

    async def list_recent(self, *, limit: int = 50) -> list[dict[str, Any]]:
        await self.connect()
        assert self._pool is not None
        cap = max(1, min(limit, 100))
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select intake_id, created_at, request_id, organization, contact_name,
                       contact_email, sku, vector, source, message, metadata,
                       qualification_json,
                       email_archive_status, email_archive_updated_at, email_archive_detail
                from noetfield.public_intakes
                order by created_at desc
                limit $1
                """,
                cap,
            )
        return [_row_to_dict(row) for row in rows]

    async def list_after(
        self,
        *,
        created_after: str | None = None,
        intake_after: str = "",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return a stable ascending cursor page for internal operational projections."""
        await self.connect()
        assert self._pool is not None
        cap = max(1, min(limit, 100))
        columns = """
            select intake_id, created_at, request_id, organization, contact_name,
                   contact_email, sku, vector, source, message, metadata,
                   qualification_json, email_archive_status, email_archive_updated_at,
                   email_archive_detail
            from noetfield.public_intakes
        """
        async with self._pool.acquire() as connection:
            if created_after:
                cursor_time = datetime.fromisoformat(created_after.replace("Z", "+00:00"))
                rows = await connection.fetch(
                    columns + """
                    where (created_at, intake_id) > ($1::timestamptz, $2)
                    order by created_at asc, intake_id asc
                    limit $3
                    """,
                    cursor_time,
                    intake_after or "",
                    cap,
                )
            else:
                rows = await connection.fetch(
                    columns + """
                    order by created_at asc, intake_id asc
                    limit $1
                    """,
                    cap,
                )
        return [_row_to_dict(row) for row in rows]

    async def update_connect_state(
        self, *, intake_id: str, expected_revision: int, stage: str,
        owner: str, next_action: str, due_date: str | None, note: str,
    ) -> dict[str, Any] | None:
        """Update existing canonical intake metadata with a locked revision check.

        No new CRM, database or table. Operator state is stored in the\n        server-owned qualification_json column, never visitor metadata.
        Returns None for unknown/non-Connect IDs; raises ValueError for conflicts.
        """
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow(
                    """SELECT intake_id, qualification_json FROM noetfield.public_intakes
                       WHERE intake_id=$1 AND metadata->>'form_id'='nfConnectWizard'
                       FOR UPDATE""", intake_id)
                if row is None:
                    return None
                qualification = row["qualification_json"]
                if isinstance(qualification, str):
                    qualification = json.loads(qualification)
                qualification = dict(qualification or {})
                existing = qualification.get("connect_ops") or {}
                if not isinstance(existing, dict):
                    existing = {}
                version = int(existing.get("revision") or 0)
                if version != expected_revision:
                    raise ValueError("OPPORTUNITY_VERSION_CONFLICT")
                changed = datetime.now(UTC).isoformat()
                history = list(existing.get("history") or [])[-19:]
                history.append({
                    "revision": version + 1, "at": changed,
                    "stage": stage, "owner": owner,
                    "next_action": next_action, "due_date": due_date,
                    "note": note,
                })
                updated = {
                    **existing,
                    "revision": version + 1, "updated_at": changed,
                    "stage": stage, "owner": owner,
                    "next_action": next_action,
                    "due_date": due_date, "note": note,
                    "history": history,
                }
                await connection.execute(
                    """UPDATE noetfield.public_intakes
                       SET qualification_json=jsonb_set(
                           coalesce(qualification_json, '{}'::jsonb),
                           '{connect_ops}', $2::jsonb, true)
                       WHERE intake_id=$1""",
                    intake_id, json.dumps(updated),
                )
                return updated


    async def list_connect_page(self, *, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """Page source-owned Connect records, never copying them into a second CRM."""
        await self.connect()
        assert self._pool is not None
        cap = max(1, min(int(limit), 100))
        skip = max(0, min(int(offset), 10000))
        predicate = """metadata->>'form_id'='nfConnectWizard'
                       AND COALESCE(metadata->>'intake_kind','lead') <> 'test'"""
        columns = """intake_id,created_at,request_id,organization,contact_name,
                     contact_email,sku,vector,source,message,metadata,qualification_json,
                     email_archive_status,email_archive_updated_at,email_archive_detail"""
        async with self._pool.acquire() as connection:
            total = await connection.fetchval(
                "SELECT COUNT(*)::int FROM noetfield.public_intakes WHERE " + predicate
            )
            rows = await connection.fetch(
                "SELECT " + columns + " FROM noetfield.public_intakes WHERE " +
                predicate + " ORDER BY created_at DESC,intake_id DESC LIMIT $1 OFFSET $2",
                cap, skip,
            )
        return {"records": [_row_to_dict(row) for row in rows],
                "total": int(total or 0), "limit": cap, "offset": skip}

    async def list_connect_by_intake(self, *, intake_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Email-exact case clusters; no name-only identity merge or cross-company export.

        The email is counterparty-reported, NOT proof of mailbox ownership. All
        graph edges retain the actual intake source and venture-specific scope.
        """
        await self.connect()
        assert self._pool is not None
        columns = """p.intake_id,p.created_at,p.request_id,p.organization,p.contact_name,
                     p.contact_email,p.sku,p.vector,p.source,p.message,p.metadata,
                     p.qualification_json,p.email_archive_status,
                     p.email_archive_updated_at,p.email_archive_detail"""
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                "SELECT " + columns + """ FROM noetfield.public_intakes p
                JOIN noetfield.public_intakes target
                  ON lower(p.contact_email)=lower(target.contact_email)
                WHERE target.intake_id=$1
                  AND target.metadata->>'form_id'='nfConnectWizard'
                  AND p.metadata->>'form_id'='nfConnectWizard'
                  AND COALESCE(p.metadata->>'intake_kind','lead')<>'test'
                ORDER BY p.created_at DESC,p.intake_id DESC LIMIT $2""",
                intake_id, max(1,min(int(limit),100)),
            )
        return [_row_to_dict(row) for row in rows]

    async def append_connect_activity(
        self, *, intake_id: str, expected_revision: int, action: str,
        body: str, evidence_url: str = "", actor: str = "operator",
    ) -> dict[str, Any] | None:
        """Bounded, revision-protected evidence timeline in the canonical intake JSON.

        This is an operator observation, not an email send, signed contract,
        external meeting booking, workpacket execution, or verified money.
        """
        if action not in {
            "qualification","research_note","interaction_observed","draft_prepared",
            "followup_planned","intro_proposed","matching_proposed",
            "human_feedback","external_source_reference","workpacket_proposed",
        }:
            raise ValueError("CONNECT_ACTIVITY_TYPE_INVALID")
        if not isinstance(body,str) or not 3 <= len(body.strip()) <= 2200:
            raise ValueError("CONNECT_ACTIVITY_BODY_INVALID")
        if evidence_url and (not isinstance(evidence_url,str)
                             or len(evidence_url)>700
                             or not evidence_url.startswith("https://")
                             or any(c.isspace() for c in evidence_url)):
            raise ValueError("CONNECT_ACTIVITY_EVIDENCE_INVALID")
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                row=await connection.fetchrow(
                    """SELECT qualification_json FROM noetfield.public_intakes
                       WHERE intake_id=$1 AND metadata->>'form_id'='nfConnectWizard'
                       FOR UPDATE""", intake_id)
                if row is None:
                    return None
                base=row["qualification_json"] or {}
                if isinstance(base,str):
                    base=json.loads(base)
                ops=dict(base.get("connect_ops") or {})
                if int(ops.get("revision") or 0)!=expected_revision:
                    raise ValueError("OPPORTUNITY_VERSION_CONFLICT")
                event={
                    "id":"act_"+uuid.uuid4().hex[:16],
                    "kind":action,"body":body.strip(),
                    "evidence_url":evidence_url,
                    "actor":actor,"state":"SOURCE_REPORTED_NOT_INDEPENDENTLY_VERIFIED",
                    "created_at":datetime.now(UTC).isoformat(),
                }
                ops["interactions"]=list(ops.get("interactions") or [])[-99:]+[event]
                ops["revision"]=expected_revision+1
                ops["updated_at"]=event["created_at"]
                await connection.execute(
                    """UPDATE noetfield.public_intakes SET qualification_json=jsonb_set(
                        COALESCE(qualification_json,'{}'::jsonb),
                        '{connect_ops}', $2::jsonb,true)
                       WHERE intake_id=$1""",intake_id,json.dumps(ops),
                )
                return {"revision":ops["revision"],"interaction":event,
                        "interactions_count":len(ops["interactions"])}

    async def create_connect_invitation(
        self, *, intake_id: str, expected_revision: int,
        scope: str, message: str, request_id: str,
    ) -> dict[str, Any] | None:
        """Create a tokenized opt-in proposal; no outbound message is sent."""
        if scope not in {"introduction","collaboration","trial","specialist_review","partner"}:
            raise ValueError("INVITATION_SCOPE_INVALID")
        if not isinstance(message,str) or not 15<=len(message.strip())<=1500:
            raise ValueError("INVITATION_MESSAGE_INVALID")
        if not isinstance(request_id,str) or not 16<=len(request_id)<=100 or not all(
            c.isascii() and (c.isalnum() or c in "-_") for c in request_id
        ):
            raise ValueError("INVITATION_REQUEST_ID_INVALID")
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                row=await connection.fetchrow(
                    """SELECT qualification_json,metadata FROM noetfield.public_intakes
                       WHERE intake_id=$1 AND metadata->>'form_id'='nfConnectWizard'
                       FOR UPDATE""",intake_id)
                if row is None:
                    return None
                base=row["qualification_json"] or {}
                if isinstance(base,str):base=json.loads(base)
                ops=dict(base.get("connect_ops") or {})
                old=list(ops.get("invitations") or [])
                for invited in old:
                    if invited.get("request_id")==request_id:
                        return {"invitation_id":invited["id"],"state":invited["state"],
                                "created":False,"share_token":None,
                                "reason":"REPLAY_EXISTING_NO_TOKEN"}
                if int(ops.get("revision") or 0)!=expected_revision:
                    raise ValueError("OPPORTUNITY_VERSION_CONFLICT")
                if len(old)>=12:
                    raise ValueError("INVITATION_LIMIT_REACHED")
                token=__import__("secrets").token_urlsafe(32)
                invitation_id="inv_"+uuid.uuid4().hex[:16]
                issued=datetime.now(UTC)
                item={
                    "id":invitation_id,"request_id":request_id,
                    "scope":scope,"message":message.strip(),
                    "token_hash":__import__("hashlib").sha256(token.encode()).hexdigest(),
                    "state":"PREPARED_NOT_SENT",
                    "created_at":issued.isoformat(),
                    "expires_at":(issued+__import__("datetime").timedelta(days=14)).isoformat(),
                    "responded_at":None,
                }
                ops["invitations"]=old+[item]
                ops["revision"]=expected_revision+1
                ops["updated_at"]=issued.isoformat()
                await connection.execute(
                    """UPDATE noetfield.public_intakes SET qualification_json=jsonb_set(
                        COALESCE(qualification_json,'{}'::jsonb),
                        '{connect_ops}', $2::jsonb,true)
                       WHERE intake_id=$1""",intake_id,json.dumps(ops),
                )
                return {"invitation_id":invitation_id,"scope":scope,
                        "state":"PREPARED_NOT_SENT","created":True,
                        "share_token":token,"expires_at":item["expires_at"],
                        "external_action_executed":False}

    async def respond_connect_invitation(
        self, *, intake_id: str, invitation_id: str,
        token: str, email: str, decision: str,
    ) -> dict[str, Any] | None:
        """Bearer response from consenting person; not verified mailbox ownership."""
        import hashlib
        import hmac
        if decision not in {"accept","decline"} or len(token)>200 or len(token)<32:
            raise ValueError("INVITATION_RESPONSE_INVALID")
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                row=await connection.fetchrow(
                    """SELECT contact_email,qualification_json FROM noetfield.public_intakes
                       WHERE intake_id=$1 AND metadata->>'form_id'='nfConnectWizard'
                       FOR UPDATE""",intake_id)
                if row is None:return None
                if not hmac.compare_digest((email or "").strip().casefold(),
                                           row["contact_email"].strip().casefold()):
                    raise ValueError("INVITATION_RECIPIENT_MISMATCH")
                base=row["qualification_json"] or {}
                if isinstance(base,str):base=json.loads(base)
                ops=dict(base.get("connect_ops") or {})
                invitations=list(ops.get("invitations") or [])
                found=next((i for i in invitations if i.get("id")==invitation_id),None)
                if found is None or not hmac.compare_digest(
                    str(found.get("token_hash") or ""),
                    hashlib.sha256(token.encode()).hexdigest()
                ):
                    raise ValueError("INVITATION_TOKEN_INVALID")
                if datetime.fromisoformat(found["expires_at"])<=datetime.now(UTC):
                    raise ValueError("INVITATION_EXPIRED")
                target="ACCEPTED_BY_TOKEN_HOLDER" if decision=="accept" else "DECLINED_BY_TOKEN_HOLDER"
                if found["state"] in {"ACCEPTED_BY_TOKEN_HOLDER","DECLINED_BY_TOKEN_HOLDER"}:
                    if found["state"]!=target:raise ValueError("INVITATION_DECISION_CONFLICT")
                    return {"state":target,"created":False,"identity_verified":False}
                found["state"]=target
                found["responded_at"]=datetime.now(UTC).isoformat()
                ops["invitations"]=invitations
                ops["revision"]=int(ops.get("revision") or 0)+1
                ops["updated_at"]=found["responded_at"]
                await connection.execute(
                    """UPDATE noetfield.public_intakes SET qualification_json=jsonb_set(
                        COALESCE(qualification_json,'{}'::jsonb),
                        '{connect_ops}', $2::jsonb,true)
                       WHERE intake_id=$1""",intake_id,json.dumps(ops),
                )
                return {"state":target,"created":True,
                        "identity_verified":False,
                        "external_action_executed":False,
                        "confirmed_meeting":False,
                        "scoped_authority_granted":False}

    async def record_connect_outcome(
        self, *, intake_id: str, expected_revision: int,
        request_id: str, outcome_type: str, evidence_url: str, note: str,
    ) -> dict[str, Any] | None:
        """Store an operator-reported result, never a verified conversion or cash."""
        import re
        from urllib.parse import urlsplit
        permitted = {"meeting", "introduction", "trial", "pilot", "contract",
                     "work_delivered", "declined", "other"}
        if outcome_type not in permitted:
            raise ValueError("CONNECT_OUTCOME_TYPE_INVALID")
        if not re.fullmatch(r"[A-Za-z0-9_-]{16,100}", request_id):
            raise ValueError("CONNECT_OUTCOME_REQUEST_ID_INVALID")
        try:
            url = urlsplit(evidence_url)
            valid = (url.scheme == "https" and bool(url.hostname)
                     and not url.username and not url.password
                     and not any(c.isspace() for c in evidence_url)
                     and len(evidence_url) <= 700)
        except ValueError:
            valid = False
        if not valid:
            raise ValueError("CONNECT_OUTCOME_EVIDENCE_REQUIRED")
        if not isinstance(note, str) or not 10 <= len(note.strip()) <= 1200:
            raise ValueError("CONNECT_OUTCOME_NOTE_REQUIRED")
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow(
                    """SELECT qualification_json FROM noetfield.public_intakes
                       WHERE intake_id=$1 AND metadata->>'form_id'='nfConnectWizard'
                         AND COALESCE(metadata->>'intake_kind','lead')<>'test'
                       FOR UPDATE""", intake_id)
                if row is None:
                    return None
                qualification = row["qualification_json"] or {}
                if isinstance(qualification, str):
                    qualification = json.loads(qualification)
                ops = dict(qualification.get("connect_ops") or {})
                outcomes = list(ops.get("reported_outcomes") or [])
                for previous in outcomes:
                    if previous.get("request_id") == request_id:
                        return {"created": False, "revision": int(ops.get("revision") or 0),
                                "reported_outcome": previous}
                version = int(ops.get("revision") or 0)
                if version != expected_revision:
                    raise ValueError("OPPORTUNITY_VERSION_CONFLICT")
                if len(outcomes) >= 25:
                    raise ValueError("CONNECT_OUTCOME_LIMIT_REACHED")
                event = {
                    "id": "out_" + uuid.uuid4().hex[:16],
                    "request_id": request_id,
                    "type": outcome_type,
                    "evidence_url": evidence_url.strip(),
                    "note": note.strip(),
                    "reported_at": datetime.now(UTC).isoformat(),
                    "evidence_level": "OPERATOR_REPORTED_NOT_INDEPENDENTLY_VERIFIED",
                    "independently_verified": False,
                    "cash_collected": None,
                }
                ops["reported_outcomes"] = outcomes + [event]
                ops["reported_outcome"] = event
                ops["revision"] = version + 1
                ops["updated_at"] = event["reported_at"]
                await connection.execute(
                    """UPDATE noetfield.public_intakes SET qualification_json=jsonb_set(
                        COALESCE(qualification_json,'{}'::jsonb),
                        '{connect_ops}', $2::jsonb, true)
                       WHERE intake_id=$1""", intake_id, json.dumps(ops))
                return {"created": True, "revision": ops["revision"],
                        "reported_outcome": event}


    async def get_connect_delivery_source(self, *, intake_id: str) -> dict[str, Any] | None:
        """Exact source contact and consent; never an arbitrary browser recipient."""
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as db:
            row = await db.fetchrow(
                """SELECT intake_id,request_id,contact_name,contact_email,metadata
                   FROM noetfield.public_intakes
                   WHERE intake_id=$1 AND metadata->>'form_id'='nfConnectWizard'
                     AND COALESCE(metadata->>'intake_kind','lead')<>'test'""",
                intake_id)
        if row is None:
            return None
        metadata = row["metadata"] or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        return {
            "intake_id": row["intake_id"], "request_id": row["request_id"],
            "contact_name": row["contact_name"] or "",
            "contact_email": row["contact_email"],
            "contact_consent": metadata.get("consent_contact") is True,
        }

    async def claim_connect_invitation_send(
        self, *, intake_id: str, invitation_id: str, token: str,
    ) -> dict[str, Any] | None:
        """Durably claim a single provider attempt before any external send.

        A crash or network timeout leaves DELIVERY_UNCONFIRMED; no blind replay
        may send a second copy. The bearer token is not written to PostgreSQL.
        """
        import hashlib
        import hmac
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as db:
            async with db.transaction():
                row = await db.fetchrow(
                    """SELECT qualification_json,metadata FROM noetfield.public_intakes
                       WHERE intake_id=$1 AND metadata->>'form_id'='nfConnectWizard'
                         AND COALESCE(metadata->>'intake_kind','lead')<>'test'
                       FOR UPDATE""", intake_id)
                if row is None:
                    return None
                metadata = row["metadata"] or {}
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                if metadata.get("consent_contact") is not True:
                    raise ValueError("CONTACT_CONSENT_REQUIRED")
                qual = row["qualification_json"] or {}
                if isinstance(qual, str):
                    qual = json.loads(qual)
                ops = dict(qual.get("connect_ops") or {})
                invited = list(ops.get("invitations") or [])
                item = next((i for i in invited if i.get("id") == invitation_id), None)
                if item is None or not hmac.compare_digest(
                    str(item.get("token_hash") or ""),
                    hashlib.sha256(token.encode()).hexdigest()
                ):
                    raise ValueError("INVITATION_TOKEN_INVALID")
                if item.get("state") != "PREPARED_NOT_SENT":
                    raise ValueError("INVITATION_ALREADY_ATTEMPTED")
                item["state"] = "SEND_ATTEMPTED_UNCONFIRMED"
                item["delivery_attempted_at"] = datetime.now(UTC).isoformat()
                ops["invitations"] = invited
                ops["revision"] = int(ops.get("revision") or 0) + 1
                ops["updated_at"] = item["delivery_attempted_at"]
                await db.execute(
                    """UPDATE noetfield.public_intakes
                       SET qualification_json=jsonb_set(
                           COALESCE(qualification_json,'{}'::jsonb),
                           '{connect_ops}',$2::jsonb,true)
                       WHERE intake_id=$1""", intake_id, json.dumps(ops))
                return {"claimed": True, "invitation_id": invitation_id,
                        "state": item["state"], "revision": ops["revision"]}

    async def finish_connect_invitation_send(
        self, *, intake_id: str, invitation_id: str,
        provider_accepted: bool, provider_message_id: str = "",
        detail: str = "",
    ) -> dict[str, Any] | None:
        """Persist provider acceptance, not mailbox delivery or human consent."""
        if provider_accepted and not provider_message_id:
            raise ValueError("PROVIDER_MESSAGE_ID_REQUIRED")
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as db:
            async with db.transaction():
                row = await db.fetchrow(
                    """SELECT qualification_json FROM noetfield.public_intakes
                       WHERE intake_id=$1 AND metadata->>'form_id'='nfConnectWizard'
                       FOR UPDATE""", intake_id)
                if row is None:
                    return None
                qual = row["qualification_json"] or {}
                if isinstance(qual, str):
                    qual = json.loads(qual)
                ops = dict(qual.get("connect_ops") or {})
                invited = list(ops.get("invitations") or [])
                item = next((i for i in invited if i.get("id") == invitation_id), None)
                if item is None:
                    return None
                if item.get("state") != "SEND_ATTEMPTED_UNCONFIRMED":
                    raise ValueError("INVITATION_SEND_STATE_CONFLICT")
                item["state"] = ("SENT_PROVIDER_ACCEPTED" if provider_accepted
                                 else "DELIVERY_UNCONFIRMED")
                item["provider_message_id"] = provider_message_id[:120] if provider_accepted else None
                item["delivery_error"] = detail[:120] if not provider_accepted else None
                item["delivery_completed_at"] = datetime.now(UTC).isoformat()
                ops["invitations"] = invited
                ops["revision"] = int(ops.get("revision") or 0) + 1
                ops["updated_at"] = item["delivery_completed_at"]
                await db.execute(
                    """UPDATE noetfield.public_intakes
                       SET qualification_json=jsonb_set(
                           COALESCE(qualification_json,'{}'::jsonb),
                           '{connect_ops}',$2::jsonb,true)
                       WHERE intake_id=$1""", intake_id, json.dumps(ops))
                return {"invitation_id": invitation_id, "state": item["state"],
                        "provider_message_id": item["provider_message_id"],
                        "revision": ops["revision"],
                        "provider_accepted": provider_accepted,
                        "recipient_delivery_verified": False}

    async def count(self) -> int:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            val = await connection.fetchval("select count(*)::int from noetfield.public_intakes")
        return int(val or 0)


def _row_to_record(row: asyncpg.Record) -> IntakeRecord:
    meta = row["metadata"]
    if isinstance(meta, str):
        meta = json.loads(meta)
    qual = row["qualification_json"] if "qualification_json" in row else None
    if isinstance(qual, str):
        qual = json.loads(qual)
    created = row["created_at"]
    if hasattr(created, "isoformat"):
        created = created.isoformat()
    archive_updated = row["email_archive_updated_at"] if "email_archive_updated_at" in row else None
    if archive_updated is not None and hasattr(archive_updated, "isoformat"):
        archive_updated = archive_updated.isoformat()
    return IntakeRecord(
        intake_id=row["intake_id"],
        created_at=str(created),
        request_id=row["request_id"],
        organization=row["organization"],
        contact_name=row["contact_name"],
        contact_email=row["contact_email"],
        sku=row["sku"],
        vector=row["vector"],
        source=row["source"],
        message=row["message"],
        metadata=dict(meta or {}),
        qualification_json=dict(qual) if qual else None,
        email_archive_status=row["email_archive_status"] if "email_archive_status" in row else None,
        email_archive_updated_at=str(archive_updated) if archive_updated else None,
        email_archive_detail=row["email_archive_detail"] if "email_archive_detail" in row else None,
    )


def _row_to_dict(row: asyncpg.Record) -> dict[str, Any]:
    rec = _row_to_record(row)
    from dataclasses import asdict

    return asdict(rec)
