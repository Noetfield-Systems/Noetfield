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
        "ai-spend/index.html",
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
    assert "https://app.noetfield.com/" in JS
    assert "/copilot/readiness/" not in JS


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
        "tools/ai-spend/index.html",
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
    for slug in ("quiet-leak", "ai-spend", "who-accepted", "copilot-seats", "board-five"):
        assert f"/tools/{slug}/?embed=1" in html
