#!/usr/bin/env bash
# One-way copy: Desktop SourceA → gitignored ops/private/sourceA/ (founder Mac only).
# Agents have READ ONLY on Desktop SSOT files — do not run this to "update" Desktop from repo.
set -euo pipefail
SRC="${1:-/Users/sinakazemnezhad/Desktop/SourceA}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/ops/private/sourceA"
if [[ ! -d "$SRC" ]]; then
  echo "SourceA not found: $SRC" >&2
  exit 1
fi
mkdir -p "$DEST"
cp -f "$SRC/SINA_OS_SSOT_LOCKED.md" "$SRC/PHASE1_UNIFIED_BLUEPRINT_v2_3.md" "$DEST/" 2>/dev/null || {
  echo "Copy failed — check filenames on Desktop" >&2
  exit 1
}
if [[ -f "$SRC/AUTO_CONFLICT_ENGINE_V3_LOCKED.md" ]]; then
  cp -f "$SRC/AUTO_CONFLICT_ENGINE_V3_LOCKED.md" "$DEST/"
fi
if [[ -f "$SRC/NOETFIELD_REPO_ALIGNMENT.md" ]]; then
  cp -f "$SRC/NOETFIELD_REPO_ALIGNMENT.md" "$DEST/"
fi
# Optional: copy when present on Desktop (hub / mandatory chain — read-only mirror)
for f in \
  SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md \
  SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md \
  SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md \
  SEMI_NOTICE_noetfield_cloud_v1.md \
  NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md \
  SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md \
  AGENT_READ_LINKS_INDEX.md; do
  if [[ -f "$SRC/$f" ]]; then
    cp -f "$SRC/$f" "$DEST/"
  fi
done
echo "Synced to $DEST (gitignored)."
ls -la "$DEST"
