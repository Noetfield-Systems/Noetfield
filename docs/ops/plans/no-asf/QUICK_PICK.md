# PLAN WITH NO ASF — quick pick

When the founder says **PLAN WITH NO ASF**, start here. Pick the next **≤3 agent** items (not `asf_only` / not S8 Hub).

**v2 intelligence:** [PICK_INTELLIGENCE_v1.md](../PROMPT_PACK_LOCKED/PICK_INTELLIGENCE_v1.md) · **Unified 500:** [UNIFIED_500_MASTER_v1.md](../PROMPT_PACK_LOCKED/UNIFIED_500_MASTER_v1.md)  
**Tier taxonomy:** [SUCCESS_MODEL_TIERS_v1.md](../PROMPT_PACK_LOCKED/SUCCESS_MODEL_TIERS_v1.md)  
**Next 50 auto-ranked:** [ENRICHED_PICKS_NEXT_50_v1.md](../PROMPT_PACK_LOCKED/ENRICHED_PICKS_NEXT_50_v1.md)  
**Machine index:** [unified_500_index.json](../PROMPT_PACK_LOCKED/unified_500_index.json) (`prompt_structured` per plan)

**Regenerate:** `python3 scripts/generate_unified_prompt_pack_500.py`

## Wise pick order (v2)

1. Filter `ship_status: open` — skip `partial` unless extending a live slice
2. Sort `priority_rank` ascending (lower = sooner)
3. Max **2× S0** per iter · diversify tier · never 3× S7
4. Read `prompt_structured.pre_read` + obey `stop_if` before code

| Tier | Pick when |
|------|-----------|
| **S0-proof** | Customer #1 — demo · TLE · procurement |
| **S6-tle-wedge** | Receipt differentiation at procurement close |
| **S2-copilot** | Agent 365 / Purview complement story |
| **S4-trust-ui** | Diligence questionnaire inbound |
| **S3-msp / S5-federal** | Lane-locked only when ICP matches |

## Next 3 recommended (v2 computed — open rows)

| Priority | ID | FQ | Tier | GTM | Plan |
|----------|-----|-----|------|-----|------|
| 1 | ship-fwd-087 | 028 | S0 | 100 | Behavioral log export endpoint stub |
| 2 | ship-fwd-091 | 032 | S0 | 100 | QuickScan scoring rubric v2 |
| 3 | ship-fwd-081 | 022 | S6 | 88 | Tamper FAIL export verify hardening |

**Also high rank:** `ship-fwd-170` (Playwright smoke, S0 rank ~8) · `ship-fwd-520` (partner-verify, MSP)

## GTM_NEXT (disk verify — iter 19 carry)

1. **ship-procurement-openapi-verify-057** · `/openapi.json` 200 in gtm-ops bundle
2. **ship-services-governance-readme-openapi-058** · services/governance README OpenAPI path
3. **ship-tenth-audit-merge-rule-059** · tenth-audit manifest closeout template

## Agentic only — Hub (S8 — skip NF-CLOUD)

| ID | Outcome |
|----|---------|
| **ship-design-partner-outreach-026** | One named CIO + demo URL sent |

## Suggested iter bundle 1 (smart 3-pack)

See [UNIFIED_500_MASTER_v1.md](../PROMPT_PACK_LOCKED/UNIFIED_500_MASTER_v1.md) § Suggested iter bundles — proof-first diversified packs.

## Recently completed (context)

- v2 intelligence engine: weighted tiers · ship-aware · GTM impact scoring
- 440 open · 60 partial forward-queue rows (filesystem-aware)
- Institutional benchmark 10-step www + console pass (PR #54)
