#!/usr/bin/env bash
# verify-stripe-catalog.sh — GTM Stripe catalog anti-drift
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

STRIPE_CAT="$ROOT/governance/STRIPE_CATALOG.json"
PUBLIC_CAT="$ROOT/assets/noetfield-stripe-catalog.json"
SALES_PAGE="$ROOT/gate/sales/index.html"

[[ -f "$STRIPE_CAT" ]] || fail "missing governance/STRIPE_CATALOG.json"
[[ -f "$PUBLIC_CAT" ]] || fail "missing assets/noetfield-stripe-catalog.json"
[[ -f "$SALES_PAGE" ]] || fail "missing gate/sales/index.html"

python3 -c "
import json
from pathlib import Path
root = Path('$ROOT')
stripe = json.loads((root / 'governance/STRIPE_CATALOG.json').read_text())
public = json.loads((root / 'assets/noetfield-stripe-catalog.json').read_text())
allowed = set(stripe['allowed_gtm_skus'])
checkout = [o for o in stripe['offerings'] if o.get('checkout_type') == 'payment_link']
if len(checkout) < 2:
    raise SystemExit('expected at least 2 payment_link offerings')
for o in checkout:
    if not o.get('payment_link_url', '').startswith('https://buy.stripe.com/'):
        raise SystemExit(f'invalid payment link: {o.get(\"gtm_sku\")}')
    if o['gtm_sku'] not in allowed:
        raise SystemExit(f'offering not in allowed GTM SKUs: {o[\"gtm_sku\"]}')
pub_skus = {o['gtm_sku'] for o in public['offerings']}
if pub_skus != allowed:
    raise SystemExit(f'public catalog SKU mismatch: {pub_skus} vs {allowed}')
sales = (root / 'gate/sales/index.html').read_text()
if 'nf-stripe-disclaimer' not in sales:
    raise SystemExit('gate/sales missing nf-stripe-disclaimer')
if 'noetfield-stripe-catalog.json' not in sales:
    raise SystemExit('gate/sales missing catalog fetch')
" || fail "stripe catalog validation failed"

ok "STRIPE_CATALOG.json and public purchase hub valid"

grep -q "STRIPE_WEBHOOK_SECRET" .env.example || fail ".env.example missing STRIPE_WEBHOOK_SECRET"
grep -q "verify-stripe-catalog" Makefile || fail "Makefile missing verify-stripe-catalog"

ok "env template and Makefile wired"
echo ""
echo "verify-stripe-catalog: all checks passed"
