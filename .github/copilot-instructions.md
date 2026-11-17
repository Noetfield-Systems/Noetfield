# Noetfield repo instructions

**P0 always active:** Before execution read `AGENTS.md` and `.cursor/rules/010-execution-first-alternatives.mdc`. A provider/tool outage triggers immediate search, selection and execution of an existing authorized alternative, not a report-only stop. Verify the real result, preserve the original mission and the evidence, and keep the Founder update brief.


- Operate in this repository only (`Noetfield-Systems/Noetfield`).
- Follow `repo-policy.json` and run `python3 scripts/check_repo_policy.py` after policy/config changes.
- Keep cross-repo coordination contract-based only (contracts, exports, manifests, APIs, receipts).
- Do not add active implementation work for TrustField, VIRLUX, noetfeld-os runtime, or studio-ide in this repo.
- Prefer safe, repo-local updates; preserve historical evidence documents unless a task explicitly asks to rewrite history.

## Forbidden active-config markers

The following legacy slug must not appear in active configuration (see `docs/FORBIDDEN_MARKERS.txt`):

- `kazemnezhadsina144[-]dot`
