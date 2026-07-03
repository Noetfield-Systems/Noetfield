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

# AIE Protocol Tokenomics — Adaptive Supply Model

Document key: `aie-protocol-tokenomics-adaptive-supply-model`

## Core identity

S_{t+1} = S_t + I_t - B_t

## Emissions

I_t = λ · S_t · g(U_t) · h(Q_t) with g(U_t) = U_t / (1 + U_t) and h(Q_t) ∈ [0.5, 1.5]

## Burn

B_t = α · F_t · log(1 + U_t)

## Equilibrium target

lim |I_t - B_t| → 0 — usage-responsive emissions matched by execution-based burns.

## Supersession

Superseded by `aie-protocol-tokenomics-mathematical-model-v1` for staking yield
and stress-scenario detail. Retained for provenance.
