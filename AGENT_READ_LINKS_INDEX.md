# Agent read links index

**Purpose:** One map for **every repo / lane** — ecosystem (SourceA) vs **Noetfield cloud** (this git repo).  
**Agent id (Noetfield cloud):** `noetfield_cloud` · **Thread:** `THREAD-PORTFOLIO` · **Plane:** `[DELIVERY]`

---

## Hub (Mac founder only — cloud cannot use)

| What | Open |
|------|------|
| **Sina Command hub (UI)** | http://127.0.0.1:13020/ |
| **Start hub** (if links 404) | `~/Desktop/SourceA/scripts/serve-sina-command.sh` |
| **Essentials map (live)** | http://127.0.0.1:13020/?tab=essentials |
| **Command** | http://127.0.0.1:13020/?tab=command |
| **Personal DB** | http://127.0.0.1:13020/?tab=personal-db |
| **Repos** | http://127.0.0.1:13020/?tab=repos |
| **Track** | http://127.0.0.1:13020/?tab=track |
| **Live agents** | http://127.0.0.1:13020/?tab=intelligence |
| **Incident Room** | http://127.0.0.1:13020/?tab=incident-room |
| **Doc library** | http://127.0.0.1:13020/?tab=doc-library |
| **Agent hub** | http://127.0.0.1:13020/?tab=agent-hub |
| **Products** | http://127.0.0.1:13020/?tab=products |
| **Actions** | http://127.0.0.1:13020/?tab=actions |

**Cloud / Cursor VM:** Hub URLs point at **founder Mac loopback**. Use the **file paths** below (or `ops/private/sourceA/` mirror after sync). Do not expect `127.0.0.1:13020` to work in cloud.

---

## Everyone first (general — Desktop SourceA)

Canonical root: `~/Desktop/SourceA/`  
Gitignored mirror (founder sync): `ops/private/sourceA/` — see [scripts/sync-sourceA-desktop.sh](scripts/sync-sourceA-desktop.sh)

| What | File (Desktop SourceA) | In Noetfield git? |
|------|------------------------|-------------------|
| Master system update (full) | `SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md` | No — hub / Desktop |
| Essentials law | `SINA_HUB_ESSENTIALS_LOCKED_v1.md` | No |
| Personal DB Layer A law | `SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md` | No |
| Mac Health Guard law | `SINA_MAC_HEALTH_GUARD_LOCKED_v1.md` | No |
| Thread registry | `ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md` | No |
| Output contract | `AGENT_OUTPUT_CONTRACT_v1.yaml` | No |
| YAML ingest law | `SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md` | **Repo echo:** [docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md](docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md) |
| Incidents index | `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` | No |
| Agent desk | `AGENT_DESK_START_HERE.md` | No |
| Semi-separate master | `SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md` | No |
| Read chain entry | `README_SOURCE_A.md` | No |

### Mandatory read chain (1→14)

All under `~/Desktop/SourceA/` unless noted. **Read-only for agents** — ASF edits on Mac only.

1. `README_SOURCE_A.md`
2. `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md`
3. `SINA_OS_SSOT_LOCKED.md` — mirror: [ops/private/sourceA/SINA_OS_SSOT_LOCKED.md](ops/private/sourceA/SINA_OS_SSOT_LOCKED.md) when synced
4. `SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md`
5. `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md`
6. `SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md`
7. `SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md`
8. `SINA_PROMPT_FAST_LOOP_LOCKED_v1.md`
9. `SINA_AGENT_LOOP_ORDER_v1.md`
10. `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md`
11. `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md`
12. `SINA_MAC_HEALTH_GUARD_LOCKED_v1.md`
13. `SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md`
14. `SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md`

**Also in mirror (when synced):** `AUTO_CONFLICT_ENGINE_V3_LOCKED.md`, `PHASE1_UNIFIED_BLUEPRINT_v2_3.md`, `NOETFIELD_REPO_ALIGNMENT.md` — see [ops/private/sourceA/README.md](ops/private/sourceA/README.md)

**Execution truth (cross-repo):** `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` (Desktop) — Noetfield ingest rules: [docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md](docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md)

---

## Noetfield cloud — full read links (this repo)

**Lane:** `noetfield_cloud` · **Hub pack:** Agent hub → `noetfield_cloud` · Repos → lane `noetfield_cloud`

| What | Link in **this** repository | Desktop-only (if not synced) |
|------|-----------------------------|------------------------------|
| **Read order (locked)** | [docs/agent/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](docs/agent/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md) | — |
| Semi lane notice | — | `~/Desktop/SourceA/SEMI_NOTICE_noetfield_cloud_v1.md` |
| Paste into chat | [docs/agent/ready_to_paste_noetfield_cloud.txt](docs/agent/ready_to_paste_noetfield_cloud.txt) | Desktop copy may differ |
| Ship plan | [os/plan.json](os/plan.json) | — |
| Ship now | [os/SHIP_NOW.md](os/SHIP_NOW.md) · [docs/SHIP_NOW.md](docs/SHIP_NOW.md) | — |
| Trust Ledger positioning | [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) | Alias name on hub: `NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md` |
| Product scope (public) | [PRODUCT_TRUTH.md](PRODUCT_TRUTH.md) · [POSITIONING.md](POSITIONING.md) · [OFFERINGS_LOCKED.md](OFFERINGS_LOCKED.md) | — |
| Boundaries | [PROJECT_BOUNDARIES_LOCKED.md](PROJECT_BOUNDARIES_LOCKED.md) | — |
| Agent workflow | [.cursor/AGENT_TRACKING.md](.cursor/AGENT_TRACKING.md) | — |
| Sprint backlog | [docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md](docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md) | — |
| TLE schema + examples | [schemas/tle-v1.schema.yaml](schemas/tle-v1.schema.yaml) · [docs/spec/examples/](docs/spec/examples/) | — |
| Local dev (unified) | [Makefile](Makefile) `dev-local` → http://localhost:13080/ | Mac: forward port 13080 from cloud VM if needed |
| Verify ship | `make ship-verify` | — |

### Noetfield cloud read order (short)

1. This index → [docs/agent/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](docs/agent/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md)
2. [os/SHIP_NOW.md](os/SHIP_NOW.md) → [os/plan.json](os/plan.json)
3. [PRODUCT_TRUTH.md](PRODUCT_TRUTH.md) + Trust Ledger blueprint
4. Task PR / issue
5. Ingest: [docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md](docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md) (**after** ship; does **not** block ship)

**Do not:** edit Sina Prompt OS codebase · idle waiting for next Prompt OS order · treat README alone as structural SSOT.

---

## Fresher SourceA on cloud

Founder Mac only:

```bash
./scripts/sync-sourceA-desktop.sh
# optional: ./scripts/sync-sourceA-desktop.sh /path/to/Desktop/SourceA
```

Extends mirror when Desktop files exist (see script). **Never** `git add ops/private/`.

---

## Other repos (separate — not this index body)

| Entity | Tracking |
|--------|----------|
| **SinaaiMonoRepo** | DESIGN + EXECUTION — SSOT chain above |
| **Sina Prompt OS** | Coordinate only — **do not edit** from Noetfield agents |
| **777 Foundation** | Separate repo / deploy |
| **TrustField / VIRLUX** | Out of scope — [PROJECT_BOUNDARIES_LOCKED.md](PROJECT_BOUNDARIES_LOCKED.md) |

---

*Noetfield copy of hub index — paths verified in git. Desktop/hub filenames unchanged on founder Mac.*
