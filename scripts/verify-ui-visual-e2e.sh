#!/usr/bin/env bash
# Visual structure checks — institutional v4 trust-hero discipline (no browser).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
fail=0

echo "=== verify-ui-visual-e2e (institutional v4) ==="

home_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/" 2>/dev/null || true)"

check_home() {
  local needle="$1"
  local label="$2"
  if echo "$home_html" | grep -qF "$needle"; then
    echo "OK   homepage $label"
  else
    echo "FAIL homepage missing $label" >&2
    fail=1
  fi
}

check_home 'class="nf-trust-hero"' "nf-trust-hero layout"
check_home 'class="nf-tle-receipt-card"' "TLE receipt preview card"
check_home 'class="nf-framework-grid-v4"' "framework grid v4"
check_home 'class="nf-hero-actions nf-hero-actions--primary"' "hero primary CTA discipline"
check_home 'noetfield-institutional-v4.css' "institutional-v4.css"
check_home 'rel="preconnect" href="https://fonts.googleapis.com"' "font preconnect"
check_home 'class="nf-site-2026 nf-bank-grade nf-v4"' "nf-v4 body class"

# Hero must not stack six button CTAs in a single nf-hero-actions block.
hero_cta_count="$(echo "$home_html" | python3 -c "
import re, sys
html = sys.stdin.read()
blocks = re.findall(r'<div class=\"nf-hero-actions[^\"]*\">(.*?)</div>', html, re.S)
for block in blocks:
    if 'btn-primary' in block or 'btn-secondary' in block:
        print(len(re.findall(r'class=\"btn ', block)))
        break
else:
    print(0)
" 2>/dev/null || echo "99")"
if [[ "$hero_cta_count" -le 2 ]]; then
  echo "OK   homepage hero button count ($hero_cta_count ≤ 2)"
else
  echo "FAIL homepage hero has $hero_cta_count buttons (max 2 in primary hero)" >&2
  fail=1
fi

# Redundant stacked sections removed from homepage.
if echo "$home_html" | grep -qF 'class="nf-trust"'; then
  echo "FAIL homepage still has redundant nf-trust strip" >&2
  fail=1
else
  echo "OK   homepage no redundant nf-trust strip"
fi
if echo "$home_html" | grep -qF 'class="nf-prs"'; then
  echo "FAIL homepage still has redundant nf-prs block" >&2
  fail=1
else
  echo "OK   homepage no redundant nf-prs block"
fi

# v4 frame on GTM tier routes.
for path in "/" "/enterprise/" "/trust-center/" "/copilot/" "/bank-pilot/" "/copilot/trial/" "/copilot/demo/" "/gate/intake/" "/copilot/procurement/"; do
  label="${path//\//}"
  label="${label:-homepage}"
  html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}${path}" 2>/dev/null || true)"
  if echo "$html" | grep -qF "noetfield-institutional-v4.css"; then
    echo "OK   ${label} institutional-v4.css"
  else
    echo "FAIL ${label} missing institutional-v4.css" >&2
    fail=1
  fi
  if echo "$html" | grep -qF "nf-v4"; then
    echo "OK   ${label} nf-v4 body class"
  else
    echo "FAIL ${label} missing nf-v4 body class" >&2
    fail=1
  fi
done

# Copilot hub — hero CTA discipline (≤2 in primary block).
copilot_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/copilot/" 2>/dev/null || true)"
copilot_cta="$(echo "$copilot_html" | python3 -c "
import re, sys
html = sys.stdin.read()
m = re.search(r'nf-hero-actions--primary\">(.*?)</div>', html, re.S)
if not m:
    print(99)
else:
    print(len(re.findall(r'class=\"btn ', m.group(1))))
" 2>/dev/null || echo "99")"
if [[ "$copilot_cta" -le 2 ]]; then
  echo "OK   copilot hero primary button count ($copilot_cta ≤ 2)"
else
  echo "FAIL copilot hero has $copilot_cta primary buttons" >&2
  fail=1
fi

# Demo async stepper present.
demo_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/copilot/demo/" 2>/dev/null || true)"
if echo "$demo_html" | grep -qF 'class="nf-demo-stepper"'; then
  echo "OK   demo nf-demo-stepper"
else
  echo "FAIL demo missing nf-demo-stepper" >&2
  fail=1
fi

# Header tag no longer truncates long institutional phrase.
header_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/assets/partials/header.html" 2>/dev/null || true)"
if echo "$header_html" | grep -qF "Governance &amp; evidence"; then
  echo "OK   header short brand tag"
else
  echo "FAIL header missing short brand tag" >&2
  fail=1
fi
if echo "$header_html" | grep -qF "Governance execution infrastructure"; then
  echo "FAIL header still has long truncating tag" >&2
  fail=1
else
  echo "OK   header no long truncating tag"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-ui-visual-e2e passed (institutional v4)."
  exit 0
fi
exit 1
