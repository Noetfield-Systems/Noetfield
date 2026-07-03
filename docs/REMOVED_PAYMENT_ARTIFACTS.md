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

# Removed Payment / Routing Public Artifacts

Production alignment sprint — institutional GTM (GCIP v4 / North Star).

## Replaced or retired pages

| Path | Action |
|------|--------|
| `/index.html` | Full rewrite — pre-execution governance infrastructure |
| `/platform/index.html` | Rewrite — governance platform hub |
| `/platform/dashboard/index.html` | Rewrite — pilot governance console (no treasury/corridors) |
| `/app/index.html` | Retired → redirect to `/` |
| `/portal/index.html` | Retired → redirect to `/` |
| `/ex/index.html` | Retired → redirect to `/` |
| `/gate/index.html` | Removed payment/procurement routing copy in JS |

## Language still allowed (non-financial)

- **Invoice / PO** — B2B procurement for governance services  
- **Lane assignment / Request ID** — intake discipline (not fund routing)  
- **Card checkout** — purchase of Trust Brief / QuickScan **services** via card (commercial, not money transmission)

## Backend

- `forbidden_financial_actions` in `GovernancePolicyPack`
- Golden Edge v3: `POST /v3/evaluate`, `POST /v3/agent-loop` on port **8001** (`make api-v3`)

## Prohibited terms (public layer)

cross-border payments, payment intent, FX calculator, active corridors, settlement route, treasury routing, corridor, MSB orchestration, meta-gateway PSP
