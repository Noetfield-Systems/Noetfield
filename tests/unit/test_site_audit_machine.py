"""Site-audit machine — receipts, lenses, crawl guards."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_site_audit_registry_locked_files_exist() -> None:
    for rel in (
        "data/nf-site-audit-registry-v1.json",
        "docs/www/NF_SITE_AUDIT_MACHINE_LOCKED_v1.md",
        "scripts/site_audit/lenses/noetfield-lenses-v1.json",
        "scripts/site_audit/lenses/noetfield-pricing-table.json",
        "scripts/nf_site_audit_v1.py",
        "scripts/verify-site-audit.sh",
    ):
        assert (ROOT / rel).is_file(), rel


def test_site_audit_disk_run_p0_clean() -> None:
    import subprocess

    proc = subprocess.run(
        ["python3", "scripts/nf_site_audit_v1.py", "--mode", "disk", "--fail-on", "P0"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "P0=0" in proc.stdout or "PASS" in proc.stdout


def test_latest_receipt_has_schema_v2() -> None:
    manifest = ROOT / "reports" / "www-audit" / "MANIFEST.json"
    if not manifest.is_file():
        return
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data.get("receipts"), "manifest should list receipts"
    receipt_path = ROOT / data["receipts"][0]["path"]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt.get("schema") == "nf-site-audit-receipt-v2"
    assert "/Users/" not in json.dumps(receipt)
