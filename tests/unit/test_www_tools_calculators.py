"""Public operator tools: math, routes, and honest leave-alone copy."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
JS = (ROOT / "assets" / "noetfield-tools.js").read_text(encoding="utf-8")

LOAD = 1.3
WEEKS = 48
HOBBY = 3000


def process_cost(touches: float, minutes: float, rate: float, people: float) -> float:
    return touches * (minutes / 60) * rate * LOAD * people * WEEKS


def test_engine_constants_match_the_operator_post() -> None:
    assert "var LOAD = 1.3;" in JS
    assert "var WEEKS = 48;" in JS
    assert "var HOBBY = 3000;" in JS
    assert "Nothing is posted" in JS


def test_quiet_leak_hobby_line() -> None:
    small = process_cost(2, 5, 30, 1)
    large = process_cost(10, 12, 45, 3)
    assert small < HOBBY
    assert large > HOBBY
    assert round(large) == 16848


def test_required_tool_pages_exist_and_are_indexable() -> None:
    routes = [
        "index.html",
        "quiet-leak/index.html",
        "meeting-tax/index.html",
        "handoff/index.html",
        "ai-spend/index.html",
        "shadow-ai/index.html",
        "who-accepted/index.html",
        "copilot-seats/index.html",
        "board-five/index.html",
        "embed/index.html",
    ]
    for rel in routes:
        path = TOOLS / rel
        html = path.read_text(encoding="utf-8")
        assert 'content="index,follow"' in html
        assert "noetfield-tools.js" in html
        assert "Nothing stored" in html or "nothing stored" in html.lower()
        assert "http-equiv" not in html.lower()
        assert re.search(r'canonical" href="https://www.noetfield.com/tools/', html)


def test_live_ctas_are_real_noetfield_urls() -> None:
    assert "/copilot/pilot/" in JS
    assert "/trust-brief/" in JS
    assert "/copilot/readiness/" not in JS
    assert "Open the app" in JS
    assert JS.count("noetfield.com") >= 1


def test_homepage_and_applications_link_tools() -> None:
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    apps = (ROOT / "applications" / "index.html").read_text(encoding="utf-8")
    assert 'href="/tools/"' in home
    assert 'href="/tools/"' in apps


def test_public_artifact_allowlist_includes_tools() -> None:
    import json

    data = json.loads((ROOT / "governance" / "www-public-artifact-v1.json").read_text(encoding="utf-8"))
    files = set(data["static_files"])
    for path in (
        "tools/index.html",
        "tools/quiet-leak/index.html",
        "tools/meeting-tax/index.html",
        "tools/handoff/index.html",
        "tools/ai-spend/index.html",
        "tools/shadow-ai/index.html",
        "tools/who-accepted/index.html",
        "tools/copilot-seats/index.html",
        "tools/board-five/index.html",
        "tools/embed/index.html",
        "assets/noetfield-tools.css",
        "assets/noetfield-tools.js",
    ):
        assert path in files
    assert "tools/pr-conflict-resolver-report/report.html" not in files


def test_embed_kit_lists_iframe_sources() -> None:
    html = (TOOLS / "embed" / "index.html").read_text(encoding="utf-8")
    for slug in (
        "quiet-leak",
        "meeting-tax",
        "handoff",
        "ai-spend",
        "shadow-ai",
        "who-accepted",
        "copilot-seats",
        "board-five",
    ):
        assert f"/tools/{slug}/?embed=1" in html


def test_salary_and_practical_controls_exist() -> None:
    js = JS
    assert "var HOURS = 40;" in js
    assert "pay" in (TOOLS / "quiet-leak" / "index.html").read_text(encoding="utf-8")
    html = (TOOLS / "quiet-leak" / "index.html").read_text(encoding="utf-8")
    assert "nf-tools-print" in html
    assert "Copy for Slack" in html
    assert 'name="pay"' in html
    assert "Halve the touches" in html
    meeting = (TOOLS / "meeting-tax" / "index.html").read_text(encoding="utf-8")
    assert "standing meeting" in meeting.lower() or "Standing meeting" in meeting
    shadow = (TOOLS / "shadow-ai" / "index.html").read_text(encoding="utf-8")
    assert "personal" in shadow.lower()


def test_meeting_tax_hobby_line() -> None:
    small = 1 * (15 / 60) * 30 * LOAD * 3 * WEEKS
    big = 3 * (60 / 60) * 70 * LOAD * 12 * WEEKS
    assert small < HOBBY
    assert big > HOBBY


def test_practical_field_output_is_wired() -> None:
    quiet = (TOOLS / "quiet-leak" / "index.html").read_text(encoding="utf-8")
    assert "data-result-formula" in quiet
    assert "data-result-warn" in quiet
    assert "data-result-blurb" in quiet
    assert "Copy for Slack" in quiet
    assert "nf-tools-print" in quiet
    assert "nf-tools-embed-v1" in JS
    embed = (TOOLS / "embed" / "index.html").read_text(encoding="utf-8")
    assert "With a client" in embed
