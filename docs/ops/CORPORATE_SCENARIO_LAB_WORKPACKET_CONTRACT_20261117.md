# Commercial Execution — Scenario Lab, WorkPacket Contract and Production Handoff v1

**Status:** Implemented operator training interface; real outbound/payment/execution remain independently verified.  
**Production UX:** [Corporate CRM](https://platform.noetfield.com/api/corporate-crm/app) → **Scenario Lab** at `/api/corporate-crm/scenario-lab` (requires operator session).  
**Document date:** 2026-11-17  
**Original commercial source:** `qualification_json.commercial_ops`, real accepted SOW, signed Stripe Checkout and approved customer membership.  
**Independent public clinical reference:** https://scan.noetfield.com/rwa-clinic/ — *Clinic v3 nine evaluated clinical gates, Gate 10 derived*.  
**Marketing company identity:** Noetfield Systems Inc., 7816 Windsor Street, Vancouver, BC V5X 4A8, Canada. Actual mailing address supplied by founder and set in Railway `CORPORATE_OUTREACH_MAILING_ADDRESS`.

## 1 · What the simulator implements and what it does not

Scenario Lab is an **isolated browser-memory case simulator** behind the existing operator authentication. It has two fully prefilled fictional cases, including original source, fictional contact, owner, qualifying need, offered price, editable scope, acceptance terms, evidence references, provider packet, verifier training receipt, customer acceptance and renewal. No mock record is written to public_intakes, corp_crm_*, Stripe payment_evidence, Company OS, RWA Clinic or Fieldwork. No email, charge or dispatch is executed by the case lab. It uses `DEMO-` records and `.invalid` emails and reports **$0 live verified cash**.

**Separate accounting:** `SOURCE_RESEARCH ≠ VERIFIED_RECIPIENT ≠ SMTP_PROVIDER_ACCEPTED ≠ REPLIED ≠ MEETING ≠ ACCEPTED_SCOPE ≠ PAID_LIVE ≠ WORKPACKET_ACKNOWLEDGED ≠ INDEPENDENT_VERIFIED ≠ CUSTOMER_ACCEPTED ≠ BANK_SETTLED`.

## 2 · Fictional RWA Technical Sprint

**Buyer:** HarborBridge Private Credit Ltd. (fictional); Maya Bennett, investment operations lead (fictional, reserved `.invalid` email).  
**Example asset:** CAD 2.4m receivables pool; BC, Canada; SPV formation proposed.  
**Product code:** `rwa_technical_sprint`; fixed SOW total **US$950**; initial charge **US$475** only *after written acceptance* of the actual scope.  
**Authorized product:** technical readiness, evidence register, controls mapping, potential off-chain workflow, prioritized remediation backlog. **Not** token issuance, transfer of securities, financing, legal opinion or investment eligibility.

**Clinic v3 training fields prefilled:** issuer, jurisdiction, asset value, investor type, structure, yield bps, frequency, ledger choice/rationale; loan/security/appraisal evidence lifecycle and digest; borrower/SPV lifecycle, legal name, registration, articles; cashflow/coverage/terms; counsel status and instrument question; custody/servicing and their documents; transfer/recovery/risk-register and external reviews JSON. Status values follow not_submitted/submitted/under_review/verified vocabulary where applicable.

**Clinical rule:** the actual Clinic server evaluates nine clinical checks and derives Gate 10. The Lab's separate *illustrative* nine-gate checkbox score is a training checklist only and must never be presented as the Clinic's official verdict. Real Clinic may return DO NOT TOKENIZE; this is a legitimate completed diagnostic outcome.

**Example SOW and acceptance:** Deliver a technical readiness matrix, evidence gaps and an engineering remediation roadmap; customer acceptance is against those explicitly agreed deliverables. The simulated signature is `[NOT SIGNED]` and generated evidence is `DEMO-`, not an HTTPS legal receipt.

## 3 · Fictional Company OS AI Sales pilot

**Buyer:** Northshore Service Operations Ltd. (fictional), 18-person operations service team; Jordan Patel, operations director (fictional).  
**Product code:** `ai_sales_os_pilot`; fixed pilot **C$750** paid after accepted written SOW.  
**Input:** estimated 75 inbound inquiries per month, web form + shared Gmail + Sheets.  
**Outcome:** source-bound lead intake, one CRM opportunity per real authorized inquiry, owner assignment, next-action queue, provider-visible email drafts, duplicate prevention, deterministic fallback, weekly evidence-only report. No unsolicited outbound; no guarantees of booked meetings or sales.

**Simulated positive case:** one authorized inquiry is assigned to an actual owner and receives a follow-up due date. **Negative cases:** repeated lead doesn't generate a second opportunity; a contact without permission cannot be emailed; failed runtime/provider produces visible UNCONFIRMED, not false SUCCESS.  
**Handoff output:** live code task/run ID and acceptance tests only when Company OS provides a real receipt; a simulated checklist is not live execution.

## 4 · Authoritative live contract — source to payment to WorkPacket

Source workflow (already implemented in `Noetfield` Platform):

1. Original Noetfield `INT-[A-Z0-9]{12}` persists under `noetfield.public_intakes`; reject other-venture and synthetic test intakes from production deals.
2. Operator qualifies real buyer and links one commercial deal and accepted SOW/acceptance evidence.
3. Real Noetfield Stripe webhook `checkout.session.completed` or `checkout.session.async_payment_succeeded` is HMAC-verified and persisted. Bind only exact Payment Link, livemode, expected amount/currency, customer authorization and original intake. Refund/dispute reverses payment eligibility.
4. `POST /api/corporate-crm/workpackets/admit` creates one source-scoped WorkPacket per real paid deal.
5. `POST /api/corporate-crm/workpackets/dispatch` attempts provider dispatch only if a real endpoint and credential are configured.
6. Receiver returns a **real** ACK: `{status:"ACCEPTED",source_intake_id,engine,workpacket_id,provider_receipt_url}`. HTTP timeout or unknown body becomes DISPATCH_UNCONFIRMED, never ACKNOWLEDGED.
7. An independent Verifier reports via `POST /api/corporate-crm/workpackets/verifier-result`, signing raw JSON with configured HMAC SHA-256 secret in `X-Noetfield-Verifier-Signature`; payload source, provider event, external workpacket and payment must all match. `VERIFIED` requires a real artifact URL, verifier receipt URL and cost.
8. Actual Google-authenticated customer sees only their explicitly authorized deal and clicks Accept verified deliverable. Only then may the canonical commercial ledger permit DELIVERED and CLOSED. Old intake-level and CRM-level routes now share this requirement.
9. Record follow-up, renewal opportunity and independently evidenced client referral. Never use simulated receipts in real ledger.

### Provider receiver request (production format, not a mock execution)

```json
{
  "idempotency_key": "<actual UUID from paid corporate workpacket>",
  "source_intake_id": "<real INT- identifier>",
  "scope_ref": "<real accepted written SOW ref>",
  "payment_event_id": "<actual Stripe event id already bound>",
  "engine": "COMPANY_OS",
  "requested_work": "Perform accepted, paid, narrowly scoped commercial deliverable"
}
```

Other supported engine: `RWA_CLINIC`. Headers: `Authorization: Bearer <private scoped dispatch token>`, `Idempotency-Key: <same actual UUID>`. Use an allowlisted HTTPS receiver. No `DEMO-` ID is admissible to this path. Receiver must verify the trusted origin, preserve idempotency, persist its actual work assignment, and only return ACCEPTED after that durable admission. It does **not** claim the worker finished.

### Production configuration contracts

On the existing Platform API service:
- `CORPORATE_OUTREACH_MAILING_ADDRESS`: **configured** from founder-provided corporate address.
- `GMAIL_MAILBOX`, `GMAIL_APP_PASSWORD`: previously available; real send only to qualified eligible recipient, with opt-out handling.
- `CORPORATE_WORKPACKET_DISPATCH_TOKEN`: private shared secret with actual receiver; must not be invented.
- `CORPORATE_COMPANY_OS_WORKPACKET_URL`: exact real Company OS receiver route; not yet verified.
- `CORPORATE_RWA_CLINIC_WORKPACKET_URL`: exact real RWA Clinic receiver route; not yet verified.
- `CORPORATE_WORKPACKET_VERIFIER_SECRET`: separate independent verifier secret; must correspond to actual external verifier signer. No hardcoded key in repository.

**Observed services** in Railway: production `business-os-core` on `business-os-core-production.up.railway.app`, private source repo `Noetfield-Systems/noetfeld-os`; `verification-layer-api` on `verify.noetfield.com`; public Clinic UI `scan.noetfield.com/rwa-clinic/`. Their mere presence does not prove compatible POST WorkPacket endpoints, signed callbacks or a customer execution. The receiver source repository is not accessible through this session's GitHub installation. Do **not** configure a guessed URL or make Platform claim a real accepted job.

## 5 · Acceptance matrix for executable integration

| Check | Training lab | Production proof required |
|---|---|---|
| Source intake | Fictional fields complete | Genuine source accepted into canonical intake |
| Scope | Editable SOW draft | Signed accepted SOW linked to real customer |
| Payment | DEMO Checkout case only | Noetfield live Stripe-signed paid event and source binding |
| Dispatch | DEMO WorkPacket sample | Actual receiving service ACK with durable external ID |
| Execution | Fictional delivery plan | Worker run, cost and artifact with provider trace |
| Verification | Unsigned DEMO receipt | Independently HMAC-signed receipt and artifact check |
| Customer acceptance | Simulated click | Authorized real buyer's authenticated action |
| Retention | Follow-up template | Actual follow-up evidence and next commercial action |

**Hard rule:** a case study is useful for learning and the sales demonstration, but must never be counted in paid conversions, meetings, outreach, verified artifacts or customer acceptance.

## 6 · Immediate operational sequence

1. Open CRM → Scenario Lab, complete both cases, export JSON and copy fictional contracts.
2. Verify actual official Clinic's own v3 example case against its server-evaluated nine gates (Lab score remains clearly marked illustrative).
3. Implement one compatible WorkPacket receiver in the real Company OS repository, with a distinct worker execution receipt and independent verifier signature; reuse its actual data store.
4. Bind exact production URL and private token on both ends; replay test same idempotency key and reject wrong source/payment.
5. Repeat for actual RWA Clinic worker/receipts, retaining its existing 9+1 diagnostic engine.
6. Move one genuine externally accepted SOW through live paid Stripe → worker → Verifier → buyer acceptance → renewal; capture receipts in Issues #401–403. Never mutate production cash using demo events.

**Repository workflow:** Tests in `tests/unit/test_commercial_scenario_lab.py` check private auth, HTML/noindex, Node JS parse, fictional document generation and absence of browser network/payment side effects.
