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

# Deferred product work (Tier 3)

Implement **after** production go-live and first paid brief or pilot LOI ([GO_LIVE.md](./GO_LIVE.md)).

| ID | Item | Trigger |
|----|------|---------|
| NF-ENG-12 | pgvector RAG over `knowledge_chunks` | Chat quality gaps in prod logs |
| NF-ENG-13 | Langfuse dashboards | Active pilot debugging |
| NF-ENG-16 | WAF / edge rate limits | Traffic or abuse signals |
| NF-WWW-10 | `/pricing` paid ads page | Paid acquisition starts |
| NF-WWW-11 | Light-mode www | Design sprint |
| NF-ENG-11 | CRM sync (HubSpot/Salesforce) | Ops volume justifies |

**Shipped early (Tier 3 partial):** NF-ENG-17 Telegram `INTAKE: org | email | message` → intake pipeline.
