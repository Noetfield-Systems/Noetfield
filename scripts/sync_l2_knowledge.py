#!/usr/bin/env python3
"""Sync uploaded SOT corpus into L2-knowledge clean architecture."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Noetfield-All-Documents" / "uploaded"
if not SRC.is_dir():
    SRC = ROOT / "docs" / "SOURCE_OF_TRUTH" / "uploaded"

L2 = ROOT / "L2-knowledge"
FULL = L2 / "strategy" / "full"
NOETFIELD = L2 / "strategy" / "noetfield"
REF = L2 / "strategy" / "reference-products"

REFERENCE_PREFIXES = (
    "posa-",
    "aie-",
    "aiis-",
    "paios-",
    "paes-",
    "paas-",
    "slf-",
    "slg-",
    "sot-engine",
    "sot-extraction",
    "sot-guidelines",
    "manifesto-",
    "architecture-of-meaning",
    "context-resonance",
    "grok-",
    "perplexity-",
    "cursor-ide",
    "shopify-",
    "unified-system-genealogy",
    "chat-corpora",
    "architecture-md-v2",
)

ARCHIVED_TOOLS = ("n8n", "ollama", "paios")


def classify(name: str) -> str:
    lower = name.lower()
    if lower.startswith("noetfield-") or lower.startswith("wp-") or lower.startswith("governed-"):
        return "noetfield"
    if any(lower.startswith(p) for p in REFERENCE_PREFIXES):
        return "reference"
    if "orchestration-policy-layer" in lower and "noetfield" not in lower:
        return "reference"
    return "noetfield" if "noetfield" in lower else "reference"


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"Source not found: {SRC}")

    for path in (FULL, NOETFIELD, REF):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    counts = {"full": 0, "noetfield": 0, "reference": 0}
    for batch_dir in sorted(SRC.glob("2026-05-batch-*")):
        dest_full = FULL / batch_dir.name
        shutil.copytree(batch_dir, dest_full)
        counts["full"] += len(list(dest_full.rglob("*.md")))

        for md in batch_dir.glob("*.md"):
            if md.name == "README.md":
                continue
            bucket = classify(md.name)
            target_root = NOETFIELD if bucket == "noetfield" else REF
            target_batch = target_root / batch_dir.name
            target_batch.mkdir(parents=True, exist_ok=True)
            shutil.copy2(md, target_batch / md.name)
            counts[bucket] += 1

    perplexity_src = SRC / "2026-05-batch-002" / "perplexity-ai-native-development-guidelines.md"
    if perplexity_src.is_file():
        shutil.copy2(perplexity_src, L2 / "perplexity-ai-native-development-guidelines.md")

    readme = L2 / "README.md"
    readme.write_text(
        """# L2 Knowledge Architecture

## Layout

| Path | Purpose |
|------|---------|
| `strategy/full/` | Complete mirror of all uploaded batches |
| `strategy/noetfield/` | Production runtime + GTM knowledge only |
| `strategy/reference-products/` | POSA, AIE, SLF, PAIOS, theory — **must not drive Noetfield runtime** |
| `perplexity-ai-native-development-guidelines.md` | Operator/dev guidelines (L2 root) |

## Archived tooling (do not wire to Noetfield runtime)

- **n8n** — workflow automation experiments (archived)
- **Ollama** — local model dev only in docker-compose; not production authority
- **PAIOS** — separate personal AI OS lineage; PAIOS-only reference

## Supremacy

`NORTH_STAR.md` and GCIP v4 override this tree on conflict.
""",
        encoding="utf-8",
    )

    print(f"L2 sync complete: {counts}")
    print(f"  full markdown files: {counts['full']}")
    print(f"  noetfield: {counts['noetfield']}")
    print(f"  reference-products: {counts['reference']}")


if __name__ == "__main__":
    main()
