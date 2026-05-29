# Golden Edge Synthesis

Produces the **maximum coherence system state** — not voting, not model preference.

Rules:

- Keep stability
- Minimize architectural entropy
- Preserve optionality
- Reduce system complexity

**Runtime (v3):** `services/governance/noetfield_governance/golden_edge_v3.py`

- `POST /v3/evaluate` — policy-only
- `POST /v3/agent-loop` — evaluate then execute unless REJECT

Start: `make api-v3` (port 8001)
