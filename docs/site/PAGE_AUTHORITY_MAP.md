# Page authority map

**Status:** URL → governing doc matrix  
**Updated:** 2026-06-12  
**Verify:** `make verify-gtm` · `./scripts/verify-gtm-ops-docs.sh`

---

## Matrix

| URL | Owns (one slice) | Governing doc(s) | Allowed claims | Intake |
|-----|------------------|------------------|----------------|--------|
| `/` | Brand home · three offerings · Copilot wedge | `PRODUCT_TRUTH`, `NOETFIELD_SME_PROVIDER_BLUEPRINT` | Governance execution · TLE · design partner | Trust Brief CTA |
| `/enterprise/` | Institutional PRS · three offerings | `public-surface-map`, `OFFERINGS_LOCKED` | CISO/CRO narrative | `operations@` |
| `/trust-brief/` | $10K diagnostic | `OFFERINGS_LOCKED` | 6-week engagement scope | `/trust-brief/intake/` |
| `/copilot/` | Copilot Governance Pack hero | `NOETFIELD_COPILOT_SME_*`, SME blueprint | M365 governance · evidence | `/copilot/pilot/` |
| `/copilot/demo/` | Full async demo | `DEMO_REHEARSAL_CHECKLIST` | Evaluate → TLE → export · no sales call | Link + trial |
| `/copilot/trial/` | Starter tier · trial | `PACKAGING_TIER_SANDBOX_LOCKED` | 14-day · 50 checks · dev sandbox | `/gate/intake/?vector=trial` |
| `/copilot/pilot/` | Sandbox · design partner | `DESIGN_PARTNER_*`, SME blueprint | Dev + production mode · CAD $2K–10K | `operations@` |
| `/copilot/procurement/` | Diligence pack | `PROCUREMENT_ONE_PAGER` | Controls · OpenAPI cite | `operations@` |
| `/copilot/quickscan/*` | Self-assessment | SME buyer journey | Readiness steps | Optional |
| `/copilot/readiness/` | Rollout checklist | `copilot-readiness-pilot-runbook` | Pre-pilot gates | Link |
| `/bank-pilot/` | Shadow simulation | `PILOT_OFFERING_PACKS` | Read-only · no execution | `operations@` |
| `/trust-ledger/` | Audit lineage brand | `TRUST_LEDGER_POSITIONING_*` | TLE concept · evidence | Link |
| `/console/` | Evaluation UI | `STRATEGIC_LOCK` § Golden Edge | RID · compliance log | No sales |
| `/workspace/` | TLE workspace pointer | TLE blueprint | Review · approve | Dev/demo |
| `/docs/api/` | HTTP contracts | `services/governance/README` | OpenAPI · routes | Technical |
| `/partners/` | Channel programs | `channel-outreach/*` | Canada timing | Partner intake |
| `/status/` | Health | ops | Uptime only | None |
| `/gate/intake/` | Intake router | `STRATEGIC_LOCK` § intake | Vector metadata | `operations@` |

---

## Forbidden on all www pages

- Portfolio engine / SourceA as product name  
- Payment initiation · custody · settlement · FX  
- Credit-card checkout · NO-CC infra  
- “Trust OS” / “Decision Cloud” as buyer SKU  
- TrustField implementation claims (handoff line only when needed)  

---

## Copilot procurement parity guards

Scripts assert these buyer pages stay aligned:

- `/copilot/procurement/` ↔ `docs/copilot/PROCUREMENT_ONE_PAGER.md`  
- Trust-brief links on hub · pilot · demo · procurement  
- `/openapi.json` reachable in gtm-ops verify (iter 19)

---

## Related

- [ACTIVE_SITE_POLICY.md](./ACTIVE_SITE_POLICY.md)  
- [SSOT_INDEX.md](../SSOT_INDEX.md)
