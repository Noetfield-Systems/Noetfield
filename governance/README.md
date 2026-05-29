# Governance — Opinion Arbitration & Alignment

Canonical artifacts for **internal cognitive OS** (not public GTM).

| Path | Purpose |
|------|---------|
| `strategy-alignment-map.json` | Core brain file — principles, anti-patterns, OAS weights |
| `oas-engine/README.md` | OAS pipeline steps (claim → conflict → score → synth → ratify) |
| `alignment-scoring/README.md` | ASE formula reference |
| `golden-edge-synth/README.md` | Synthesis rules + link to runtime API |

**SOT documents (batch 020):**

- `noetfield-sot-master-document-v1` — layer hierarchy authority
- `noetfield-unified-cognitive-governance-system-v1` — full OAS spec

**Legal supremacy:** GCIP v4 (`docs/SOURCE_OF_TRUTH/`) overrides this tree on conflict.

**Runtime:** `POST /v3/evaluate`, `POST /v3/agent-loop` — `make api-v3` (port 8001)
