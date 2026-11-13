# Noetfield AEGIS — ISC readiness cockpit (Persian)

Dedicated, private, evidence-gated operational application for **EN578-24ISC4/100**. It is an internal estimate, **not a federal ISC assessment**. Scenario values 43/102/120 are analytical hypotheticals and do not seed real evidence.

## Run

Node 22+ (no third-party packages). Set `ADMIN_PASSWORD` (12+ characters), `SESSION_SECRET` (32+ chars), and `DATA_DIR` (persistent, writable path). `npm start`; visit `http://localhost:3000`. For Railway, mount a **persistent volume at `/data`**, set `DATA_DIR=/data`, and use one replica. `GET /api/health` is public; all data endpoints require a signed, HttpOnly, SameSite=Strict session.

## Evidence and score contract

- The **actual internal score** starts at 0/130 until manually reviewed, dated, linked, non-hypothetical evidence is registered and criterion scoring is assessed using allowed government score bins.
- Q3b requires reviewed benchmark evidence; Q1b is capped by reviewed A1–A4 coverage; Q7 requires signed documented availability; Q8's 20-point path requires directory evidence.
- Mandatory gates E1–E6, eligibility, TRL, innovation and state-of-the-art remain separate from the >=65 numerical threshold.
- Metadata links in `referenceEvidence` are **leads for verification** and never counted automatically.
- `status=reviewed` means reviewer-attested in the cockpit. No automatic file authenticity or independent third-party validation is implied.
- Every mutation is appended to audit and score-history. Export JSON and CSV; no personally identifying evidence is sent to external providers.
- This is a **single-admin pilot**. The owner labels track accountability; they are not multi-user sign-in accounts. One service replica with a mounted volume is required for durability.

## Scope & official sources

Official challenge: https://ised-isde.canada.ca/site/innovative-solutions-canada/en/artificial-intelligence-ai-decision-making-process-visibility-traceability-and-compliance-governance
Notice/amendments: https://canadabuys.canada.ca/en/tender-opportunities/tender-notice/cb-189-51083224
Deadline: 22 Dec 2026, 14:00 ET. Pass: 65/130 **and all mandatory criteria**. Government rules and amendments supersede this internal cockpit.

## QA

`npm test` tests evidence gating, scenario isolation, criterion scoring, team availability, and special Q8 conditions.