# Active site policy

**Status:** Authoritative route policy for agents and GTM  
**Updated:** 2026-06-12  
**Resolves:** `SITE_ARCHITECTURE.md` vs `FINAL_PUBLIC_SITE.md` vs `public-surface-map.md`

---

## Policy summary

| Class | Rule |
|-------|------|
| **Live primary** | Routes in § Primary surfaces — maintain, verify, link from nav |
| **Live secondary** | Copilot funnel + trust-ledger + gate — maintain; not all in header nav |
| **Technical** | `/docs/api/`, `/openapi.json`, `/status/` — diligence only |
| **Legacy / redirect** | `/directory/` → `/`; collapsed experiments → redirect or noindex |
| **Forbidden on www** | Engine SKU · SourceA · payment rails · credit-card checkout · AUTO-RUN |

---

## Primary surfaces (live)

| URL | Status | Governing doc |
|-----|--------|---------------|
| `/` | **Live** | `PRODUCT_TRUTH`, homepage |
| `/enterprise/` | **Live** | `public-surface-map` |
| `/trust-brief/` | **Live** | `OFFERINGS_LOCKED` |
| `/copilot/` | **Live** | `NOETFIELD_SME_PROVIDER_BLUEPRINT` |
| `/bank-pilot/` | **Live** | Shadow simulation only |
| `/console/` | **Live** | Simulation pointer |
| `/trust-ledger/` | **Live** | TLE positioning lock |

---

## Copilot funnel (live secondary)

| URL | Status | Notes |
|-----|--------|-------|
| `/copilot/demo/` | Live | 5-minute demo |
| `/copilot/pilot/` | Live | Design partner CAD $2K–$10K |
| `/copilot/procurement/` | Live | Diligence pack |
| `/copilot/readiness/` | Live | Readiness checklist |
| `/copilot/quickscan/` | Live | SME self-assessment |
| `/copilot/governance/` | Live | Governance narrative |
| `/copilot/quickscan/*` | Live | Step pages |

---

## Gate & intake (live)

| URL | Status | Notes |
|-----|--------|-------|
| `/gate/intake/` | Live | Unified intake forward |
| `/gate/procurement/` | Live | Procurement vector |
| `/trust-brief/intake/` | Live | Trust Brief CTA |
| `operations@noetfield.com` | **Canonical** | Sole public intake |

---

## Technical corner (live)

| URL | Status |
|-----|--------|
| `/docs/api/` | Live |
| `/openapi.json` (via :13080 / prod) | Live — verify 200 |
| `/status/` | Live |
| `/partners/` | Live |
| `/playbook/` | Live |

---

## Legacy / redirect

| URL | Policy |
|-----|--------|
| `/directory/` | Redirect → `/` |
| Retired `contact@` / `procurement@` / `sales@` | **Removed** from public mailto |
| `FINAL_PUBLIC_SITE` 5-page collapse | **Not enforced** — full Copilot funnel remains live for SME GTM |

**Note:** `FINAL_PUBLIC_SITE.md` simplification is deferred until post–design-partner proof. SME provider path requires Copilot subroutes.

---

## Navigation lock

**Header (5):** Home · Enterprise · Trust Brief · Copilot · Governance Console  

**Footer additions:** Governance API · Status · Procurement (Copilot)

---

## Verify

```bash
make verify-gtm
./scripts/verify-gtm-ops-docs.sh
./scripts/plan-with-no-asf-verify.sh
```

---

## Related

- [PAGE_AUTHORITY_MAP.md](./PAGE_AUTHORITY_MAP.md)  
- [SITE_ARCHITECTURE.md](../SITE_ARCHITECTURE.md) — full IA reference  
- [public-surface-map.md](../strategy/public-surface-map.md) — tone law
