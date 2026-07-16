#!/usr/bin/env bash
# Rebuild twice and require an identical path+hash deployment manifest.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MANIFEST="tmp/noetfield-www/public-artifact-manifest.json"
FIRST="$(mktemp "${TMPDIR:-/tmp}/nf-rel-002-artifact-manifest.XXXXXX")"
trap 'rm -f "$FIRST"' EXIT

bash scripts/build-www-pages-dist.sh
cp "$MANIFEST" "$FIRST"
bash scripts/build-www-pages-dist.sh

if ! cmp -s "$FIRST" "$MANIFEST"; then
  echo "FAIL artifact determinism: repeated builds produced different manifests" >&2
  diff -u "$FIRST" "$MANIFEST" || true
  exit 1
fi

python3 scripts/build-public-www-artifact.py --mode verify
HASH="$(shasum -a 256 "$MANIFEST" | awk '{print $1}')"
echo "verify-www-artifact-determinism: PASS (manifest_sha256=$HASH)"
