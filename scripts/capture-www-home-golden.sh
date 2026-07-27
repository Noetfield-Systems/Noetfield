#!/usr/bin/env bash
# capture-www-home-golden.sh — optional Playwright first-viewport baselines.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="tests/www/visual/home-golden"
mkdir -p "$OUT"

if ! command -v npx >/dev/null 2>&1; then
  echo "capture-www-home-golden: npx unavailable — skip" >&2
  exit 0
fi

# Serve local index via python and capture with playwright if installed.
PORT="${NF_WWW_GOLDEN_PORT:-8765}"
python3 -m http.server "$PORT" >/tmp/nf-www-golden-http.log 2>&1 &
PID=$!
cleanup() { kill "$PID" >/dev/null 2>&1 || true; }
trap cleanup EXIT
sleep 1

npx --yes playwright@1.49.0 install chromium >/tmp/nf-www-golden-pw-install.log 2>&1 || true
node << NODE
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://127.0.0.1:${PORT}/', { waitUntil: 'networkidle' });
  await page.screenshot({ path: '${OUT}/home-first-viewport.png', fullPage: false });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: '${OUT}/home-mobile.png', fullPage: false });
  await browser.close();
  console.log('capture-www-home-golden: wrote PNGs under ${OUT}');
})().catch((err) => { console.error(err); process.exit(1); });
NODE
