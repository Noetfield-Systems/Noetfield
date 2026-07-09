# Noetfield Repo Agent Policy

This repo's agent boundary policy is machine-defined in `repo-policy.json` and verified by:

```bash
python3 scripts/check_repo_policy.py
```

## L0 repo graph memory — broad-read gate

**Read before broad reads:** `graph-out/GRAPH_REPORT.md` · query: `python3 scripts/query_repo_graph_v1.py <term>` · design: `docs/L0_REPO_GRAPH_MEMORY_v1.md`

Do not spawn a broad "understand the repo", "map subsystem X", "architecture
review", or "audit Y" task (multi-agent or single-agent) by reading files
directly as the first step. This repo is large and sprawling (~90 subsystems
incl. the `os/plan-library` library, `L2-knowledge`, and `.cursor/agent-memory`).
First read `graph-out/GRAPH_REPORT.md` (compact subsystem map) and, for anything
it doesn't answer, run `python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>`
(bounded output, no full file reads). Only open — or delegate reading of — the
specific files the graph names as relevant. Token budget: orientation (the report
plus a few targeted queries) should cost a few thousand tokens, not the hundreds
of thousands a blind multi-agent understand pass costs. The full index is a local
cache (gitignored, ~4MB); if it is missing or stale, rebuild first with
`python3 scripts/build_repo_graph_v1.py` (~2s, zero-token) rather than a blind
read. Verify wiring: `bash scripts/verify_l0_repo_graph_memory_v1.sh`.

## Repo-Policy Lane

- Use one lane per pass. Pick exactly one of the policy lanes in `repo-policy.json` before editing.
- Keep repo-owned work in this repo. Do not store active work for TrustField, VIRLUX, SourceA, SinaPromptOS, Noetfield OS, or Studio IDE here unless a repo-local contract/export/manifest explicitly says this repo owns that artifact.
- Cross-repo dependencies must use contracts, exports, manifests, APIs, or receipts. Do not call or depend on another repo's private scripts as this repo's execution path.
- Generated, evidence, receipt, backlog, and archive outputs must be represented by snapshots plus manifests or tracked receipts, not loose dirty files.
- Keep each pass to 20-40 changed files maximum and one coherent lane. Commit one atomic change per coherent lane when a commit is requested.
- Use high-intelligence/deep analysis for decisions and reviews. For bulk scanning, use deterministic validators and manifests first.

Authority sources used by this policy are listed in `repo-policy.json`; do not expand the policy from chat memory alone.
