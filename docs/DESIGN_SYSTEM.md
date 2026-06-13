# Noetfield design system (www)

Institutional dark + gold UI for public GTM surfaces. **Do not** change positioning copy or SKU count when editing styles.

**Canonical doc map:** [ops/DOCS_UNIFIED_MAP_LOCKED_v1.md](ops/DOCS_UNIFIED_MAP_LOCKED_v1.md) · **UI ladder:** [strategy/UI_TIER1_10_UPGRADES_v1.md](strategy/UI_TIER1_10_UPGRADES_v1.md)

## Stylesheet load order (June 2026 institutional frame)

```html
<link rel="stylesheet" href="/assets/noetfield-tokens.css" />
<link rel="stylesheet" href="/assets/noetfield-shell.css" />
<link rel="stylesheet" href="/assets/noetfield-components.css" />
<link rel="stylesheet" href="/assets/noetfield-institutional.css" />
<link rel="stylesheet" href="/assets/noetfield-sales.css" />
<link rel="stylesheet" href="/assets/noetfield-institutional-2026.css" />
<link rel="stylesheet" href="/assets/noetfield-institutional-grid.css" />
<link rel="stylesheet" href="/assets/noetfield-bank-grade.css" />
<link rel="stylesheet" href="/assets/noetfield-institutional-v4.css" />
```

Intake adds [`/assets/noetfield-intake.css`](/assets/noetfield-intake.css). FRFI lanes add `noetfield-frfi.css`.

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
| `.nf-trust` | Capability strip (legacy — removed from homepage v4) |
| `.nf-trust-hero` | Two-column hero + TLE receipt card (v4) |
| `.nf-tle-receipt-card` | Signed TLE preview beside hero |
| `.nf-framework-grid-v4` | Framework orientation above fold |
| `.nf-hero-actions--primary` | Max 2 hero CTAs |
| `.nf-hero-links` | Secondary product entry links |
| `.nf-offerings` | Three SKU cards |
| `.nf-cta-band` | Primary CTA footer on page |
| `.nf-section` | Generic content block |
| `.nf-framework-grid` | Trust center framework cards (benchmark UI) |
| `.nf-msp-tier` | MSP two-tier model cards |
| `.nf-compare-table` | TLE / federal mapping tables |
| `.nf-api-table` | `/docs/api/` routes |
| `.nf-status-panel` | `/status/` |
| `.nf-prose` | Legal / long-form |

June 2026 frame: v4 [`noetfield-institutional-v4.css`](/assets/noetfield-institutional-v4.css) · verify: `scripts/verify-ui-visual-e2e.sh` · plans: [INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md](strategy/INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md) · [INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md](strategy/INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md) · [UI_TIER1_10_UPGRADES_v1.md](strategy/UI_TIER1_10_UPGRADES_v1.md)

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
