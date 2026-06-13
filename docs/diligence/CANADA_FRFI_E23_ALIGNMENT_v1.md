# Canada FRFI — OSFI E-23 alignment (orientation)

**Use:** Internal diligence and bank committee prep. Not legal advice. Founder attest before external claims.

---

## Scope

| Framework | Noetfield role | Buyer action |
|-----------|----------------|--------------|
| **OSFI Guideline E-23** (effective May 1, 2027) | Governance evidence layer — model inventory fields, RID lineage, TLE export | FRFI owns model risk management program |
| **Bank of Canada RPAA** (2026 retail payments supervision) | **Out of scope** for Noetfield — PSP/MSB execution via licensed partners (e.g. TrustField) | FRFIs generally excluded from RPAA retail payments perimeter |
| **Microsoft Agent 365 / Copilot** | Complement — pre-execution evaluate before M365 acts | Platform policy + Noetfield receipt |

---

## E-23 mapping (starter)

| E-23 expectation | Noetfield artifact |
|------------------|-------------------|
| Model inventory metadata | TLE cover sheet — model ID, risk tier, owner (optional fields) |
| Third-party / vendor AI | Vendor evidence pack — `GET /api/v1/governance/vendor-evidence` |
| Lifecycle governance | Shadow evaluate → enforce when policy owners sign off |
| Audit trail | `GET /api/v1/governance/audit-export` by RID |
| Board / committee pack | Board pack PDF + procurement ZIP from Trust Ledger |

---

## Regulatory fences (www-safe)

- Noetfield is **not** a payment service provider, custodian, or RPAA-regulated entity.
- Bank Pilot is **read-only shadow simulation** — no execution rights, no payment rails.
- Do **not** claim Bank of Canada supervision, RPAA registration, or OSFI licensing on public www.

---

## Related artifacts

- [RPAA-safe positioning one-pager](./rpaa-positioning-onepager.md)
- [Bank Pilot demo](../BANK_PILOT_DEMO.md)
- Public surfaces: `/bank-pilot/`, `/enterprise/`, `/trust-center/`
