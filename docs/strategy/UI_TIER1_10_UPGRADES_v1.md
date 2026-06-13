# UI tier-1 upgrades (10 big moves)

| Field | Value |
|-------|--------|
| Status | Strategy — post institutional v4 |
| Updated | 2026-06-12 |
| Parent | [INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md](./INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md) |

Ten upgrades to move www + console from institutional baseline to **world-class buyer credibility**. Archetypes SM-01–SM-10 only — no vendor names.

---

## P0 — ship first

### 1. Trust center as primary product surface (SM-01)
Rebuild `/trust-center/` with v4 trust hero + TLE receipt card + proof bar. Promote Trust center in primary nav.

### 2. Unified design system v5
Merge overlapping CSS into one token source shared by www and `governance-console/frontend`.

### 3. Playwright visual + journey regression
Screenshot baselines + 5 buyer journeys; wire into `plan-with-no-asf-verify.sh`.

---

## P1 — credibility depth

### 4. Continuous proof UI
`last_verified_at` timestamps; three-state badges (passing · needs attention · stale).

### 5. Persona-based buyer portals
CIO · CISO · Procurement · Board — tailored above-fold blocks on home/trust center.

### 6. Export integrity surfaces
ZIP checksum + tamper badge visible on procurement, TLE detail, trust center.

---

## P2 — enterprise table stakes

### 7. Subprocessor transparency table
Sortable vendor table with `last_updated` — GDPR/DORA diligence self-serve.

### 8. Console workflow wizards
Guided evaluate → pilot → procurement flows; unify `/console/` → `/cognitive-dashboard/`.

### 9. Print-grade board meeting mode
Wire `noetfield-print.css` to enterprise, bank-pilot, trust-center, TLE samples.

### 10. AI-readable trust profile
JSON-LD + public FAQ + gated doc request path — questionnaire deflection at scale.

---

## Success metric

Buyer can **see → trust → verify → export → defend** the TLE receipt in 90 seconds on any tier-1 surface.

**Regression:** `verify-ui-visual-e2e.sh` + future Playwright suite.
