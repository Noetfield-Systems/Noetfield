# Wisdom pick rules — unified 500 v4

**Status:** LOCKED wise pick logic for cloud agents
**Use:** Read `prompt_wise` in index JSON before every implement

## The one rule

> Sort by **`wisdom_score`** descending among `open` rows.
> Pick ≤3 that span **proof-demo** + **proof-export** clusters when possible.
> Never outrun the 5-min board PDF moment.

## Wisdom score formula

| Component | Weight |
|-----------|--------|
| GTM impact | 38% |
| Goal alignment | 38% |
| Unlocks (buyer outcomes) | up to +20 |
| Effort S/M/L | +10 / +5 / 0 |
| Proof-chain position | up to +15 |
| Partial penalty | −25 |

## Pick clusters

| Cluster | Count | Wise use |
|---------|-------|----------|
| general | 190 | Evaluate case-by-case |
| msp-channel | 76 | MSP sprint only (M lane) |
| proof-export | 68 | Same iter or next — tamper, board pack, TLE export |
| federal-lane | 49 | Federal intake only (F lane) |
| copilot-registry | 46 | Design partner briefing — Agent 365 complement |
| proof-demo | 27 | Customer #1 iter — demo script, Playwright, QuickScan |
| ops-hardening | 26 | After proof ships |
| trust-diligence | 18 | Security questionnaire inbound |

## Sprint themes (founder pick one/week)

- **customer-1-proof-week** (avg wisdom 100): ship-fwd-097 · ship-fwd-109 · ship-fwd-124 · ship-fwd-170 · ship-fwd-260
- **copilot-story-week** (avg wisdom 88): ship-fwd-062 · ship-fwd-461 · ship-fwd-060 · ship-fwd-220 · ship-fwd-229
- **trust-diligence-week** (avg wisdom 72): ship-fwd-385 · ship-fwd-203 · ship-fwd-083 · ship-fwd-166 · ship-fwd-161
- **msp-enablement-week** (avg wisdom 87): ship-fwd-477 · ship-fwd-499 · ship-fwd-489 · ship-fwd-492 · ship-fwd-490
- **federal-intake-week** (avg wisdom 49): ship-fwd-401 · ship-fwd-373 · ship-fwd-374 · ship-fwd-412 · ship-fwd-395

## Next 3 (proof-chain wise)

1. **ship-fwd-097** wisdom 100 · proof-demo
   - WHY NOW: Directly enables customer #1 — buyer sees proof in <5 minutes.
   - DEFER IF: Do not pick if iter already has 2 S0 or 3× same cluster.

2. **ship-fwd-109** wisdom 100 · proof-export
   - WHY NOW: Closes procurement on receipt portability — TLE wedge.
   - DEFER IF: Do not pick if iter already has 2 S0 or 3× same cluster.

3. **ship-fwd-081** wisdom 95 · proof-export
   - WHY NOW: Closes procurement on receipt portability — TLE wedge.
   - DEFER IF: Do not pick if iter already has 2 S0 or 3× same cluster.

## prompt_wise template

Every plan has `prompt_wise` — one screen with WHY NOW + DEFER IF + UNLOCKS.

## Related

- [PICK_INTELLIGENCE_v1.md](./PICK_INTELLIGENCE_v1.md)
- [PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md](./PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md)
- [QUICK_PICK.md](../no-asf/QUICK_PICK.md)
