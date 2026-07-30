#!/usr/bin/env python3
"""NOETFIELD_SFF_FINAL_RECONCILIATION_V1 — orchestrate regen, audit, release receipt."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

CANONICAL_ROUTES = [
    "/",
    "/system/",
    "/applications/",
    "/applications/trustfield/",
    "/public-interest/",
    "/proof/",
    "/about/",
    "/investors/",
    "/contact/",
    "/motors/",
    "/runways/",
    "/trust/",
    "/privacy/",
]

OLD_NAV_MARKERS = (
    "AI Motors / Runways / Proof / Company / Deploy / Contact",
    'href="/deploy/"',
    ">Deploy</a>",
)

FORBIDDEN_SOURCEB_ROUTES = (
    "index.html",
    "about/index.html",
    "applications/index.html",
    "applications/trustfield/index.html",
    "proof/index.html",
    "public-interest/index.html",
    "investors/index.html",
)


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def route_audit() -> dict:
    findings: list[dict] = []
    v2_nav = ('href="/system/"', 'href="/applications/"', 'href="/proof/"', 'href="/public-interest/"', 'href="/about/"')
    for route in CANONICAL_ROUTES:
        rel = "index.html" if route == "/" else route.lstrip("/") + "index.html"
        path = ROOT / rel
        if not path.is_file():
            findings.append({"route": route, "severity": "P0", "reason": "missing file"})
            continue
        text = path.read_text(encoding="utf-8")
        if "SourceB" in text:
            findings.append({"route": route, "severity": "P0", "reason": "SourceB present"})
        for marker in OLD_NAV_MARKERS:
            if marker in text:
                findings.append({"route": route, "severity": "P1", "reason": f"old nav marker: {marker}"})
        if route != "/":
            nav_match = 'nf-corp-nav' in text
            if not nav_match:
                findings.append({"route": route, "severity": "P1", "reason": "missing v2 corporate nav"})
            else:
                for item in v2_nav:
                    if item not in text:
                        findings.append({"route": route, "severity": "P1", "reason": f"missing nav item {item}"})
        if route == "/" and ("nf-sourcea-xlink" in text or "Ops Health Audit" in text):
            findings.append({"route": route, "severity": "P0", "reason": "SourceA Ops Health Audit block"})
        if route == "/" and "Open client-zero alpha" not in text:
            findings.append({"route": route, "severity": "P1", "reason": "missing Open client-zero alpha CTA"})
    for rel in FORBIDDEN_SOURCEB_ROUTES:
        path = ROOT / rel
        if path.is_file() and "SourceB" in path.read_text(encoding="utf-8"):
            findings.append({"route": rel, "severity": "P0", "reason": "SourceB on canonical page"})
    noetfield = ROOT / "proof/noetfield/index.html"
    if noetfield.is_file():
        t = noetfield.read_text(encoding="utf-8")
        if "HISTORICAL ARTIFACT" not in t or "noindex,nofollow" not in t:
            findings.append({"route": "/proof/noetfield/", "severity": "P0", "reason": "superseded banner incomplete"})
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8") if (ROOT / "sitemap.xml").is_file() else ""
    if "/proof/noetfield/" in sm:
        findings.append({"route": "sitemap.xml", "severity": "P0", "reason": "proof/noetfield still in sitemap"})
    return {"routes_checked": len(CANONICAL_ROUTES), "findings": findings, "pass": not findings}


def patch_sitemap_superseded() -> None:
    sm_path = ROOT / "sitemap.xml"
    if not sm_path.is_file():
        return
    text = sm_path.read_text(encoding="utf-8")
    import re

    new_text = re.sub(r"\s*<url>\s*<loc>https://www\.noetfield\.com/proof/noetfield/.*?</url>", "", text, flags=re.DOTALL)
    if new_text != text:
        sm_path.write_text(new_text, encoding="utf-8")
        print("removed /proof/noetfield/ from sitemap.xml")


def main() -> int:
    py = sys.executable
    run([py, str(SCRIPTS / "write_canonical_domain_v2_v1.py")])
    run([py, str(SCRIPTS / "write_claims_boundary_proof_v1.py")])
    run([py, str(SCRIPTS / "sync_canonical_v2_shell_v1.py")])
    run([py, str(SCRIPTS / "apply_legacy_route_containment_v1.py")])
    run([py, str(SCRIPTS / "generate_sitemap.py")])
    patch_sitemap_superseded()
    run([py, str(SCRIPTS / "write_sff_long_form_reconciliation_v1.py")])
    run([py, str(SCRIPTS / "noetfield_social_preview_v2.py"), "sync-sources"])
    run(["bash", str(SCRIPTS / "build-www-pages-dist.sh")])
    run([py, str(SCRIPTS / "noetfield_social_preview_v2.py"), "verify"])
    run([py, str(SCRIPTS / "verify_canonical_claim_audit_v1.py")])
    run(["bash", str(SCRIPTS / "verify-static-www.sh")])

    audit = route_audit()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipt = {
        "release": "NOETFIELD_SFF_FINAL_RECONCILIATION_V1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trustfield_boundary": (
            "TrustField is a Noetfield Systems Inc. product whose synthetic "
            "demonstrations provide a bounded validation context; it is not a "
            "Noetfield Systems Inc. product or subsidiary."
        ),
        "budget_amounts_preserved": {
            "base_usd": 180000,
            "minimum_usd": 25000,
            "ambitious_usd": 450000,
            "maximum_usd": 750000,
        },
        "route_audit": audit,
        "artifacts": {},
    }
    pdf = ROOT / "public-interest/artifacts/SFF_Noetfield_Long_Form_For_Profit_RECONCILIATION_V1.pdf"
    docx = ROOT / "public-interest/artifacts/SFF_Noetfield_Long_Form_For_Profit_RECONCILIATION_V1.docx"
    for path in (pdf, docx):
        if path.is_file():
            receipt["artifacts"][path.name] = {"sha256": sha256_file(path), "path": str(path.relative_to(ROOT))}
    receipt_path = ROOT / f"receipts/NOETFIELD_SFF_FINAL_RECONCILIATION_V1_{ts}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {receipt_path.relative_to(ROOT)}")
    if not audit["pass"]:
        for f in audit["findings"]:
            print(f"FAIL route-audit: {f}", file=sys.stderr)
        return 1
    print("PASS NOETFIELD_SFF_FINAL_RECONCILIATION_V1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
