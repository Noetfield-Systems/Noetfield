#!/usr/bin/env bash
# sync-derived-docs.sh — regenerate L2 + All-Documents from SOURCE_OF_TRUTH (anti-drift)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Building desktop document bundle (L2-knowledge + Noetfield-All-Documents)"
python3 scripts/build_desktop_document_bundle.py

echo "==> Syncing L2 knowledge from registry"
python3 scripts/sync_l2_knowledge.py

echo "==> Derived docs synced from docs/SOURCE_OF_TRUTH/"
echo "    Run: make verify-law-stack"
