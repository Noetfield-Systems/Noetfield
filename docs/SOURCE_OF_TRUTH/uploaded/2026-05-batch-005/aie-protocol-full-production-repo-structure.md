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

# AIE Protocol — Full Production Repo Structure

Document key: `aie-protocol-full-production-repo-structure`

## Normalized purpose

Defines the target monorepo layout for AIE Protocol spanning Ethereum contracts,
Cosmos SDK chain, agent-runtime, validator-network, bridge, SDK, frontend, and
infra layers.

## Top-level layout

- `contracts/` — Solidity core (AIEToken, TaskEscrow, StakeManager, Governance, BridgeAdapter)
- `cosmos/` — Cosmos SDK modules (`x/agent`, `x/task`, `x/execution`, `x/validation`, `x/reputation`, `x/economy`)
- `agent-runtime/` — off-chain cognitive engine (planner, executor, memory, critic, tools)
- `validator-network/` — consensus, scoring, slashing, validator API
- `bridge/` — ethereum-to-cosmos and cosmos-to-ethereum relayers
- `sdk/` — TypeScript/Python developer toolkit
- `frontend/` — dashboard and agent marketplace UI
- `infra/` — Kubernetes, Terraform, monitoring, CI/CD
- `specs/` and `docs/` — protocol truth and investor/developer documentation

## Three coordinated systems

1. Economic Layer (Ethereum) — tokens, staking, settlement, governance
2. Cognitive Layer (Cosmos) — agents, task graphs, validation, reputation
3. Execution Layer (off-chain) — AI runtime, tools, memory, orchestration

## Registry note

Separate protocol lineage from Noetfield. Use as implementation scaffold reference
only unless an AIE module is explicitly scoped.
