---
service_id: never-miss-a-call
doc_id: never-miss-a-call-stripe-test-setup-v1
created: "2026-07-09"
---

# Stripe test-mode setup — Never Miss a Call (AI receptionist)

**Status:** Prepared, not wired. The live page (`services/never-miss-a-call/index.html`)
has no Stripe button — its only conversion action is the free missed-call-audit lead
form. This doc plus `never-miss-a-call-stripe-test-catalog-v1.json` in this folder are
the scaffold for turning an audited lead into a paid signup later, in Stripe **test
mode**, with no live charges.

## Why a separate catalog

`governance/STRIPE_CATALOG.json` is the live catalog for the existing Noetfield GTM
SKUs (Trust Brief, Copilot Readiness Pack, Bank Pilot) on a live Stripe account, and is
guarded by `scripts/verify-stripe-catalog.sh`. This offer is a different product, a
different price shape (setup fee + flat subscription + metered overage), and must stay
in test mode until a real decision is made — so it is kept in its own file
(`docs/services/never-miss-a-call-stripe-test-catalog-v1.json`) rather than mixed into
the live catalog or its verifier.

## What to create in the Stripe Dashboard (test mode)

1. Switch the Stripe Dashboard to **Test mode** (top-left toggle).
2. Create one **Product**: "AI Receptionist — Never Miss a Call".
3. Add three **Prices** to that product:
   - One-time: **$497.00 USD** — setup fee.
   - Recurring monthly: **$297.00 USD / month** — base plan, 500 answered minutes
     included (minutes are tracked and enforced by the call-handling system, not by
     Stripe — Stripe only bills the flat amount).
   - Recurring monthly, **metered** (`usage_type: metered`, `billing_scheme: per_unit`):
     **$0.49 USD / unit**, unit = 1 minute. Reported via usage records once overage
     minutes exist.
4. Copy the resulting `prod_...` / `price_...` test-mode IDs into
   `never-miss-a-call-stripe-test-catalog-v1.json`.
5. Leave `payment_link_url` as `null` / `checkout_type: "not_wired"` until a human
   decides how the offer converts (self-serve Payment Link vs. sales-assisted Checkout
   Session after the audit call) and that decision is approved.

## What NOT to do

- Do not create these products on the live Stripe account.
- Do not add a "Pay now" / "Buy" button to `services/never-miss-a-call/index.html`
  pointing at a live or placeholder Stripe URL — the page must not imply a real charge
  can happen until test-mode checkout has been built and reviewed.
- Do not reuse `buy.stripe.com/PLACEHOLDER_*`-style dead links on a page that captures
  real leads — a broken/fake payment link on a live lead-gen page is worse than no
  button at all.
