"""Run source-only Fieldwork corporate discovery on existing Platform scheduler.

Immediate production start followed by six-hourly bounded source refresh.
No sales contact, CRM promotion, email or provider-payment side effects.
"""
from __future__ import annotations
import asyncio
import logging
from typing import Any

from noetfield_governance.corporate_discovery import _fieldwork_config, sync_corporate_research
from noetfield_governance.corporate_crm import CorporateCRMError

logger=logging.getLogger("noetfield.governance.corporate_discovery")
_task:asyncio.Task[None]|None=None
_last:dict[str,Any]={"state":"NOT_RUN","scanned":0,"created":0,"total_staged":0}


def configured() -> bool:
    try:
        _fieldwork_config()
        return True
    except CorporateCRMError:
        return False


def latest() -> dict[str,Any]:
    return {"configured":configured(),"last":dict(_last)}


async def run_once(settings:object)->dict[str,Any]:
    global _last
    if not configured():
        _last={"state":"UNCONFIGURED","scanned":0,"created":0,"total_staged":0}
        return dict(_last)
    scanned=created=accepted=rejected=0
    next_offset=0
    try:
        for _ in range(5):
            row=await sync_corporate_research(settings,limit=100,offset=next_offset)
            scanned+=row["scanned"];created+=row["created"]
            accepted+=row["accepted"];rejected+=row["rejected"]
            if row["next_offset"] is None:
                break
            next_offset=row["next_offset"]
        _last={"state":"COMPLETE","scanned":scanned,"created":created,
               "accepted":accepted,"rejected":rejected,
               "total_staged":row["total_staged"],
               "staged_by_lane":row["staged_by_lane"],
               "no_outreach":True,"no_people_imported":True}
        logger.warning("corporate_fieldwork_sync=COMPLETE scanned=%d new=%d total=%d lanes=%s",
          scanned,created,row["total_staged"],row["staged_by_lane"])
    except Exception:
        _last={"state":"FAILED","scanned":scanned,"created":created,
               "error":"SOURCE_BRIDGE_READ_OR_DB_FAILED"}
        logger.exception("corporate_fieldwork_sync=FAILED")
    return dict(_last)


async def reconcile_proven_outreach(settings:object)->dict[str,Any]:
    """Check Gmail headers only for existing provider-acknowledged CRM messages.

    No emails are sent and no booked meeting is inferred. A provider outage
    must not interrupt Fieldwork source discovery or the existing app server.
    """
    from noetfield_governance.corporate_outbound import reconcile_real_replies
    try:
        result=await reconcile_real_replies(settings,limit=120)
        logger.warning("corporate_mailbox_readback=COMPLETE acknowledged=%d new_replies=%d optouts=%d",
             result.get("provider_ack_sent",0),result.get("new_verified_replies",0),
             result.get("new_suppressed_recipients",0))
        return {"state":"COMPLETE",**result}
    except CorporateCRMError as exc:
        logger.warning("corporate_mailbox_readback=NOT_CONFIGURED_OR_NOT_AVAILABLE code=%s",str(exc))
        return {"state":"NOT_CONFIGURED_OR_NOT_AVAILABLE","new_verified_replies":0}
    except Exception:
        logger.exception("corporate_mailbox_readback=FAILED")
        return {"state":"FAILED","new_verified_replies":0}


async def reconcile_paid_company_os_drafts(settings:object)->dict[str,Any]:
    """Actual paid jobs only. A hash-approved draft never equals customer delivery."""
    from noetfield_governance.corporate_workpacket import reconcile_pending_company_os_drafts
    try:
        result=await reconcile_pending_company_os_drafts(settings,limit=3)
        logger.warning(
            "corporate_company_os_verifier_readback=%s checked=%d draft_proofs=%d",
            result.get("state","UNKNOWN"),result.get("checked",0),
            result.get("verified_drafts",0))
        return result
    except Exception:
        logger.exception("corporate_company_os_verifier_readback=FAILED")
        return {"state":"FAILED","checked":0,"verified_drafts":0}


async def start_scheduler(settings:object)->None:
    global _task
    if not configured():
        logger.warning("corporate_fieldwork_sync=UNCONFIGURED")
        return
    if _task is not None and not _task.done():
        return
    async def loop()->None:
        while True:
            await run_once(settings)
            await reconcile_proven_outreach(settings)
            await reconcile_paid_company_os_drafts(settings)
            # Small, real public-source research batch; no founder data entry,
            # no unsolicited send, no guessed customer or AI model usage.
            try:
                from noetfield_governance.corporate_founder_scout import run_scout_batch
                scout = await run_scout_batch(settings, limit=3)
                logger.warning(
                    "corporate_founder_scout=%s checked=%s public_channels=%s",
                    scout["state"], scout["scanned"], scout["found_public_business_channels"])
            except Exception:
                logger.exception("corporate_founder_scout=FAILED_SOURCE_RESEARCH")
            await asyncio.sleep(6*3600)
    _task=asyncio.create_task(loop())


async def stop_scheduler()->None:
    global _task
    if _task is not None:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task=None
