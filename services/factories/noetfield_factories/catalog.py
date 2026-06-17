"""Machine-readable factory and tier catalog loaders."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
FACTORY_CATALOG_PATH = REPO_ROOT / "governance" / "FACTORY_CATALOG.json"
TIER_CATALOG_PATH = REPO_ROOT / "governance" / "CAPABILITY_TIER_CATALOG.json"


@lru_cache(maxsize=1)
def load_factory_catalog() -> dict[str, Any]:
    return json.loads(FACTORY_CATALOG_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_tier_catalog() -> dict[str, Any]:
    return json.loads(TIER_CATALOG_PATH.read_text(encoding="utf-8"))


def catalog_factory_entries() -> list[dict[str, Any]]:
    return list(load_factory_catalog().get("factories", []))


def live_factory_entries() -> list[dict[str, Any]]:
    return [f for f in catalog_factory_entries() if f.get("status") == "live"]


def factory_entry(factory_id: str) -> dict[str, Any] | None:
    for entry in catalog_factory_entries():
        if entry.get("id") == factory_id:
            return entry
    return None


def is_factory_live(factory_id: str) -> bool:
    entry = factory_entry(factory_id)
    return entry is not None and entry.get("status") == "live"


def allowed_gtm_skus() -> list[str]:
    return list(load_factory_catalog().get("allowed_gtm_skus", []))


def blocked_capabilities() -> list[str]:
    return list(load_factory_catalog().get("blocked_capabilities", []))


def _factory_status_map() -> dict[str, dict[str, Any]]:
    return {entry["id"]: entry for entry in catalog_factory_entries()}


def enrich_platform_tree(node: dict[str, Any], status_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Merge factory status from catalog into platform_tree nodes."""
    enriched = dict(node)
    factory_id = enriched.get("factory_id")
    if factory_id and factory_id in status_map:
        entry = status_map[factory_id]
        enriched["status"] = entry.get("status")
        enriched["sku"] = entry.get("sku")
        enriched["route"] = entry.get("route")
        enriched["callable"] = entry.get("status") == "live"
    anchor_key = enriched.get("anchor_key")
    if anchor_key:
        anchors = load_factory_catalog().get("platform_layer_anchors", {})
        enriched["anchor"] = anchors.get(anchor_key)
    children = enriched.get("children")
    if children:
        enriched["children"] = [
            enrich_platform_tree(child, status_map) for child in children if isinstance(child, dict)
        ]
    return enriched


def load_platform_catalog() -> dict[str, Any]:
    catalog = load_factory_catalog()
    status_map = _factory_status_map()
    platform_tree = catalog.get("platform_tree", {})
    return {
        "catalog_version": catalog.get("catalog_version"),
        "platform_tree": enrich_platform_tree(platform_tree, status_map),
        "layer_anchors": catalog.get("platform_layer_anchors", {}),
        "callable_factory_ids": [f["id"] for f in live_factory_entries()],
        "factories": [
            {
                "id": e["id"],
                "name": e.get("name"),
                "alias": e.get("alias"),
                "tier": e.get("tier"),
                "capability": e.get("capability"),
                "sku": e.get("sku"),
                "status": e.get("status"),
                "route": e.get("route"),
                "callable": e.get("status") == "live",
            }
            for e in catalog_factory_entries()
        ],
    }
