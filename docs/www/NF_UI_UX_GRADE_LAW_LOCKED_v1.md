---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-07-27"
doc_id: nf-ui-ux-grade-law-locked-v1
---

> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-07-27

# NF UI/UX Grade Law — LOCKED v1

**Status:** LOCKED  
**Authority:** Founder order — high-grade UI/UX structural strategy  
**Machine SSOT:** `data/www-home-golden-baseline-v1.json`  
**Gate:** `bash scripts/verify-www-ui-grade.sh`

## One law

Compliance gates (language, SKUs, stamps, thin stubs) are not grade.  
A page may pass CI and still be raw. Grade is fail-closed.

## Golden baseline (corporate homepage)

**Binding class = PR #186 / restore #191:** Claude v2 content and IA + Codex corporate restyle.

| Must keep | Must not ship |
|---|---|
| `nf-corp` shell + `nf-corp-*` tokens | Bare P1 thin IA as a “fix” |
| Fonts: Inter + Newsreader + DM Mono | IBM Plex / random font swaps |
| `assets/noetfield-corporate-v1.css` + home-v2 preserving those tokens | New accent system without founder order |
| Sectioned narrative (problem → architecture → evidence → runways → commission → …) | “Calm / simplify / eye comfort” shrinks |
| Institutional CTAs (sentence case) | ALL-CAPS marketing buttons |

Pinned hashes and markers live in `data/www-home-golden-baseline-v1.json`.  
Visual fixtures: `tests/www/visual/home-golden/`.

## Three layers

### A — Design system freeze

Corporate www may only use locked tokens from:

- `assets/noetfield-corporate-v1.css`
- `assets/noetfield-home-v2.css` (only while preserving corporate tokens)

Forbidden without founder order: new font families, new accent systems, regenerating hubs in a way that drops home-v2 / nf-corp.

### B — Copy craft freeze

Machine-checkable:

- H1 length band (see baseline JSON)
- Hero lead length band
- Ban: em-dash spam, ALL-CAPS CTA labels, invitation copy, founder jargon (see language layers)
- Ban filler openers: `we help companies`, `we help businesses`
- Institutional verb presence on homepage body (govern / commission / inspect / bound / receipt / deterministic / authority)
- New factual claims still need claim→evidence / verdict matrix (existing www rule)

### C — Visual grade freeze

1. Structural probes against golden baseline (always on in CI)
2. Playwright screenshot diff when fixtures + browser available (`NF_WWW_VISUAL=1`)
3. Lighthouse / a11y are secondary — never a substitute for grade

## Agent workflow

1. Read this law + `NF_UI_BUILD_CHECKLIST_LOCKED_v1.md` + golden baseline JSON  
2. Propose **delta only** — no full-page rewrite unless founder ordered replace  
3. Self-grade: `bash scripts/verify-www-ui-grade.sh`  
4. Homepage / primary marketing: founder visual accept (screenshot compare) before merge  
5. Ship only if interactive fidelity + UI checklist + **grade gate** PASS  

### Hard bans

- Calm / simplify / eye-comfort refactors that shrink hierarchy  
- Restoring older thinner IA because validators were easier  
- Mixing compliance-only PRs (asset stamps, CI) with visual rewrite in one merge  

## Cheap-LLM customer landings (company-new)

Separate surface. Law:

1. Model returns JSON brief only (copy + palette + pack id)  
2. Deterministic template renders HTML  
3. Machine grades contrast, font allowlist, H1 length, structure  
4. Model revises failing brief fields only — never freeform HTML  
5. Publish fail-closed until grade PASS  

Sector style packs are template variants, not model-invented design systems.

## Related

- `docs/www/NF_UI_BUILD_CHECKLIST_LOCKED_v1.md`  
- `docs/DESIGN_REFERENCE_GOALS_LOCKED_v1.md` (R35 visual QA)  
- `.cursor/rules/nf-ui-ux-grade-law.mdc`  
- R-012 interactive anti-downgrade  

**Locked:** 2026-07-27
