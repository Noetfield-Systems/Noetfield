#!/usr/bin/env python3
"""Noetfield site-audit engine v2 — deterministic lenses over crawl snapshots."""
from __future__ import annotations

import hashlib
import json
import re
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
LENSES = PKG / "lenses" / "noetfield-lenses-v1.json"
PRICING = PKG / "lenses" / "noetfield-pricing-table.json"
DENYLIST = ROOT / "governance" / "PUBLIC_OUTPUT_DENYLIST.json"
HEADER_PARTIAL = ROOT / "assets" / "partials" / "header.html"
PATH_LEAK_RE = re.compile(r"/Users/[^\s\"'<>]+|~/[^\s\"'<>]+")
NAV_BLOCK_RE = re.compile(
    r'<(?:nav|div)[^>]*(?:role=["\']navigation["\']|class=["\'][^"\']*(?:\bnav\b|menuPrimary)[^"\']*)[^>]*>(.*?)</(?:nav|div)>',
    re.I | re.S,
)
NAV_HREF_RE = re.compile(r'href=["\'](/[^"\']*)["\']', re.I)
PRICE_RE = re.compile(r"\$[\d,]+(?:\.\d{2})?(?:k|K)?|\$[\d,]+(?:\s*[–-]\s*\$?[\d,]+(?:k|K)?)?")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ev(text: str, limit: int = 200) -> str:
    return text[:limit]


def audit_rows(idx: dict) -> list[dict]:
    snap = Path(idx["snapshots_dir"])
    lenses = load_json(LENSES)
    pricing = load_json(PRICING)
    findings: list[dict] = []
    auditable = [p for p in idx["index"] if p.get("row_class") == "HTML"]

    for page in auditable:
        html = (snap / page["snapshot"]).read_text(encoding="utf-8", errors="replace")
        for cid, sev, reason, evidence in regex_checks(html, lenses):
            findings.append(_row(page, cid, sev, reason, evidence))
        for cid, sev, reason, evidence in structural_checks(page, html, pricing):
            findings.append(_row(page, cid, sev, reason, evidence))

    for cid, sev, reason, evidence in cross_page_checks(auditable, snap, idx, pricing):
        findings.append(
            {
                "page": "SITE-WIDE",
                "check": cid,
                "severity": sev,
                "decision": "FAIL",
                "reason": reason,
                "evidence": evidence,
            }
        )
    return findings


def _row(page: dict, cid: str, sev: str, reason: str, evidence: str) -> dict:
    return {
        "page": page.get("url", page.get("www_path", "")),
        "www_path": page.get("www_path", ""),
        "check": cid,
        "severity": sev,
        "decision": "FAIL",
        "reason": reason,
        "evidence": evidence,
        "snapshot_sha": page.get("sha256", ""),
    }


def regex_checks(html: str, lenses: dict) -> list[tuple[str, str, str, str]]:
    out: list[tuple[str, str, str, str]] = []
    for lens in lenses.get("lenses", {}).values():
        for check in lens.get("checks", []):
            if "regex" not in check:
                continue
            for match in re.finditer(check["regex"], html):
                ctx = html[max(0, match.start() - 60) : match.end() + 60].replace("\n", " ")
                out.append((check["id"], check["severity"], check["name"], ev(ctx.strip())))
    return out


def structural_checks(page: dict, html: str, pricing: dict) -> list[tuple[str, str, str, str]]:
    out: list[tuple[str, str, str, str]] = []
    www_path = page.get("www_path", "/")

    anchors = set(re.findall(r'href=["\']#([^"\']+)', html))
    ids = set(re.findall(r'id=["\']([^"\']+)', html))
    for anchor in anchors - ids:
        out.append(("RI-4", "P1", f"anchor #{anchor} has no target id", f"href='#{anchor}' present, id absent"))

    money_paths = ("pricing", "pilot", "trust-brief", "start", "intake", "enterprise")
    if any(k in www_path for k in money_paths) and page.get("mailto_links"):
        primary_mailto = page["mailto_links"]
        if www_path.startswith("/pricing") or www_path.startswith("/copilot/pilot"):
            out.append(
                (
                    "BF-1",
                    "P0",
                    "money-page CTA is mailto (no intake, no receipt)",
                    ev(", ".join(primary_mailto[:3])),
                )
            )

    hero = html[:5000]
    ctas = len(re.findall(r'<a[^>]+class="[^"]*(?:btn|button|cta|nav-cta)[^"]*"', hero, re.I))
    if ctas > 3:
        out.append(("BF-3", "P1", f"{ctas} CTAs above fold (max 3)", f"hero region CTA count={ctas}"))

    h1_count = len(re.findall(r"<h1[\s>]", html, re.I))
    if h1_count != 1:
        out.append(("SM-1", "P1", f"{h1_count} <h1> tags (must be 1)", f"count={h1_count}"))

    title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    desc = re.search(r'name=["\']description["\'][^>]*content=["\']([^"\']*)', html, re.I)
    og = re.search(r'property=["\']og:image["\']', html, re.I)
    if title and len(title.group(1).strip()) > 60:
        out.append(("SM-2", "P1", f"title {len(title.group(1).strip())}ch > 60", ev(title.group(1).strip())))
    if not desc or not (50 <= len(desc.group(1)) <= 160):
        out.append(
            (
                "SM-2",
                "P1",
                "meta description missing or outside 50-160ch",
                ev(desc.group(1)) if desc else "absent",
            )
        )
    if not og:
        out.append(("SM-2", "P1", "og:image absent", "no og:image property in head"))

  # BF-2 price drift
    allowed = set(pricing.get("allowed_phrases", []))
    for match in PRICE_RE.findall(html):
        token = match.replace(" ", "")
        if not any(a.replace(" ", "") in token or token in a.replace(" ", "") for a in allowed):
            out.append(("BF-2", "P1", "price figure not in canonical pricing table", ev(match)))
            break

    if www_path == "/":
        missing = [p for p in pricing.get("required_cta_phrases", []) if p not in html]
        if missing:
            out.append(("BF-5", "P2", "homepage missing stable CTAs (deferred until copy verdict)", ", ".join(missing)))

    leak = PATH_LEAK_RE.search(html)
    if leak:
        out.append(("RH-1", "P0", "absolute local path leak in public html", ev(leak.group(0))))

    return out


def nav_fingerprint(html: str) -> frozenset[str]:
    links: set[str] = set()
    for block in NAV_BLOCK_RE.findall(html):
        links.update(NAV_HREF_RE.findall(block))
    if not links and HEADER_PARTIAL.is_file():
        partial = HEADER_PARTIAL.read_text(encoding="utf-8", errors="replace")
        links.update(NAV_HREF_RE.findall(partial))
    return frozenset(links)


def cross_page_checks(auditable: list[dict], snap: Path, idx: dict, pricing: dict) -> list[tuple[str, str, str, str]]:
    out: list[tuple[str, str, str, str]] = []
    navs: dict[str, frozenset[str]] = {}
    entities: set[str] = set()
    inbound = Counter()
    urls = {p.get("www_path", p["url"]) for p in auditable}

    for page in auditable:
        html = (snap / page["snapshot"]).read_text(encoding="utf-8", errors="replace")
        navs[page.get("www_path", page["url"])] = nav_fingerprint(html)
        for entity in re.findall(r"(Noetfield Systems Inc\.|\{ENTITY\})", html):
            entities.add(entity)
        for link in page.get("internal_links", []):
            path = link if link.startswith("/") else urllib_parse_path(link)
            if path in urls:
                inbound[path] += 1

    fingerprints = Counter(navs.values())
    max_nav = pricing.get("max_nav_fingerprints", 2)
    if len(fingerprints) > max_nav:
        out.append(
            (
                "NC-1",
                "P0",
                f"{len(fingerprints)} distinct nav fingerprints across {len(navs)} pages",
                f"expected <= {max_nav}; header partial SSOT={HEADER_PARTIAL.is_file()}",
            )
        )

    if len(entities) > 1:
        out.append(("EP-3", "P0", "legal entity inconsistent across footers", str(sorted(entities))))

    root_path = auditable[0].get("www_path", "/") if auditable else "/"
    for path in urls:
        if inbound[path] == 0 and path not in ("/", root_path):
            out.append(("SM-5", "P2", "orphan page: 0 inbound internal links", path))

    if DENYLIST.is_file():
        deny = load_json(DENYLIST)
        blocked = [p for p in deny.get("probe_paths", []) if p in urls]
        if blocked:
            out.append(("DI-2", "P0", "crawl included denylisted internal paths as HTML", str(blocked[:5])))

    golden = pricing.get("header_partial_sha256")
    if golden and HEADER_PARTIAL.is_file():
        actual = hashlib.sha256(HEADER_PARTIAL.read_bytes()).hexdigest()
        if actual != golden:
            out.append(
                (
                    "NC-2",
                    "P1",
                    "header partial drift vs pricing-table golden sha",
                    f"expected {golden[:12]}… got {actual[:12]}…",
                )
            )

    spa_rows = [p for p in idx["index"] if p.get("row_class") == "SPA_FALLBACK"]
    if spa_rows:
        out.append(
            (
                "DI-1",
                "P1",
                f"{len(spa_rows)} SPA fallback rows excluded from audit math",
                ", ".join(p.get("www_path", "") for p in spa_rows[:5]),
            )
        )

    return out


def urllib_parse_path(url: str) -> str:
    if url.startswith("/"):
        return url
    if url.startswith("disk://"):
        return url.replace("disk://", "")
    import urllib.parse

    return urllib.parse.urlparse(url).path or "/"


def llm_proposals(lenses: dict) -> list[dict]:
    return [
        {"check": check["id"], "prompt": check["llm"], "status": "PROPOSAL_NEEDS_LLM"}
        for lens in lenses.get("lenses", {}).values()
        for check in lens.get("checks", [])
        if "llm" in check
    ]


def build_receipt(idx: dict, findings: list[dict], lane: str = "noetfield") -> dict:
    lenses = load_json(LENSES)
    sev_count = Counter(f["severity"] for f in findings)
    crawl_root = idx.get("root", "")
    if crawl_root.startswith("disk://"):
        crawl_root = "disk://noetfield-repo"
    sanitized_findings = []
    for row in findings:
        clean = dict(row)
        for key in ("evidence", "reason", "page"):
            if key in clean and isinstance(clean[key], str):
                clean[key] = PATH_LEAK_RE.sub("<redacted-path>", clean[key])
        sanitized_findings.append(clean)
    body = {
        "receipt_type": "SITE_AUDIT_CYCLE",
        "schema": "nf-site-audit-receipt-v2",
        "lane": lane,
        "loop": "site-audit",
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "crawl_root": crawl_root,
        "crawl_mode": idx.get("mode", "disk"),
        "pages_audited": len([p for p in idx["index"] if p.get("row_class") == "HTML"]),
        "pages_crawled": idx.get("pages", 0),
        "lenses_version": lenses.get("version", "unknown"),
        "state": "COMPLETE" if sanitized_findings else "PASS",
        "findings_total": len(sanitized_findings),
        "by_severity": dict(sev_count),
        "findings": sanitized_findings,
        "llm_proposals_pending": llm_proposals(lenses),
        "cost": {"provider": "local", "model": "deterministic", "tokens_in": 0, "tokens_out": 0, "usd": 0.0},
        "value_class": "risk_reduction",
        "verifier_note": (
            "L4: PASS claims about fixes require crawl from a runner the fixing agent does not control; "
            "re-run >=60s after deploy."
        ),
    }
    if PATH_LEAK_RE.search(json.dumps(body)):
        raise SystemExit("receipt_hygiene FAIL: receipt body contains local path leak")
    return body
