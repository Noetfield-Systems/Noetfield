"""Unit tests for www UI/UX grade gate."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_golden_baseline_json_valid() -> None:
    path = ROOT / "data" / "www-home-golden-baseline-v1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema"] == "www-home-golden-baseline-v1"
    assert "Inter" in data["required_font_families"]
    assert "Newsreader" in data["required_font_families"]
    assert "IBM+Plex" in data["forbidden_font_families"]
    assert data["min_nf_corp_section"] >= 6


def test_verify_www_ui_grade_script_pass() -> None:
    script = ROOT / "scripts" / "verify-www-ui-grade.sh"
    assert script.is_file()
    proc = subprocess.run(
        ["bash", str(script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PASS" in proc.stdout


def test_grade_python_rejects_ibm_plex(tmp_path: Path, monkeypatch) -> None:
    # Smoke: current index must not contain IBM Plex
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "IBM+Plex" not in html and "IBM Plex" not in html


def test_premium_editorial_headline_is_backed_by_buyer_clarity() -> None:
    """A concise art-directed H1 is valid only when the lead and CTA are clear."""
    import re
    baseline = json.loads((ROOT / "data" / "www-home-golden-baseline-v1.json").read_text())
    copy = baseline["copy_grade"]
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 18 <= copy["h1_min_chars"] < 40
    assert copy["require_explicit_buyer_lead"] is True
    assert copy["h1_max_chars"] >= 120
    match = re.search(r'<p[^>]*class="[^"]*nf-ins-lead[^"]*"[^>]*>(.*?)</p>', html, re.I | re.S)
    assert match is not None, "A beautiful hero without buyer clarity is insufficient"
    lead = re.sub(r"<[^>]+>", "", match.group(1)).lower()
    for category in copy["required_buyer_lead_substrings"]:
        assert category.lower() in lead
    hero = html.split('id="top"', 1)[1].split("</section>", 1)[0]
    for destination in copy["required_hero_cta_destinations"]:
        assert f'href="{destination}"' in hero
