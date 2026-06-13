# Noetfield SME Provider Blueprint (LOCKED v1)

**Status:** LOCKED — high-grade SME governance provider model  
**Path:** `docs/architecture/NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md`  
**Updated:** 2026-06-12  
**Buyer:** CISO · GRC · M365 admin · procurement (Copilot governance)  
**Authority:** [NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md](../strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md) · [UNIFIED_ENGINE_COMMERCIAL_MODEL_LOCKED_v1.md](./UNIFIED_ENGINE_COMMERCIAL_MODEL_LOCKED_v1.md)

---

## 1. Provider identity

### One sentence (buyer)

> Noetfield is the **AI Governance & Evidence** provider for Microsoft 365 Copilot adoption — pre-execution policy, signed receipts, and export bundles your board and auditors can defend.

### Provider grade markers

| Marker | Noetfield delivers |
|--------|-------------------|
| **Pre-execution** | Evaluate intent **before** M365 or partner systems act |
| **BLOCK / ALLOW** | Invalid Copilot-adjacent changes blocked; allowed paths receipted |
| **Receipt spine** | TLE v1 signed go/no-go + confidence score |
| **Tamper FAIL** | Export integrity check fails on drift — diligence-safe |
| **Evidence index** | Purview · Entra · audit metadata (no content hoarding) |
| **Procurement-ready** | ZIP + board PDF + OpenAPI for technical reviewers |

### Hard negatives (SME copy law)

Per [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md): **no** payment rails · custody · settlement · FX · money transmission · credit-card infra · cloud deploy hero in W3.

---

## 2. Commercial package (W3)

### Design partner — primary wedge

| Field | Value |
|-------|-------|
| **Program** | 90-day design partner · Copilot governance sandbox |
| **Fee band** | CAD **$2K–$10K** (4–6 weeks typical) |
| **Buyer** | One referenceable org using board PDF in real governance meeting |
| **Deliverable** | Approved TLE + board pack PDF + optional procurement ZIP |
| **Intake** | `operations@noetfield.com` · [/copilot/pilot/](../../copilot/pilot/) |
| **SOW** | [DESIGN_PARTNER_SOW_OUTLINE.md](../../copilot/DESIGN_PARTNER_SOW_OUTLINE.md) |

### Three contract offerings (only)

| SKU | Price / type | SME fit |
|-----|--------------|---------|
| [Trust Brief](../../OFFERINGS_LOCKED.md) | $10,000 · 6 weeks | Diagnostic before Copilot scale |
| Copilot Governance Pack | Enterprise engagement | **Primary SME SKU** |
| Bank Pilot | Shadow simulation | Regulated shadow mode — no execution rights |

---

## 3. System architecture (Lane A — build in Noetfield)

Aligned with [NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md](../strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md) Lane A:

```
┌──────────────────────────────────────────────────────────────┐
│  BUYER WWW (noetfield.com/copilot/*)                         │
│  Demo · QuickScan · Pilot · Procurement                      │
├──────────────────────────────────────────────────────────────┤
│  GOVERNANCE CONSOLE (dev) / API (prod)                       │
│  Evaluate → RID → compliance log → TLE → export              │
├──────────────────────────────────────────────────────────────┤
│  TRUST LEDGER (TLE v1)                                       │
│  Signed digest · evidence index · board pack PDF             │
├──────────────────────────────────────────────────────────────┤
│  CONNECTORS (metadata)                                       │
│  Purview · Entra manifest · last_sync status                 │
├──────────────────────────────────────────────────────────────┤
│  POLICY + CONTROLS                                           │
│  Copilot control catalog · preflight · human-in-the-loop       │
└──────────────────────────────────────────────────────────────┘
         ▲ powered by portfolio engine (internal — not SKU)
```

### Module map

| Module | Spec source | Shipped evidence |
|--------|-------------|------------------|
| Policy + Control Registry | SME design § Compliance | [copilot-control-catalog.md](../spec/copilot-control-catalog.md) |
| Workflow lite | SME design § Operations | QuickScan → pilot checklist |
| Agent framework (guardrails) | SME design § AI | `/evaluate` · RID · review gates |
| Trust Ledger Bridge | TLE blueprint v1.2 | `audit_events` · `/api/v1/tle` |
| Knowledge / RAG | Phase 3.5+ | Evidence-first — block without source |
| Finance / payments | **Lane B/C — external** | **Not in Noetfield repo** |

---

## 4. SME buyer journey

| Stage | URL | Artifact | Owner |
|-------|-----|----------|-------|
| **Awareness** | `/` · `/copilot/` | Hero + trust strip | www |
| **QuickScan** | `/copilot/quickscan/*` | Self-assessment steps | www + runbook |
| **Demo** | `/copilot/demo/` | 5-minute rehearsal | NF-CLOUD verify |
| **Pilot** | `/copilot/pilot/` | Design partner SOW path | Founder + agentic send |
| **Procurement** | `/copilot/procurement/` | Diligence ZIP + controls | NF-CLOUD disk |
| **Technical** | `/docs/api/` · `/openapi.json` | HTTP contracts | services/governance |
| **Intake** | `operations@noetfield.com` | Unified inbox | Founder Hub |

Detail: [SME_BUYER_JOURNEY.md](../copilot/SME_BUYER_JOURNEY.md)

---

## 5. Governance execution flows

### Flow A — Copilot intent evaluation

1. User or agent submits operational intent (metadata envelope)  
2. Policy engine evaluates against control catalog  
3. **BLOCK** → reject + audit log + remediation tip (`operations@`)  
4. **ALLOW** → RID issued → TLE draft  
5. Human approval (if required) → signed TLE  
6. Export board pack / audit bundle  

### Flow B — Procurement diligence

1. Buyer opens `/copilot/procurement/`  
2. Reviews controls + OpenAPI link + trust-brief parity  
3. Downloads procurement pack  
4. Technical review on `/docs/api/`  
5. Contract via `operations@noetfield.com`  

### Flow C — Design partner (W3)

1. Agentic outreach as **Noetfield** (not engine brand)  
2. Demo URL + pipeline doc  
3. Founder Hub approves send  
4. Pilot SOW · CAD ≥2K  
5. 4–6 week sandbox · board PDF in governance meeting  
6. Reference + expand to Copilot Governance Pack  

---

## 6. Evidence & verify contract

| Check | Command |
|-------|---------|
| Full GTM + coherence | `./scripts/plan-with-no-asf-verify.sh` |
| Buyer links | `make verify-gtm` |
| TLE API | `./scripts/tle-smoke.sh --api` |
| Intake email lock | `python3 scripts/audit_intake_email.py` |
| Copilot E2E | `./scripts/copilot-pilot-e2e.sh` |

---

## 7. Dual-brand handoff

When deal includes TrustField delivery: [trustfield-noetfield-conflict-matrix.md](../spec/trustfield-noetfield-conflict-matrix.md)

> Noetfield = control layer (policy, evidence, allow/reject). TrustField = regulated-delivery layer. Separate SOW lines.

---

## 8. W3 agentic outreach (not NF-CLOUD send)

| Item | Disk (NF-CLOUD) | Execute (Hub) |
|------|-----------------|---------------|
| Pipeline copy | [DESIGN_PARTNER_PIPELINE_v1.md](../../copilot/DESIGN_PARTNER_PIPELINE_v1.md) | Agentic layer |
| Demo URL | `make demo-url` | Founder approve |
| CRM row | n8n · Apollo/HubSpot glue | Hub before send |
| ship-design-partner-outreach-026 | Listed in GTM_NEXT | **Agentic only** |

---

## 9. Roadmap fence (SME)

| Horizon | Ship |
|---------|------|
| **Now (W3)** | Design partner · demo film · procurement pack · TLE export |
| **Next** | QuickScan hardening · connector last_sync UX · SSO (post-revenue) |
| **Not W3** | Payment connectors · credit card · cloud deploy hero · engine SKU GTM |

---

## 10. Implementation pointer

When founder says **implement**: pick **one** Lane A task from [GTM_NEXT.md](../ops/plans/no-asf/GTM_NEXT.md) or `os/plan.json` `next_tasks`; verify PASS; update [ENGINEERING_DONE_MANIFEST.md](../ops/plans/PROMPT_PACK_LOCKED/ENGINEERING_DONE_MANIFEST.md).

**Do not** implement Lane B payment execution or promote internal engine docs to www without Form PICK + confidentiality review.
