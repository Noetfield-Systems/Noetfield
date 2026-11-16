# Noetfield Corporate CRM — Operational v1

**Purpose:** A dedicated buyer and commercial relationship workspace for Noetfield Systems Inc., separate from the Web3-investor/builder contact database in Fieldwork.

**Access:** [Internal CRM](https://platform.noetfield.com/api/corporate-crm/app) on the existing Platform API. Access requires the existing authenticated Connect Desk operator session or server-side admin key. The HTML shell is non-indexable and contains no records. Source and financial data are fetched only from authenticated endpoints. The browser cookie is HttpOnly, Secure, SameSite=Strict, and session writes require an origin check and CSRF token. Seven-day persistent login is **opt-in**.

**DO NOT TOUCH** the founder-approved homepage V5 / PR #388 or copy Fieldwork's Web3 audience into Noetfield CRM. This implementation lives under the existing `platform.noetfield.com` runtime and PostgreSQL schema, not on `www.noetfield.com`.

## Domain model and commercial focus

| Record | Purpose | Source of truth | Action |
|---|---|---|---|
| Corporate account | Buyer, operator, asset originator, referral/delivery/capital partner, advisor | Dedicated `noetfield.corp_crm_accounts` table | Account profile and qualified owner |
| Corporate contact | Named stakeholder at a corporate account | `noetfield.corp_crm_people` | Contact role, source reference, marketing consent **false by default** |
| Corporate deal | Owned company opportunity in RWA, AI Sales OS, operations, asset administration or commercial partnership | `noetfield.corp_crm_deals` | Next action, deadline, offer, estimated value, stage, revision |
| Engagement evidence | Calls, sent outreach, replies, meetings, accepted scope, referrals and accepted delivery | `noetfield.corp_crm_activities` | Report external outcomes only with evidence URLs |
| Inbound request | Original customer submission | Existing `noetfield.public_intakes` | Import once by `INT-` source; never overwrite source or copy unrelated venture |
| Commercial contract | Scope approval, paid checkout, delivery acceptance | Existing `qualification_json.commercial_ops` and `noetfield.commercial_payment_evidence` | Existing six-stage state machine, no parallel billing |
| Actual money | Signed *live* Stripe paid Checkout bound to accepted scope and exact product | Existing verified Stripe ledger | Show paid Checkout evidence; do **not** conflate with forecast or settled cash |

**UI workspace:** Pipeline, Organizations, Contacts and Partners. Filterable deals, ownership, due follow-ups, deal detail, source-backed activity, directly recorded accepted scope, payment reconciliation, and delivery. The account and contact tables deliberately do not share Fieldwork person IDs, leads or outreach metrics.

## How first leads enter

- Noetfield Capital Intake on `www.noetfield.com/real-world-capital/` with `form_id=nfCapitalIntake` → RWA scope candidate.
- Noetfield Connect `form_id=nfConnectWizard`, `initiative=noetfield` and `category=business` → generic corporate operations lead; **do not automatically label it an AI Sales OS sale.**
- Noetfield Connect `category=partnership` → corporate partnership prospect.
- Explicit operator import by real persisted `INT-` for a verified corporate source.
- Manual research/prospects can be entered as accounts/deals. They are **not** represented as inbound customers or paid conversions.

Other venture `initiative` values and synthetic/E2E records are excluded from inbound import. Auto-import is source-ID idempotent and does not send a message, create a contract or take a payment.

## Customer-to-revenue sequence

1. **Lead and qualification:** account, contact, owner, offer classification and next follow-up. An operator can manually add a corporate prospect before receiving an inbound intake.
2. **Scope:** for an RWA sprint or AI Sales OS pilot, link the deal to a real Noetfield intake and call **Open commercial case**. Record an actual accepted written SOW reference and HTTPS acceptance evidence.
3. **Payment:** only at `SCOPE_ACCEPTED` does the CRM display the approved product-specific Stripe Payment Link. RWA technical sprint is US$950 with US$475 agreed deposit; AI Sales OS pilot is CAD $750. The URL is for operator use after a real accepted scope, not automatic billing.
4. **Reconciliation:** once Stripe sends a **verified signed live paid Checkout event**, link its real `cs_live_...` session through the protected CRM action. The backend checks the right account/payment link, exact amount/currency, source intake, scope evidence, payer identity/authorization and reversal flags.
5. **Delivery:** start a real RWA Clinic or Company OS workpacket via the existing product/runtime. Mark delivery accepted only with actual deliverable and customer acceptance evidence; the CRM does not falsely claim an automatic RWA Clinic execution.
6. **Growth:** record follow-ups, additional requests, referrals and retention work using accountable owners and evidence-backed activity logs.

## API endpoints (private Platform service)

- `GET /api/corporate-crm/app` — private-capable, noindex interface shell (contains no customer data)
- `GET /api/corporate-crm/board` — accounts, people, deals, next actions, global KPI/verified paid Checkout data (requires operator session)
- `POST /api/corporate-crm/accounts` — upsert/de-duplicate corporate organization
- `POST /api/corporate-crm/people` — create company contact with explicit marketing-consent state
- `POST /api/corporate-crm/deals` — record a corporate deal; intake-linked account/contacts must match the canonical source
- `POST /api/corporate-crm/import-intake` — explicitly import eligible source once
- `GET /api/corporate-crm/deals/{id}` — deal, timeline and commercial status
- `PATCH /api/corporate-crm/deals/{id}` — revision-checked stage, owner, dates, scope and forecast changes
- `POST /api/corporate-crm/deals/{id}/activities` — record reported or evidenced activity
- `POST /api/corporate-crm/deals/{id}/commercial` — operate real case via canonical accepted scope and payment ledger

## Separately retained

**Fieldwork:** Web3 community, investors, token/quest ecosystem, contributor/contact research and introductions for independent ventures. No automatic CRM merge, no copied private person records and no rewritten venture identity.

**Noetfield Corporate CRM:** Canadian SMEs, enterprise buyers, private-credit originators, asset sponsors, consultants, integrations and paying corporate clients. Reporting distinguishes operator-entered *estimated pipeline* from genuinely verified Stripe Checkout evidence.

**RWA Clinic:** existing 9+1 readiness and scoped project delivery platform. Corporate CRM is the commercial front-end, not a duplicate asset scoring or tokenization system.

## Operational safeguards and verification

- Real company PII stays in protected API and corporate tables. Never include contacts in public website, JavaScript HTML shell or Fieldwork exports.
- No client or partner message is automatically sent by CRM creation or stage updates.
- Intake records from E2E probes, other ventures or mismatched source organizations cannot become corporate paid leads.
- No automatic customer permission, financing approval, securities offering or invoice is inferred from an intake or portal.
- Paid totals are **global verified Checkout receipts**, independent of UI filters or limit, and never include reversed funds; not settlement/bank revenue.
- Admin session and CSRF guard apply to record modification.
- New partner introductions must be sourced, recorded and legally agreed before compensation.
- A failed read of the database produces an error, not fake empty successes.

## Measurable business experiment

Use the existing two bounded commercial offers concurrently:

- **Company OS:** 30 targeted, sourced SME contacts; qualify lead-to-follow-up automation pain and propose CAD $750 scope.
- **RWA:** 30 targeted, sourced asset/private-credit operators; assess ownership/rights/mandate and propose US$950 sprint with the US$475 scope-first deposit.
- Track real sent actions, replies, booked meetings, qualified SOWs, paid Checkout evidence, accepted delivery and second-order work. Never fill these stages with projections or fixtures.

**Release acceptance:** GitHub PR CI PASS; exact commit Railway Platform API deployment SUCCESS; authenticated CRM shell and API load; true DB schema initialization and first real-source import; homepage V5 SHA equal to PR #388 baseline. Live customers, paid orders and outbound messages must be independently evidenced before reporting them.
