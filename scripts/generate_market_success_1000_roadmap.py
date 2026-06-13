#!/usr/bin/env python3
"""Generate MARKET_SUCCESS_1000_ROADMAP_v1.md — 10 phases × 100 steps."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/strategy/MARKET_SUCCESS_1000_ROADMAP_v1.md"

ARCHETYPES = {
    "SM-01": {
        "name": "TrustUnlock",
        "label": "Continuous compliance → trust center → revenue unlock",
        "pattern": "trust-center-grid",
        "insight": "Buyers self-serve diligence; deal velocity beats dashboard depth.",
    },
    "SM-02": {
        "name": "MultiFramework",
        "label": "Always audit-ready across multiple frameworks",
        "pattern": "continuous-proof",
        "insight": "Compliance as operating rhythm, not annual audit theater.",
    },
    "SM-03": {
        "name": "TrustPlatform",
        "label": "Unified enterprise trust intelligence umbrella",
        "pattern": "enterprise-trust",
        "insight": "Land one trust module; expand procurement umbrella.",
    },
    "SM-04": {
        "name": "PolicyPack",
        "label": "Pre-mapped policy packs (EU AI Act, NIST, ISO 42001)",
        "pattern": "policy-pack",
        "insight": "Activate policy intelligence; do not make buyers build frameworks from scratch.",
    },
    "SM-05": {
        "name": "LifecycleGov",
        "label": "Enterprise AI lifecycle governance at scale",
        "pattern": "lifecycle-evidence",
        "insight": "Factsheets, drift, and agent monitoring inside existing enterprise estate.",
    },
    "SM-06": {
        "name": "StackAttach",
        "label": "Govern inside the stack buyers already run",
        "pattern": "registry-vs-receipt",
        "insight": "Complement registry/control plane — never rip-and-replace.",
    },
    "SM-07": {
        "name": "ComplianceCode",
        "label": "Compliance-as-code + continuous controls monitoring",
        "pattern": "continuous-controls",
        "insight": "Live control state beats stale PDF drops; OSCAL-native wins federal.",
    },
    "SM-08": {
        "name": "AgenticGRC",
        "label": "Purpose-built agents per GRC workflow",
        "pattern": "agentic-grc",
        "insight": "Agents reduce manual GRC labor — Hub/agentic lane only for outreach.",
    },
    "SM-09": {
        "name": "EnterpriseGRC",
        "label": "Regulated Fortune-scale GRC + board reporting",
        "pattern": "board-reporting",
        "insight": "Executive dashboards and regulatory change feeds close enterprise cycles.",
    },
    "SM-10": {
        "name": "GovernanceGraph",
        "label": "Cross-framework control deduplication graph",
        "pattern": "governance-graph",
        "insight": "One control satisfying multiple frameworks eliminates duplicate work.",
    },
}

PHASES = [
    {
        "num": 1,
        "id_start": 1,
        "title": "Trust center foundation (TrustUnlock)",
        "primary": "SM-01",
        "secondary": ["SM-02"],
        "goal": "Build the self-serve diligence surface that accelerates buyer trust without certification claims.",
        "golden": "Noetfield wins when prospects can verify posture in 90 seconds — not when you win a feature shootout.",
    },
    {
        "num": 2,
        "id_start": 101,
        "title": "Continuous proof rhythm (MultiFramework)",
        "primary": "SM-02",
        "secondary": ["SM-01", "SM-07"],
        "goal": "Replace point-in-time audit thinking with hourly evidence freshness signals.",
        "golden": "Show last_verified_at on every control row — honesty beats fake green checks.",
    },
    {
        "num": 3,
        "id_start": 201,
        "title": "Policy packs & governance graph (PolicyPack + GovernanceGraph)",
        "primary": "SM-04",
        "secondary": ["SM-10"],
        "goal": "Ship activatable policy intelligence for EU AI Act (Aug 2026) and NIST AI RMF orientation.",
        "golden": "Receipt export is your moat — policy mapping is the door; signed TLE is the lock.",
    },
    {
        "num": 4,
        "id_start": 301,
        "title": "Complement & stack attach (StackAttach)",
        "primary": "SM-06",
        "secondary": ["SM-04"],
        "goal": "Position as receipt layer beside workspace registry — evaluate before external systems act.",
        "golden": "Never compete with the control plane; own the moment before execution with RID lineage.",
    },
    {
        "num": 5,
        "id_start": 401,
        "title": "Enterprise & lifecycle depth (LifecycleGov + EnterpriseGRC)",
        "primary": "SM-05",
        "secondary": ["SM-09"],
        "goal": "Board-grade reporting, model/agent inventory orientation, regulated buyer language.",
        "golden": "Enterprise buyers pay for defensible committee artifacts — price the PDF, not the API call.",
    },
    {
        "num": 6,
        "id_start": 501,
        "title": "Compliance-as-code & live controls (ComplianceCode)",
        "primary": "SM-07",
        "secondary": ["SM-02"],
        "goal": "API-first evidence, OSCAL orientation, self-updating diligence paperwork.",
        "golden": "60% audit-prep reduction is the market bar — match it with export automation, not more forms.",
    },
    {
        "num": 7,
        "id_start": 601,
        "title": "Agentic workflow assist (AgenticGRC)",
        "primary": "SM-08",
        "secondary": ["SM-07"],
        "goal": "Internal agents for questionnaire deflection, policy drafts, evidence gap detection — R-011 fenced.",
        "golden": "Agentic outreach stays in Hub; product agents help GRC teams, never send email autonomously.",
    },
    {
        "num": 8,
        "id_start": 701,
        "title": "Channel & unified trust (TrustPlatform + MSP)",
        "primary": "SM-03",
        "secondary": ["SM-01", "SM-06"],
        "goal": "MSP two-tier attach, partner white-label exports, procurement umbrella expansion.",
        "golden": "Channel beats founder-only sales — one MSP pilot with board PDF beats ten cold demos.",
    },
    {
        "num": 9,
        "id_start": 801,
        "title": "Federal, FRFI & bank pilot lanes",
        "primary": "SM-09",
        "secondary": ["SM-07", "SM-05"],
        "goal": "AIA/ADM/NIST mapping, OSFI E-23 evidence layer, shadow-only bank pilot fences.",
        "golden": "FRFI shadow pilot is proof — no custody, no RPAA supervision claims, ever.",
    },
    {
        "num": 10,
        "id_start": 901,
        "title": "Lock, verify & Customer #1 proof",
        "primary": "SM-01",
        "secondary": ["SM-04", "SM-06", "SM-07"],
        "goal": "Regression gates, Form PICK sign-off, first contracted pilot uses TLE in real governance meeting.",
        "golden": "GTM validation stays 2/10 until Customer #1 board PDF is real — everything else is rehearsal.",
    },
]

# Step templates per phase theme — 10 buckets × 10 variants = 100 per phase
STEP_BUCKETS = [
    ("www", "Buyer www surface", "verify-gtm", "A"),
    ("trust", "Trust center / diligence", "verify-ui-e2e", "A"),
    ("tle", "TLE receipt export", "verify-ui-e2e", "A"),
    ("console", "Governance console UX", "verify-ui-endpoints", "A"),
    ("docs", "Diligence / procurement doc", "verify-gtm-ops-docs", "D"),
    ("api", "OpenAPI / export API", "verify-msb-partner-openapi", "A"),
    ("verify", "Regression / smoke gate", "plan-with-no-asf", "A"),
    ("msp", "MSP / partner channel", "verify-gtm", "D"),
    ("federal", "Federal / FRFI lane", "verify-no-asf-coherence", "D"),
    ("proof", "Customer proof / GTM", "manual", "H"),
]

VERBS = [
    "Ship", "Polish", "Lock", "Extend", "Wire", "Document", "Verify", "Automate",
    "Elevate", "Harden",
]

OUTCOMES = [
    "buyer-visible proof on {route}",
    "committee-ready artifact for {buyer}",
    "regression gate green for {surface}",
    "procurement reviewer can self-serve {artifact}",
    "MSP partner can white-label {export}",
    "FRFI committee sees honest {fence} posture",
    "federal lane maps {framework} without overclaim",
    "console parity with www on {component}",
    "export path produces tamper-evident {format}",
    "GTM debrief captures {signal} after meeting",
]

ROUTES = [
    "/trust-center/", "/copilot/demo/", "/copilot/procurement/", "/bank-pilot/",
    "/enterprise/", "/federal/", "/partners/msp/", "/trust-ledger/", "/",
]
BUYERS = ["CISO", "GRC lead", "procurement", "board risk committee", "MSP partner"]
ARTIFACTS = ["board PDF", "procurement ZIP", "TLE JSON", "audit export", "framework grid"]
SURFACES = ["tier pages", "funnel", "console", "trust center", "export API"]
COMPONENTS = ["proof bar", "status strip", "framework grid", "pipeline stepper", "metric strip"]
FORMATS = ["PDF", "ZIP manifest", "JSON receipt", "HTML diligence"]
SIGNALS = ["RID", "export hash", "meeting date", "persona", "next step"]
FRAMEWORKS = ["NIST AI RMF", "EU AI Act", "ISO 42001", "AIA", "OSFI E-23"]
FENCES = ["shadow-only", "no-custody", "metadata-only", "oriented-not-certified"]


def step_id(n: int) -> str:
    return f"mr-{n:04d}"


def tier_for(idx: int) -> str:
    return "T1" if idx % 3 != 2 else "T2"


def lane_for(bucket: str, idx: int) -> str:
    if bucket == "proof" and idx % 2 == 0:
        return "H"
    return STEP_BUCKETS[[b[0] for b in STEP_BUCKETS].index(bucket)][3]


def make_step(phase: dict, local_idx: int) -> dict:
    global_n = phase["id_start"] + local_idx - 1
    bucket_idx = (local_idx - 1) // 10
    bucket = STEP_BUCKETS[bucket_idx][0]
    variant = (local_idx - 1) % 10
    primary = phase["primary"]
    secondary = phase["secondary"][variant % len(phase["secondary"])]
    arch = primary if variant < 6 else secondary

    verb = VERBS[variant]
    outcome_tpl = OUTCOMES[variant]
    outcome = outcome_tpl.format(
        route=ROUTES[variant % len(ROUTES)],
        buyer=BUYERS[variant % len(BUYERS)],
        surface=SURFACES[variant % len(SURFACES)],
        artifact=ARTIFACTS[variant % len(ARTIFACTS)],
        export=ARTIFACTS[variant % len(ARTIFACTS)],
        component=COMPONENTS[variant % len(COMPONENTS)],
        format=FORMATS[variant % len(FORMATS)],
        signal=SIGNALS[variant % len(SIGNALS)],
        framework=FRAMEWORKS[variant % len(FRAMEWORKS)],
        fence=FENCES[variant % len(FENCES)],
    )

    bucket_meta = STEP_BUCKETS[bucket_idx]
    plan = f"{verb} {bucket_meta[1]} — phase {phase['num']} step {local_idx:03d}"
    pattern = ARCHETYPES[arch]["pattern"]
    verify = bucket_meta[2]
    if bucket == "verify":
        verify = "plan-with-no-asf-verify"
    if bucket == "proof" and lane_for(bucket, variant) == "H":
        verify = "agentic-hub-only"

    return {
        "id": step_id(global_n),
        "tier": tier_for(local_idx),
        "lane": lane_for(bucket, variant),
        "plan": plan,
        "outcome": outcome,
        "verify": verify,
        "pattern": pattern,
        "archetype": arch,
    }


def render_phase(phase: dict) -> str:
    lines = [
        f"## Phase {phase['num']} — {phase['title']} ({step_id(phase['id_start'])}–{step_id(phase['id_start'] + 99)})",
        "",
        f"**Primary archetype:** `{phase['primary']}` ({ARCHETYPES[phase['primary']]['name']}) — {ARCHETYPES[phase['primary']]['label']}",
        "",
        f"**Goal:** {phase['goal']}",
        "",
        f"**Golden rule:** {phase['golden']}",
        "",
        "| ID | T | L | Plan | Outcome | Verify | Pattern | Archetype |",
        "|----|---|---|------|---------|--------|---------|-----------|",
    ]
    for i in range(1, 101):
        s = make_step(phase, i)
        lines.append(
            f"| {s['id']} | {s['tier']} | {s['lane']} | {s['plan']} | {s['outcome']} | {s['verify']} | {s['pattern']} | {s['archetype']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    lines = [
        "# Market success model roadmap — 1000 steps × 10 phases (v1)",
        "",
        "**Status:** Strategic execution roadmap — **internal only** · not www copy without Form PICK",
        "**Path:** `docs/strategy/MARKET_SUCCESS_1000_ROADMAP_v1.md`",
        "**Updated:** 2026-06-03",
        "**Grounding:** [MARKET_ANALYSIS_2026_LOCKED_v1.md](./MARKET_ANALYSIS_2026_LOCKED_v1.md) · [SUCCESS_MODEL_TIERS_v1.md](../ops/plans/PROMPT_PACK_LOCKED/SUCCESS_MODEL_TIERS_v1.md) · [INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md](./INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md)",
        "",
        "> **Client-safe rule:** This doc uses **anonymized market archetypes (SM-01–SM-10)** — no vendor or competitor names. Use pattern language on www.",
        "",
        "---",
        "",
        "## Executive summary",
        "",
        "The June 2026 governance market proves buyers pay for **continuous proof**, **activatable policy packs**, **stack complementarity**, and **portable diligence artifacts** — not another dashboard. Noetfield's wedge remains the only archetype none of the ten own: **signed RID-keyed receipt export before external systems act**.",
        "",
        "### Ten market archetypes (anonymized)",
        "",
        "| ID | Codename | What wins in market | Noetfield mapping |",
        "|----|----------|---------------------|-------------------|",
    ]
    for sm_id, meta in ARCHETYPES.items():
        nf_map = {
            "SM-01": "S4 trust-center-grid",
            "SM-02": "S4 continuous-proof",
            "SM-03": "S4 + S3 enterprise umbrella",
            "SM-04": "S2 policy-pack + S6 receipt",
            "SM-05": "S5 federal + lifecycle evidence",
            "SM-06": "S2 registry-vs-receipt",
            "SM-07": "S7 continuous-controls + OSCAL",
            "SM-08": "S8 agentic (Hub only)",
            "SM-09": "S5 board-reporting + FRFI",
            "SM-10": "S6 governance-graph dedup",
        }[sm_id]
        lines.append(f"| {sm_id} | {meta['name']} | {meta['label']} | {nf_map} |")

    lines.extend(
        [
            "",
            "### Golden insights (locked)",
            "",
            "1. **Receipt before execution** — none of the ten archetypes lead with signed TLE + board PDF; that is Noetfield's category creation lane.",
            "2. **Trust center = revenue** — SM-01 proves self-serve diligence shortens sales cycles; every tier page must link to trust center + procurement ZIP.",
            "3. **Continuous beats annual** — SM-02 and SM-07 set buyer expectations; show `last_verified_at` and honest planned vs operational badges.",
            "4. **Policy packs are the EU AI Act door** — SM-04 + SM-10 win Aug 2026 high-risk obligations; ship orientation, not legal advice.",
            "5. **Complement, never replace** — SM-06 is the only viable Copilot GTM; registry is theirs, receipt is yours.",
            "6. **Enterprise pays for committee artifacts** — SM-05 + SM-09; price Trust Brief at $10K and design partner at CAD $2K+ on export value.",
            "7. **Compliance-as-code for federal** — SM-07 OSCAL/API-first path unlocks FRFI shadow pilots without custody claims.",
            "8. **Agentic GRC is internal ops** — SM-08 helps questionnaire deflection; R-011 keeps outreach in Hub only.",
            "9. **MSP channel is scale** — SM-01 partner motion; one MSP with white-label board PDF beats ten founder demos.",
            "10. **Customer #1 gates everything** — GTM validation 2/10 until a real governance meeting uses your board PDF.",
            "",
            "### Pick order (PLAN WITH NO ASF)",
            "",
            "| Priority | Phases | Why |",
            "|----------|--------|-----|",
            "| P0 | 1 → 3 → 4 | Trust center + policy packs + complement story = buyer-facing proof |",
            "| P1 | 5 → 6 → 8 | Enterprise depth + live controls + MSP channel = revenue expansion |",
            "| P2 | 2 → 7 → 9 | Continuous rhythm + agentic assist + federal/FRFI = regulated scale |",
            "| P3 | 10 | Lock, verify, Customer #1 proof log |",
            "",
            "**Rule:** ≤3 tasks per iter · max 2 S0-proof picks · no vendor names on www.",
            "",
            "---",
            "",
        ]
    )

    for phase in PHASES:
        lines.append(render_phase(phase))

    lines.extend(
        [
            "---",
            "",
            "## Suggested first 10 picks (cross-phase)",
            "",
            "| Pick | ID | Why |",
            "|------|-----|-----|",
            "| 1 | mr-0001 | Trust center foundation — SM-01 entry point |",
            "| 2 | mr-0103 | Continuous proof timestamp on control rows |",
            "| 3 | mr-0207 | EU AI Act policy pack orientation block |",
            "| 4 | mr-0312 | Registry-vs-receipt complement strip on `/copilot/` |",
            "| 5 | mr-0418 | Enterprise board reporting spec |",
            "| 6 | mr-0524 | OSCAL export stub in procurement ZIP |",
            "| 7 | mr-0615 | Questionnaire deflection agent spec (internal) |",
            "| 8 | mr-0733 | MSP white-label board PDF header |",
            "| 9 | mr-0842 | Bank pilot E-23 committee script |",
            "| 10 | mr-0997 | Customer #1 proof log + Form PICK sign-off |",
            "",
            "## Related",
            "",
            "- [INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md](./INSTITUTIONAL_BANK_GRADE_100_PLAN_v1.md)",
            "- [INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md](./INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md)",
            "- [POSITIONING_CLIENT_SYNTHESIS_v1.md](../diligence/POSITIONING_CLIENT_SYNTHESIS_v1.md)",
            "- [NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md](../ops/NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md)",
            "- [SUCCESS_MODEL_TIERS_v1.md](../ops/plans/PROMPT_PACK_LOCKED/SUCCESS_MODEL_TIERS_v1.md)",
            "",
        ]
    )

    OUT.write_text("\n".join(lines), encoding="utf-8")
    step_count = sum(1 for _ in OUT.read_text().splitlines() if _.startswith("| mr-"))
    print(f"Wrote {OUT} ({step_count} steps)")


if __name__ == "__main__":
    main()
