# Noetfield design system v5 (www + console)

Institutional dark + gold UI for public GTM surfaces and Governance Console. **Do not** change positioning copy or SKU count when editing styles.

## v5 stylesheet load order (GTM tier pages)

```html
<link rel="stylesheet" href="/assets/noetfield-tokens.css" />
<link rel="stylesheet" href="/assets/noetfield-shell.css" />
<link rel="stylesheet" href="/assets/noetfield-components.css" />
<link rel="stylesheet" href="/assets/noetfield-institutional.css" />
<link rel="stylesheet" href="/assets/noetfield-sales.css" />
<link rel="stylesheet" href="/assets/noetfield-institutional-2026.css" />
<link rel="stylesheet" href="/assets/noetfield-institutional-grid.css" /> <!-- grid pages -->
<link rel="stylesheet" href="/assets/noetfield-bank-grade.css" />
<link rel="stylesheet" href="/assets/noetfield-institutional-v4.css" />
```

**Body classes:** `nf-site-2026 nf-bank-grade nf-v4` (+ `nf-frfi` on enterprise / bank-pilot / federal).

**Automation:** `python3 scripts/apply_institutional_2026_frame.py` · verify: `./scripts/verify-ui-frame-parity.sh`

## v4 components (tier-1 UI)

| Class | Use |
|-------|-----|
| `.nf-trust-hero` | 2-col hero + TLE receipt card (homepage) |
| `.nf-tle-receipt-card` | Live receipt preview |
| `.nf-framework-grid-v4` | Framework orientation grid |
| `.nf-hero-actions--primary` | ≤2 hero CTAs |
| `.nf-hero-links` | Secondary text links under hero |
| `.nf-demo-stepper` | Async demo visual checklist |
| `.nf-checksum-badge` | Procurement ZIP integrity |
| `.nf-last-verified` | Trust center freshness |

Console mirrors tokens via `governance-console/frontend/tailwind.config.ts` (`accent`, `surface`).

---

## v3 baseline (legacy reference)

## Stylesheet load order

```html
<link rel="stylesheet" href="/assets/noetfield-tokens.css" />
<link rel="stylesheet" href="/assets/noetfield-shell.css" />
<link rel="stylesheet" href="/assets/noetfield-components.css" />
<link rel="stylesheet" href="/assets/noetfield-institutional.css" />
<link rel="stylesheet" href="/assets/noetfield-sales.css" />
```

Intake adds [`/assets/noetfield-intake.css`](/assets/noetfield-intake.css).

## Tokens

[`noetfield-tokens.css`](/assets/noetfield-tokens.css) — colors, `--font-sans`, `--font-serif`, spacing, `--section-y`, motion.

## Components

| Class | Use |
|-------|-----|
| `.nf-page` | Main content wrapper |
| `.nf-hero` | Page hero (eyebrow, H1 serif, lead) |
| `.nf-prs` / `.nf-prs-card` | Problem · Risk · Solution |
| `.nf-pipeline` | Block · Record · Export strip |
| `.nf-metrics` | Institutional metrics row |
| `.nf-trust` | Capability strip (home) |
| `.nf-offerings` | Three SKU cards |
| `.nf-cta-band` | Primary CTA footer on page |
| `.nf-section` | Generic content block |
| `.nf-framework-grid` | Trust center framework cards (benchmark UI) |
| `.nf-msp-tier` | MSP two-tier model cards |
| `.nf-compare-table` | TLE / federal mapping tables |
| `.nf-api-table` | `/docs/api/` routes |
| `.nf-status-panel` | `/status/` |
| `.nf-prose` | Legal / long-form |

June 2026 frame: [`noetfield-institutional-2026.css`](/assets/noetfield-institutional-2026.css) · institutional grid: [`noetfield-institutional-grid.css`](/assets/noetfield-institutional-grid.css) · bank-grade: [`noetfield-bank-grade.css`](/assets/noetfield-bank-grade.css) · plan: [INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md](strategy/INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md) · 100-plan: [INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md](strategy/INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md)

## Shell

- Header/footer: [`assets/partials/`](/assets/partials/)
- Loader: [`noetfield-shell.js`](/assets/noetfield-shell.js) v3 (`SHELL_VERSION`)

## Do not break

- Homepage: **governance evaluation** or **governance execution** in copy; no `pre-execution` on `/`
- All tier pages: `nfHeader`, `Request Governance Brief`, `noetfield-shell.css`
- Five nav items only; API in footer **Reference** column
- [`make verify-final-lock`](/Makefile) and [`scripts/audit_public_site_health.py`](/scripts/audit_public_site_health.py)

## Surface map

Page roles: [public-surface-map.md](strategy/public-surface-map.md)
