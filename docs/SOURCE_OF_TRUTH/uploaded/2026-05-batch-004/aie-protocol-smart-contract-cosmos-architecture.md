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

# AIE Protocol - Smart Contract and Cosmos Module Architecture

Document key: `aie-protocol-smart-contract-cosmos-architecture`

Source status: hybrid execution layer for agentic intelligence economies

## Normalized purpose

This document defines AIE as a dual-layer execution architecture for agentic
intelligence economies.

## Architecture

Layer A: EVM Layer

- token logic
- staking
- task escrow
- settlement
- governance

Layer B: Cosmos SDK Layer

- agent coordination
- task DAG orchestration
- reputation system
- validation consensus
- inter-agent messaging

## Core modules

Solidity:

- AIEToken
- StakeManager
- TaskEscrow
- Governance
- BridgeAdapter

Cosmos SDK:

- x/agent
- x/task
- x/execution
- x/validation
- x/reputation
- x/economy

## Registry classification

Classify as active AIE protocol reference and separate protocol lineage. It is
not part of the current Noetfield backend runtime unless an AIE module is
explicitly scoped later.

