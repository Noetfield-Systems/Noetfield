# Unified Engine & Commercial Model (LOCKED v1)

**Status:** LOCKED — internal strategy + agent routing  
**Path:** `docs/architecture/UNIFIED_ENGINE_COMMERCIAL_MODEL_LOCKED_v1.md`  
**Updated:** 2026-06-12  
**Authority:** Founder strategy · aligns with portfolio SSOT meaning (not a buyer SKU)

**Related:** [SSOT_INDEX.md](../SSOT_INDEX.md) · [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) · [trustfield-noetfield-conflict-matrix.md](../spec/trustfield-noetfield-conflict-matrix.md)

---

## § External — buyer language (www-safe)

**Never say to buyers (W3):** “Buy our infra layer” · Trust OS · Decision Cloud · portfolio engine SKU · SourceA.

### What buyers buy

| Commercial front | Site | Buyer | Package |
|------------------|------|-------|---------|
| **Noetfield Systems** | noetfield.com | CISO · GRC · M365 · procurement | Design partner / pilot: **block + record + export** |
| **TrustField** | trustfield.ca | MSB · fintech · regulated ops | Regulated receipt / program wedge (separate brand) |

### Buyer one-liners

| Audience | Say |
|----------|-----|
| **Noetfield buyer** | “We govern Copilot execution — invalid changes blocked, allowed changes receipted, tamper fails on export.” |
| **TrustField buyer** | “Regulated AI actions with audit-grade receipts — FINTRAC-adjacent trail.” |
| **Investor / founder** | “A governed execution engine powers our commercial products; Noetfield is the first product on it.” |

### W3 economic signal

CAD **≥2K** design-partner bar flows through **Noetfield NF-001** (Copilot governance) or **TrustField TF-001** — not a separate engine SKU.

### Integration model (buyer-visible)

Noetfield packages **governance execution infrastructure**:

1. **Evaluate** operational intent against policy  
2. **Block or allow** before external systems execute  
3. **Record** signed Trust Ledger Entries (TLE v1)  
4. **Export** board-ready audit bundles — tamper-evident FAIL on drift  

Buyers sign SOW on **Noetfield offerings** ([OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md)). They do not license a separate “engine OS.”

---

## § Internal — portfolio architecture (founder / agent only)

```
┌─────────────────────────────────────────────────────────────┐
│  COMMERCIAL FRONTS (buyers see, pay for, sign SOW)          │
│  noetfield.com · trustfield.ca · Forge · AgentField…        │
├─────────────────────────────────────────────────────────────┤
│  PORTFOLIO ENGINE (L1) — BACKEND — NOT FOR SALE AS SKU      │
│  Pre-LLM gate · policy BLOCK/ALLOW · receipt spine ·          │
│  tamper FAIL · validators · one write path · agentic runtime │
│  (SourceA on founder Mac — sync → ops/private/, not www)    │
└─────────────────────────────────────────────────────────────┘
```

### One-line definition (locked meaning)

> Portfolio engine = infra layer · pre-LLM governance · execution spine · agentic runtime — **source and backend, not the frontend.**

### What the engine is NOT

| Wrong frame | Correct frame |
|-------------|-----------------|
| “Engine’s job is to make CAD 2K” | **Noetfield / TrustField** make the money; engine proves it works |
| “Sell engine to platform CTOs this month” | Stage 2+ embed/OEM; not W3 hero |
| “Engine is Layer 0 / Trust OS / buyer brand” | L1 motor — no public SKU, no pitch-deck hero |
| “Three equal products competing” | One engine · one primary earner (Noetfield) · one backup (TrustField) |

### Commercial company roles

| Company | Role now | Agentic outreach target |
|---------|----------|-------------------------|
| **Noetfield** | Primary earning company | CISO / GRC / M365 lists |
| **TrustField** | Second front — polish + MSB wedge | MSB / compliance buyers on trustfield.ca |
| **Engine (SourceA)** | Finish W1 film · write-path · validators | **No separate GTM** |

### Focus stack (two jobs max)

| Focus | Job |
|-------|-----|
| **A — One engine** | Gate · spine · validators · agentic runtime proof |
| **B — One earner (primary)** | Noetfield package · offer · sell · showcase on noetfield.com |
| **C — Second earner** | TrustField polish · same proof · different wedge |

**Result:** Live demo + deposit/LOI on **Noetfield** (or TrustField). Credibility flows **up** to the commercial brand.

### Apollo / HubSpot / n8n

CRM glue runs via **n8n**; **founder Hub approves before send**. NF-CLOUD maintains pipeline **copy on disk** only ([AGENTIC_COMMERCIAL_HANDOFF_v1.md](../ops/AGENTIC_COMMERCIAL_HANDOFF_v1.md)).

### Sync law

| Direction | Allowed |
|-----------|---------|
| SourceA → `ops/private/sourceA/` | Yes (founder Mac) |
| Noetfield repo → SourceA | **No** |
| LOCKED repo docs → www | Yes, via verify |
| Corpus → www without filter | **No** |

---

## § Agent routing

| Task type | Lane | Chat hint |
|-----------|------|-----------|
| SSOT / queue / closeout | P3 docs | `816a7476` |
| FastAPI / verify / ship | P4 runtime | `048e395e` |
| Form PICK | Form Office (Mac) | Human only |
| SHIP ecosystem law | Maintainer 2 | SourceA disk — not NF chat |

**NF-CLOUD:** `execution_authority: false` · draft picks only · bounded `implement` on `GTM_NEXT`.

---

## § Verification

- Buyer copy: `python3 scripts/audit_intake_email.py` · `make verify-gtm`  
- Agent coherence: `./scripts/plan-with-no-asf-verify.sh`  
- No payment-rail claims: [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) · [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md)
