#!/usr/bin/env python3
"""Noetfield site-audit CLI v2 — disk or live crawl, deterministic receipt."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "scripts" / "site_audit"
sys.path.insert(0, str(ROOT / "scripts"))

from site_audit import audit as audit_mod  # noqa: E402
from site_audit import crawl as crawl_mod  # noqa: E402

RECEIPTS = ROOT / "reports" / "www-audit" / "receipts"
SNAP_DISK = ROOT / "reports" / "www-audit" / "snapshots" / "disk"
SNAP_LIVE = ROOT / "reports" / "www-audit" / "snapshots" / "live"
MANIFEST = ROOT / "reports" / "www-audit" / "MANIFEST.json"


def update_manifest(receipt_path: Path, receipt: dict) -> None:
    manifest = {"schema": "nf-www-audit-manifest-v1", "receipts": []}
    if MANIFEST.is_file():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["receipts"] = [
        r
        for r in manifest.get("receipts", [])
        if r.get("path") != str(receipt_path.relative_to(ROOT))
    ]
    manifest["receipts"].insert(
        0,
        {
            "path": str(receipt_path.relative_to(ROOT)),
            "run_at": receipt.get("run_at"),
            "mode": receipt.get("crawl_mode"),
            "findings_total": receipt.get("findings_total"),
            "by_severity": receipt.get("by_severity"),
            "state": receipt.get("state"),
        },
    )
    manifest["receipts"] = manifest["receipts"][:24]
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Noetfield site-audit machine v2")
    parser.add_argument("--mode", choices=("disk", "live"), default="disk")
    parser.add_argument("--root", default="https://www.noetfield.com", help="live crawl root URL")
    parser.add_argument("--max-pages", type=int, default=120)
    parser.add_argument("--fail-on", default="P0", help="severity threshold (P0, P1, ANY)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    snap_dir = SNAP_LIVE if args.mode == "live" else SNAP_DISK
    snap_dir.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)

    if args.mode == "disk":
        idx = crawl_mod.crawl_disk(ROOT, snap_dir, max_pages=args.max_pages)
    else:
        idx = crawl_mod.crawl_live(args.root, snap_dir, max_pages=args.max_pages)

    idx["snapshots_dir"] = str(snap_dir)
    findings = audit_mod.audit_rows(idx)
    receipt = audit_mod.build_receipt(idx, findings)
    stamp = receipt["run_at"].replace(":", "").replace("-", "")
    out = RECEIPTS / f"audit_{stamp}.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    update_manifest(out, receipt)

    sev = receipt.get("by_severity", {})
    summary = (
        f"nf_site_audit_v1: mode={args.mode} pages={receipt['pages_audited']} "
        f"P0={sev.get('P0', 0)} P1={sev.get('P1', 0)} P2={sev.get('P2', 0)} -> {out.relative_to(ROOT)}"
    )
    if args.json:
        print(json.dumps({"ok": True, "receipt": str(out.relative_to(ROOT)), "summary": summary, **receipt}, indent=2))
    else:
        print(summary)

    fail = 0
    if args.fail_on == "ANY" and findings:
        fail = len(findings)
    elif args.fail_on == "P1":
        fail = sev.get("P0", 0) + sev.get("P1", 0)
    else:
        fail = sev.get("P0", 0)
    if fail:
        print(f"nf_site_audit_v1: FAIL ({fail} finding(s) at {args.fail_on} threshold)", file=sys.stderr)
        return 1
    print("nf_site_audit_v1: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
