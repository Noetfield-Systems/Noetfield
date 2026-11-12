"""Noetfield Connect relationship graph, projected from existing source intake rows.

No new CRM tables, new canonical IDs, or cross-venture exports. Submitted
email equality is a provisional claimed identity, not proof of mailbox ownership.
"""
from __future__ import annotations

import hashlib
from typing import Any


def project_relationship(rows: list[dict[str, Any]], intake_id: str) -> dict[str, Any]:
    valid = [r for r in rows if isinstance(r.get("metadata"), dict)
             and r["metadata"].get("form_id") == "nfConnectWizard"
             and r["metadata"].get("intake_kind") != "test"]
    selected = next((r for r in valid if r.get("intake_id") == intake_id), None)
    if not selected:
        return {}
    email = str(selected.get("contact_email") or "").strip().casefold()
    if not email:
        return {}
    valid = [r for r in valid if str(r.get("contact_email") or "").strip().casefold() == email]
    person_id = "claim_person_" + hashlib.sha256(email.encode()).hexdigest()[:20]
    nodes = [{
        "id": person_id, "type": "person_claim",
        "label": selected.get("contact_name") or "Contact",
        "email": email,
        "identity_status": "SAME_REPORTED_EMAIL_NOT_VERIFIED",
        "canonical_crm_id": None,
    }]
    edges: list[dict[str, Any]] = []
    timeline: list[dict[str, Any]] = []
    organizations: set[str] = set()
    ventures: set[str] = set()
    for row in valid:
        iid = str(row["intake_id"])
        meta = row.get("metadata") or {}
        qual = row.get("qualification_json") or {}
        ops = qual.get("connect_ops") or {} if isinstance(qual, dict) else {}
        if not isinstance(ops, dict):
            ops = {}
        venture = str(meta.get("initiative") or "portfolio")[:80]
        ventures.add(venture)
        kind = str(meta.get("topic") or "other")[:40]
        nodes.append({
            "id": iid, "type": "opportunity", "source": iid,
            "label": str(meta.get("proposal_title") or kind)[:160],
            "venture": venture, "kind": kind,
            "offer": str(meta.get("offering") or "")[:1200],
            "ask": str(meta.get("requesting") or "")[:1200],
            "role": str(meta.get("participant_role") or "")[:80],
            "contact_consent": meta.get("consent_contact") is True,
            "stage": ops.get("stage") or "NEW",
            "evidence": "SELF_REPORTED_SOURCE_INTAKE",
        })
        edges.append({"from": person_id, "to": iid, "kind": "submitted",
                      "provenance": iid, "evidence": "SAME_SUBMITTED_EMAIL"})
        org = str(row.get("organization") or "").strip()
        if org:
            oid = "claim_org_" + hashlib.sha256((email+"|"+org.casefold()).encode()).hexdigest()[:20]
            if oid not in organizations:
                nodes.append({"id": oid, "type": "organization_claim",
                              "label": org[:200], "identity_status": "SELF_REPORTED_UNVERIFIED"})
                organizations.add(oid)
            edges.append({"from": person_id, "to": oid, "kind": "claimed_affiliation",
                          "provenance": iid, "evidence": "SELF_REPORTED"})
            edges.append({"from": oid, "to": iid, "kind": "related_opportunity",
                          "provenance": iid, "evidence": "SELF_REPORTED"})
        timeline.append({"at": str(row.get("created_at") or ""),
                         "kind": "intake.persisted", "intake_id": iid,
                         "detail": "Source submission stored; no acceptance or execution",
                         "evidence": "SOURCE_RECORD"})
        for event in list(ops.get("history") or [])[-50:]:
            if isinstance(event, dict):
                timeline.append({"at": str(event.get("at") or ""),
                                 "kind": "operator.decision", "intake_id": iid,
                                 "detail": str(event.get("note") or event.get("next_action") or "")[:800],
                                 "evidence": "OPERATOR_RECORDED"})
        for event in list(ops.get("interactions") or [])[-100:]:
            if isinstance(event, dict):
                timeline.append({"at": str(event.get("created_at") or ""),
                                 "kind": str(event.get("kind") or ""), "intake_id": iid,
                                 "detail": str(event.get("body") or "")[:2200],
                                 "source_url": str(event.get("evidence_url") or ""),
                                 "evidence": "SOURCE_REPORTED_NOT_INDEPENDENTLY_VERIFIED"})
        for invitation in list(ops.get("invitations") or [])[-12:]:
            if isinstance(invitation, dict):
                timeline.append({"at": str(invitation.get("created_at") or ""),
                                 "kind": "invitation.prepared", "intake_id": iid,
                                 "detail": str(invitation.get("scope") or ""),
                                 "state": invitation.get("state"),
                                 "evidence": "PREPARED_NOT_SENT"})
                if invitation.get("responded_at"):
                    timeline.append({"at": str(invitation["responded_at"]),
                                     "kind": "invitation.response", "intake_id": iid,
                                     "detail": str(invitation.get("state") or ""),
                                     "evidence": "TOKEN_HOLDER_NOT_IDENTITY_VERIFIED"})
    timeline.sort(key=lambda x:x["at"], reverse=True)
    return {
        "schema": "noetfield.connect.relationship-graph.v1",
        "identity_basis": "SAME_SUBMITTED_EMAIL_CLAIM_ONLY",
        "canonical_crm_sync": "NOT_CONNECTED",
        "cross_venture_export": False,
        "person_id": person_id,
        "opportunity_count": len(valid),
        "ventures": sorted(ventures),
        "nodes": nodes,
        "edges": edges,
        "timeline": timeline,
        "verified_external_outcomes": 0,
        "verified_cash_collected": None,
    }
