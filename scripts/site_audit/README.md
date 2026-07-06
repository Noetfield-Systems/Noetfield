# Noetfield site-audit machine v2

Stdlib-only crawler + deterministic lenses + receipt writer for `www.noetfield.com`.

## Quick start

```bash
make verify-site-audit
python3 scripts/nf_site_audit_v1.py --mode live --root https://www.noetfield.com --fail-on P0
```

## Layout

- `crawl.py` — v2 crawler (HTML-only, SPA fallback, splat guard)
- `audit.py` — lens engine
- `lenses/noetfield-lenses-v1.json` — locked checks (L5 additive)
- `lenses/noetfield-pricing-table.json` — canonical pricing + header golden sha

Law: `docs/www/NF_SITE_AUDIT_MACHINE_LOCKED_v1.md`
