# NF Runways Landing — Wireframe & Production Copy v1

**Route:** `https://www.noetfield.com/runways/`  
**Status:** Build SSOT for MVP HTML (not a public marketing claim by itself)  
**Homepage:** `/` remains the corporate entry surface — do not collapse it into this product page  
**Aligned with:** `docs/www/WWW_IMPLEMENTATION_STATUS_v1.md` · `NF-NOETFIELD-RUNWAY-PRODUCT-V1`

---

## 1. Locked taxonomy

| Concept | Definition |
| --- | --- |
| **Goal** | The outcome a human wants |
| **Intent** | Structured, scoped expression of the goal |
| **Runway** | Versioned, governed path from intent to accepted outcome |
| **Recipe** | Executable manifest for one Runway |
| **Job** | One concrete execution of a Recipe |
| **Agent** | Bounded worker inside a Job |
| **Gate** | Policy / authority decision before or during execution |
| **Verifier** | Independent acceptance criteria for output |
| **Receipt** | Inspectable record of a Job |
| **Motor** | System that selects, executes, repairs, and records Runways |

**Product definition:** A Runway is a versioned, governed execution path that carries a human goal from intake to an accepted output.

**Category:** Verified Agentic Execution  
**Hero promise:** From goal to verified output.  
**Brand close:** Agents participate. Runways finish the work.  
**Company close:** Noetfield Runways turn human goals into governed, verified outcomes.

**Runtime stack labels (taxonomy only):**

```text
Field-Audit Compiler → GEL → Motor → Agent Fabric → Sandbox → Verifier → Trust Ledger
```

---

## 2. Status badge vocabulary

| Badge | Meaning |
| --- | --- |
| **Available** | Public surface or commissioning path exists now |
| **Demonstrated** | Internal / staging / Motor job proof exists; not paid-client traction |
| **Demonstrated on staging Runway** | Artifact loop proven on staging (DOCX/PDF/XLSX journeys) |
| **Planned** | Direction locked; public proof not yet shipped |
| **Not claimed** | Explicitly withheld (paid customer, production, margins) |

---

## 3. ASCII wireframe (MVP — 7 sections)

```text
┌──────────────────────────────────────────────────────────────┐
│ NAV  Noetfield Systems · Runways · Motors · Proof · Contact │
├──────────────────────────────────────────────────────────────┤
│ HERO                                                         │
│  VERIFIED AGENTIC RUNWAYS                                    │
│  From goal to verified output.                               │
│  [body]                                                      │
│  [ Run a live example ]  [ Explore ready runways ]           │
│  Policy-gated · Deterministically verified · …               │
│                          ┌ Live Runway Console (static) ┐    │
│                          │ GOAL / RUNWAY / STEPS / COST │    │
│                          └──────────────────────────────┘    │
├──────────────────────────────────────────────────────────────┤
│ PROBLEM — Most AI systems stop before the work is proven.    │
├──────────────────────────────────────────────────────────────┤
│ RUNWAY VIZ — Goal→Intent→Contract→Gate→Execute→Verify→…      │
│  (stage chips + static artifact panel)                       │
├──────────────────────────────────────────────────────────────┤
│ PROOF — QUALIFIED card | FAILED CHECK card                   │
├──────────────────────────────────────────────────────────────┤
│ CATALOG — BUILD / REPAIR / DECIDE / GOVERN / FULFILL / OPERATE│
├──────────────────────────────────────────────────────────────┤
│ BUY — Ready · Private · Custom                               │
├──────────────────────────────────────────────────────────────┤
│ FINAL CTA — brand close + contact                            │
└──────────────────────────────────────────────────────────────┘
```

Signature strip:

```text
Goal → Intent → Contract → Gate → Execute → Verify → Repair → Qualify → Receipt
```

---

## 4. Production copy (English)

### Nav (page-local)

- Runways (current)
- How it works → `#how-it-works`
- Catalog → `#catalog`
- Proof → `#proof`
- For teams → `#deploy`
- Primary CTA: Run a goal → `#live-console`

### Hero

**Kicker:** VERIFIED AGENTIC RUNWAYS  
**H1:** From goal to verified output.  
**Lead:** Give Noetfield a goal. The Motor breaks it into bounded intent, selects a versioned runway, dispatches the right agents and tools, executes under policy, verifies the result, repairs bounded failures, and returns the output with a receipt.  
**CTA primary:** Run a live example  
**CTA secondary:** Explore ready runways  
**Trust row:** Policy-gated · Deterministically verified · Bounded repair · Metered end to end · Private or managed  
**Manifesto line:** Agents participate. Runways finish the work.

### Live Runway Console (static, honest)

```text
GOAL
Repair the failing software check and prove the fix.

RUNWAY
software-repair@0.1

01  Diagnose        model-backed            PASS
02  Fix             model-backed            PASS
03  Verify          deterministic check     PASS

STATUS
QUALIFIED

EXECUTION STEPS              3
MODEL INVOCATIONS            2
DETERMINISTIC CHECKS         1
REPAIRS                      0
METERED MODEL COST           measuring
BUDGET CAP                   scoped per job

Evidence class
Demonstrated Motor job · redacted public console
Paid customer delivery is not claimed.
```

### Problem

**H2:** Most AI systems stop before the work is proven.  
**Body:** A model can draft. An agent can act. Coordinated workers can distribute work. But consequential work still needs scope, authority, acceptance criteria, verification, repair limits, and a usable record. That complete path is the runway.

**Distinction ladder:**

```text
Prompt   → answer
Agent    → bounded action
Runway   → qualified outcome
Motor    → repeatable governed operation
```

**Key line:** A prompt can produce an answer. Coordinated agents can distribute work. A runway defines how the work becomes acceptable.

### Determinism (inside how-it-works)

**H3:** Intelligent where reasoning helps. Deterministic where correctness matters.  
**Body:** The models may be probabilistic. The runway is controlled. Input contracts, permissions, budgets, state transitions, tool boundaries, acceptance criteria, retry limits, stop conditions, evidence requirements, and receipt generation are explicit. Models diagnose, draft, plan, and repair. Code, policy, tests, schemas, and evidence decide what passes.

### Runway visualization

**Eyebrow:** 02 · Full runway  
**H2:** From human goal to accepted output.  
**Stage artifacts (static fixtures):**

| Stage | Artifact shown |
| --- | --- |
| Goal | Original request |
| Intent | Normalized intent JSON |
| Contract | Scope and acceptance |
| Gate | APPROVE / REVIEW / DECLINE |
| Execute | Bounded steps and tools |
| Verify | Checks and evidence |
| Repair | Retry reason (when used) |
| Qualify | Accepted or refused |
| Receipt | Final job record |

### Proof

**Eyebrow:** 03 · Verifier  
**H2:** The verifier—not the model—decides what passes.  
**Body:** A failed verification is not a failed control system. It is the control system refusing to qualify an unproven result. Model call succeeded ≠ output verified.

**Success card label:** QUALIFIED  
**Failure card label:** FAILED CHECK  
**Footnote:** Demonstrated Motor jobs · redacted fields · paid acceptance not claimed.

### Catalog

**Eyebrow:** 04 · Runway catalog  
**H2:** Ready paths grouped by outcome.  
**Intro:** Status labels distinguish what is available, demonstrated, and planned. They are not client or revenue claims.

Cards (V1):

1. **Software Repair** — REPAIR — Demonstrated  
2. **Decision Brief** — DECIDE — Demonstrated on staging Runway  
3. **Spreadsheet / KPI Pack** — DECIDE — Demonstrated on staging Runway  
4. **RFP Response Pack** — FULFILL — Demonstrated on staging Runway  
5. **Governed Replacement** — OPERATE — Demonstrated · client-zero  
6. **Enterprise AI Governance** — GOVERN — Available  
7. **Investor Diligence** — DECIDE — Demonstrated internally  
8. **SourceB Client Fulfillment** — FULFILL — Live commercial service · case study planned  
9. **Repo Change** — BUILD — Planned

### Buy paths

**Eyebrow:** 05 · Deploy  
**H2:** Three ways to run a runway.  

1. **Run a Ready Runway** — standard outcomes → `/contact/?topic=governed-motor`  
2. **Deploy a Private Runway** — team process, data, tools, policy → `/contact/?topic=custom-workflow`  
3. **Commission a Custom Runway** — map goal, authority, recipe, verifier, Motor → `/contact/?topic=pilot-client`

Billing posture (copy only, no price table): Jobs, Runways, deployment, and accepted outcomes are the commercial units—not agent count.

### Final CTA

**H2:** Start with one goal that must finish—and prove it.  
**Body:** Noetfield Runways turn human goals into governed, verified outcomes.  
**CTAs:** Discuss a runway · Review proof

---

## 5. Forbidden-claim checklist (public HTML)

- [ ] No third-party vendor / competitor names  
- [ ] No TrustField product runway or TrustField links  
- [ ] No invented agent swarm counts (30 / 67 / 100)  
- [ ] No “total cost” equal to metered model cost alone  
- [ ] No margin percentages  
- [ ] No paid-customer / revenue / installation claims  
- [ ] No production promotion claim for staging Runway  
- [ ] No self-learning / marketplace / leaderboard claims  
- [ ] Homepage hero and portfolio framing unchanged except a light Systems link

---

## 6. Stage backlog (explicitly out of V1 HTML)

### Stage 2 — Live Event Ledger

- Real public/redacted job endpoint  
- SSE event stream driving Runway / Agents / Evidence / Cost tabs  
- Actual AgentInstance counts when registered  

### Stage 2 module (illustrative until live) — Agent Fabric

Label required if shown: **ILLUSTRATIVE EXECUTION ARCHITECTURE**

```text
Dozens of agents. Not dozens of wasted model calls.
Every visible agent is a real execution unit with an ID, role,
input contract, state, output, and receipt.
Not every agent needs a separate expensive model invocation.
```

### Stage 3 — Interactive demo

Safe fixtures: repair a calculation · audit a claim · decision brief · policy evaluation.

### Stage 4 — Client platform

Tenant login, private catalog, BYOK, policies, secrets, artifacts, approvals, usage.

---

## 7. Relationship to Motors

```text
Noetfield Systems (/)
  ├── AI Motors (/motors/)     category — governed execution runtime
  ├── Runways (/runways/)      product — versioned execution catalog
  ├── Enterprise / GEL         governed application
  ├── SourceA / SourceB        application surfaces
  └── Proof                    evidence index
```

Motors explain the category. Runways sell the path from goal to verified output.
