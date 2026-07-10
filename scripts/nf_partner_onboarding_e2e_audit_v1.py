#!/usr/bin/env python3
"""Partner-onboarding e2e audit — commission (Connector) + strategic (Co-partner/Partner/Investor)
funnel health, verified live against production from outside the building process.

Findings -> public.improvement_queue (Kaizen-consumable, machine_safe gates auto-fix)
Run summary -> public.partner_onboarding_audit_runs (score history for the admin cockpit)
Receipt -> reports/agent-auto/partner-onboarding-audit/latest.json (committed, cockpit reads this)
Telegram -> @noetfield_ops_bot on any critical finding (same channel as deploy-check alerts)

HTTP checks always run (stdlib urllib only). Browser checks need Playwright + Chromium
(`pip install playwright && playwright install --with-deps chromium`) and are skipped with a
loud WARN — never a silent pass — when unavailable locally.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from nf_improvement_queue_enqueue import enqueue_rows  # noqa: E402
from nf_partner_onboarding_audit_client import insert_audit_run  # noqa: E402

BASE = os.environ.get("NOETFIELD_E2E_BASE", "https://www.noetfield.com").rstrip("/")
SOURCE = "github:partner-onboarding-e2e-audit"
EXPECTED_ROI = "partner_conversion_integrity"
TEST_EMAIL = "e2e@noetfield.com"  # recognized by api/_lib/intake-test.js — never a real lead/alert

RUN_ID = str(uuid.uuid4())
TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

RECEIPT_DIR = ROOT / "reports" / "agent-auto" / "partner-onboarding-audit"
LATEST_PATH = RECEIPT_DIR / "latest.json"

VAULT = Path.home() / ".sina" / "secrets.env"

SEVERITY_WEIGHT = {"critical": 25, "high": 10, "medium": 5}

# Routes checked purely by HTTP status — the partner/strategic-lane surface, not the full
# site (scripts/check_noetfield_com_e2e.py already owns the general www E2E contract).
ROUTE_SWEEP = (
    "/partners/",
    "/work-with-us/",
    "/msp/",
    "/investors/",
    "/investors/diligence/",
    "/next/",
    "/trust-brief/intake/",
    "/gate/partners/",
    "/gate/partners/hub/",
    "/gate/partners/structure/",
    "/gate/partners/channel/",
    "/gate/partners/programs/",
    "/gate/partners/apply/",
    "/gate/partners/intake/",
    "/gate/partners/intake2/",
    "/gate/partners/deal/",
    "/gate/partners/delivery/",
    "/gate/partners/notes/",
    "/gate/partners/case-bank-1/",
    "/gate/partners/investors/",
    "/gate/partners/integration/",
    "/gate/partners/apply-integration/",
)


def read_vault(key: str) -> str:
    if not VAULT.is_file():
        return ""
    for line in VAULT.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"')
    return ""


def telegram_creds() -> tuple[str, str]:
    # GHA secrets land in os.environ; local dev falls back to the ~/.sina vault file.
    token = os.environ.get("TELEGRAM_NOETFIELD_OPS_BOT_TOKEN") or read_vault(
        "TELEGRAM_NOETFIELD_OPS_BOT_TOKEN"
    )
    chat_id = os.environ.get("TELEGRAM_OPS_CHAT_ID") or read_vault("TELEGRAM_OPS_CHAT_ID")
    return token, chat_id


def send_telegram_alert(*, title: str, lines: list[str]) -> bool:
    token, chat_id = telegram_creds()
    if not token or not chat_id:
        print(
            "WARN: TELEGRAM_NOETFIELD_OPS_BOT_TOKEN or TELEGRAM_OPS_CHAT_ID not set "
            "(env or ~/.sina/secrets.env) — alert not sent",
            file=sys.stderr,
        )
        return False
    text = f"<b>{title}</b>\n" + "\n".join(lines)
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text[:4096],
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return bool(body.get("ok"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"WARN: telegram alert failed: {exc}", file=sys.stderr)
        return False


def fetch(url: str, *, timeout: float = 20.0) -> tuple[int, str]:
    req = urllib.request.Request(
        url, headers={"Accept": "text/html", "User-Agent": "noetfield-partner-e2e-audit/1"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, str(exc.reason)


def make_finding(
    *,
    check_id: str,
    severity: str,
    summary: str,
    detail: str,
    machine_safe: bool = False,
    kaizen_recipe: str | None = None,
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "severity": severity,
        "summary": summary,
        "detail": detail,
        "machine_safe": machine_safe,
        "kaizen_recipe": kaizen_recipe,
    }


# --------------------------------------------------------------------------
# HTTP-only checks (always run, no browser needed)
# --------------------------------------------------------------------------


def check_route_sweep() -> list[dict[str, Any]]:
    findings = []
    for path in ROUTE_SWEEP:
        code, _ = fetch(f"{BASE}{path}")
        if not (200 <= code < 400):
            findings.append(
                make_finding(
                    check_id="route_sweep",
                    severity="high",
                    summary=f"{path} returned {code}",
                    detail=f"Expected 2xx/3xx from {BASE}{path}, got {code}.",
                )
            )
    return findings


def check_dead_gate_partners_redirect() -> list[dict[str, Any]]:
    code, body = fetch(f"{BASE}/gate/partners/intake/")
    if code and 'url=/enterprise/' in body:
        return [
            make_finding(
                check_id="dead_gate_partners_redirect",
                severity="critical",
                summary="/gate/partners/intake/ still redirects to /enterprise/",
                detail=(
                    "Meta-refresh stub sends every gate/partners/* visitor (including MSP "
                    "and 'next step' CTAs) to the unrelated /enterprise/ page instead of a "
                    "partner intake form."
                ),
            )
        ]
    return []


def check_msp_and_next_dead_ctas() -> list[dict[str, Any]]:
    findings = []
    for path, label, severity in (("/msp/", "msp_dead_cta", "critical"), ("/next/", "next_dead_cta", "high")):
        _, body = fetch(f"{BASE}{path}")
        if 'href="/gate/partners/intake/"' in body:
            findings.append(
                make_finding(
                    check_id=label,
                    severity=severity,
                    summary=f"{path} still links its partner CTA to the dead /gate/partners/intake/ redirect",
                    detail=f"{path} contains href=\"/gate/partners/intake/\" — repoint to a live intake destination.",
                )
            )
    return findings


def check_commission_disclosure() -> list[dict[str, Any]]:
    # A dollar figure ANYWHERE on the page (e.g. the Governance Pack price) doesn't count —
    # it must sit near the referral/commission/intro-fee language itself, or it's not a
    # disclosed commission at all.
    money_pattern = re.compile(r"\d+(\.\d+)?\s?%|\$\s?\d")
    referral_pattern = re.compile(r"referral|commission|intro fee", re.I)
    proximity_chars = 150
    findings = []
    for path in ("/partners/", "/work-with-us/"):
        _, body = fetch(f"{BASE}{path}")
        text = re.sub(r"<[^>]+>", " ", body)
        has_nearby_figure = False
        for m in referral_pattern.finditer(text):
            window = text[max(0, m.start() - proximity_chars) : m.end() + proximity_chars]
            if money_pattern.search(window):
                has_nearby_figure = True
                break
        has_referral_copy = bool(referral_pattern.search(text))
        if has_referral_copy and not has_nearby_figure:
            findings.append(
                make_finding(
                    check_id="commission_disclosure_missing",
                    severity="high",
                    summary=f"{path} mentions referral/commission language with no stated figure",
                    detail=(
                        f"{path} references a referral or intro fee but never states a percentage "
                        "or dollar amount — a Connector applicant cannot evaluate the offer."
                    ),
                )
            )
    return findings


def check_nav_discoverability() -> list[dict[str, Any]]:
    _, home = fetch(f"{BASE}/")
    nav_match = re.search(r'<nav class="menu.*?</nav>', home, re.S)
    nav_html = nav_match.group(0) if nav_match else ""
    hits = [p for p in ("/partners/", "/work-with-us/", "/investors/") if p in nav_html]
    if not hits:
        return [
            make_finding(
                check_id="nav_partner_discoverability",
                severity="high",
                summary="Partners / Work with us / Investors absent from primary navigation",
                detail=(
                    "None of /partners/, /work-with-us/, /investors/ appear inside the header "
                    "<nav class=\"menu\"> block — only reachable via the footer."
                ),
            )
        ]
    return []


def check_orphaned_partner_pdfs() -> list[dict[str, Any]]:
    findings = []
    for pdf in ("/gate/partners/pack/partner-overview.pdf", "/gate/partners/pack/co-sell-play.pdf"):
        code, _ = fetch(f"{BASE}{pdf}")
        if not (200 <= code < 300):
            continue
        linked = False
        for page in ("/msp/", "/work-with-us/", "/partners/"):
            _, body = fetch(f"{BASE}{page}")
            if pdf in body:
                linked = True
                break
        if not linked:
            findings.append(
                make_finding(
                    check_id="orphaned_partner_pdf",
                    severity="medium",
                    summary=f"{pdf} is live but linked from no partner page",
                    detail=f"{pdf} resolves 200 but is not referenced from /partners/, /work-with-us/, or /msp/.",
                )
            )
    return findings


HTTP_CHECKS = (
    check_route_sweep,
    check_dead_gate_partners_redirect,
    check_msp_and_next_dead_ctas,
    check_commission_disclosure,
    check_nav_discoverability,
    check_orphaned_partner_pdfs,
)


# --------------------------------------------------------------------------
# Browser checks (Playwright + Chromium) — real page load, real click, real
# console/network observation. Skipped (loudly) if Playwright isn't installed.
# --------------------------------------------------------------------------


def run_browser_checks() -> tuple[list[dict[str, Any]], bool]:
    """Returns (findings, ran). ran=False means Playwright unavailable — caller must not
    treat that as a pass."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "WARN: playwright not installed — quick-apply / ecosystem-form / investor-form "
            "browser checks SKIPPED (not counted as pass)",
            file=sys.stderr,
        )
        return [], False

    findings: list[dict[str, Any]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            findings.extend(_check_quick_apply_reference_error(browser))
            findings.extend(_check_ecosystem_estimator_leak(browser))
            findings.extend(_check_investor_form_regression(browser))
        finally:
            browser.close()
    return findings, True


def _check_quick_apply_reference_error(browser) -> list[dict[str, Any]]:
    page = browser.new_page()
    page_errors: list[str] = []
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))
    try:
        page.goto(f"{BASE}/work-with-us/", wait_until="networkidle", timeout=30000)
        page.locator('[data-wwu-pick="connector"]').first.click()
        page.locator('#nfPartnerApplyForm [name="email"]').fill(TEST_EMAIL)
        page.locator('#nfPartnerApplyForm [name="org"]').fill("Noetfield E2E Audit")

        fired = {"ok": False}
        try:
            with page.expect_request(
                lambda r: r.method == "POST" and "/api/intake" in r.url, timeout=4000
            ):
                page.locator('#nfPartnerApplyForm button[type="submit"]').click()
            fired["ok"] = True
        except Exception:
            pass

        if page_errors:
            return [
                make_finding(
                    check_id="quick_apply_reference_error",
                    severity="critical",
                    summary="Quick Apply form on /work-with-us/ throws a JS error on submit",
                    detail=f"page.on('pageerror') captured: {page_errors[0][:500]}",
                    machine_safe=True,
                    kaizen_recipe="partner_apply_reference_error",
                )
            ]
        if not fired["ok"]:
            return [
                make_finding(
                    check_id="quick_apply_no_network_activity",
                    severity="critical",
                    summary="Quick Apply submit produced no POST /api/intake and no JS error",
                    detail="Clicked #nfPartnerApplyForm submit; no POST to /api/intake within 4s and no pageerror captured.",
                    machine_safe=True,
                    kaizen_recipe="partner_apply_reference_error",
                )
            ]
        return []
    finally:
        page.close()


def _check_ecosystem_estimator_leak(browser) -> list[dict[str, Any]]:
    page = browser.new_page()
    try:
        page.goto(
            f"{BASE}/trust-brief/intake/?interest=partner&vector=work-with-us&role=connector",
            wait_until="networkidle",
            timeout=30000,
        )
        try:
            page.wait_for_selector("body.intake-ecosystem-mode", timeout=5000)
        except Exception:
            return [
                make_finding(
                    check_id="ecosystem_mode_not_activated",
                    severity="critical",
                    summary="Ecosystem intake mode never activated for a partner-vector URL",
                    detail="body.intake-ecosystem-mode class never appeared — the page stayed in Trust Brief mode.",
                )
            ]

        leaked = []
        for field_id in ("tb_usecases", "tb_teams", "tb_risk", "tb_evidence"):
            sel = f"#{field_id}"
            if page.locator(sel).count() == 0:
                continue
            info = page.locator(sel).evaluate(
                """el => {
                    const s = getComputedStyle(el);
                    return {
                        required: el.hasAttribute('required') || el.required === true,
                        display: s.display,
                        visibility: s.visibility,
                        opacity: s.opacity,
                        w: el.offsetWidth,
                        h: el.offsetHeight,
                    };
                }"""
            )
            hidden = (
                info["display"] == "none"
                or info["visibility"] == "hidden"
                or float(info["opacity"]) == 0
                or (info["w"] == 0 and info["h"] == 0)
            )
            if info["required"] and not hidden:
                leaked.append(field_id)

        if leaked:
            return [
                make_finding(
                    check_id="ecosystem_estimator_fields_leak",
                    severity="critical",
                    summary="Trust Brief pricing-scope fields leak into the partner application form",
                    detail=(
                        "Required, visible fields with no partner-relevant meaning: "
                        + ", ".join(leaked)
                        + " — noetfield-intake-ecosystem-mode.js hides only one of two "
                        ".tb-estimator-fields elements (querySelector vs querySelectorAll)."
                    ),
                    machine_safe=True,
                    kaizen_recipe="ecosystem_estimator_fields_leak",
                )
            ]
        return []
    finally:
        page.close()


def _check_investor_form_regression(browser) -> list[dict[str, Any]]:
    page = browser.new_page()
    page_errors: list[str] = []
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))
    try:
        page.goto(f"{BASE}/investors/", wait_until="networkidle", timeout=30000)
        page.locator('#nfInvestorForm [name="email"]').fill(TEST_EMAIL)
        page.locator('#nfInvestorForm [name="org"]').fill("Noetfield E2E Audit")
        page.locator('#nfInvestorForm button[type="submit"]').click()
        try:
            page.wait_for_selector(
                "#nfInvestorStatus.nf-intake-async-status--ok", timeout=8000
            )
        except Exception:
            return [
                make_finding(
                    check_id="investor_form_regression",
                    severity="critical",
                    summary="Investor inquiry form on /investors/ no longer submits successfully",
                    detail=(
                        f"No success state on #nfInvestorStatus within 8s. "
                        f"pageerror: {page_errors[0][:300] if page_errors else 'none'}"
                    ),
                )
            ]
        return []
    finally:
        page.close()


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def score_from_findings(findings: list[dict[str, Any]]) -> int:
    penalty = sum(SEVERITY_WEIGHT.get(f["severity"], 5) for f in findings)
    return max(0, 100 - penalty)


def to_queue_row(f: dict[str, Any]) -> dict[str, Any]:
    metadata = {
        "sweep": "partner-onboarding-e2e-audit",
        "run_id": RUN_ID,
        "check_id": f["check_id"],
        "severity": f["severity"],
    }
    if f.get("kaizen_recipe"):
        metadata["kaizen_recipe"] = f["kaizen_recipe"]
    return {
        "finding": f"{f['summary']}: {f['detail']}"[:8000],
        "source": f"{SOURCE}:{f['check_id']}"[:200],
        "expected_roi": EXPECTED_ROI,
        "machine_safe": bool(f.get("machine_safe")),
        "status": "open",
        "metadata": metadata,
    }


def build_receipt(findings: list[dict[str, Any]], *, browser_ran: bool, score: int) -> dict[str, Any]:
    critical = [f for f in findings if f["severity"] == "critical"]
    high = [f for f in findings if f["severity"] == "high"]
    status = "fail" if critical else ("error" if not browser_ran else "pass" if not findings else "fail")

    def check_state(check_ids: tuple[str, ...], label: str) -> dict[str, Any]:
        hit = [f for f in findings if f["check_id"] in check_ids]
        if hit:
            return {"id": label, "label": label, "state": "fail", "detail": hit[0]["summary"]}
        return {"id": label, "label": label, "state": "available", "detail": "OK"}

    checks = [
        check_state(("quick_apply_reference_error", "quick_apply_no_network_activity"), "Quick Apply (Connector) submits cleanly"),
        check_state(("ecosystem_mode_not_activated", "ecosystem_estimator_fields_leak"), "Ecosystem apply form free of Trust Brief leakage"),
        check_state(("investor_form_regression",), "Investor inquiry form submits cleanly"),
        check_state(("dead_gate_partners_redirect", "msp_dead_cta", "next_dead_cta"), "MSP / next-step CTAs reach a live intake"),
        check_state(("commission_disclosure_missing",), "Commission/referral figure disclosed"),
        check_state(("nav_partner_discoverability",), "Partner program discoverable from primary nav"),
        check_state(("route_sweep",), "Partner-adjacent routes all resolve"),
        check_state(("orphaned_partner_pdf",), "Partner collateral linked and reachable"),
    ]
    if not browser_ran:
        for c in checks[:3]:
            c["state"] = "orientation"
            c["detail"] = "Playwright unavailable in this run — not verified"

    return {
        "schema": "nf-partner-onboarding-audit-v1",
        "run_id": RUN_ID,
        "generated_at": TS,
        "base": BASE,
        "score": score,
        "status": status,
        "critical_count": len(critical),
        "high_count": len(high),
        "browser_checks_ran": browser_ran,
        "checks": checks,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="skip Supabase/queue/Telegram writes")
    parser.add_argument("--skip-browser", action="store_true", help="skip Playwright checks")
    args = parser.parse_args()

    findings: list[dict[str, Any]] = []
    for check in HTTP_CHECKS:
        findings.extend(check())

    browser_ran = False
    if not args.skip_browser:
        browser_findings, browser_ran = run_browser_checks()
        findings.extend(browser_findings)

    score = score_from_findings(findings)
    receipt = build_receipt(findings, browser_ran=browser_ran, score=score)

    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    (RECEIPT_DIR / f"{TS.replace(':', '')}.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )

    if args.dry_run:
        print(json.dumps(receipt, indent=2))
        return 0 if not receipt["critical_count"] else 1

    enqueued = enqueue_rows([to_queue_row(f) for f in findings]) if findings else 0

    try:
        insert_audit_run(
            run_id=RUN_ID,
            score=score,
            status=receipt["status"],
            critical_count=receipt["critical_count"],
            high_count=receipt["high_count"],
            findings=findings,
        )
    except RuntimeError as exc:
        print(f"WARN: partner_onboarding_audit_runs insert failed: {exc}", file=sys.stderr)

    if receipt["critical_count"]:
        title = "Noetfield partner funnel regression FAIL"
        lines = [
            f"score: {score}/100",
            f"critical: {receipt['critical_count']}",
            f"high: {receipt['high_count']}",
            f"run_id: {RUN_ID}",
            *[f"- {f['check_id']}: {f['summary']}" for f in findings if f["severity"] == "critical"],
        ]
        send_telegram_alert(title=title, lines=lines)

    summary = {
        "sweep": SOURCE,
        "run_id": RUN_ID,
        "score": score,
        "status": receipt["status"],
        "findings": len(findings),
        "enqueued": enqueued,
        "browser_checks_ran": browser_ran,
    }
    if args.json:
        print(json.dumps(summary))
    else:
        print(
            f"nf_partner_onboarding_e2e_audit: score={score} status={receipt['status']} "
            f"findings={len(findings)} enqueued={enqueued} browser_checks_ran={browser_ran}"
        )

    return 1 if receipt["critical_count"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
