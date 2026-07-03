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

# Noetfield / Sina AI OS — Unified Cognitive Governance System (v1.0)

Document key: `noetfield-unified-cognitive-governance-system-v1`

**Classification:** Active methodology reference (internal cognitive OS). **Legal/regulatory L0** remains `noetfield-constitution-gcip-v4`.

---

## Core principle

The system is not “AI-assisted architecture.” It is a **human-owned, AI-evaluated, constitutionally governed execution OS**.

### Non-negotiables

- Owner = final authority
- Agents = proposal generators only
- No autonomous overwrite of truth layers
- All decisions must pass structured arbitration

---

## System architecture (clean layers)

Unifies conflicting models into one stable hierarchy:

```text
L0 — CONSTITUTION (IMMUTABLE LAW)
L1 — EXECUTION CORE (SYSTEM BEHAVIOR)
L2 — KNOWLEDGE & TOOLS (REFERENCE + STRATEGY)
L3 — EXTERNAL / EXPERIMENTAL SYSTEMS
ARCHIVE — DEAD / OBSOLETE / PROHIBITED
```

### L0 — Constitution

Defines reality boundaries. Identity rules, governance rules, permission boundaries, safety constraints, structural invariants.

- Cannot be modified by AI
- Cannot be overridden by L1/L2
- Only owner can change
- **In this repo:** `NORTH_STAR.md` + GCIP v4 constitution documents

### L1 — Execution core

Operating brain: ingestion, agent orchestration, memory, runtime logic, FastAPI backend, UI triggers, cycle execution.

- Must obey L0
- Minimal and deterministic
- No strategic ideology inside L1
- **In this repo:** `services/`, `Makefile api-v3`, Golden Edge v3

### L2 — Knowledge and strategy

Thinking layer only — never execution authority.

- **In this repo:** `L2-knowledge/strategy/noetfield/` (production) and `reference-products/`

### L3 — External / experimental

Sandbox: Grok, Perplexity analysis, experimental architectures, GTM concepts. Zero authority until promoted through OAS.

### Archive

Obsolete drafts, prohibited positioning, deprecated architectures. Cold storage only.

- **In this repo:** `L2-knowledge/strategy/reference-products/`, SOT `prohibited_positioning_draft`

---

## Opinion Arbitration System (OAS)

Every multi-agent / multi-chatbot output goes through:

### Step 1 — Claim extraction

Convert answers into atomic claims (YAML). No prose past this stage.

### Step 2 — Conflict graph

Detect contradictions, overlaps, mutual exclusions.

### Step 3 — Alignment Scoring Engine (ASE)

| Metric | Weight |
|--------|--------|
| Constitutional fit | 0.35 |
| Runtime feasibility | 0.25 |
| Strategic coherence | 0.20 |
| Simplicity gain | 0.10 |
| Drift risk (subtract) | 0.10 |

```text
Score =
(Constitution Fit × 0.35)
+ (Runtime Feasibility × 0.25)
+ (Strategic Coherence × 0.20)
+ (Simplicity × 0.10)
- (Drift Risk × 0.10)
```

### Step 4 — Golden Edge synthesis

Not voting, majority, or preference. Construct **maximum coherence system state**: stability, minimal entropy, preserved optionality, reduced complexity.

**Runtime:** `POST /v3/evaluate`, `POST /v3/agent-loop` (policy REJECT before forbidden execution).

### Step 5 — Owner ratification

```text
AI → Proposal → Evaluation → Synth → OWNER → COMMIT
```

Nothing applied without human confirmation.

---

## Strategy alignment map

See `governance/strategy-alignment-map.json` at repository root.

---

## End-to-end OS loop

```text
1. Input (chat / file / idea)
2. Ingestion
3. L0 validation
4. Claim extraction
5. Conflict detection
6. Alignment scoring
7. Golden Edge synthesis
8. Owner approval
9. Write to L1/L2/L3
10. Archive old states
```

---

## Repo mapping (canonical)

| Spec directory | This repository |
|----------------|-----------------|
| `L0-law/` | `NORTH_STAR.md`, `docs/SOURCE_OF_TRUTH/.../noetfield-constitution-gcip-v4` |
| `L1-operational/` | `services/`, `apps/`, `infrastructure/` |
| `L2-reference/` | `L2-knowledge/` |
| `L3-external/` | `L2-knowledge/strategy/reference-products/` |
| `_archive/` | SOT prohibited + `docs/REMOVED_PAYMENT_ARTIFACTS.md` |
| `governance/` | `governance/` (OAS, alignment map) |

---

## Final insight

Hierarchy system + contradiction solver + ingestion + strategy layer = **one sovereign decision-making OS for AI-mediated cognition**.

Reduce entropy while preserving human sovereignty.
