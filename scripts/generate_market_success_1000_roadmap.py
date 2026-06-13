#!/usr/bin/env python3
"""Generate MARKET_SUCCESS_1000_ROADMAP_v1.md — 10 phases × 100 curated steps."""

from __future__ import annotations

from pathlib import Path

from market_success_1000_steps_data import ALL_PHASE_STEPS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/strategy/MARKET_SUCCESS_1000_ROADMAP_v1.md"

ARCHETYPES = {
    "SM-01": {
        "name": "TrustUnlock",
        "example": 1,
        "category": "Compliance automation + trust",
        "buyer": "CISO / security lead (mid-market SaaS)",
        "wins": "Continuous compliance → trust center → revenue unlock",
        "artifact": "Live trust center, badges, auto evidence, questionnaire deflection",
        "gtm": "Land first audit → expand frameworks → publish trust center",
        "signal": "16K+ customers; IDC/Forrester leader; trust center = sales ROI",
        "nf": "S4 trust-center-grid + S0 board-ready proof",
        "pattern": "trust-center-grid",
        "golden": "Prospects self-serve diligence in 90 seconds — trust center is a revenue surface, not a footer link.",
    },
    "SM-02": {
        "name": "MultiFramework",
        "example": 2,
        "category": "Continuous compliance",
        "buyer": "CISO / security (upmarket SaaS)",
        "wins": "Always audit-ready — compliance as operating rhythm",
        "artifact": "Real-time control status, auditor workspace, multi-framework dashboard",
        "gtm": "Product-led + security community + MSP channel",
        "signal": "ISO 27001 + multi-framework stickiness",
        "nf": "S4 continuous evidence posture",
        "pattern": "continuous-proof",
        "golden": "Show last_verified_at — hourly rhythm beats annual audit theater.",
    },
    "SM-03": {
        "name": "TrustPlatform",
        "example": 3,
        "category": "Enterprise trust intelligence",
        "buyer": "CISO, privacy, legal, GRC (global enterprise)",
        "wins": "Unified trust platform — privacy + risk + AI in one procurement umbrella",
        "artifact": "Trust center, regulatory mapping, AI inventory, policy workflows",
        "gtm": "Enterprise sales; land privacy → expand AI governance",
        "signal": "14K+ orgs; broadest enterprise trust brand",
        "nf": "S4 framework grid at enterprise scale",
        "pattern": "enterprise-trust",
        "golden": "Land one trust module; expand procurement umbrella — do not boil the ocean day one.",
    },
    "SM-04": {
        "name": "PolicyPack",
        "example": 4,
        "category": "Dedicated AI governance",
        "buyer": "AI governance lead, GRC, legal (regulated AI)",
        "wins": "Policy packs as product — EU AI Act, NIST, ISO 42001 pre-mapped",
        "artifact": "Policy pack activation, risk register, automated AI evidence",
        "gtm": "Design-partner → enterprise; marketplace accelerators",
        "signal": "Gartner/Forrester cited; OEM partnership pattern",
        "nf": "S2 policy/receipt complement + S6 exportable diligence",
        "pattern": "policy-pack",
        "golden": "Policy mapping is the door; signed TLE receipt is the lock — ship orientation, not legal advice.",
    },
    "SM-05": {
        "name": "LifecycleGov",
        "example": 5,
        "category": "Enterprise AI lifecycle GRC",
        "buyer": "CRO, model risk, federal/regulated enterprise",
        "wins": "Incumbent stack extension — govern models/agents in existing estate",
        "artifact": "AI factsheets, bias/drift monitoring, FedRAMP path, accelerators",
        "gtm": "Sell through enterprise accounts + marketplace add-ons",
        "signal": "FedRAMP authorization; agent monitoring 2026",
        "nf": "S5 federal lane + lifecycle evidence depth",
        "pattern": "lifecycle-evidence",
        "golden": "Enterprise pays for committee artifacts — price the board PDF, not the API call.",
    },
    "SM-06": {
        "name": "StackAttach",
        "example": 6,
        "category": "ITSM/GRC incumbent attach",
        "buyer": "CIO/CISO on existing platform stack",
        "wins": "Govern inside the stack you already run — no rip-and-replace",
        "artifact": "Control dashboards, policy hooks, ITSM-linked risk",
        "gtm": "Platform attach on existing procurement",
        "signal": "Wins where incumbent is system of record",
        "nf": "S2 complement-not-replace positioning",
        "pattern": "registry-vs-receipt",
        "golden": "Registry is theirs; receipt is yours — evaluate before external systems act.",
    },
    "SM-07": {
        "name": "ComplianceCode",
        "example": 7,
        "category": "Continuous controls monitoring (CCM)",
        "buyer": "CISO, federal, Fortune 500 GRC",
        "wins": "Compliance-as-code + agents — OSCAL-native live assurance",
        "artifact": "Live control state, self-updating paperwork, API-first evidence",
        "gtm": "Federal + F500; Series B scale signal",
        "signal": "300% revenue growth; 140% NRR; 90% faster cert claims",
        "nf": "S0 measurable time-to-proof + S7 automation depth",
        "pattern": "continuous-controls",
        "golden": "60% audit-prep reduction is the market bar — match via export automation.",
    },
    "SM-08": {
        "name": "AgenticGRC",
        "example": 8,
        "category": "AI-native agentic GRC",
        "buyer": "Enterprise GRC (healthcare, tech, FS)",
        "wins": "Purpose-built agents per workflow — not bolt-on AI",
        "artifact": "16+ agents expanding; 100+ frameworks orientation",
        "gtm": "Stealth → Series A; Fortune 500 design wins",
        "signal": "$28M raised; 70% less manual GRC positioning",
        "nf": "S8 agentic ops (internal) + S0 pilot proof",
        "pattern": "agentic-grc",
        "golden": "Agents help GRC teams internally; outreach stays in Hub only (R-011).",
    },
    "SM-09": {
        "name": "EnterpriseGRC",
        "example": 9,
        "category": "Enterprise GRC suite",
        "buyer": "Global banks, insurers, energy, Fortune 500",
        "wins": "AI-first GRC at scale — board reporting + regulatory feeds",
        "artifact": "Enterprise risk register, regulatory change feeds, exec dashboards",
        "gtm": "Long enterprise cycles; analyst-led",
        "signal": "IDC MarketScape Leader 2026; AI productivity ROI",
        "nf": "S5 regulated ICP + board-level reporting",
        "pattern": "board-reporting",
        "golden": "FRFI shadow pilot is proof — no custody, no RPAA supervision claims.",
    },
    "SM-10": {
        "name": "GovernanceGraph",
        "example": 10,
        "category": "Dedicated AI governance automation",
        "buyer": "GRC + AI program owners (EU/multinational)",
        "wins": "Governance Graph — one control satisfies multiple frameworks",
        "artifact": "Cross-framework map, risk quantification, agent governance",
        "gtm": "Mid-market/enterprise hybrid; product-led demos",
        "signal": "Framework overlap math; dedicated AIGP positioning",
        "nf": "S6 receipt portability + framework mapping efficiency",
        "pattern": "governance-graph",
        "golden": "Customer #1 board PDF in a real meeting gates GTM validation — everything else is rehearsal.",
    },
}

PHASES = [
    {"num": 1, "id_start": 1, "sm": "SM-01", "title": "TrustUnlock — trust center → revenue unlock"},
    {"num": 2, "id_start": 101, "sm": "SM-02", "title": "MultiFramework — always audit-ready rhythm"},
    {"num": 3, "id_start": 201, "sm": "SM-03", "title": "TrustPlatform — enterprise trust umbrella"},
    {"num": 4, "id_start": 301, "sm": "SM-04", "title": "PolicyPack — EU AI Act + NIST policy products"},
    {"num": 5, "id_start": 401, "sm": "SM-05", "title": "LifecycleGov — AI lifecycle + federal depth"},
    {"num": 6, "id_start": 501, "sm": "SM-06", "title": "StackAttach — complement not replace"},
    {"num": 7, "id_start": 601, "sm": "SM-07", "title": "ComplianceCode — OSCAL + live controls"},
    {"num": 8, "id_start": 701, "sm": "SM-08", "title": "AgenticGRC — workflow agents (R-011 fenced)"},
    {"num": 9, "id_start": 801, "sm": "SM-09", "title": "EnterpriseGRC — regulated board reporting"},
    {"num": 10, "id_start": 901, "sm": "SM-10", "title": "GovernanceGraph — cross-framework dedup + Customer #1"},
]

ARCHETYPE_ORDER = ["SM-01", "SM-02", "SM-03", "SM-04", "SM-05", "SM-06", "SM-07", "SM-08", "SM-09", "SM-10"]


def step_id(n: int) -> str:
    return f"mr-{n:04d}"


def tier_for(idx: int) -> str:
    return "T1" if idx % 3 != 2 else "T2"


def render_phase(phase: dict, steps: list[tuple[str, str, str, str, str]]) -> str:
    sm = ARCHETYPES[phase["sm"]]
    lines = [
        f"## Phase {phase['num']} — {phase['title']} ({step_id(phase['id_start'])}–{step_id(phase['id_start'] + 99)})",
        "",
        f"**Archetype:** `{phase['sm']}` ({sm['name']}) · **Market example #{sm['example']}**",
        f"**Category:** {sm['category']}",
        f"**Primary buyer:** {sm['buyer']}",
        f"**What wins:** {sm['wins']}",
        f"**Proof artifact:** {sm['artifact']}",
        f"**GTM motion:** {sm['gtm']}",
        f"**2026 signal:** {sm['signal']}",
        f"**Noetfield pattern:** {sm['nf']}",
        "",
        f"**Golden rule:** {sm['golden']}",
        "",
        "| ID | T | L | Plan | Outcome | Verify | Pattern |",
        "|----|---|---|------|---------|--------|---------|",
    ]
    for i, (plan, outcome, verify, pattern, lane) in enumerate(steps, start=1):
        global_n = phase["id_start"] + i - 1
        lines.append(
            f"| {step_id(global_n)} | {tier_for(i)} | {lane} | {plan} | {outcome} | {verify} | {pattern} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    lines = [
        "# Market success model roadmap — 1000 steps × 10 phases (v2)",
        "",
        "**Status:** Strategic execution roadmap — **internal only** · not www copy without Form PICK",
        "**Path:** `docs/strategy/MARKET_SUCCESS_1000_ROADMAP_v1.md`",
        "**Updated:** 2026-06-03",
        "**Generator:** `scripts/generate_market_success_1000_roadmap.py` + `scripts/market_success_1000_steps_data.py`",
        "**Grounding:** [MARKET_ANALYSIS_2026_LOCKED_v1.md](./MARKET_ANALYSIS_2026_LOCKED_v1.md) · [SUCCESS_MODEL_TIERS_v1.md](../ops/plans/PROMPT_PACK_LOCKED/SUCCESS_MODEL_TIERS_v1.md)",
        "",
        "> **Client-safe rule:** Archetypes **SM-01–SM-10** map to June 2026 market examples **#1–#10** — **no vendor names** in repo or www. Use pattern language externally.",
        "",
        "---",
        "",
        "## Executive summary",
        "",
        "June 2026 governance spend (~$2.5B category) rewards **continuous proof**, **policy packs** (EU AI Act Aug 2 2026), **stack complementarity**, and **portable diligence** — not dashboards alone.",
        "",
        "**Noetfield's unique lane:** signed **RID-keyed Trust Ledger receipt** exported **before** workspace/Copilot acts — receipt layer, not full GRC replacement. None of the ten market archetypes lead here.",
        "",
        "### Archetype index (market examples #1–#10)",
        "",
        "| Ex | SM ID | Codename | What wins | Proof artifact | Noetfield tier |",
        "|----|-------|----------|-----------|----------------|----------------|",
    ]
    for sm_id in ARCHETYPE_ORDER:
        m = ARCHETYPES[sm_id]
        lines.append(
            f"| {m['example']} | {sm_id} | {m['name']} | {m['wins']} | {m['artifact']} | {m['nf']} |"
        )

    lines.extend([
        "",
        "### Five archetype clusters (what works in 2026)",
        "",
        "| Cluster | Archetypes | Buyer pays for | Proof moment |",
        "|---------|------------|----------------|--------------|",
        "| **A — Trust unlock** | SM-01, SM-02 | Faster sales + fewer questionnaires | Prospect self-serves diligence in trust center |",
        "| **B — AI policy product** | SM-04, SM-10 | EU AI Act / NIST readiness without building policy from scratch | Activated policy pack + evidence bundle |",
        "| **C — Incumbent attach** | SM-05, SM-06, SM-03 | Govern inside current stack | Dashboard inside existing procurement |",
        "| **D — Continuous assurance** | SM-07, SM-02 | Live controls vs point-in-time audit | Cert faster; audit prep reduced via automation |",
        "| **E — Agentic GRC** | SM-08 | Agents per workflow | GRC team hours saved on chores |",
        "",
        "### Golden insights (locked)",
        "",
        "1. **Receipt before execution** — category creation; none of #1–#10 lead with signed TLE + board PDF.",
        "2. **Trust center = revenue** (SM-01) — every tier page links trust center + procurement ZIP.",
        "3. **Continuous beats annual** (SM-02, SM-07) — `last_verified_at` + honest badges.",
        "4. **EU AI Act Aug 2, 2026** (SM-04, SM-10) — policy packs are the urgency door.",
        "5. **Complement only** (SM-06) — registry is theirs; receipt is yours.",
        "6. **Enterprise = artifacts** (SM-05, SM-09) — Trust Brief $10K · design partner CAD $2K+.",
        "7. **OSCAL/API federal path** (SM-07) — FRFI shadow without custody.",
        "8. **Agentic = internal** (SM-08) — R-011 fences outreach to Hub.",
        "9. **MSP = scale** (SM-01 GTM motion) — one partner board PDF beats ten demos.",
        "10. **Customer #1 gates all** (Phase 10) — GTM 2/10 until real governance meeting uses export.",
        "",
        "### Noetfield tier ↔ market proof",
        "",
        "| Noetfield tier | Market proof |",
        "|----------------|--------------|",
        "| S0 board PDF moment | SM-01/02 trust centers — buyers need defensible artifacts |",
        "| S4 trust center grid | SM-01/03 framework grids close diligence |",
        "| S6 receipt export wedge | SM-04/07 portable evidence to legal/procurement |",
        "| S2 complement not replace | SM-05/06 attach to workspace/registry rails |",
        "| S3 MSP channel | SM-01 partner ecosystem beats solo founder sales |",
        "",
        "### Pick order (PLAN WITH NO ASF)",
        "",
        "| Priority | Phases | Archetypes | Why |",
        "|----------|--------|------------|-----|",
        "| P0 | 1 → 4 → 6 | SM-01, SM-04, SM-06 | Trust + policy + complement = buyer proof |",
        "| P1 | 3 → 5 → 7 | SM-03, SM-05, SM-07 | Enterprise + lifecycle + live controls |",
        "| P2 | 2 → 8 → 9 | SM-02, SM-08, SM-09 | Rhythm + agentic + regulated scale |",
        "| P3 | 10 | SM-10 | Graph dedup + Customer #1 proof log |",
        "",
        "**Rule:** ≤3 tasks per iter · max 2 S0-proof picks · no vendor names on www.",
        "",
        "---",
        "",
    ])

    for phase, steps in zip(PHASES, ALL_PHASE_STEPS):
        lines.append(render_phase(phase, steps))

    lines.extend([
        "---",
        "",
        "## Suggested first 10 picks",
        "",
        "| Pick | ID | Archetype | Action |",
        "|------|-----|-----------|--------|",
        "| 1 | mr-0001 | SM-01 | Trust center hero + shadow fence |",
        "| 2 | mr-0011 | SM-01 | last_verified_at on control rows |",
        "| 3 | mr-0031 | SM-01 | Honest certification posture audit |",
        "| 4 | mr-0201 | SM-03 | Enterprise trust umbrella nav |",
        "| 5 | mr-0301 | SM-04 | EU AI Act policy pack block |",
        "| 6 | mr-0501 | SM-06 | Registry-vs-receipt complement strip |",
        "| 7 | mr-0601 | SM-07 | OSCAL export stub in procurement ZIP |",
        "| 8 | mr-0701 | SM-08 | Questionnaire deflection agent (internal) |",
        "| 9 | mr-0801 | SM-09 | OSFI E-23 committee script |",
        "| 10 | mr-0907 | SM-10 | Customer #1 proof log + Form PICK |",
        "",
        "## Related",
        "",
        "- [INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md](./INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md)",
        "- [POSITIONING_CLIENT_SYNTHESIS_v1.md](../diligence/POSITIONING_CLIENT_SYNTHESIS_v1.md)",
        "- [NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md](../ops/NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md)",
        "",
    ])

    OUT.write_text("\n".join(lines), encoding="utf-8")
    count = sum(1 for ln in OUT.read_text().splitlines() if ln.startswith("| mr-"))
    print(f"Wrote {OUT} ({count} steps)")


if __name__ == "__main__":
    main()
