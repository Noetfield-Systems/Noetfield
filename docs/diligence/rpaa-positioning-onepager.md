<!-- ADVISOR_ARCHITECT_CHECKLIST_STUB (auto-inserted) -->
Advisor / Architect Minimal Checklist (AUTO-STUB)
-----------------------------------------------

- protects: Which founder goal does this protect? (pick one)
- sina_workload: reduces / increases + short rationale
- permission_loop: yes / no + explanation
- sandbox_autonomy: yes / no + where/how (sandbox lane path)
- target_to_blocker: yes / no + mitigation
- canon_version: (string)
- sandbox_evidence: link(s) to sandbox receipt(s)

# Noetfield — RPAA-safe positioning (diligence)

**Use:** Attach to bank / FRFI diligence folders. Do not paste payment-rail language on public www.

---

## What Noetfield is

- **Governance execution infrastructure** — evaluates operational intent **before** regulated execution layers act.
- **Shadow / enforce modes** for pilots; production pilots use documented `/api/v1/governance/*` only.

## What Noetfield is not

- Not a payment service provider, custodian, or money transmitter.
- Does not route funds, hold balances, or submit payment instructions.
- Does not replace bank core, treasury, or partner MSB execution systems.

## Regulatory framing (Canada)

- Positioned as **vendor / governance layer** adjacent to OSFI E-23 (model risk) readiness — not RPAA retail payment claims.
- Pilot artifacts: policy evaluation metadata, RID lineage, immutable audit export — see [sample-audit-export.redacted.json](./sample-audit-export.redacted.json).

## Evidence endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/governance/evaluate` | Policy decision on intent |
| `GET /api/v1/governance/audit-export` | RID-scoped compliance slice |
| `GET /api/v1/governance/vendor-evidence` | E-23 starter pack metadata |

## Contact

Engagement intake: [trust-brief intake](https://www.noetfield.com/trust-brief/intake/) · operations@noetfield.com
