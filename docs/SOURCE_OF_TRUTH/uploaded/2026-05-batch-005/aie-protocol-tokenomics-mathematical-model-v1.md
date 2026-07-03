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

# AIE Protocol Tokenomics Mathematical Model

Document key: `aie-protocol-tokenomics-mathematical-model-v1`

## Supply dynamics

S_{t+1} = S_t + I_t - B_t

## Inflation

I_t = λ · S_t · (U_t / (1 + U_t)) · V_t

## Burn

B_t = α · F_t · (1 + log(1 + U_t))

## Staking yield

R_t = (I_t + β · F_t) / St_t with equilibrium St* ≈ √((I_t + βF_t) / k)

## Net supply pressure

NSP_t = I_t - B_t — target lim NSP_t → 0

## Value capture

Token_Value ∝ (Network_Usage × Fee_Pressure) / Supply_Expansion

## Active tokenomics SOT

This document is the authoritative tokenomics reference for the AIE protocol lineage.
