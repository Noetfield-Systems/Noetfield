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

# Chat Corpora Deduplication Pipeline (Methodology)

Document key: `chat-corpora-deduplication-pipeline-methodology-fa`

## Pipeline stages

1. Ingestion and parsing to unified Markdown/JSON
2. Semantic clustering via embeddings
3. Dedup merge and `[CONTRADICTION_FLAG]` reasoning pass
4. Structured output to relational DB, Notion, or Obsidian

## Tools referenced

AnythingLLM, Open WebUI, Flowise, Fabric CLI, custom Python + Pydantic structured outputs.

## Registry

Methodology reference for future chat-archive ingestion; not Noetfield runtime SOT.
