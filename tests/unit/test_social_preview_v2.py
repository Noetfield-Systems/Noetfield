"""Deterministic social-preview package contracts."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "noetfield_social_preview_v2.py"
SPEC = importlib.util.spec_from_file_location("noetfield_social_preview_v2", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_six_cards_preserve_exact_canonical_copy() -> None:
    config = json.loads((ROOT / "data" / "noetfield-social-preview-v2.json").read_text())
    assert list(config["cards"]) == [
        "corporate",
        "enterprise",
        "motors",
        "investors",
        "proof",
        "frontier",
    ]
    assert config["cards"]["corporate"]["headline"] == "Governed AI execution."
    assert config["cards"]["enterprise"]["headline"] == "Governed Application Factory"
    assert config["cards"]["motors"]["headline"] == "Custom AI Motors"
    assert config["cards"]["investors"]["headline"] == "Built to be examined."
    assert config["cards"]["proof"]["headline"] == "Evidence before claims."
    assert config["cards"]["frontier"]["headline"] == "Shared work before title."


def test_required_routes_map_to_the_intended_cards() -> None:
    config = MODULE.load_config()
    expected = {
        "/": "corporate",
        "/about/": "corporate",
        "/enterprise/": "enterprise",
        "/enterprise/application-factory/": "enterprise",
        "/motors/": "motors",
        "/investors/": "investors",
        "/invest/": "investors",
        "/proof/": "proof",
        "/frontier-systems/": "frontier",
        "/frontier-systems/memo/": "frontier",
    }
    assert {route: MODULE.profile_for_route(route, config) for route in expected} == expected


def test_key_route_sources_have_complete_current_metadata() -> None:
    config = MODULE.load_config()
    for route in config["source_sync_routes"]:
        path = ROOT / MODULE.path_for_route(route)
        text = path.read_text(encoding="utf-8")
        parsed = MODULE.parse_document(text)
        profile = MODULE.profile_for_route(route, config)
        image = MODULE.card_url(profile, config)
        assert parsed.canonical == f"https://www.noetfield.com{route}"
        assert parsed.meta_properties["og:type"] == "website"
        assert parsed.meta_properties["og:image"] == image
        assert parsed.meta_properties["og:image:width"] == "1200"
        assert parsed.meta_properties["og:image:height"] == "630"
        assert parsed.meta_names["twitter:card"] == "summary_large_image"
        assert parsed.meta_names["twitter:image"] == image
        for forbidden in MODULE.FORBIDDEN_STALE_STRINGS:
            assert forbidden.casefold() not in text.casefold()
