# Noetfield documentation hub

**Start:** [LAWS/README.md](./LAWS/README.md) — current law stack (anti-drift entry point)

---

## Quick links

| I need… | Go to |
|---------|--------|
| **Current law (L0–L5)** | [LAWS/CURRENT_STACK_v2026.md](./LAWS/CURRENT_STACK_v2026.md) |
| **Routing (www + repo)** | [LAWS/ROUTING.md](./LAWS/ROUTING.md) |
| **Pipelines (verify, ingest, sync)** | [LAWS/PIPELINES.md](./LAWS/PIPELINES.md) |
| **Old / superseded versions** | [SOURCE_OF_TRUTH/archive/SUPERSESSION_INDEX.md](./SOURCE_OF_TRUTH/archive/SUPERSESSION_INDEX.md) |
| **Developer setup** | [DEVELOPER_BOOTSTRAP.md](./DEVELOPER_BOOTSTRAP.md) |
| **Upload corpus (canonical)** | [SOURCE_OF_TRUTH/uploaded/](./SOURCE_OF_TRUTH/uploaded/) |
| **Registry (machine SSOT)** | [SOURCE_OF_TRUTH/registry/](./SOURCE_OF_TRUTH/registry/) |
| **Investor diligence** | [strategy/INVESTOR_GOVERNANCE_LANE_LOCKED_v1.md](./strategy/INVESTOR_GOVERNANCE_LANE_LOCKED_v1.md) |
| **Commercial agentic UI** | [strategy/COMMERCIAL_AGENTIC_UI_REFERENCE_v1.md](./strategy/COMMERCIAL_AGENTIC_UI_REFERENCE_v1.md) |

---

## Repo root law (short form)

- [NORTH_STAR.md](../NORTH_STAR.md)
- [OFFERINGS.md](../OFFERINGS.md)
- [PLATFORM_BLUEPRINT.md](../PLATFORM_BLUEPRINT.md)
- [DEPLOYMENT_ARCHITECTURE.md](../DEPLOYMENT_ARCHITECTURE.md)

---

## Layer folders

| Folder | Role |
|--------|------|
| `L0-law/` | Constitution pointer → GCIP v4 |
| `L1-operational/` | Runtime services |
| `L2-knowledge/` | **Derived** — run `make sync-derived-docs` |
| `L3-external/` | Reference product sandbox |
| `_archive/` | Cold storage |

---

## Runtime phases

- [PHASE_3_2_RUNTIME_HARDENING.md](./PHASE_3_2_RUNTIME_HARDENING.md)
- [PHASE_3_3_POSTGRES_VERIFICATION.md](./PHASE_3_3_POSTGRES_VERIFICATION.md)
- [PHASE_3_5_COPILOT_DEMO_PACKAGE.md](./PHASE_3_5_COPILOT_DEMO_PACKAGE.md)
- [PRODUCTION_READINESS_REPORT.md](./PRODUCTION_READINESS_REPORT.md)

---

## Anti-fragmentation

1. **Write** only to `docs/SOURCE_OF_TRUTH/uploaded/` and `registry/`
2. **Regenerate** `L2-knowledge/` and `Noetfield-All-Documents/` via `make sync-derived-docs`
3. **Verify** with `make verify-law-stack` before merge

Machine manifest: [governance/LAW_STACK.json](../governance/LAW_STACK.json)
