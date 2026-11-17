"""Noetfield Founder commercial mission controller on canonical CRM evidence.

MISSION CONTRACT v1:
  SOURCE -> FIRST_PARTY_RESEARCH -> ACTUAL_MODEL_TRACE -> SOURCE-BOUND NEXT ACTION
  -> VERIFIED PERSON/PERMISSION -> PROVIDER SEND/REPLY -> ACCEPTED SOW
  -> LIVE PAID CHECKOUT -> COMPANY OS/RWA JOB -> INDEPENDENT VERIFIED DELIVERY
  -> REAL CUSTOMER ACCEPTANCE -> RETENTION.

This is a materialized work view of the EXISTING source/AI/deal/WorkPacket
tables, never a second CRM or permission to create a contact, send an email or
claim customer revenue. Discovery, inference, provider communications, payment
and delivery remain owned by their source systems.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import asyncpg

from noetfield_governance.commercial_pipeline import _database_url
from noetfield_governance.corporate_founder_ai import (
    _source_signature,_validate_model_analysis,prepare_ai,
)
from noetfield_governance.corporate_workpacket import prepare_workpackets
from noetfield_governance.corporate_outbound import _schema as prepare_outreach

SCHEMA="noetfield.founder-commercial-mission.v1"
_MAX_WRITE=150
_TERMINAL={"SUPPRESSED","OUT_OF_SCOPE","VERIFIED_DELIVERY"}


def compose_review_draft(row:dict[str,Any],analysis:dict[str,Any]) -> dict[str,str]|None:
    """Internal draft only, with actual first-party public phrase as context."""
    email=str(row.get("published_general_channel") or "").strip().lower()
    quote=str(analysis.get("evidence_phrase") or "").strip()
    if not email or not quote:
        return None
    lane=row.get("lane")
    name=str(row.get("organization") or "your team").strip()[:100]
    if lane=="RWA":
        subject="RWA technical feasibility — potential collaboration"
        offer=("Noetfield works on scoped RWA technical-readiness reviews, "
               "including the supporting technology and controls.")
        question="Would that type of technical feasibility discussion be relevant to your team?"
    else:
        subject="Sales workflow and AI operations — potential collaboration"
        offer=("Noetfield helps businesses evaluate sales follow-up "
               "and qualification workflows through a scoped AI Sales OS pilot.")
        question="Would an initial discussion be useful for your organization?"
    # Quote is already strictly validated against the source by the model
    # adapter; it is not presented as a known need, budget or purchase intent.
    text=("Hello "+name+" team,\n\n"
          "I found your public description mentioning “"+quote[:110]+"”. "
          +offer+"\n\n"+question+"\n\n"
          "Regards,\nNoetfield Systems")
    return {"to_public_business_channel":email,"subject":subject,
        "body":text,"status":"DRAFT_ONLY_NOT_SENT",
        "send_permission_verified":False,"company_need_verified":False}


def _plain(row:dict[str,Any])->dict[str,Any]:
    """Evidence-first next move; never promote a hypothetical buyer."""
    raw=row.get("analysis_json")
    analysis:dict[str,Any]={}
    if isinstance(raw,str) and raw:
        try:
            candidate=json.loads(raw)
            if isinstance(candidate,dict):
                analysis=candidate
        except ValueError:
            analysis={}
    evidence_current=bool(analysis and row.get("ai_source_signature") and
        str(row.get("ai_source_signature"))==_source_signature(row))
    if evidence_current:
        try:
            analysis=_validate_model_analysis(analysis,{
                "published_site_title":str(row.get("site_title") or ""),
                "published_site_description":str(row.get("site_description") or "")})
        except (ValueError,TypeError):
            analysis={}
    else:
        analysis={}
    contact=str(row.get("published_general_channel") or "")
    page=str(row.get("contact_page_url") or "")
    team=str(row.get("team_page_url") or "")
    scan=str(row.get("scan_state") or "NOT_RESEARCHED")
    review=str(row.get("review_status") or "")
    promoted=row.get("promoted_deal_id") is not None
    workpacket_state=str(row.get("workpacket_state") or "")
    if review in ("DO_NOT_CONTACT","DISQUALIFIED") or str(row.get("deal_stage") or "")=="LOST":
        state="SUPPRESSED"
        action="No commercial contact. Keep source in suppressed history."
    elif workpacket_state=="VERIFIED":
        state="VERIFIED_DELIVERY"
        action="Obtain the customer's authenticated acceptance and track retention."
    elif workpacket_state in ("ACKNOWLEDGED","RUNNING"):
        state="DELIVERY_IN_PROGRESS"
        action="Monitor the provider-admitted paid job and independent verifier receipt."
    elif workpacket_state in ("READY","DISPATCH_UNCONFIRMED","DISPATCHING","FAILED"):
        state="DELIVERY_DISPATCH_ATTENTION"
        action=("A paid WorkPacket exists but its provider admission or final proof "
                "is not confirmed. Inspect the original WorkPacket receipt and "
                "restore its original provider route; do not create a duplicate.")
    elif promoted and bool(row.get("has_verified_reply")):
        state="VERIFIED_CUSTOMER_REPLY"
        action="Review the actual buyer reply in the existing CRM and qualify next steps; no meeting is inferred."
    elif promoted and row.get("send_status")=="PROVIDER_ACCEPTED":
        state="SMTP_PROVIDER_ACCEPTED"
        action="The Noetfield mail provider accepted the introduction. Await a verified reply; inbox delivery is not proven."
    elif promoted and row.get("send_status"):
        state="OUTREACH_PROVIDER_UNCONFIRMED"
        action="Review this exact attempted message receipt before any retry. Do not send a duplicate."
    elif promoted:
        state="QUALIFIED_CRM_RECORD"
        action="Use the existing CRM deal next action; confirm SOW and payment before dispatch."
    elif analysis.get("fit_label")=="OUT_OF_SCOPE":
        state="OUT_OF_SCOPE"
        action="Do not use paid outreach on this source; revisit only if evidence changes."
    elif scan in ("SOURCE_UNAVAILABLE","NO_USABLE_WEBSITE"):
        state="OFFICIAL_SOURCE_NEEDED"
        action="Find an original official company website from a public source."
    elif not row.get("scanned_at"):
        state="SOURCE_RESEARCH_PENDING"
        action="Visit the company website and record public source evidence."
    elif not analysis:
        state="AGENT_RESEARCH_PENDING"
        action="Run the evidence-grounded sales specialist on the company source."
    elif contact and analysis.get("fit_label") in ("POSSIBLE_FIT","STRONG_FIT"):
        state="INTRO_REVIEW_READY"
        action=("Confirm the published channel's relevance and absence of a no-solicitation "
                "notice before using the existing outreach workflow.")
    elif page or team:
        state="PEOPLE_RESEARCH_PENDING"
        action="Review the actual company contact/team page for a relevant decision-maker."
    else:
        state="CONTACT_RESEARCH_PENDING"
        action="Find a documented business contact path, not an inferred personal email."
    draft=(compose_review_draft(row,analysis) if state=="INTRO_REVIEW_READY" else None)
    score=max(0,min(100,int(row.get("score") or 0)))
    priority=min(100,round(score*.55)+
        (20 if scan not in ("NOT_RESEARCHED","NO_USABLE_WEBSITE","SOURCE_UNAVAILABLE") else 0)+
        (15 if contact else 0)+
        (10 if analysis.get("fit_label") in ("STRONG_FIT","POSSIBLE_FIT") else 0))
    return {"source_key":str(row.get("source_key") or ""),
        "organization":str(row.get("organization") or ""),
        "lane":row.get("lane"),"offer":(
            "rwa_technical_sprint" if row.get("lane")=="RWA" else "ai_sales_os_pilot"),
        "state":state,"priority":priority,
        "next_action":action,"source_url":str(row.get("original_url") or ""),
        "contact_evidence_url":str(row.get("channel_evidence_url") or ""),
        "contact_page_url":page,"team_page_url":team,
        "published_business_channel":contact,
        "buyer_role_to_research":str(analysis.get("buyer_role") or ""),
        "fit_hypothesis":str(analysis.get("fit_label") or "NOT_ANALYZED"),
        "fit_reason":str(analysis.get("reason") or ""),
        "model_route":str(row.get("model_route") or "") if analysis else "",
        "model_artifact_sha256":row.get("artifact_sha256") if analysis else None,
        "draft":draft,
        "deal_id":str(row["promoted_deal_id"]) if promoted else None,
        "external_dispatch_state":workpacket_state or None,
        "outreach_provider_status":str(row.get("send_status") or ""),
        "outreach_smtp_accepted":str(row.get("send_status") or "")=="PROVIDER_ACCEPTED",
        "outreach_verified_reply":bool(row.get("has_verified_reply")),
        "outreach_message_id":str(row.get("provider_message_id") or "")[:250],
        "dispatch_attempts":int(row.get("dispatch_attempts") or 0),
        "delivery_error_code":str(row.get("delivery_error_code") or "")[:90],
        "provider_receipt_url":str(row.get("provider_receipt_url") or ""),
        "verifier_receipt_url":str(row.get("verifier_receipt_url") or ""),
        "source_verified_as_buyer":False,
        "permission_to_send_inferred":False,
        "email_sent_by_mission":False,
        "paid_checkout_inferred":False,
        "customer_acceptance_inferred":False}


async def prepare_missions(db:asyncpg.Connection)->None:
    await prepare_ai(db)
    await prepare_workpackets(db)
    await prepare_outreach(db)
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_founder_missions (
      source_key text PRIMARY KEY REFERENCES noetfield.corp_research_sources(source_key),
      state text NOT NULL,
      fingerprint text NOT NULL,
      mission_json text NOT NULL,
      updated_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_founder_mission_events (
      id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      source_key text NOT NULL REFERENCES noetfield.corp_research_sources(source_key),
      previous_state text NOT NULL DEFAULT '',
      new_state text NOT NULL,
      fingerprint text NOT NULL,
      happened_at timestamptz NOT NULL DEFAULT now(),
      UNIQUE(source_key,fingerprint)
    )""")
    await db.execute("""CREATE INDEX IF NOT EXISTS founder_mission_state_priority
      ON noetfield.corp_founder_missions(state,updated_at DESC)""")


async def materialize_missions(settings:object,*,limit:int=100)->dict[str,Any]:
    """Refresh source-bound tasks with idempotent transitions and exact evidence."""
    if type(limit) is not int or not 1<=limit<=_MAX_WRITE:
        raise ValueError("INVALID_FOUNDER_MISSION_LIMIT")
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_missions(db)
        rows=await db.fetch("""SELECT
          r.source_key,r.organization,r.lane,r.score,r.original_url,
          r.review_status,r.promoted_deal_id,r.website,
          s.page_url,s.site_title,s.site_description,s.scan_state,s.scanned_at,
          s.published_general_channel,s.channel_evidence_url,
          s.contact_page_url,s.team_page_url,
          a.analysis_json,a.source_signature AS ai_source_signature,
          a.model_route,a.artifact_sha256,
          d.stage AS deal_stage,w.state AS workpacket_state,
          w.dispatch_attempts,w.last_error_code AS delivery_error_code,
          w.provider_receipt_url,w.verifier_receipt_url,
          msg.status AS send_status,msg.provider_message_id,
          msg.has_verified_reply
          FROM noetfield.corp_research_sources r
          LEFT JOIN noetfield.corp_founder_scout s ON s.source_key=r.source_key
          LEFT JOIN noetfield.corp_founder_ai a ON a.source_key=r.source_key
          LEFT JOIN noetfield.corp_crm_deals d ON d.id=r.promoted_deal_id
          LEFT JOIN noetfield.corp_workpackets w ON w.deal_id=d.id
          LEFT JOIN LATERAL (
            SELECT t.status,t.provider_message_id,
             EXISTS(SELECT 1 FROM noetfield.corp_outreach_replies reply
                    WHERE reply.send_id=t.id) AS has_verified_reply
            FROM noetfield.corp_outreach_sends t WHERE t.deal_id=d.id
            ORDER BY t.created_at DESC LIMIT 1
          ) msg ON TRUE
          ORDER BY r.score DESC,r.imported_at ASC LIMIT $1""",limit)
        updated=0
        for row in rows:
            mission=_plain(dict(row))
            body=json.dumps(mission,ensure_ascii=False,sort_keys=True,separators=(",",":"))
            fingerprint=hashlib.sha256(body.encode("utf-8")).hexdigest()
            async with db.transaction():
                previous=await db.fetchval("""SELECT state FROM noetfield.corp_founder_missions
                   WHERE source_key=$1 FOR UPDATE""",mission["source_key"])
                changed=await db.fetchrow("""INSERT INTO noetfield.corp_founder_missions(
                    source_key,state,fingerprint,mission_json)
                  VALUES($1,$2,$3,$4)
                  ON CONFLICT(source_key) DO UPDATE
                    SET state=excluded.state,fingerprint=excluded.fingerprint,
                        mission_json=excluded.mission_json,updated_at=now()
                  WHERE noetfield.corp_founder_missions.fingerprint <> excluded.fingerprint
                  RETURNING source_key""",mission["source_key"],mission["state"],fingerprint,body)
                if changed:
                    updated+=1
                    await db.execute("""INSERT INTO noetfield.corp_founder_mission_events(
                       source_key,previous_state,new_state,fingerprint)
                       VALUES($1,$2,$3,$4) ON CONFLICT DO NOTHING""",
                       mission["source_key"],previous or "",mission["state"],fingerprint)
        return {"schema":"noetfield.founder-mission-cycle.v1",
            "state":"COMPLETE","scanned":len(rows),"created_or_changed":updated,
            "emails_sent":0,"contacts_auto_qualified":0,
            "deals_auto_created":0,"payments_inferred":0,
            "read_only_projection_of_existing_canonical_evidence":True}
    finally:
        await db.close()


async def founder_mission_board(settings:object,*,limit:int=12)->dict[str,Any]:
    """Only Founder-approved private CRM session can read this board."""
    if type(limit) is not int or not 1<=limit<=40:
        raise ValueError("INVALID_FOUNDER_MISSION_LIMIT")
    db=await asyncpg.connect(_database_url(settings))
    try:
        await prepare_missions(db)
        rows=await db.fetch("""SELECT mission_json FROM noetfield.corp_founder_missions
          WHERE state NOT IN ('SUPPRESSED','OUT_OF_SCOPE')
          ORDER BY
          CASE state WHEN 'VERIFIED_CUSTOMER_REPLY' THEN 1
           WHEN 'OUTREACH_PROVIDER_UNCONFIRMED' THEN 1
           WHEN 'INTRO_REVIEW_READY' THEN 2
           WHEN 'SMTP_PROVIDER_ACCEPTED' THEN 3
           WHEN 'QUALIFIED_CRM_RECORD' THEN 2
           WHEN 'DELIVERY_DISPATCH_ATTENTION' THEN 1
           WHEN 'DELIVERY_IN_PROGRESS' THEN 3
           WHEN 'AGENT_RESEARCH_PENDING' THEN 4
           WHEN 'PEOPLE_RESEARCH_PENDING' THEN 5
           WHEN 'SOURCE_RESEARCH_PENDING' THEN 6 ELSE 7 END,
          (mission_json::jsonb->>'priority')::integer DESC
          LIMIT $1""",limit)
        stats=await db.fetch("""SELECT state,count(*)::int AS n
          FROM noetfield.corp_founder_missions GROUP BY state ORDER BY state""")
        return {"schema":"noetfield.founder-mission-board.v1",
            "objective":"REAL_CUSTOMERS_VERIFIED_REVENUE_AND_RETAINED_RELATIONSHIPS",
            "missions":[json.loads(row["mission_json"]) for row in rows],
            "states":{str(x["state"]):int(x["n"]) for x in stats},
            "plan_is_an_executable_work_queue_not_sales_claim":True,
            "external_actions_inferred":0}
    finally:
        await db.close()
