# SME buyer journey — Copilot Governance Pack

**Status:** GTM funnel reference  
**Updated:** 2026-06-12  
**Blueprint:** [NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md](../architecture/NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md)

---

## Journey map

```
Awareness → QuickScan → Demo → Pilot → Procurement → Contract
    /          quickscan/*   demo    pilot    procurement   operations@
 /copilot/
```

---

## Stage 1 — Awareness

| Field | Value |
|-------|-------|
| **URLs** | `/`, `/copilot/`, `/enterprise/` |
| **Message** | Audit trail your Copilot deployment will be asked for later |
| **Proof strip** | TLE v1 · Evidence index · Board export · Design partner |
| **CTA** | Demo · Pilot · Procurement |

---

## Stage 2 — QuickScan (self-qualify)

| Field | Value |
|-------|-------|
| **URLs** | `/copilot/quickscan/`, step pages |
| **Buyer** | IT / GRC lead assessing Copilot readiness |
| **Outcome** | Gap list → readiness checklist |
| **Runbook** | [copilot-readiness-pilot-runbook.md](../spec/copilot-readiness-pilot-runbook.md) |

---

## Stage 3 — Demo (5 minutes)

| Field | Value |
|-------|-------|
| **URL** | `/copilot/demo/` |
| **Flow** | Submit intent → evaluate → RID → TLE preview → export mention |
| **Rehearsal** | [DEMO_REHEARSAL_CHECKLIST_v1.md](../ops/DEMO_REHEARSAL_CHECKLIST_v1.md) |
| **Verify** | `make verify-gtm` before buyer call |

**Say:** “Invalid changes blocked; allowed changes receipted; export tamper-check fails on drift.”

---

## Stage 4 — Design partner pilot (W3 revenue)

| Field | Value |
|-------|-------|
| **URL** | `/copilot/pilot/` |
| **Fee** | CAD $2K–$10K · 4–6 weeks |
| **Success** | Board PDF used in real governance meeting |
| **Artifacts** | [DESIGN_PARTNER_SOW_OUTLINE.md](./DESIGN_PARTNER_SOW_OUTLINE.md) · [DESIGN_PARTNER_PIPELINE_v1.md](./DESIGN_PARTNER_PIPELINE_v1.md) |
| **Outreach** | Agentic layer · Hub approve · **not** NF-CLOUD send |

---

## Stage 5 — Procurement diligence

| Field | Value |
|-------|-------|
| **URL** | `/copilot/procurement/` |
| **Buyer** | Procurement · legal · security reviewer |
| **Pack** | Controls · OpenAPI · trust-brief links · ZIP |
| **Doc** | [PROCUREMENT_ONE_PAGER.md](./PROCUREMENT_ONE_PAGER.md) |
| **Technical** | `/docs/api/` · `/openapi.json` |

---

## Stage 6 — Contract & expand

| Field | Value |
|-------|-------|
| **Intake** | `operations@noetfield.com` |
| **SKUs** | Trust Brief ($10K) · Copilot Governance Pack · Bank Pilot shadow |
| **Expand** | Annual license post-pilot ([GO_FORWARD_NOW.md](../strategy/GO_FORWARD_NOW.md)) |

---

## Agentic vs NF-CLOUD

| Activity | Owner |
|----------|-------|
| Pipeline copy on disk | NF-CLOUD |
| Email / call / CRM send | Agentic + Hub |
| Demo URL evidence | NF-CLOUD (`make demo-url`) |
| SOW negotiation | Founder |

---

## Verify path

```bash
./scripts/plan-with-no-asf-verify.sh
make verify-gtm
./scripts/copilot-pilot-e2e.sh
```
