"""Research product SKU → recipe mapping for shared Job Gateway intake."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

RESEARCH_RUNWAY_ID = "research"
RESEARCH_RECIPE_IDS = frozenset(
    {"vendor-decision-brief", "spreadsheet-kpi-pack", "rfp-response-pack"}
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@lru_cache(maxsize=1)
def load_research_product_catalog() -> dict[str, Any]:
    path = _repo_root() / "data" / "nf_research_product_catalog_v1.json"
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("runway_id") != RESEARCH_RUNWAY_ID:
        raise ValueError("research product catalog runway_id must be research")
    return payload


def _normalize_sku(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def resolve_research_product(sku: str) -> dict[str, Any] | None:
    raw = (sku or "").strip()
    if not raw:
        return None
    normalized = _normalize_sku(raw)
    catalog = load_research_product_catalog()
    recipe_version = str(catalog.get("recipe_version") or "0.1.0")
    for product in catalog.get("products") or []:
        if not isinstance(product, dict):
            continue
        candidates = {str(product.get("gtm_sku") or "")}
        candidates.update(str(alias) for alias in product.get("sku_aliases") or [])
        if any(_normalize_sku(candidate) == normalized for candidate in candidates if candidate):
            recipe_id = str(product.get("recipe_id") or "")
            if recipe_id not in RESEARCH_RECIPE_IDS:
                raise ValueError(f"catalog recipe_id {recipe_id!r} is not an approved research recipe")
            return {
                "gtm_sku": str(product.get("gtm_sku") or raw),
                "recipe_id": recipe_id,
                "recipe_version": recipe_version,
                "runway_id": RESEARCH_RUNWAY_ID,
                "display_name": str(product.get("display_name") or recipe_id),
                "price_hypothesis_usd": product.get("price_hypothesis_usd"),
            }
    return None


def is_research_recipe(recipe_id: str) -> bool:
    return recipe_id in RESEARCH_RECIPE_IDS
