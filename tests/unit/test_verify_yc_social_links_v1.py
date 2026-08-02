"""YC social-links verifier contracts."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_yc_social_links_v1.py"
SPEC = importlib.util.spec_from_file_location("verify_yc_social_links_v1", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_config_lists_all_yc_links() -> None:
    config = json.loads((ROOT / "data" / "yc-social-links-v1.json").read_text())
    ids = {link["id"] for link in config["links"]}
    assert ids == {
        "app-product",
        "www-home",
        "motors",
        "trustfield",
        "investors",
        "proof-hub",
        "case-001",
        "governed-replacement",
        "claims-boundary",
        "customer-zero",
        "postmortem",
    }


def test_artifact_mode_passes_after_build() -> None:
    artifact = ROOT / "www-pages-dist"
    assert artifact.is_dir(), "run build-www-pages-dist before this test"
    rows, errors = MODULE.verify(artifact=artifact, live=False, user_agent=None)
    www_rows = [row for row in rows if row["id"] != "app-product" and row["id"] != "postmortem"]
    assert errors == [], errors
    assert len(www_rows) == 9
    assert all(row["verdict"] == "PASS" for row in www_rows)
