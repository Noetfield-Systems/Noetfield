# L0 Repo Graph Memory v1 — Noetfield

**Status:** ACTIVE — rolled out from the `sina-governance-SSOT` pilot. Custom
stdlib-only script: no deploy, no database, no LLM calls, no network (see that
repo's `docs/GRAPH_TOOL_DECISION_v1.md` for why Graphiti/Graphify were rejected).

## Why

Noetfield is large and sprawling (~90 top-level dirs — website routes + governance
layers, 1.5GB). Blind "understand the repo" / audit passes are prohibitively
expensive. This layer gives agents a compact, static subsystem + file + reference
map to query **before** opening files.

## Pieces

| Piece | Path |
|---|---|
| Graph builder | `scripts/build_repo_graph_v1.py` |
| Graph query | `scripts/query_repo_graph_v1.py` |
| Compact report (read first) | `graph-out/GRAPH_REPORT.md` |
| Full index (gitignored local cache) | `graph-out/graph_index_v1.json` |
| Verifier | `scripts/verify_l0_repo_graph_memory_v1.sh` |
| Broad-read gate | `AGENTS.md` (§ "L0 repo graph memory — broad-read gate") |

## Commands

```
python3 scripts/build_repo_graph_v1.py                 # build/refresh (~2s, zero-token)
python3 scripts/query_repo_graph_v1.py <subsystem|keyword>
bash scripts/verify_l0_repo_graph_memory_v1.sh         # PASS/FAIL receipt in receipts/
```

## Noetfield tuning (vs the other repos)

1. **Auto-discovered subsystems.** With ~90 top-level dirs a hardcoded list is
   fragile, so `SUBSYSTEM_DIRS` is auto-populated from the filesystem, excluding
   only build/dependency/cache noise (`node_modules`, `.next`, `dist`, `_archive`,
   `www-pages-dist`, `var`, `vendor`, `tmp`, `.vercel`, …). This **guarantees the
   library and memory are covered by construction:**
   - Library: `os/plan-library` (~2k files) + `L2-knowledge`
   - Memory: `.cursor/agent-memory/MEMORY_LOCKED.yaml`
   - Agent config: `.agents`
2. **Index gitignored.** ~4MB local cache; only the compact `GRAPH_REPORT.md` is
   committed. Rebuild once after a fresh clone.
3. **Symlink-hardened** builder (shared template with SourceA).
4. **Verifier** keyword check uses `README` (present repo-wide).

## Possible next improvement (not done)

Noetfield is a real JS/TS app; edges are currently best-effort path-string
references. Adding a JS/TS `import`/`require` parser (and `ast` for Python) would
produce a truer import graph here than in the docs/JSON-heavy SSOT repos. Deferred.

All paths are repo-relative; the tool indexes **this** clone
(`~/Desktop/Noetfield-Systems/Noetfield`), never an outside `~/Projects` copy.
