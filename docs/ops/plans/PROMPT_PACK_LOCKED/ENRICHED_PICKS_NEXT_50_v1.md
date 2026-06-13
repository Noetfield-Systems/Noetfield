# Enriched prompt picks — next 50 (unified 500)

**Status:** Human + agent pick list — success-model ordered  
**Path:** `docs/ops/plans/PROMPT_PACK_LOCKED/ENRICHED_PICKS_NEXT_50_v1.md`  
**Machine index:** [unified_500_index.json](./unified_500_index.json)

**Pick rule:** ≤3 per `PLAN WITH NO ASF` iter · S0 first · skip rows marked **shipped**.

---

## Wave A — S0 proof (customer #1)

| # | ID | FQ | Plan | Enriched prompt (abbrev) |
|---|-----|-----|------|--------------------------|
| A1 | ship-fwd-170 | 111 | Playwright smoke suite | Add Playwright to verify-ui-e2e; retain traces on failure; routes: `/`, `/copilot/demo/`, `/trust-center/` |
| A2 | ship-fwd-474 | 415 | `make partner-demo-url` | MSP demo URL artifact in partner pack; verify plan-with-no-asf |
| A3 | ship-fwd-520 | 461 | `make partner-verify` | Partner pytest smoke subset for MSP technical enablement |
| A4 | ship-fwd-091 | 032 | QuickScan rubric v2 | 5-dimension readiness score on `/copilot/quickscan/` when revived |
| A5 | ship-fwd-139 | 080 | `make demo-url` CI | Stable demo URL in CI artifact for outreach handoff |

## Wave B — S6 TLE wedge (procurement)

| # | ID | FQ | Plan |
|---|-----|-----|------|
| B1 | ship-fwd-078 | 019 | TLE export OSFI field template |
| B2 | ship-fwd-290 | 231 | TLE schema v1.3 diff doc |
| B3 | ship-fwd-493 | 434 | `partner_name` on TLE export |
| B4 | ship-fwd-490 | 431 | White-label board PDF header v2 |

## Wave C — S2 Copilot complement

| # | ID | FQ | Plan |
|---|-----|-----|------|
| C1 | ship-fwd-060 | 001 | Agent 365 complement one-pager |
| C2 | ship-fwd-061 | 002 | Purview parity checklist |
| C3 | ship-fwd-064 | 005 | `/copilot/governance/` Agent 365 section |
| C4 | ship-fwd-515 | 456 | Agent 365 Step 5 client worksheet |

## Wave D — S4 Trust UI

| # | ID | FQ | Plan |
|---|-----|-----|------|
| D1 | ship-fwd-160 | 101 | Trust center diligence posture (**shipped** — extend framework rows) |
| D2 | ship-fwd-219 | 160 | Procurement verify hardening |
| D3 | ship-fwd-529 | 470 | Trust center partner row |

## Wave E — S3 MSP channel (v5 batch entry)

| # | ID | FQ | Plan |
|---|-----|-----|------|
| E1 | ship-fwd-460 | 401 | MSP enablement kit v3 (**partial** — `/partners/msp/` shipped) |
| E2 | ship-fwd-470 | 411 | 90-day pilot SOW template v2 |
| E3 | ship-fwd-471 | 412 | Activation dashboard spec |
| E4 | ship-fwd-490 | 431 | White-label board PDF |

## Wave F — S5 Federal (F lane only)

| # | ID | FQ | Plan |
|---|-----|-----|------|
| F1 | ship-fwd-360 | 301 | `/federal/` landing (**shipped** — extend AIA table) |
| F2 | ship-fwd-370 | 311 | FedRAMP orientation fence doc |
| F3 | ship-fwd-380 | 321 | NIST AI RMF federal annex |

## Wave G — S7 hardening (after proof)

| # | ID | FQ | Plan |
|---|-----|-----|------|
| G1 | ship-fwd-550 | 491 | Forward queue v5 coherence gate |
| G2 | ship-fwd-552 | 493 | SSOT_INDEX v5 MSP link |
| G3 | ship-fwd-558 | 499 | 500-plan master index one-pager |

---

## Copy-paste agent prompt (template)

```
PLAN WITH NO ASF — pick ≤3 from ENRICHED_PICKS_NEXT_50 Wave {A–G}.

For each task:
1. Read MEMORY_LOCKED + SUCCESS_MODEL_TIERS_v1 + lane doc
2. Branch cursor/{slug}-37f0
3. Implement outcome only — no scope creep
4. Run ./scripts/plan-with-no-asf-verify.sh
5. Update cursor-reply-latest.txt + GTM_NEXT shipped table
```

---

## Related

- [SUCCESS_MODEL_TIERS_v1.md](./SUCCESS_MODEL_TIERS_v1.md)
- [UNIFIED_500_MASTER_v1.md](./UNIFIED_500_MASTER_v1.md)
