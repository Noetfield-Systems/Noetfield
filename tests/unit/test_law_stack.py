"""Law stack unification — entry points, manifest, anti-drift."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def manifest() -> dict:
    return json.loads((ROOT / "governance/LAW_STACK.json").read_text(encoding="utf-8"))


def test_law_stack_manifest_active_l0(manifest: dict) -> None:
    assert manifest["active_l0"]["doc_id"] == "noetfield-constitution-gcip-v4"
    assert manifest["active_gtm"]["path"] == "OFFERINGS.md"


def test_law_entry_points_exist(manifest: dict) -> None:
    for name, rel in manifest["entry_points"].items():
        path = ROOT / rel
        assert path.is_file(), f"entry point {name} missing: {rel}"


def test_current_stack_visible() -> None:
    text = (ROOT / "docs/LAWS/CURRENT_STACK_v2026.md").read_text(encoding="utf-8")
    assert "GCIP v4" in text
    assert "GTM operational locks" in text or "OFFERINGS" in text
    assert "FINAL LOCK" in text or "Trust Brief" in text


def test_l0_current_pointer() -> None:
    text = (ROOT / "L0-law/CURRENT.md").read_text(encoding="utf-8")
    assert "noetfield-constitution-gcip-v4" in text
    assert "docs/LAWS/CURRENT_STACK_v2026.md" in text


def test_supersession_index_covers_duplicates() -> None:
    uploaded = ROOT / "docs/SOURCE_OF_TRUTH/uploaded"
    index = (ROOT / "docs/SOURCE_OF_TRUTH/archive/SUPERSESSION_INDEX.md").read_text(encoding="utf-8")
    for dup in uploaded.glob("*-duplicate.md"):
        assert dup.name in index, f"duplicate not indexed: {dup.name}"


def test_documents_registry_has_active_l0(manifest: dict) -> None:
    reg = json.loads(
        (
            ROOT / "docs/SOURCE_OF_TRUTH/registry/source_of_truth_registry.json"
        ).read_text(encoding="utf-8")
    )
    active_id = manifest["active_l0"]["doc_id"]
    l0 = next((d for d in reg["decisions"] if d["domain"] == "noetfield_constitution_l0"), None)
    assert l0 is not None
    assert l0["active_document_key"] == active_id
    inv = json.loads(
        (
            ROOT / "docs/SOURCE_OF_TRUTH/registry/source_document_inventory.json"
        ).read_text(encoding="utf-8")
    )
    doc = next((d for d in inv["documents"] if d["document_key"] == active_id), None)
    assert doc is not None
    assert doc.get("classification") == "active_source_of_truth"
