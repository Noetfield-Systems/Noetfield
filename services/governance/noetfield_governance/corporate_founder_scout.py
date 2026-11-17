"""Founder-first corporate sourcing assistant over canonical Fieldwork research.

Automatically inspects ONLY public HTTPS organization websites already supplied
by Fieldwork. Evidence comes from an actual page fetch; never invent a person,
permission, sent message, buyer, revenue, or model-run receipt. Its contact
channel suggestions are not CRM-qualified contacts.

No new CRM or prospect database: small readback attached to the existing
noetfield.corp_research_sources source key, with independent timestamped proof.
"""
from __future__ import annotations

import asyncio
import ipaddress
import logging
import re
import socket
import uuid
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote

import asyncpg
import httpx

from noetfield_governance.commercial_pipeline import _database_url
from noetfield_governance.corporate_discovery import _schema as prepare_research

logger = logging.getLogger("noetfield.governance.corporate_founder_scout")
_GENERIC_MAILBOXES = frozenset({
    "sales", "business", "partnerships", "partners", "contact", "hello", "info",
    "enquiries", "inquiries", "growth", "bizdev", "bd", "commercial",
})
_MAX_HTML = 160_000
_MAX_BATCH = 5
_RESCAN_DAYS = 7


class _PageSignals(HTMLParser):
    def __init__(self, source_url: str):
        super().__init__(convert_charrefs=True)
        self.source_url = source_url
        self.title = ""
        self.description = ""
        self.in_title = False
        self.links: list[tuple[str, str]] = []
        self._anchor: str | None = None
        self._anchor_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        fields = {key.lower(): (value or "") for key, value in attrs}
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            key = (fields.get("name") or fields.get("property") or "").lower()
            if key in {"description", "og:description"} and not self.description:
                self.description = fields.get("content", "")[:500]
        elif tag == "a":
            self._anchor = fields.get("href", "")
            self._anchor_text = []

    def handle_data(self, data: str) -> None:
        if self.in_title and len(self.title) < 220:
            self.title += data[:220]
        if self._anchor is not None and len(self._anchor_text) < 20:
            self._anchor_text.append(data[:100])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "a" and self._anchor is not None:
            self.links.append((self._anchor[:500], " ".join(self._anchor_text)[:170]))
            self._anchor = None
            self._anchor_text = []


def _source_url(value: str) -> str:
    """Reject credentials, query-based SSRF targets, nonstandard ports and IPs."""
    try:
        u = urlsplit(str(value).strip())
        host = (u.hostname or "").lower().rstrip(".")
        if (u.scheme != "https" or not host or "." not in host
                or u.username or u.password or u.port not in (None, 443)
                or any(c.isspace() for c in host)
                or not re.fullmatch(r"[a-z0-9.-]{4,253}", host)
                or host.startswith(".") or ".." in host
                or len(u.path) > 550):
            return ""
        try:
            ipaddress.ip_address(host)
            return ""
        except ValueError:
            pass
        if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal", ".localhost", ".test")):
            return ""
        return urlunsplit(("https", host, u.path or "/", "", ""))
    except ValueError:
        return ""


def _page_summary(page_url: str, raw_html: str) -> dict[str, Any]:
    """Published organization contact/partnership channels, never guessed people."""
    parsed = _PageSignals(page_url)
    parsed.feed(raw_html[:_MAX_HTML])
    host = urlsplit(page_url).hostname or ""
    root = host.removeprefix("www.")
    contact_url = ""
    team_url = ""
    published_channel = ""
    for href, label in parsed.links[:700]:
        ref = href.strip()
        if ref.lower().startswith("mailto:"):
            mail = unquote(ref[7:].split("?", 1)[0]).strip().lower()
            if re.fullmatch(r"[a-z0-9][a-z0-9._+\-]{0,63}@[a-z0-9.\-]{4,253}", mail):
                local, domain = mail.split("@", 1)
                if (local in _GENERIC_MAILBOXES and
                        (domain == root or host == domain or host.endswith("." + domain))):
                    published_channel = mail
                    continue
        url = _source_url(urljoin(page_url, ref))
        if not url or urlsplit(url).hostname != host:
            continue
        path = urlsplit(url).path.lower().strip("/")
        label_lower = label.lower()
        if (not contact_url and (any(k in path.split("/") for k in
                    ("contact", "partnerships", "partners", "business"))
                    or re.search(r"\b(contact|partnerships|partnership)\b", label_lower))):
            contact_url = url
        if (not team_url and (any(k in path.split("/") for k in
                    ("team", "leadership", "people"))
                    or re.search(r"\b(our team|leadership|meet the team)\b", label_lower))):
            team_url = url
    return {
        "title": re.sub(r"\s+", " ", parsed.title).strip()[:180],
        "description": re.sub(r"\s+", " ", parsed.description).strip()[:400],
        "public_channel": published_channel,
        "contact_url": contact_url,
        "team_url": team_url,
        "scan_state": ("PUBLISHED_GENERAL_BUSINESS_EMAIL" if published_channel
                       else "PUBLIC_CONTACT_PAGE" if contact_url
                       else "PUBLIC_TEAM_PAGE" if team_url else "NO_CHANNEL_OBSERVED"),
    }


async def _public_ip(host: str) -> str:
    """Resolve before connecting and pin chosen public address; avoid DNS rebinding."""
    records = await asyncio.wait_for(
        asyncio.to_thread(socket.getaddrinfo, host, 443, type=socket.SOCK_STREAM),
        timeout=5,
    )
    addresses: list[str] = []
    for record in records:
        try:
            candidate = ipaddress.ip_address(record[4][0])
            if candidate.is_global:
                addresses.append(str(candidate))
        except ValueError:
            continue
    if not addresses:
        raise ValueError("NO_PUBLIC_DNS_ADDRESS")
    # Prefer IPv4 for predictable Cloud/railway egress.
    return next((ip for ip in addresses if ":" not in ip), addresses[0])


async def fetch_official_signals(website: str) -> dict[str, Any]:
    """Fetch one first-party source with bounded bytes, no redirects, pinned TLS SNI.

    A published generic mailbox is a CONTACT CHANNEL, not a verified individual
    or an assertion that the business accepts solicitation.
    """
    source = _source_url(website)
    if not source:
        return {"scan_state": "NO_USABLE_WEBSITE", "page_url": "", "error": "NO_VALID_HTTPS_SOURCE"}
    host = urlsplit(source).hostname
    assert host
    try:
        ip = await _public_ip(host)
        u = urlsplit(source)
        dest = urlunsplit(("https", "[" + ip + "]" if ":" in ip else ip, u.path or "/", "", ""))
        async with httpx.AsyncClient(trust_env=False, follow_redirects=False,
                                    timeout=httpx.Timeout(7, connect=5),
                                    verify=True) as client:
            async with client.stream("GET", dest, headers={
                "Host": host, "Accept": "text/html",
                "User-Agent": "NoetfieldPublicCorporateResearch/1.0 (+https://noetfield.com/)",
            }, extensions={"sni_hostname": host}) as response:
                if response.status_code != 200:
                    return {"scan_state": "SOURCE_UNAVAILABLE", "page_url": source,
                            "error": "HTTP_" + str(response.status_code)}
                if not response.headers.get("content-type", "").lower().startswith(("text/html", "application/xhtml")):
                    return {"scan_state": "SOURCE_UNAVAILABLE", "page_url": source,
                            "error": "NOT_HTML"}
                buf = bytearray()
                async for chunk in response.aiter_bytes():
                    if len(buf) + len(chunk) > _MAX_HTML:
                        break
                    buf.extend(chunk)
        if not buf:
            return {"scan_state": "SOURCE_UNAVAILABLE", "page_url": source, "error": "EMPTY_PAGE"}
        signals = _page_summary(source, buf.decode("utf-8", errors="replace"))
        return {"page_url": source, "error": "", **signals}
    except (ValueError, OSError, httpx.HTTPError, asyncio.TimeoutError) as exc:
        reason = ("DNS_OR_NETWORK_UNAVAILABLE" if not isinstance(exc, ValueError) else str(exc))
        return {"scan_state": "SOURCE_UNAVAILABLE", "page_url": source,
                "error": reason[:90]}


async def prepare_scout(db: asyncpg.Connection) -> None:
    await prepare_research(db)
    await db.execute("""CREATE TABLE IF NOT EXISTS noetfield.corp_founder_scout (
       source_key text PRIMARY KEY REFERENCES noetfield.corp_research_sources(source_key),
       page_url text NOT NULL DEFAULT '',
       site_title text NOT NULL DEFAULT '',
       site_description text NOT NULL DEFAULT '',
       published_general_channel text NOT NULL DEFAULT '',
       contact_page_url text NOT NULL DEFAULT '',
       team_page_url text NOT NULL DEFAULT '',
       scan_state text NOT NULL,
       error_code text NOT NULL DEFAULT '',
       scanned_at timestamptz NOT NULL DEFAULT now()
    )""")
    await db.execute("""CREATE INDEX IF NOT EXISTS corp_founder_scout_scanned_idx
       ON noetfield.corp_founder_scout(scanned_at)""")


def _priority(row: dict[str, Any]) -> dict[str, Any]:
    """Original research fit and observed contact evidence stay different signals."""
    base = max(0, min(int(row.get("score") or 0), 100))
    state = row.get("scan_state") or "NOT_RESEARCHED"
    has_channel = state in ("PUBLISHED_GENERAL_BUSINESS_EMAIL", "PUBLIC_CONTACT_PAGE")
    score = min(100, round(base * .65) + (25 if has_channel else 10 if state == "PUBLIC_TEAM_PAGE" else 0))
    lane = row.get("lane")
    hypothesis = ("RWA technical readiness" if lane == "RWA"
                  else "AI Sales OS discovery")
    next_step = (
        "Prepare role-relevant introduction using published business channel"
        if has_channel else
        "Research a real decision-maker and a relevant public contact channel"
        if state not in ("SOURCE_UNAVAILABLE", "NO_USABLE_WEBSITE") else
        "Find an alternative original company source before outreach"
    )
    return {"source_key": str(row.get("source_key") or ""),
        "organization": str(row.get("organization") or ""),
        "lane": lane, "fit_score": score, "original_research_score": base,
        "offer_hypothesis": hypothesis, "website": str(row.get("website") or ""),
        "original_source": str(row.get("original_url") or ""),
        "scan_state": state, "contact_page_url": str(row.get("contact_page_url") or ""),
        "team_page_url": str(row.get("team_page_url") or ""),
        "general_business_channel": str(row.get("published_general_channel") or ""),
        "site_description": str(row.get("site_description") or "")[:200],
        "site_title": str(row.get("site_title") or "")[:140],
        "last_scanned": row["scanned_at"].isoformat() if row.get("scanned_at") else None,
        "next_step": next_step,
        "contact_verified_person": False, "customer_qualified": False,
        "email_sent": False, "paid": False,
        "recommendation_basis": "ORIGINAL_SOURCE_PLUS_OBSERVED_PUBLIC_SITE" if row.get("scanned_at") else "ORIGINAL_SOURCE_ONLY"}


async def founder_scout_board(settings: object, *, limit: int = 12) -> dict[str, Any]:
    db = await asyncpg.connect(_database_url(settings))
    try:
        await prepare_scout(db)
        totals = await db.fetchrow("""SELECT count(*)::int total,
          count(*) FILTER(WHERE promoted_deal_id IS NULL)::int pending
          FROM noetfield.corp_research_sources""")
        statuses = await db.fetchrow("""SELECT count(*) FILTER(WHERE scan_state IN (
            'PUBLISHED_GENERAL_BUSINESS_EMAIL','PUBLIC_CONTACT_PAGE',
            'PUBLIC_TEAM_PAGE','NO_CHANNEL_OBSERVED'))::int scanned,
          count(*)::int attempted,
          count(*) FILTER(WHERE scan_state='NO_USABLE_WEBSITE')::int no_website,
          count(*) FILTER(WHERE scan_state='PUBLISHED_GENERAL_BUSINESS_EMAIL')::int published_mailboxes,
          count(*) FILTER(WHERE scan_state='PUBLIC_CONTACT_PAGE')::int contact_pages,
          count(*) FILTER(WHERE scan_state='PUBLIC_TEAM_PAGE')::int team_pages,
          count(*) FILTER(WHERE scan_state='SOURCE_UNAVAILABLE')::int unavailable
          FROM noetfield.corp_founder_scout""")
        rows = await db.fetch("""SELECT r.source_key,r.organization,r.lane,r.score,
          r.website,r.original_url,s.page_url,s.site_title,s.site_description,
          s.published_general_channel,s.contact_page_url,s.team_page_url,
          s.scan_state,s.scanned_at
          FROM noetfield.corp_research_sources r
          LEFT JOIN noetfield.corp_founder_scout s ON s.source_key=r.source_key
          WHERE r.promoted_deal_id IS NULL
             AND r.review_status NOT IN ('DO_NOT_CONTACT','DISQUALIFIED')
          ORDER BY r.score DESC,r.imported_at ASC LIMIT 100""")
        cards = [_priority(dict(r)) for r in rows]
        cards.sort(key=lambda c: (-c["fit_score"],
            0 if c["general_business_channel"] else 1 if c["contact_page_url"] else 2,
            c["organization"].lower()))
        return {"schema": "noetfield.founder-scout.v1",
            "scope": "CANONICAL_FIELDWORK_PUBLIC_ORGANIZATIONS",
            "summary": {"research_organizations": int(totals["total"]),
                        "awaiting_contact_research": int(totals["pending"]),
                        "websites_checked": int(statuses["scanned"]),
                        "website_checks_attempted": int(statuses["attempted"]),
                        "no_original_website": int(statuses["no_website"]),
                        "public_business_emails": int(statuses["published_mailboxes"]),
                        "public_contact_pages": int(statuses["contact_pages"]),
                        "public_team_pages": int(statuses["team_pages"]),
                        "unavailable_websites": int(statuses["unavailable"])},
            "prospects": cards[:max(1, min(int(limit), 25))],
            "source_count_sampled": len(cards),
            "research_method": "PUBLIC_WEBSITE_CHECK_WITH_ORIGINAL_URL_EVIDENCE_NOT_AI_LLM",
            "qualified_buyers_inferred": 0,
            "contacts_verified_inferred": 0, "messages_sent": 0,
            "paid_sales_inferred": 0}
    finally:
        await db.close()


async def run_scout_batch(settings: object, *, limit: int = 3,
                          source_key: str = "") -> dict[str, Any]:
    """A bounded no-form scan. Scheduler uses this directly; operator may run it now.

    Small network quotas avoid overloading external websites. Results are
    idempotently attached to the original Fieldwork source and remain research.
    """
    count = max(1, min(int(limit), _MAX_BATCH))
    db = await asyncpg.connect(_database_url(settings))
    try:
        await prepare_scout(db)
        rows = await db.fetch("""SELECT r.source_key,r.organization,r.website,r.original_url
          FROM noetfield.corp_research_sources r
          LEFT JOIN noetfield.corp_founder_scout s ON s.source_key=r.source_key
          WHERE r.promoted_deal_id IS NULL
            AND r.review_status NOT IN ('DO_NOT_CONTACT','DISQUALIFIED')
            AND ($2::text = '' OR r.source_key=$2)
            AND (s.scanned_at IS NULL OR s.scanned_at < now()-interval '7 days'
                 OR $2::text <> '')
          ORDER BY (s.scanned_at IS NULL) DESC,
            s.scanned_at ASC NULLS FIRST, r.score DESC
          LIMIT $1""",count,source_key.strip())
        outcomes = []
        # Fetch independent sources concurrently; only persistence is serialized.
        # A five-site button stays responsive even when one source is unavailable.
        findings = await asyncio.gather(*(
            asyncio.wait_for(fetch_official_signals(str(row["website"] or "")),timeout=12)
            for row in rows
        ),return_exceptions=True)
        for row, observed in zip(rows, findings):
            # Only an explicit website from original Fieldwork research.
            finding = (observed if isinstance(observed, dict) else {
                "scan_state": "SOURCE_UNAVAILABLE", "page_url": "",
                "error": "PROVIDER_TIMEOUT_OR_FAILURE"
            })
            await db.execute("""INSERT INTO noetfield.corp_founder_scout(
               source_key,page_url,site_title,site_description,
               published_general_channel,contact_page_url,team_page_url,
               scan_state,error_code,scanned_at)
               VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,now())
               ON CONFLICT(source_key) DO UPDATE SET
               page_url=excluded.page_url,site_title=excluded.site_title,
               site_description=excluded.site_description,
               published_general_channel=excluded.published_general_channel,
               contact_page_url=excluded.contact_page_url,
               team_page_url=excluded.team_page_url,
               scan_state=excluded.scan_state,error_code=excluded.error_code,
               scanned_at=now()""",
               row["source_key"],finding.get("page_url", ""),
               finding.get("title", ""),finding.get("description", ""),
               finding.get("public_channel", ""),finding.get("contact_url", ""),
               finding.get("team_url", ""),finding["scan_state"],
               finding.get("error", ""))
            outcomes.append({
                "source_key":row["source_key"],"organization":row["organization"],
                "scan_state":finding["scan_state"],
                "page_url":finding.get("page_url", ""),
                "public_business_channel_observed":bool(finding.get("public_channel")),
                "contact_page_observed":bool(finding.get("contact_url"))})
        return {"schema":"noetfield.founder-scout-run.v1",
            "state":"COMPLETE","scanned":len(outcomes),
            "found_public_business_channels":sum(x["public_business_channel_observed"] for x in outcomes),
            "found_contact_pages":sum(x["contact_page_observed"] for x in outcomes),
            "results":outcomes,
            "source_only":True,"messages_sent":0,"contacts_qualified":0,
            "models_called":0,"provider_cost_minor":0}
    finally:
        await db.close()
