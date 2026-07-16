#!/usr/bin/env bash
# Build static output directory for Cloudflare Pages.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
DIST="${ROOT}/www-pages-dist"

log() { printf '[build-www-pages-dist] %s\n' "$*"; }

log "sync greeting SSOT…"
python3 scripts/sync_chat_greeting_asset.py
python3 scripts/generate-cf-redirects.py
python3 scripts/generate-www-deny-middleware.py
node scripts/bundle-pages-functions.mjs

log "clean ${DIST}"
if [[ "$DIST" != "${ROOT}/www-pages-dist" || "$ROOT" == "/" ]]; then
  log "FAIL: unsafe artifact path ${DIST}"
  exit 1
fi
rm -rf -- "$DIST"
mkdir -p "$DIST"

log "copy exact tracked public allowlist and generate deterministic receipt…"
python3 scripts/build-public-www-artifact.py --mode build
log "done — exact artifact receipt reports $(find "$DIST" -type f | wc -l | tr -d ' ') static files"
