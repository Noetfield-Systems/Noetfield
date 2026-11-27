"""Source-permission-backed business email with real SMTP and IMAP receipts.

No automatic cold blasts or fabricated sends. Idempotency protects a real
provider send from retries, ambiguous delivery or duplicate operator clicks.
Only original Fieldwork research promoted with documented contact basis may
be contacted. Provider SMTP acknowledgment means accepted for delivery, not
inbox delivery, reply, meeting or qualified opportunity.
"""
from __future__ import annotations

import asyncio
import hashlib
import imaplib
import os
import re
import smtplib
import uuid
from datetime import datetime, timedelta, UTC
from email.message import EmailMessage
from email.parser import BytesParser
from email.policy import default as email_policy
from email.utils import make_msgid, parseaddr
from typing import Any

import asyncpg

from noetfield_governance.corporate_crm import CorporateCRMError
from noetfield_governance.communication_policy import CommunicationRejected, corporate_sender
from noetfield_governance.commercial_pipeline import _database_url


_ALLOWED_BASIS = {
    "OPTED_IN","EXISTING_RELATIONSHIP","INTRODUCED_BY_MUTUAL_CONTACT",
    "PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL",
}
_MAX_BODY=5000


def _mailbox() -> tuple[str,str]:
    sender=os.environ.get("GMAIL_MAILBOX","").strip().lower()
    secret=(os.environ.get("GMAIL_APP_PASSWORD")
            or os.environ.get("NF_OPERATIONS_GOOGLE_WORKSPACE_APP_PASSWORD") or "").strip()
    if not re.fullmatch(r"[^\s@]+@noetfield\.com",sender) or len(secret)<12:
        raise CorporateCRMError("CORPORATE_SMTP_PROVIDER_NOT_CONFIGURED")
    try:
        corporate_sender(sender)
    except CommunicationRejected as exc:
        raise CorporateCRMError(str(exc)) from exc
    return sender,secret


def _digest(value:str)->str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sender_footer(mailbox:str)->str:
    """A business CEM needs a real sender mailing address and easy opt-out."""
    address=os.environ.get("CORPORATE_OUTREACH_MAILING_ADDRESS","").strip()
    if not 15<=len(address)<=300:
        raise CorporateCRMError("REAL_BUSINESS_POSTAL_ADDRESS_REQUIRED_FOR_OUTREACH")
    return (
      "\n\n—\nNoetfield Systems Inc.\n"+address+
      "\nhttps://www.noetfield.com/contact/ | "+mailbox+
      "\nStop commercial email: send a message to "+mailbox+
      " with subject 'Unsubscribe'. Requests are respected without a fee.\n"
    )


def unsubscribe_subject(subject:str)->bool:
    """Distinct opt-out signal: not a positive sales reply."""
    return bool(re.match(
       r"^(?:re:\s*)?(?:unsubscribe|remove\s+me|stop\s+(?:emails?|messages))\b",
       str(subject or "").strip(),re.IGNORECASE))


async def _schema(db:asyncpg.Connection)->None:
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_outreach_sends (
      id uuid PRIMARY KEY,
      deal_id uuid NOT NULL REFERENCES noetfield.corp_crm_deals(id),
      recipient_hash text NOT NULL,
      fingerprint text NOT NULL UNIQUE,
      provider_message_id text NOT NULL,
      status text NOT NULL DEFAULT 'CLAIMED',
      send_provider text NOT NULL DEFAULT 'GOOGLE_WORKSPACE_SMTP',
      actor text NOT NULL,
      provider_ack_at timestamptz,
      created_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_outreach_replies (
       id uuid PRIMARY KEY,
       send_id uuid NOT NULL REFERENCES noetfield.corp_outreach_sends(id),
       imap_uid text NOT NULL UNIQUE,
       response_message_id text NOT NULL DEFAULT '',
       received_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_outreach_suppression (
       recipient_hash text PRIMARY KEY,
       source text NOT NULL,
       actor text NOT NULL DEFAULT '',
       suppressed_at timestamptz NOT NULL DEFAULT now()
    )""")


def _send_provider(mailbox:str,password:str,recipient:str,subject:str,body:str,
                   message_id:str)->bool:
    # Also enforce at the actual transport boundary, not only in the caller.
    try:
        corporate_sender(mailbox)
    except CommunicationRejected as exc:
        raise CorporateCRMError(str(exc)) from exc
    mail=EmailMessage()
    mail["From"]=mailbox
    mail["To"]=recipient
    mail["Subject"]=subject
    mail["Message-ID"]=message_id
    mail["Reply-To"]=mailbox
    mail["Auto-Submitted"]="no"
    mail["List-Unsubscribe"]=f"<mailto:{mailbox}?subject=Unsubscribe>"
    mail.set_content(body+_sender_footer(mailbox))
    with smtplib.SMTP_SSL("smtp.gmail.com",465,timeout=13) as smtp:
        smtp.login(mailbox,password)
        refused=smtp.send_message(mail)
        if refused:
            raise smtplib.SMTPRecipientsRefused(refused)
    return True


async def send_sourced_outreach(settings:object, *, deal_id:str, subject:str,
                                body:str, actor:str)->dict[str,Any]:
    try:
        key=uuid.UUID(deal_id)
    except (ValueError,TypeError) as exc:
        raise CorporateCRMError("INVALID_DEAL_ID") from exc
    subject=subject.strip();body=body.strip()
    if not 4<=len(subject)<=160 or not 20<=len(body)<=_MAX_BODY or not actor.strip():
        raise CorporateCRMError("INVALID_OUTREACH_CONTENT_OR_ACTOR")
    sender,password=_mailbox()
    # A missing legal sender mailing address is a deterministic configuration
    # error: reject BEFORE claiming the idempotency fingerprint. Otherwise
    # every later retry of the same legitimate message would remain stuck
    # in FAILED_UNCONFIRMED even after the configuration is corrected.
    _sender_footer(sender)
    db=await asyncpg.connect(_database_url(settings))
    try:
        await _schema(db)
        entry=await db.fetchrow("""SELECT p.email, r.contact_basis,r.contact_evidence,
                     r.review_status,r.outreach_role_relevance,
                     r.publication_no_solicitation_confirmed,d.stage, d.account_id
           FROM noetfield.corp_crm_deals d
           JOIN noetfield.corp_research_sources r ON r.promoted_deal_id=d.id
           JOIN noetfield.corp_crm_people p ON p.id=d.person_id
           WHERE d.id=$1""",key)
        if not entry or entry["contact_basis"] not in _ALLOWED_BASIS or not entry["contact_evidence"]:
            raise CorporateCRMError("VERIFIED_CONTACT_PERMISSION_REQUIRED")
        if entry["review_status"] in {"DO_NOT_CONTACT","DISQUALIFIED"} or entry["stage"]=="LOST":
            raise CorporateCRMError("OUTREACH_SUPPRESSED")
        if entry["contact_basis"]=="PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL" and (
            entry["publication_no_solicitation_confirmed"] is not True or
            len(str(entry["outreach_role_relevance"] or "").strip()) < 20
        ):
            raise CorporateCRMError("PUBLIC_BUSINESS_CHANNEL_MUST_HAVE_DOCUMENTED_ROLE_RELEVANCE")
        recipient=str(entry["email"] or "").strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",recipient):
            raise CorporateCRMError("VERIFIED_CONTACT_EMAIL_REQUIRED")
        if (await db.fetchval(
              "SELECT 1 FROM noetfield.corp_outreach_suppression WHERE recipient_hash=$1",
              _digest(recipient))) == 1:
            raise CorporateCRMError("OUTREACH_RECIPIENT_SUPPRESSED")
        fingerprint=_digest("|".join([str(key),recipient,subject,body]))
        msgid=make_msgid(domain="noetfield.com")
        receipt_id=uuid.uuid4()
        reserved=await db.fetchrow("""INSERT INTO noetfield.corp_outreach_sends(
            id,deal_id,recipient_hash,fingerprint,provider_message_id,actor)
            VALUES($1,$2,$3,$4,$5,$6)
            ON CONFLICT(fingerprint) DO NOTHING RETURNING id""",
            receipt_id,key,_digest(recipient),fingerprint,msgid,actor[:120])
        if not reserved:
            existing=await db.fetchrow("""SELECT id,status,provider_message_id
                FROM noetfield.corp_outreach_sends WHERE fingerprint=$1""",fingerprint)
            return {"state":existing["status"],"idempotent":True,
                    "send_id":str(existing["id"]),"message_id":existing["provider_message_id"],
                    "new_provider_send":False}
    finally:
        await db.close()
    try:
        accepted=await asyncio.to_thread(_send_provider,
                  sender,password,recipient,subject,body,msgid)
        status="PROVIDER_ACCEPTED" if accepted else "FAILED_UNCONFIRMED"
    except Exception:
        status="FAILED_UNCONFIRMED"
    db=await asyncpg.connect(_database_url(settings))
    try:
        await db.execute("""UPDATE noetfield.corp_outreach_sends
                  SET status=$2,provider_ack_at=CASE WHEN $2='PROVIDER_ACCEPTED' THEN now() ELSE NULL END
                  WHERE id=$1""",receipt_id,status)
    finally:
        await db.close()
    return {"state":status,"send_id":str(receipt_id),"idempotent":False,
            "provider":"GOOGLE_WORKSPACE_SMTP","message_id":msgid,
            "new_provider_send":status=="PROVIDER_ACCEPTED",
            "delivered_to_inbox":False,"reply_verified":False}


async def send_prequalified_corporate_introductions(settings:object,*,limit:int=2)->dict[str,Any]:
    """Small-volume actual sends ONLY after existing source/contact qualification.

    Reuses canonical source records, SMTP sender, Message-ID ledger, global
    opt-out and the existing send_sourced_outreach exact permission checks.
    Fieldwork research / a model suggestion is NEVER permission to email.
    No follow-up blast: ANY prior attempt for the deal permanently excludes
    it from this initial introduction, including ambiguous sends.
    """
    if type(limit) is not int or not 1<=limit<=3:
        raise CorporateCRMError("INVALID_AUTONOMOUS_OUTREACH_LIMIT")
    daily_cap=6
    try:
        mailbox,_password=_mailbox()
        _sender_footer(mailbox)
    except CorporateCRMError:
        return {"schema":"noetfield.prequalified-outreach.v1",
            "state":"SENDER_NOT_CONFIGURED","eligible":0,"attempted":0,
            "provider_accepted":0,"unverified_delivery_claims":0,
            "verified_replies_inferred":0}
    db=await asyncpg.connect(_database_url(settings))
    try:
        await _schema(db)
        # Original qualification is a human-reviewed persistent fact,
        # not a model claim. Explicit reviewed basis and suppression checks.
        daily=await db.fetchval("""SELECT count(*)::int
          FROM noetfield.corp_outreach_sends
          WHERE created_at >= date_trunc('day',
            now() at time zone 'America/Vancouver') AT TIME ZONE 'America/Vancouver'""")
        available=max(0,daily_cap-int(daily or 0))
        if available==0:
            return {"schema":"noetfield.prequalified-outreach.v1",
                "state":"DAILY_SEND_CAP","eligible":0,"attempted":0,
                "provider_accepted":0,"daily_cap":daily_cap,
                "unverified_delivery_claims":0,"verified_replies_inferred":0}
        rows=await db.fetch("""SELECT d.id AS deal_id,a.name AS account_name,
                 d.offer,d.stage,d.owner,d.next_action
           FROM noetfield.corp_research_sources r
           JOIN noetfield.corp_crm_deals d ON d.id=r.promoted_deal_id
           JOIN noetfield.corp_crm_people p ON p.id=d.person_id
           JOIN noetfield.corp_crm_accounts a ON a.id=d.account_id
           WHERE d.stage IN ('NEW','QUALIFYING','DISCOVERY','SCOPE_SENT','NEGOTIATING')
             AND d.source_channel='FIELDWORK_OPERATOR_QUALIFIED'
             AND d.offer IN ('rwa_technical_sprint','ai_sales_os_pilot',
                             'strategic_partnership')
             AND r.review_status NOT IN ('DO_NOT_CONTACT','DISQUALIFIED')
             AND nullif(r.contact_evidence,'') IS NOT NULL
             AND nullif(p.email,'') IS NOT NULL
             AND r.contact_basis IN ('OPTED_IN','EXISTING_RELATIONSHIP',
               'INTRODUCED_BY_MUTUAL_CONTACT','PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL')
             AND (r.contact_basis <> 'PUBLIC_BUSINESS_PARTNERSHIP_CHANNEL'
               OR (r.publication_no_solicitation_confirmed IS TRUE
                 AND length(trim(r.outreach_role_relevance)) >= 20))
             AND NOT EXISTS (
                 SELECT 1 FROM noetfield.corp_outreach_sends past
                 WHERE past.deal_id=d.id)
           ORDER BY d.created_at ASC,d.id ASC
           LIMIT $1""",min(limit,available))
    finally:
        await db.close()
    # Canonical sender rechecks current global opt-out right before email;
    # sender owns the fingerprint, SMTP event and ambiguous retry policy.
    from noetfield_governance.corporate_revenue_ops import outreach_draft
    accepted=0
    failures=[]
    for record in rows:
        deal_id=str(record["deal_id"])
        draft=outreach_draft(dict(record))
        try:
            result=await send_sourced_outreach(settings,
                deal_id=deal_id,subject=draft["subject"],body=draft["body"],
                actor="Noetfield Revenue Auto / verified CRM source")
            if result.get("new_provider_send"):
                accepted+=1
            else:
                failures.append({"deal_id":deal_id,
                                 "state":str(result.get("state") or "UNCONFIRMED")})
        except CorporateCRMError as exc:
            failures.append({"deal_id":deal_id,"state":str(exc)[:95]})
        except Exception:
            failures.append({"deal_id":deal_id,"state":"SMTP_OR_DB_UNCONFIRMED"})
    return {"schema":"noetfield.prequalified-outreach.v1",
        "state":"COMPLETE" if not failures else "PARTIAL_OR_BLOCKED",
        "eligible":len(rows),"attempted":len(rows),
        "provider_accepted":accepted,"failures":failures,
        "daily_cap":daily_cap,"unverified_delivery_claims":0,
        "verified_replies_inferred":0,"customer_meetings_inferred":0,
        "paid_customers_inferred":0,"research_only_recipients_contacted":0}


def _imap_headers(mailbox:str,password:str,limit:int)->list[tuple[str,Any]]:
    """Headers-only IMAP; no email body or attachments leave the mailbox."""
    since=(datetime.now(UTC)-timedelta(days=30)).strftime("%d-%b-%Y")
    items=[]
    with imaplib.IMAP4_SSL("imap.gmail.com",993) as imap:
        imap.login(mailbox,password)
        typ,_=imap.select("INBOX",readonly=True)
        if typ!="OK":
            return []
        typ,ids=imap.uid("SEARCH",None,"SINCE",since)
        if typ!="OK" or not ids or not ids[0]:
            return []
        for uid in ids[0].split()[-min(limit,120):]:
            status,parts=imap.uid("FETCH",uid,
                     "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID IN-REPLY-TO REFERENCES FROM AUTO-SUBMITTED SUBJECT)])")
            if status!="OK" or not parts:
                continue
            for part in parts:
                if isinstance(part,tuple) and isinstance(part[1],bytes):
                    head=BytesParser(policy=email_policy).parsebytes(part[1],headersonly=True)
                    items.append((uid.decode("ascii","ignore"),head))
                    break
        imap.close()
    return items


async def reconcile_real_replies(settings:object, *, limit:int=120)->dict[str,Any]:
    if type(limit) is not int or not 1<=limit<=120:
        raise CorporateCRMError("INVALID_RECONCILIATION_LIMIT")
    mailbox,password=_mailbox()
    db=await asyncpg.connect(_database_url(settings))
    try:
        await _schema(db)
        sends=await db.fetch("""SELECT s.id,s.provider_message_id,s.recipient_hash
             FROM noetfield.corp_outreach_sends s
             WHERE s.status='PROVIDER_ACCEPTED' AND
                   s.created_at > now() - interval '30 days'
             ORDER BY s.created_at DESC LIMIT 200""")
        known={str(row["provider_message_id"]).strip().lower():dict(row) for row in sends}
        all_sent=await db.fetch("""SELECT DISTINCT recipient_hash
             FROM noetfield.corp_outreach_sends LIMIT 10000""")
        known_recipients={str(x["recipient_hash"]) for x in all_sent}
        if not known_recipients:
            return {"provider_ack_sent":0,"scanned_headers":0,
                    "new_verified_replies":0,"new_suppressed_recipients":0}
        headers=await asyncio.to_thread(_imap_headers,mailbox,password,limit)
        added=0
        suppressed=0
        for uid,head in headers:
            auto=str(head.get("Auto-Submitted") or "").strip().lower()
            if auto and auto!="no":
                continue
            references=(str(head.get("In-Reply-To") or "")+" "+str(head.get("References") or "")).lower()
            sender=parseaddr(str(head.get("From") or ""))[1].strip().lower()
            if not sender:
                continue
            sender_hash=_digest(sender)
            if unsubscribe_subject(str(head.get("Subject") or "")):
                if sender_hash in known_recipients:
                    created=await db.fetchrow("""INSERT INTO noetfield.corp_outreach_suppression
                        (recipient_hash,source,actor)
                        VALUES($1,'IMAP_UNSUBSCRIBE_SUBJECT','CUSTOMER')
                        ON CONFLICT(recipient_hash) DO NOTHING RETURNING recipient_hash""",
                        sender_hash)
                    suppressed+=int(bool(created))
                continue
            for msg_id,original in known.items():
                if msg_id not in references or original["recipient_hash"]!=sender_hash:
                    continue
                response_id=str(head.get("Message-ID") or "")[:250]
                row=await db.fetchrow("""INSERT INTO noetfield.corp_outreach_replies
                      (id,send_id,imap_uid,response_message_id)
                      VALUES($1,$2,$3,$4)
                      ON CONFLICT(imap_uid) DO NOTHING RETURNING id""",
                      uuid.uuid4(),original["id"],uid,response_id)
                added+=int(bool(row))
                break
        return {"provider_ack_sent":len(known),"scanned_headers":len(headers),
                "new_verified_replies":added,
                "new_suppressed_recipients":suppressed,
                "human_qualification_not_inferred":True}
    finally:
        await db.close()


async def provider_outreach_metrics(settings:object)->dict[str,Any]:
    db=await asyncpg.connect(_database_url(settings))
    try:
        await _schema(db)
        rows=await db.fetch("SELECT status,count(*)::int n FROM noetfield.corp_outreach_sends GROUP BY status")
        replies=await db.fetchval("SELECT count(*)::int FROM noetfield.corp_outreach_replies")
        suppressed=await db.fetchval("SELECT count(*)::int FROM noetfield.corp_outreach_suppression")
        return {"source":"SMTP_PROVIDER_ACK_AND_IMAP_HEADERS",
                "sending_status":{r["status"]:int(r["n"]) for r in rows},
                "provider_verified_replies":int(replies or 0),
                "suppressed_recipients":int(suppressed or 0),
                "meetings_confirmed":0,"unverified_email_events_included":False}
    finally:
        await db.close()


async def suppress_sourced_recipient(settings:object,*,deal_id:str,actor:str)->dict[str,Any]:
    """Immediate global opt-out across all related CRM deals; no personal email returned."""
    try:
        identifier=uuid.UUID(deal_id)
    except (TypeError,ValueError) as exc:
        raise CorporateCRMError("INVALID_DEAL_ID") from exc
    if not actor.strip() or len(actor)>120:
        raise CorporateCRMError("ACTOR_REQUIRED")
    db=await asyncpg.connect(_database_url(settings))
    try:
        await _schema(db)
        person=await db.fetchrow("""SELECT p.email FROM noetfield.corp_crm_deals d
          JOIN noetfield.corp_crm_people p ON p.id=d.person_id
          WHERE d.id=$1""",identifier)
        if not person or not person["email"]:
            raise CorporateCRMError("SOURCE_CONTACT_EMAIL_NOT_FOUND")
        digest=_digest(str(person["email"]).strip().lower())
        row=await db.fetchrow("""INSERT INTO noetfield.corp_outreach_suppression(
             recipient_hash,source,actor)
             VALUES($1,'OPERATOR_CONFIRMED_OPT_OUT',$2)
             ON CONFLICT(recipient_hash) DO NOTHING RETURNING recipient_hash""",
             digest,actor)
        return {"suppressed":True,"created":bool(row),"deal_id":deal_id,
                "scope":"ALL_FUTURE_CORPORATE_COMMERCIAL_EMAIL",
                "customer_email_exposed":False}
    finally:
        await db.close()
