"""Evidence-separated Corporate growth funnel on the existing Noetfield ledgers.

No new CRM, contact scraper, payment recorder or mail sender. This is a
read-only projection. Research is not a contact, SMTP ACK is not delivery,
an operator-evidenced meeting is not an independent provider attestation,
and a paid checkout is not bank settlement.
"""
from __future__ import annotations

from typing import Any
import asyncpg

from noetfield_governance.commercial_pipeline import OFFER_TERMS, _database_url
from noetfield_governance.corporate_discovery import _schema as prepare_research
from noetfield_governance.corporate_outbound import _schema as prepare_outreach
from noetfield_governance.corporate_workpacket import prepare_workpackets


STAGE_EVIDENCE = {
    "research": "Fieldwork original public organization source; no person inferred",
    "qualified_contacts": "Human-reviewed contact evidence and documented contact basis",
    "smtp_accepted": "Google Workspace SMTP provider acknowledgment; not inbox delivery",
    "verified_replies": "IMAP headers linked to both sent Message-ID and recipient",
    "meetings_booked_documented": "Operator activity with an HTTPS evidence reference; not provider attested",
    "meetings_held_documented": "Operator activity with an HTTPS evidence reference; not provider attested",
    "accepted_scopes": "Canonical source-linked accepted written SOW",
    "paid_live_checkouts": "Live signed source-bound Stripe Checkout, nonreversed and offer-matched",
    "runtime_acknowledged": "Provider job admission, not completed execution",
    "independently_verified_deliveries": "Signed verifier result with artifact reference; draft RUNNING is excluded",
    "customer_acceptances": "Authenticated customer acceptance tied to verified WorkPacket",
    "closed_paid_engagements": "Canonical CLOSED after delivery and customer acceptance",
    "retained_relationships_reported": "CRM retained status only; new renewal payment is not implied",
}


async def growth_funnel_snapshot(settings: object, *, limit: int = 12) -> dict[str, Any]:
    """Query genuine pipeline evidence, preserving each stage's own meaning."""
    count = max(1, min(int(limit), 25))
    db = await asyncpg.connect(_database_url(settings))
    try:
        await prepare_research(db)
        await prepare_outreach(db)
        await prepare_workpackets(db)
        metrics = await db.fetchrow("""
          SELECT
          (SELECT count(*)::int FROM noetfield.corp_research_sources) AS research,
          (SELECT count(*)::int FROM noetfield.corp_research_sources
            WHERE promoted_deal_id IS NULL) AS research_pending_review,
          (SELECT count(*)::int FROM noetfield.corp_research_sources r
            JOIN noetfield.corp_crm_deals d ON d.id=r.promoted_deal_id
            JOIN noetfield.corp_crm_people p ON p.id=d.person_id
            WHERE r.contact_basis <> '' AND r.contact_evidence <> ''
              AND p.email <> '' AND r.review_status NOT IN ('DO_NOT_CONTACT','DISQUALIFIED'))
            AS qualified_contacts,
          (SELECT count(DISTINCT s.deal_id)::int
            FROM noetfield.corp_outreach_sends s
            WHERE s.status='PROVIDER_ACCEPTED') AS smtp_accepted,
          (SELECT count(DISTINCT s.deal_id)::int
            FROM noetfield.corp_outreach_replies r
            JOIN noetfield.corp_outreach_sends s ON s.id=r.send_id
            WHERE s.status='PROVIDER_ACCEPTED') AS verified_replies,
          (SELECT count(DISTINCT deal_id)::int
            FROM noetfield.corp_crm_activities
            WHERE kind='MEETING_BOOKED_REPORTED' AND evidence_url <> '')
            AS meetings_booked_documented,
          (SELECT count(DISTINCT deal_id)::int
            FROM noetfield.corp_crm_activities
            WHERE kind='MEETING_HELD' AND evidence_url <> '')
            AS meetings_held_documented,
          (SELECT count(DISTINCT d.id)::int
            FROM noetfield.corp_crm_deals d
            JOIN noetfield.public_intakes i ON i.intake_id=d.source_intake_id
            WHERE i.qualification_json->'commercial_ops'->>'offer'=d.offer
              AND nullif(i.qualification_json->'commercial_ops'->>'scope_ref','') IS NOT NULL
              AND nullif(i.qualification_json->'commercial_ops'->>'acceptance_evidence','') IS NOT NULL
              AND i.qualification_json->'commercial_ops'->>'stage'
                  IN ('SCOPE_ACCEPTED','PAYMENT_CONFIRMED','IN_DELIVERY','DELIVERED','CLOSED'))
            AS accepted_scopes,
          (SELECT count(DISTINCT w.deal_id)::int
            FROM noetfield.corp_workpackets w
            WHERE w.state IN ('ACKNOWLEDGED','RUNNING','VERIFIED')
              AND nullif(w.external_workpacket_id,'') IS NOT NULL)
            AS runtime_acknowledged,
          (SELECT count(DISTINCT w.deal_id)::int
            FROM noetfield.corp_workpackets w
            WHERE w.state='VERIFIED'
              AND nullif(w.artifact_url,'') IS NOT NULL
              AND nullif(w.verifier_receipt_url,'') IS NOT NULL)
            AS independently_verified_deliveries,
          (SELECT count(DISTINCT a.deal_id)::int
            FROM noetfield.corp_workpacket_acceptances a
            JOIN noetfield.corp_workpackets w ON w.id=a.workpacket_id
            WHERE w.state='VERIFIED'
              AND a.artifact_url=w.artifact_url)
            AS customer_acceptances,
          (SELECT count(DISTINCT d.id)::int
            FROM noetfield.corp_crm_deals d
            JOIN noetfield.public_intakes i ON i.intake_id=d.source_intake_id
            JOIN noetfield.corp_workpackets w ON w.deal_id=d.id
            JOIN noetfield.corp_workpacket_acceptances a
              ON a.deal_id=d.id AND a.workpacket_id=w.id
            WHERE i.qualification_json->'commercial_ops'->>'stage'='CLOSED'
              AND w.state='VERIFIED'
              AND w.artifact_url=a.artifact_url
              AND nullif(w.verifier_receipt_url,'') IS NOT NULL)
            AS closed_paid_engagements,
          (SELECT count(*)::int FROM noetfield.corp_crm_deals
            WHERE stage='RETAINED') AS retained_relationships_reported
        """)
        by_lane = await db.fetch("""
          SELECT lane, count(*)::int AS research,
            count(*) FILTER (WHERE promoted_deal_id IS NOT NULL)::int AS promoted
          FROM noetfield.corp_research_sources GROUP BY lane ORDER BY lane
        """)
        queue = await db.fetch("""
          SELECT source_key,organization,lane,score,review_status,
                 original_url,evidence_url
          FROM noetfield.corp_research_sources
          WHERE promoted_deal_id IS NULL
            AND review_status NOT IN ('DO_NOT_CONTACT','DISQUALIFIED')
          ORDER BY score DESC, imported_at ASC
          LIMIT $1
        """, count)
        # Match the approved offer, exact payment link, amount, currency,
        # accepted scope and source-bound nonreversed live Stripe event.
        # A CRM stage or payment-link click alone is not revenue.
        rwa = OFFER_TERMS["rwa_technical_sprint"]
        company = OFFER_TERMS["ai_sales_os_pilot"]
        paid = await db.fetch("""
          SELECT e.currency,
            count(DISTINCT d.id)::int AS engagements,
            coalesce(sum(e.amount_minor),0)::bigint AS checkout_amount_minor
          FROM noetfield.corp_crm_deals d
          JOIN noetfield.public_intakes i ON i.intake_id=d.source_intake_id
          JOIN noetfield.commercial_payment_evidence e
            ON e.source_intake_id=d.source_intake_id
          WHERE e.livemode=true AND e.reversed=false AND e.bound_at IS NOT NULL
            AND i.qualification_json->'commercial_ops'->>'offer'=d.offer
            AND i.qualification_json->'commercial_ops'->>'payment_session_id'=e.session_id
            AND i.qualification_json->'commercial_ops'->>'payment_event_id'=e.event_id
            AND nullif(i.qualification_json->'commercial_ops'->>'acceptance_evidence','') IS NOT NULL
            AND i.qualification_json->'commercial_ops'->>'stage'
                 IN ('PAYMENT_CONFIRMED','IN_DELIVERY','DELIVERED','CLOSED')
            AND ((d.offer='rwa_technical_sprint'
                  AND e.payment_link_id=$1 AND e.currency=$2 AND e.amount_minor=$3)
              OR (d.offer='ai_sales_os_pilot'
                  AND e.payment_link_id=$4 AND e.currency=$5 AND e.amount_minor=$6))
          GROUP BY e.currency
        """, rwa["payment_link_id"], rwa["currency"], rwa["payment_minor"],
             company["payment_link_id"], company["currency"], company["payment_minor"])
        result = {key: int(metrics[key] or 0) for key in STAGE_EVIDENCE
                  if key not in {"paid_live_checkouts"}}
        result["research_pending_review"] = int(metrics["research_pending_review"] or 0)
        result["paid_live_checkouts"] = sum(int(row["engagements"]) for row in paid)
        amount_by_currency = {str(row["currency"]).upper(): int(row["checkout_amount_minor"])
                              for row in paid}
        return {
            "schema": "noetfield.corporate-growth-funnel.v1",
            "scope": "EXISTING_CANONICAL_LEDGER_READ_ONLY",
            "stages": result,
            "evidence_definitions": STAGE_EVIDENCE,
            "research_by_lane": {str(row["lane"]): {
                "research": int(row["research"]), "promoted": int(row["promoted"])
            } for row in by_lane},
            "paid_checkout_amount_minor_by_currency": amount_by_currency,
            "priority_source_review": [
                {"source_key": row["source_key"], "organization": row["organization"],
                 "lane": row["lane"], "score": int(row["score"] or 0),
                 "review_status": row["review_status"], "original_url": row["original_url"],
                 "evidence_url": row["evidence_url"],
                 "next_action": "Open original evidence; identify and validate a relevant business contact and permission basis, then qualify in the existing CRM"}
                for row in queue
            ],
            "identity_imports": "ORGANIZATION_RESEARCH_ONLY",
            "cash_settled_in_bank": "NOT_MEASURED",
            "unverified_meetings_counted_as_provider_confirmed": False,
            "automatic_email_sent": False,
            "renewal_payment_verified_by_retained_stage": False,
        }
    finally:
        await db.close()
