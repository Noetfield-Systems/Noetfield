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

# AIE Protocol — VC Technical Appendix

Document key: `aie-protocol-vc-technical-appendix`

## Classification

Decentralized Cognitive Execution Network (DCEN): blockchain settlement + multi-agent
AI execution + task graph networks + cryptoeconomic validation.

## Formal models

- Agent = (S, P, M, T) — state, policy, memory, tools
- Validation score V = Σ(w_i × v_i) with acceptance if V ≥ τ
- Supply dynamics and adversarial threat matrix (Sybil, collusion, bridge attacks)

## Performance boundary

| Layer | Determinism | Latency | Trust |
|-------|-------------|---------|-------|
| Ethereum | deterministic | high | cryptographic |
| Cosmos | semi-deterministic | medium | consensus |
| Off-chain | probabilistic | low | reputation + validation |

## Registry note

Diligence supplement; defers to whitepaper for normative protocol specification.
