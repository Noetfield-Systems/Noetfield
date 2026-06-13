# Agentic autonomous workflows (LOCKED v1)

| Field | Value |
|-------|--------|
| Agent tag | `NF-CLOUD-AGENT` |
| Updated | 2026-06-13 |
| Tier | **Production** mode only (contracted) |

---

## Positioning

**Fully agentic autonomous** — governance agents **execute** workflows end-to-end within policy bounds. Not "AI assist" or copilot chat.

| Assist (not us) | Autonomous (Noetfield production tier) |
|-----------------|----------------------------------------|
| Suggest next step | Investigate evidence gaps automatically |
| Draft text for human paste | Triage policy violations · route severity |
| Chat Q&A on policies | Draft TLE recommendations with RID lineage |
| — | Act on **low-risk** approvals within signed policy fence |

**Shadow-first:** autonomous act only after evaluate → record → export path proven in sandbox.

---

## Workflow classes (production tier)

| Class | Agent action | Human gate |
|-------|--------------|------------|
| **Investigate** | Pull metadata evidence · flag missing connectors | Review index completeness |
| **Triage** | Classify intent severity · block high-risk | Override on exception |
| **Draft** | Generate TLE draft · confidence score · board PDF skeleton | Sequential approval chain |
| **Act (low-risk)** | Auto-approve within policy allow-list | Audit log + escalation on deny |

### Out of scope (all tiers)

- Payments · custody · settlement execution
- Unsupervised external system changes without TLE
- Founder impersonation · Hub outreach from NF-CLOUD (R-011)

---

## Tier mapping

| Mode | Agentic depth |
|------|---------------|
| **Starter** (trial) | Guided async demo · manual evaluate |
| **Sandbox** (design partner) | Draft + human approve · rehearsal |
| **Production** (contracted) | Full autonomous investigate → triage → draft → low-risk act |

---

## Implementation reference

| Surface | Path |
|---------|------|
| Evaluate API | `services/governance/noetfield_governance/api.py` |
| TLE workflow | `governance-console/backend/services/` |
| Buyer narrative | `/copilot/trial/` · `/enterprise/` production tier row |
| Hub commercial | Agentic layer only — not NF-CLOUD disk |

**Verify:** packaging tier copy on www; `copilot-pilot-e2e.sh` for sandbox path.
