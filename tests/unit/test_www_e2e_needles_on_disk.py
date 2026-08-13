"""Keep production E2E needles on the HTML that actually ships."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = (ROOT / "scripts" / "check_noetfield_com_e2e.py").read_text(encoding="utf-8")


def _assign(name: str) -> tuple[str, ...]:
    tree = ast.parse(SRC)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    value = ast.literal_eval(node.value)
                    assert isinstance(value, tuple)
                    return value
    raise AssertionError(f"missing {name}")


def test_homepage_e2e_needles_exist_on_disk() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for needle in _assign("HOME_NEEDLES"):
        assert needle in html, needle


def test_motors_e2e_needles_exist_on_disk() -> None:
    html = (ROOT / "motors" / "index.html").read_text(encoding="utf-8")
    for needle in _assign("MOTORS_NEEDLES"):
        assert needle in html, needle


def test_intake_pages_keep_enterprise_ctas() -> None:
    html = (ROOT / "start" / "index.html").read_text(encoding="utf-8")
    html += (ROOT / "trust-brief" / "index.html").read_text(encoding="utf-8")
    for needle in _assign("ENTERPRISE_NEEDLES"):
        assert needle in html, needle


def test_tools_hub_needles_exist_on_disk() -> None:
    html = (ROOT / "tools" / "index.html").read_text(encoding="utf-8")
    for needle in _assign("TOOL_HUB_NEEDLES"):
        assert needle in html, needle
