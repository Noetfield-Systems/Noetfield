# Packaging tier & sandbox model (LOCKED v1)

| Field | Value |
|-------|--------|
| Agent tag | `NF-CLOUD-AGENT` |
| Updated | 2026-06-13 |
| Status | LOCKED — three SKUs only; packaging modes are **within** offerings |

---

## Purpose

Upgrade Noetfield buyer packaging to match institutional SaaS patterns:

1. **Full async demo** — try evaluate → TLE → export without a sales call
2. **Sign up → sandbox/trial** — dev sandbox first, production mode after contract
3. **Published tiers** — named programs buyers can apply to and buy
4. **Agentic autonomous** — agents execute governance workflows, not chat assist only

**Still locked:** three contract offerings (`OFFERINGS_LOCKED.md`). Tiers are **access modes**, not new SKUs.

---

## Packaging ladder (Copilot Governance Pack)

| Mode | Tier label | Access | Limits | Buyer CTA |
|------|------------|--------|--------|-----------|
| **Starter** | Free dev sandbox | Self-serve sign-up | **14-day trial** · **50 evaluate checks** · async demo path | Start sandbox |
| **Sandbox** | Design partner | Named program application | Dev + **production mode** · board PDF · CAD $2K–10K | Apply to program |
| **Production** | Enterprise contracted | SOW + procurement | **Agentic autonomous** workflows · full API · MSP attach | Request Governance Brief |

### Trust Brief & Bank Pilot packaging

| Offering | Starter path | Contract path |
|----------|--------------|---------------|
| **Trust Brief** | Async diligence pack preview (`/trust-center/`) | $10,000 · 6-week diagnostic |
| **Bank Pilot** | Shadow evaluate demo (`mode: shadow`) | Enterprise FRFI engagement |

---

## Full async demo (buyer journey)

```
Sign up (no sales call)
  → Dev sandbox (/workspace/ · /evaluate/)
  → 14-day trial · 50 evaluate checks
  → Full async demo (/copilot/demo/ · /cognitive-dashboard/)
  → Board PDF export path
  → Apply to design partner (sandbox + production mode)
  → Procurement ZIP + contracted production
```

**No credit-card checkout.** Trial provisioning routes to `operations@noetfield.com` or `/gate/intake/?vector=trial` until automated signup ships.

---

## Published tiers (www surfaces)

Every tier page must show:

| Element | Copy anchor |
|---------|-------------|
| Starter | Free dev sandbox · 14-day trial · 50 evaluate checks |
| Sandbox | Dev + production modes · 90-day program |
| Production | Agentic autonomous governance workflows |

**Verify:** `./scripts/verify-ui-e2e.sh` · `./scripts/verify-packaging-tier.sh`

---

## Goals & targets (packaging sprint)

| Goal ID | Target | Metric |
|---------|--------|--------|
| PKG-01 | Async demo without sales call | Trial page live · evaluate path linked |
| PKG-02 | Published tier table on www | index · copilot · enterprise |
| PKG-03 | Trial → sandbox → production ladder | pilot + trial pages aligned |
| PKG-04 | Agentic autonomous narrative | production tier copy + architecture doc |
| PKG-05 | Prompt pack picks aligned | GTM_NEXT iter 20 · QUICK_PICK packaging row |

**Bottleneck unchanged:** Customer #1 board PDF in real meeting — packaging accelerates **trial → design partner**, not proof skip.

---

## Related

| Doc | Role |
|-----|------|
| [AGENTIC_AUTONOMOUS_WORKFLOWS_LOCKED_v1.md](../architecture/AGENTIC_AUTONOMOUS_WORKFLOWS_LOCKED_v1.md) | Production-tier agent execution |
| [OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md) | Three SKUs |
| [NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md](../architecture/NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md) | Design partner wedge |
| [PAGE_AUTHORITY_MAP.md](../site/PAGE_AUTHORITY_MAP.md) | URL authority |
