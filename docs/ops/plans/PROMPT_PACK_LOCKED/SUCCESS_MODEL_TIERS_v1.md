# Success model tiers — prompt pack taxonomy (v1)

**Status:** LOCKED taxonomy for unified 500 + 1000 pack picks  
**Path:** `docs/ops/plans/PROMPT_PACK_LOCKED/SUCCESS_MODEL_TIERS_v1.md`  
**Parent:** [UNIFIED_500_MASTER_v1.md](./UNIFIED_500_MASTER_v1.md)

---

## Why this exists

The **1000 NF-PLAN registry** is fully synced (`done` = pattern dedup). The **500 forward queue** (FQ-001–500) is the live strategic backlog. This doc **re-tiers both** against the **benchmark success model** so agents pick proof-first work, not infra sprawl.

**Bottleneck (locked):** GTM validation 2/10 — pick **S0** before **S7**.

---

## Two axes

| Axis | Values | Meaning |
|------|--------|---------|
| **Success tier (S0–S8)** | Benchmark-aligned buyer outcome | What wins deals |
| **Execution lane (A/D/H/F/M)** | How work ships | A=disk · D=docs · H=Hub · F/M=ICP lock |

---

## Success tiers (priority order)

| Tier | Benchmark reference | Noetfield goal | Max picks / iter |
|------|---------------------|----------------|------------------|
| **S0-proof** | 5-min demo · board PDF | One contracted pilot uses TLE export in meeting | **2** |
| **S6-tle-wedge** | Veridra · ADJUDON · Audital | Procurement closes on receipt portability | 1 |
| **S2-copilot-complement** | Purview · Agent 365 · Inforcer | Registry-vs-receipt story on www | 1 |
| **S4-trust-ui** | OneTrust · Vanta · Drata | Trust center + framework grid diligence | 1 |
| **S1-positioning** | Credo · Holistic | Hero/copy refresh (Form PICK) | 0–1 |
| **S3-msp-channel** | AvePoint · Lighthouse | `/partners/msp/` + SOW attach | 0–1 |
| **S5-federal** | AIA · ADM · NIST | `/federal/` F lane only | 0–1 |
| **S7-hardening** | Engineering best practice | Coherence · openapi · pytest | after S0–S4 |
| **S8-agentic** | Hub commercial | Outreach send/call — **never NF-CLOUD** | Hub only |

**Rule:** `PLAN WITH NO ASF` picks **≤3** from **S0 → S6 → S2 → S4** first; never three S7 tasks in one iter.

---

## 1000-pack pattern → success tier map

| NF-PLAN pattern (×50 each) | Default success tier | Notes |
|----------------------------|---------------------|-------|
| `demo-rehearsal` | **S0-proof** | Highest GTM weight |
| `www-copy` | S1-positioning / S4-trust-ui | Split by area |
| `diligence-doc` | S4-trust-ui | Procurement |
| `customer-outreach` | **S8-agentic** | Hub only (R-011) |
| `buyer-debrief` | S0-proof | Post-meeting evidence |
| `smoke-script` | S0-proof | verify-ui-e2e family |
| `console-ui` | S0-proof | Workspace / evaluate |
| `openapi-sync` | S7-hardening | After demo path stable |
| `drift-impl` | S7-hardening | P9 / deferred |
| `performance` | S7-hardening | Tier B gate often |

---

## 500 forward queue → ICP batch

| Batch | FQ | ICP | Success tier bias |
|-------|-----|-----|-------------------|
| v1 | 001–100 | Mixed | S2 Copilot + S0 proof |
| v2 | 101–200 | Mixed upgraded | S4 trust + S6 TLE |
| v3 | 201–300 | Scale | S3 MSP seed + S7 hardening |
| v4 | 301–400 | **F only** | **S5 federal** |
| v5 | 401–500 | **M only** | **S3 MSP** |

---

## Enriched prompt template (copy-paste)

```
As NF-CLOUD-AGENT (Noetfield only), implement {ship-fwd-NNN} FQ-{NNN}:
{plan title}. Outcome: {outcome}. Success tier: {S0–S8}.
Read: MEMORY_LOCKED + INSTITUTIONAL_BENCHMARK_10_STEP_PLAN + {lane doc}.
Verify: {verify}. ≤3 tasks this iter. Update cursor-reply-latest.txt.
```

**F lane suffix:** `Read FEDERAL_AIA_ADM_NIST_v1 — no clearance/RPAA claims.`  
**M lane suffix:** `MSP channel only — no client billing through NF.`  
**H lane prefix:** `[AGENTIC Hub only]` — NF-CLOUD maintains copy only.

---

## Related

- [UNIFIED_500_MASTER_v1.md](./UNIFIED_500_MASTER_v1.md)
- [unified_500_index.json](./unified_500_index.json)
- [INSTITUTIONAL_BENCHMARK_10_STEP_PLAN_v1.md](../../strategy/INSTITUTIONAL_BENCHMARK_10_STEP_PLAN_v1.md)
