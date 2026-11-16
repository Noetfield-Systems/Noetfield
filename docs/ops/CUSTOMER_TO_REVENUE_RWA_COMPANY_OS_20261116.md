# Noetfield — Customer-to-Revenue Operations (2026-11-16)

**Scope:** Existing Platform FastAPI and `noetfield.public_intakes`, signed Stripe webhook, Company OS, RWA Clinic and Fieldwork. **Homepage V5 (PR #388) is protected and untouched.**

## What was implemented

Commercial intake cases are stored under the **existing** canonical PostgreSQL row in `qualification_json.commercial_ops`. This is the project-level commercial state, not a new CRM, site, payment processor or duplicate contact database.

Two published offers have live payment links in **Noetfield Systems Inc.** Stripe account:

| Offer | Contract reference | Payment required after accepted written scope | Official Stripe Payment Link |
|---|---:|---:|---|
| RWA / Policy-to-Execution Technical Sprint | USD 950 | USD 475 deposit | `plink_1UbG9CJ03eJkL57JNNK0P3cY` |
| Company OS — AI Sales OS pilot | CAD 750 | CAD 750 one-time | `plink_1UcS8RJ03eJkL57J4IMvmFuD` |

The Stripe links exist and are **not** the authority for a contract. A buyer receives a relevant link only after scope acceptance; no wallet gate, forced account creation, new tax/fee or automatic billing.

### Commercial state transitions

`QUALIFY → SCOPE_ACCEPTED → PAYMENT_CONFIRMED → IN_DELIVERY → DELIVERED → CLOSED`

- **QUALIFY** requires a real persisted source intake, known offer, accountable owner and next action.
- **SCOPE_ACCEPTED** requires a written scope reference and HTTPS link to acceptance evidence.
- **PAYMENT_CONFIRMED** requires a **valid Stripe-signed** `checkout.session.completed` (paid) or `checkout.session.async_payment_succeeded` (paid), live mode, exact product-specific Payment Link, exact amount and currency, and the same email as the intake or independent HTTPS evidence authorizing a different payer. The session can attach to only one intake.
- **IN_DELIVERY** requires paid evidence still current (no known refund/dispute). This is the point to open an actual scoped WorkPacket in the existing RWA Clinic or Company OS, using the `intake_id`, SOW and source facts. It does **not** claim a WorkPacket was dispatched automatically.
- **DELIVERED** requires links to the actual deliverable and the customer's acceptance. Merely uploading a PDF does not prove acceptance.
- **CLOSED** requires accepted delivery. A reported opportunity or amount in Fieldwork is not verified cash.

Known reversals mark the payment evidence `REVERSED`. Rerunning a signed webhook cannot duplicate a receipt or steal a session from another case. Operator writes use revision checking. No generated synthetic revenue.

## Private operator API (already-existing Platform service)

Existing `X-Admin-Secret` is required for all endpoints; do not send it from the public website or browser, and do not add it to a repo.

- `POST /api/operations/commercial/cases`
- `GET /api/operations/commercial/funnel?limit=50`

Examples below are *schemas only*. Replace `INT-...` and HTTPS references with real existing Noetfield source and signed documents. Never execute them as production probes.

1. **Open a sourced case:**
```json
{
  "intake_id": "INT-XXXXXXXXXXXX", "action": "open",
  "expected_revision": 0,
  "offer": "rwa_technical_sprint",
  "owner": "RWA commercial operator",
  "next_action": "Qualify asset, rights, mandate and jurisdiction",
  "due_date": "2026-11-18"
}
```

2. **Record accepted SOW** (after collecting a real signature outside the API):
```json
{
  "intake_id": "INT-XXXXXXXXXXXX", "action": "scope",
  "expected_revision": 1,
  "scope_ref": "SOW-RWA-0001",
  "acceptance_evidence": "https://your-private-document-repository.example.org/signed-sow"
}
```

3. **Reconcile live payment** (after the existing verified Stripe webhook records `cs_live_...`):
```json
{
  "intake_id": "INT-XXXXXXXXXXXX", "action": "reconcile_payment",
  "expected_revision": 2,
  "session_id": "cs_live_XXXXXXXXXXXX"
}
```

4. **Start delivery** after payment confirmation, with an owner and real work assignment:
```json
{"intake_id":"INT-XXXXXXXXXXXX","action":"start_delivery","expected_revision":3}
```

5. **Record accepted delivery** (not just project creation):
```json
{
  "intake_id":"INT-XXXXXXXXXXXX","action":"deliver","expected_revision":4,
  "delivery_evidence":"https://your-authorized-proof-host.example.org/report",
  "acceptance_url":"https://your-authorized-proof-host.example.org/customer-acceptance"
}
```

The endpoint rejects placeholder/example evidence hosts; example JSON is instructional, not a valid live submission.

## Fieldwork and Company OS operating link

Fieldwork's existing CRM project identities include **Noetfield** and **RWA Clinic**, and the source-backed network supports outreach attempts, replies, opportunities and next actions. Use Fieldwork for **research, contact verification and interaction history**. On a real customer conversion, pass only the canonical `intake_id` and approved source reference to Noetfield commercial operations. Do not duplicate contact details or make source-only claims of payment.

In Company OS, retain the existing lead→owner→task routing. A commercial case's `next_action` and `due_date` are accountable operator fields. The PII-free internal funnel readback provides receipt and delivery statuses; it is **not** a new public contact endpoint.

For RWA Clinic, reuse its existing 9+1 diagnostic and source case execution workflow rather than rebuilding a second scoring engine. A technical handoff occurs only when a real WorkPacket receipt is available; changing commercial status alone does not prove it.

## Acceptance evidence for production

- Existing public Intake persists a unique source `INT-` record and rejects synthetic test records for commercial conversion.
- Signed live Stripe event stored in `noetfield.commercial_payment_evidence`. Only signed events are captured; amounts, currency and fixed Payment Link must match.
- Exactly one Stripe Checkout Session binds to one source intake; retry and concurrency tests are meaningful.
- Real signed SOW and payer authorization if required.
- Real delivery and customer acceptance, with source citations/URLs.
- At least one actual customer payment and one delivered acceptance before claiming commercial activation.

### Known remaining external work

The first real buyer and signed SOW are external commercial events, not code test fixtures. A live Stripe Payment Link being active is **not** proof that a buyer paid. No RWA Clinic automation or Fieldwork sent outreach is claimed from an unverified integration.

Deployment is established only by verified Platform API runtime receipt or Railway deployment readback, not a green GitHub PR alone.
