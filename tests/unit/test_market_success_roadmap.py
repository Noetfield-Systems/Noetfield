"""Market success 1000-step roadmap integrity."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROADMAP = ROOT / "docs/strategy/MARKET_SUCCESS_1000_ROADMAP_v1.md"
VENDOR_RE = re.compile(
    r"Vanta|Drata|OneTrust|Credo AI|IBM watsonx|ServiceNow|RegScale|"
    r"Complyance|MetricStream|Modulos|Microsoft Purview|Microsoft 365|\bM365\b",
    re.I,
)


def test_roadmap_has_1000_steps() -> None:
    text = ROADMAP.read_text(encoding="utf-8")
    rows = re.findall(r"^\| mr-\d{4} \|", text, re.M)
    assert len(rows) == 1000


def test_roadmap_has_10_phases() -> None:
    text = ROADMAP.read_text(encoding="utf-8")
    phases = re.findall(r"^## Phase \d+ —", text, re.M)
    assert len(phases) == 10


def test_roadmap_no_vendor_names() -> None:
    text = ROADMAP.read_text(encoding="utf-8")
    assert not VENDOR_RE.search(text)


def test_roadmap_generator_in_sync() -> None:
    before = ROADMAP.read_text(encoding="utf-8")
    subprocess.run(
        ["python3", "scripts/generate_market_success_1000_roadmap.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    after = ROADMAP.read_text(encoding="utf-8")
    assert before == after
