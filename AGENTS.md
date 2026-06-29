# Noetfield Repo Agent Policy

This repo's agent boundary policy is machine-defined in `repo-policy.json` and verified by:

```bash
python3 scripts/check_repo_policy.py
```

## Repo-Policy Lane

- Use one lane per pass. Pick exactly one of the policy lanes in `repo-policy.json` before editing.
- Keep repo-owned work in this repo. Do not store active work for TrustField, VIRLUX, SourceA, SinaPromptOS, Noetfield OS, or Studio IDE here unless a repo-local contract/export/manifest explicitly says this repo owns that artifact.
- Cross-repo dependencies must use contracts, exports, manifests, APIs, or receipts. Do not call or depend on another repo's private scripts as this repo's execution path.
- Generated, evidence, receipt, backlog, and archive outputs must be represented by snapshots plus manifests or tracked receipts, not loose dirty files.
- Keep each pass to 20-40 changed files maximum and one coherent lane. Commit one atomic change per coherent lane when a commit is requested.
- Use high-intelligence/deep analysis for decisions and reviews. For bulk scanning, use deterministic validators and manifests first.

Authority sources used by this policy are listed in `repo-policy.json`; do not expand the policy from chat memory alone.
