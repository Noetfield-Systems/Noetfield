# NF Site Audit Machine — LOCKED v2

**Law:** Receipt-backed, role-lensed audit of `www.noetfield.com`. Deterministic on disk (L13). LLM checks emit proposals only — never auto-PASS.

**Registry:** `data/nf-site-audit-registry-v1.json`

---

## 0 — Run (every www ship pass)

```bash
make verify-site-audit          # disk crawl, P0 fail-closed
python3 scripts/nf_site_audit_v1.py --mode live --fail-on P0   # post-deploy (L4 runner)
```

---

## 1 — What it is

| Component | Path | Role |
|-----------|------|------|
| Crawler v2 | `scripts/site_audit/crawl.py` | sitemap + BFS (live) or ROUTE_INVENTORY (disk); HTML-only; SPA fallback + splat guards |
| Lenses v2 | `scripts/site_audit/lenses/noetfield-lenses-v1.json` | 8 role lenses merged with mechanical-gate v2 |
| Pricing SSOT | `scripts/site_audit/lenses/noetfield-pricing-table.json` | Canonical $ phrases + header partial golden sha |
| Auditor | `scripts/site_audit/audit.py` | Deterministic findings `{decision, reason, evidence, snapshot_sha}` |
| CLI | `scripts/nf_site_audit_v1.py` | `--mode disk|live`, receipt to `reports/www-audit/receipts/` |
| Gate | `scripts/verify-site-audit.sh` | CI/PR — **P0 fail-closed** |

---

## 2 — Lenses (v2)

- **render_integrity** — `{ENTITY}`, placeholder counters, lorem
- **buyer_founder** — mailto on money pages, price drift, CTA overload, stable CTA triad on homepage
- **enterprise_procurement** — entity consistency, legal pages
- **seo_machine** — h1, meta, og:image, orphans
- **nav_coherence** — max 2 nav fingerprints; header partial golden sha
- **deploy_integrity** — SPA fallback rows excluded; denylist paths never audited as HTML
- **receipt_hygiene** — no founder path leaks in HTML or receipts
- **investor_vc** — IV-3 LLM proposal only

**L5:** Agents may **add** checks via PR. Never weaken or delete a failing check.

---

## 3 — Receipt law

- Receipts live under `reports/www-audit/receipts/audit_<ts>.json` + `MANIFEST.json`
- Snapshots are **gitignored** (`reports/www-audit/snapshots/`)
- `crawl_root` in receipts never contains founder home paths
- PASS claims about **fixes** require re-run from a runner the fixing agent does not control (Railway cron or founder Mac), ≥60s after deploy

---

## 4 — Relationship to existing gates

| Gate | Site-audit adds |
|------|-----------------|
| `verify-static-www.sh` | Cross-page entity, render leaks, SEO meta, CTA discipline |
| `check_noetfield_com_e2e.py` | Receipt evidence + snapshot sha; live crawl complements route smoke |
| `verify-ui-build-checklist` | Step 9 — disk site-audit P0 |

---

## 5 — Autorun (registry-only until Railway cron wired)

Weekly live crawl → receipt PR → Telegram on **new P0**. Bootstrap: 2 consecutive cron-fired runs + 24h zero-manual window before VERIFIED.

---

**Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-07-06
