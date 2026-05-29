# Sina / Noetfield AI OS — Source of Truth Master Document (v1.0)

Document key: `noetfield-sot-master-document-v1`

**Classification:** Active source of truth (internal layer hierarchy + OAS). **Supremacy on conflict:** GCIP v4 (`noetfield-constitution-gcip-v4`) for legal/commercial identity; this document governs **repository cognition structure**.

---

## 0. System definition

A **human-owned, AI-assisted cognitive governance and execution operating system**.

It is **not**:

- a chatbot system only
- a knowledge base only
- an autonomous AI agent swarm
- a financial or external orchestration system

It **is**:

> A controlled decision + execution + memory system with strict constitutional hierarchy.

---

## 1. Core governance principle

> **AI proposes. Human disposes. System executes only after ratification.**

No exceptions.

---

## 2. System hierarchy (only valid structure)

```text
L0 — CONSTITUTION (IMMUTABLE TRUTH)
L1 — EXECUTION SYSTEM (RUNNING ENGINE)
L2 — KNOWLEDGE & STRATEGY LAYER
L3 — EXTERNAL / EXPERIMENTAL INPUTS
ARCHIVE — DEPRECATED / INVALIDATED CONTENT
```

---

## 3. L0 — Constitution

**Purpose:** Identity, limits, governance rules.

**Contains:** Core identity principles, system boundaries, permission model, safety and integrity rules, authority hierarchy.

**Rules:**

- Cannot be modified by AI
- Cannot be overridden by lower layers
- Only owner can update
- Any conflict resolves in favor of L0

### L0 core laws

| Law | Statement |
|-----|-----------|
| **AUTHORITY** | Human owner is final authority |
| **EXECUTION SAFETY** | No system action without explicit or implicit ratification |
| **ISOLATION** | External systems cannot directly modify L0 or L1 |
| **INTEGRITY** | No contradictory logic in active runtime state |
| **MINIMAL GOVERNANCE** | L0 remains small, stable, immutable |

**Noetfield Inc. legal L0:** GCIP v4 constitution (batch 014/015). **Engineering L0 surface:** `NORTH_STAR.md`.

---

## 4. L1 — Execution system

**Purpose:** The living system.

**Contains:** FastAPI backend, agent loop, ingestion, memory, UI triggers, runtime orchestration, scheduling.

**Rules:** Obey L0; no strategic speculation; deterministic or semi-deterministic; observable (loggable, traceable).

```text
ingestion/
runtime/
agents/
memory/
api/
ui/
monitoring/
```

**Repo:** `services/*`, `apps/*`, Golden Edge v3 (`/v3/evaluate`, `/v3/agent-loop`).

---

## 5. L2 — Knowledge and strategy

**Purpose:** Cognitive support — no execution authority.

**Contains:** Design docs, architecture research, prompts, comparisons, strategy maps, future-state models (control plane as **reference only**).

**Rules:** Cannot override L1/L0; may contain conflicting ideas safely; input to decision engine only.

```text
strategy/
architecture/
prompts/
research/
models/
```

**Repo:** `L2-knowledge/strategy/noetfield/` (production), `full/` (mirror).

---

## 6. L3 — External / experimental

**Purpose:** Sandbox for uncontrolled inputs.

**Contains:** External AI outputs, experimental frameworks, speculative architectures.

**Rules:** Zero authority; never executed directly; promotion via OAS + owner ratification.

**Repo:** `L2-knowledge/strategy/reference-products/`.

---

## 7. Archive

**Purpose:** Permanent cold storage.

**Contains:** Deprecated systems, prohibited positioning, obsolete versions.

**Rules:** Never executed; never auto re-ingested; only human can resurrect.

**Repo:** SOT `prohibited_positioning_draft`, `_archive/` README.

---

## 8. Opinion Arbitration System (OAS)

1. **Claim extraction** — atomic claims only  
2. **Conflict detection** — contradictions, overlaps, redundancy  
3. **Alignment scoring** — weighted formula (see unified cognitive governance v1)  
4. **Golden Edge synthesis** — lowest entropy + highest coherence (not majority vote)  
5. **Owner ratification** — final authority human  

---

## 9. Strategy alignment map

Canonical JSON: `governance/strategy-alignment-map.json`

---

## 10. Full execution loop

```text
INPUT
→ INGESTION
→ L0 VALIDATION
→ CLAIM EXTRACTION
→ CONFLICT DETECTION
→ ALIGNMENT SCORING
→ GOLDEN EDGE SYNTHESIS
→ OWNER REVIEW
→ EXECUTION
→ MEMORY UPDATE
→ ARCHIVE OLD STATE
```

---

## 11. Canonical directory structure (mapped to repo)

```text
SinaaiDataBase/                    →  Noetfield repo root
├── L0-law/                        →  NORTH_STAR + docs/SOURCE_OF_TRUTH constitution
├── L1-operational/                →  services/, apps/, infrastructure/
├── L2-reference/                  →  L2-knowledge/
├── L3-external/                   →  L2-knowledge/strategy/reference-products/
├── _archive/                      →  archive README + SOT prohibited
└── governance/                    →  governance/ (OAS, scoring, alignment map)
```

---

## 12. Final system truth

> Reduce entropy while preserving human sovereignty.

Everything else is implementation detail.

---

## Pairing

Detailed OAS and layer narrative: `noetfield-unified-cognitive-governance-system-v1` (same batch 020).
