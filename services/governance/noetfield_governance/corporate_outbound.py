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
from noetfield_governance.commercial_pipeline import _database_url


_ALLOWED_BASIS = {"OPTED_IN","EXISTING_RELATIONSHIP","INTRODUCED_BY_MUTUAL_CONTACT"}
_MAX_BODY=5000


def _mailbox() -> tuple[str,str]:
    sender=os.environ.get("GMAIL_MAILBOX","").strip().lower()
    secret=(os.environ.get("GMAIL_APP_PASSWORD")
            or os.environ.get("NF_OPERATIONS_GOOGLE_WORKSPACE_APP_PASSWORD") or "").strip()
    if not re.fullmatch(r"[^\s@]+@noetfield\.com",sender) or len(secret)<12:
        raise CorporateCRMError("CORPORATE_SMTP_PROVIDER_NOT_CONFIGURED")
    return sender,secret


def _digest(value:str)->str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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


def _send_provider(mailbox:str,password:str,recipient:str,subject:str,body:str,
                   message_id:str)->bool:
    mail=EmailMessage()
    mail["From"]=mailbox
    mail["To"]=recipient
    mail["Subject"]=subject
    mail["Message-ID"]=message_id
    mail["Reply-To"]=mailbox
    mail["Auto-Submitted"]="no"
    mail.set_content(body)
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
    db=await asyncpg.connect(_database_url(settings))
    try:
        await _schema(db)
        entry=await db.fetchrow("""SELECT p.email, r.contact_basis,r.contact_evidence,
                     r.review_status, d.stage, d.account_id
           FROM noetfield.corp_crm_deals d
           JOIN noetfield.corp_research_sources r ON r.promoted_deal_id=d.id
           JOIN noetfield.corp_crm_people p ON p.id=d.person_id
           WHERE d.id=$1""",key)
        if not entry or entry["contact_basis"] not in _ALLOWED_BASIS or not entry["contact_evidence"]:
            raise CorporateCRMError("VERIFIED_CONTACT_PERMISSION_REQUIRED")
        if entry["review_status"] in {"DO_NOT_CONTACT","DISQUALIFIED"} or entry["stage"]=="LOST":
            raise CorporateCRMError("OUTREACH_SUPPRESSED")
        recipient=str(entry["email"] or "").strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",recipient):
            raise CorporateCRMError("VERIFIED_CONTACT_EMAIL_REQUIRED")
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
                     "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID IN-REPLY-TO REFERENCES FROM AUTO-SUBMITTED)])")
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
        if not known:
            return {"provider_ack_sent":0,"scanned_headers":0,"new_verified_replies":0}
        headers=await asyncio.to_thread(_imap_headers,mailbox,password,limit)
        added=0
        for uid,head in headers:
            auto=str(head.get("Auto-Submitted") or "").strip().lower()
            if auto and auto!="no":
                continue
            references=(str(head.get("In-Reply-To") or "")+" "+str(head.get("References") or "")).lower()
            sender=parseaddr(str(head.get("From") or ""))[1].strip().lower()
            if not sender:
                continue
            sender_hash=_digest(sender)
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
                "human_qualification_not_inferred":True}
    finally:
        await db.close()


async def provider_outreach_metrics(settings:object)->dict[str,Any]:
    db=await asyncpg.connect(_database_url(settings))
    try:
        await _schema(db)
        rows=await db.fetch("SELECT status,count(*)::int n FROM noetfield.corp_outreach_sends GROUP BY status")
        replies=await db.fetchval("SELECT count(*)::int FROM noetfield.corp_outreach_replies")
        return {"source":"SMTP_PROVIDER_ACK_AND_IMAP_HEADERS",
                "sending_status":{r["status"]:int(r["n"]) for r in rows},
                "provider_verified_replies":int(replies or 0),
                "meetings_confirmed":0,"unverified_email_events_included":False}
    finally:
        await db.close()
