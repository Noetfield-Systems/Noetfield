# L1 — Execution Core (Running System)

| Component | Location |
|-----------|----------|
| FastAPI governance API | `services/governance/` |
| Golden Edge v3 | `noetfield_governance/golden_edge_v3.py` |
| Event bus + ledger | `services/events/`, `services/ledger/` |
| Workflow / graph / inspectors | `services/workflow/`, `services/graph/`, `services/inspectors/` |
| Copilot governance demo | `services/copilot-governance/` |
| App shells (deferred UI) | `apps/web`, `apps/platform`, `apps/admin` |
| Infrastructure | `infrastructure/docker/`, `infrastructure/supabase/migrations/` |

**Run API:** `make api` (default) or `make api-v3` (port 8001)

Must obey L0. No strategic ideology in L1 code paths.
