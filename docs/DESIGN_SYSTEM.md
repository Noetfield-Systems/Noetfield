<!-- ADVISOR_ARCHITECT_CHECKLIST_STUB (auto-inserted) -->
Advisor / Architect Minimal Checklist (AUTO-STUB)
-----------------------------------------------

- protects: Which founder goal does this protect? (pick one)
- sina_workload: reduces / increases + short rationale
- permission_loop: yes / no + explanation
- sandbox_autonomy: yes / no + where/how (sandbox lane path)
- target_to_blocker: yes / no + mitigation
- canon_version: (string)
- sandbox_evidence: link(s) to sandbox receipt(s)

# Noetfield design system v7 (www)

**Ground-up rebuild — one CSS, one generator, reference-grade layout.**

## Stack (only these three + optional intake)

```html
<link rel="stylesheet" href="/assets/noetfield-tokens.css" />
<link rel="stylesheet" href="/assets/noetfield-shell.css" />
<link rel="stylesheet" href="/assets/noetfield-www.css?v=7" />
<script src="/assets/noetfield-shell.js?v=7" defer></script>
<body class="nf-www">
```

Intake adds `noetfield-intake.css` only.

**Do not** load components, enterprise, institutional, or sales CSS on public pages.

## Regenerate + migrate everything

```bash
python3 scripts/rebuild-www-v6.py      # 20 GTM hub pages from zero
python3 scripts/migrate-all-public-www.py  # force remaining shell pages to v7
```

## Reference patterns

[DESIGN_REFERENCE_GOALS_LOCKED_v1.md](./DESIGN_REFERENCE_GOALS_LOCKED_v1.md) — receipt hero, honest scope, numbered sections, three SKUs.

## Live preview

`python3 -m http.server 13081` → http://127.0.0.1:13081/
