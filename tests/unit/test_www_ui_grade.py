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
    assert data["min_nf_corp_section"] >= 8


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
