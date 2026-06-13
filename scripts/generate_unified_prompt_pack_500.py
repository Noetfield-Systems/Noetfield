#!/usr/bin/env python3
"""Analyze + emit unified 500 forward-queue index — v4 wisdom engine."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

QUEUE_FILES = (
    ("v1", "docs/strategy/NOETFIELD_FORWARD_QUEUE_100_v1.md", "mixed"),
    ("v2", "docs/strategy/NOETFIELD_FORWARD_QUEUE_100_v2.md", "mixed"),
    ("v3", "docs/strategy/NOETFIELD_FORWARD_QUEUE_100_v3.md", "mixed"),
    ("v4", "docs/strategy/NOETFIELD_FORWARD_QUEUE_100_v4_FEDERAL.md", "F"),
    ("v5", "docs/strategy/NOETFIELD_FORWARD_QUEUE_100_v5_MSP.md", "M"),
)

ROW_RE = re.compile(
    r"^\| (ship-fwd-\d+) \| (\d+) \| (T\d) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|"
)

# Weighted keywords — (keyword, weight)
SUCCESS_TIER_KEYWORDS: dict[str, tuple[tuple[str, int], ...]] = {
    "S0-proof": (
        ("board pack", 4), ("5-min", 4), ("5 minute", 4), ("demo", 3), ("quickscan", 3),
        ("procurement", 3), ("confidence", 3), ("playwright", 3), ("smoke suite", 3),
        ("verify-ui", 3), ("workspace", 2), ("pilot sow", 3), ("demo-url", 3),
        ("board pdf", 4), ("export", 2), ("evaluate", 2),
    ),
    "S1-positioning": (
        ("homepage", 3), ("positioning", 3), ("hero", 2), ("copy", 2), ("one-pager", 3),
        ("buyer deck", 3), ("meta refresh", 2), ("seo", 2),
    ),
    "S2-copilot-complement": (
        ("agent 365", 4), ("purview", 4), ("copilot", 3), ("m365", 2), ("registry", 2),
        ("microsoft", 2), ("entra", 2),
    ),
    "S3-msp-channel": (
        ("msp", 3), ("partner", 2), ("gdap", 3), ("white-label", 3), ("csp", 2),
        ("channel", 2), ("pax8", 3), ("90-day", 3), ("partner-verify", 4), ("partner-demo", 3),
    ),
    "S4-trust-ui": (
        ("trust center", 4), ("trust-center", 4), ("control checkpoint", 3),
        ("framework", 2), ("diligence", 3), ("procurement zip", 3), ("security faq", 2),
        ("posture", 2),
    ),
    "S5-federal": (
        ("federal", 3), ("aia", 3), ("adm", 2), ("fedramp", 3), ("osfi", 2),
        ("frfi", 2), ("e-23", 2), ("bank pilot", 3), ("omb", 2), ("nist", 2),
    ),
    "S6-tle-wedge": (
        ("trust ledger", 4), ("tle", 3), ("audit-export", 3), ("immutable", 2),
        ("rid", 2), ("compare", 2), ("tamper", 3), ("receipt", 3),
    ),
    "S7-hardening": (
        ("pytest", 2), ("coherence", 2), ("manifest", 2), ("registry", 1),
        ("openapi", 2), ("load test", 2), ("perf", 2), ("ssot", 2),
    ),
    "S8-agentic": (
        ("outreach", 4), ("hub", 2), ("agentic", 4), ("n8n", 3), ("tracker row", 3),
    ),
}

TIER_PICK_ORDER = {
    "S0-proof": 0,
    "S6-tle-wedge": 1,
    "S2-copilot-complement": 2,
    "S4-trust-ui": 3,
    "S1-positioning": 4,
    "S3-msp-channel": 5,
    "S5-federal": 6,
    "S7-hardening": 7,
    "S8-agentic": 8,
}

GTM_BASE = {
    "S0-proof": 100,
    "S6-tle-wedge": 88,
    "S2-copilot-complement": 82,
    "S4-trust-ui": 78,
    "S1-positioning": 65,
    "S3-msp-channel": 72,
    "S5-federal": 70,
    "S7-hardening": 45,
    "S8-agentic": 40,
}

LANE_TO_ICP = {
    "A": "disk",
    "D": "docs",
    "H": "hub",
    "F+A": "federal-disk",
    "F+D": "federal-docs",
    "F+H": "federal-hub",
    "M+A": "msp-disk",
    "M+D": "msp-docs",
    "M+H": "msp-hub",
}

# Filesystem hints for partial/shipped inference
PATH_ARTIFACTS: tuple[tuple[str, str], ...] = (
    ("/partners/msp/", "partners/msp/index.html"),
    ("/federal/", "federal/index.html"),
    ("/trust-center/", "trust-center/index.html"),
    ("/bank-pilot/", "bank-pilot/index.html"),
    ("/enterprise/", "enterprise/index.html"),
    ("/copilot/demo/", "copilot/demo/index.html"),
    ("/copilot/procurement/", "copilot/procurement/index.html"),
)

PRE_READ_BY_TIER: dict[str, tuple[str, ...]] = {
    "S0-proof": (
        "MEMORY_LOCKED.yaml",
        "INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md",
        "NOETFIELD_GTM_60_DAY_LOCKED_v1.md",
    ),
    "S6-tle-wedge": (
        "MEMORY_LOCKED.yaml",
        "TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md",
        "POSITIONING_CLIENT_SYNTHESIS_v1.md",
    ),
    "S2-copilot-complement": (
        "MEMORY_LOCKED.yaml",
        "COPILOT_COMPLEMENT_GUIDE_v1.md",
        "NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md",
    ),
    "S4-trust-ui": (
        "MEMORY_LOCKED.yaml",
        "INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md",
        "PAGE_AUTHORITY_MAP.md",
    ),
    "S1-positioning": (
        "MEMORY_LOCKED.yaml",
        "PRODUCT_TRUTH.md",
        "POSITIONING_CLIENT_SYNTHESIS_v1.md",
    ),
    "S3-msp-channel": (
        "MEMORY_LOCKED.yaml",
        "NOETFIELD_FORWARD_QUEUE_100_v5_MSP.md",
        "partners/msp/index.html",
    ),
    "S5-federal": (
        "MEMORY_LOCKED.yaml",
        "FEDERAL_AIA_ADM_NIST_v1.md",
        "federal/index.html",
    ),
    "S7-hardening": (
        "MEMORY_LOCKED.yaml",
        "ENGINEERING_DONE_MANIFEST.md",
    ),
    "S8-agentic": (
        "FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md",
        "AGENTIC_COMMERCIAL_HANDOFF_v1.md",
    ),
}

STOP_ALWAYS = (
    "No TrustField bleed (R-001)",
    "No RPAA / BoC supervision claims on www",
    "No Hub send/call from NF-CLOUD (R-011)",
    "≤3 tasks per PLAN WITH NO ASF iter",
)

ANTI_SCOPE = (
    "SSO / multi-tenant hardening (Tier C)",
    "Real M365 read-only before customer #2 (Tier B)",
    "Drift ML implementation (P9)",
    "Infrastructure sprawl unrelated to outcome",
)

# Success patterns — maps tiers to internal pattern labels + 10-step plan
PATTERN_BY_TIER: dict[str, dict[str, str | int | tuple[str, ...]]] = {
    "S0-proof": {
        "refs": ("board-pdf-moment", "demo-path", "procurement-zip"),
        "step": 5,
        "wedge": "5-min board PDF moment — buyer sees confidence + export path",
        "goal": "customer_1",
    },
    "S6-tle-wedge": {
        "refs": ("receipt-export-wedge", "rid-lineage", "tamper-verify"),
        "step": 7,
        "wedge": "One receipt board, auditor, and MSP cite — same RID",
        "goal": "tle_wedge",
    },
    "S2-copilot-complement": {
        "refs": ("registry-vs-receipt", "metadata-index", "msp-evaluate"),
        "step": 3,
        "wedge": "Registry tells what exists; Noetfield tells what was permitted",
        "goal": "copilot_story",
    },
    "S4-trust-ui": {
        "refs": ("trust-center-grid", "framework-rows", "diligence-shortcut"),
        "step": 5,
        "wedge": "Honest framework grid — oriented not certified",
        "goal": "trust_diligence",
    },
    "S1-positioning": {
        "refs": ("buyer-hero", "receipt-wedge", "procurement-line"),
        "step": 2,
        "wedge": "Audit trail your Copilot deployment will be asked for",
        "goal": "positioning",
    },
    "S3-msp-channel": {
        "refs": ("msp-two-tier", "90-day-sow", "white-label-export"),
        "step": 4,
        "wedge": "MSP delivers receipt, not another dashboard",
        "goal": "msp_channel",
    },
    "S5-federal": {
        "refs": ("federal-framework-map", "aia-adm-nist", "vendor-layer-only"),
        "step": 6,
        "wedge": "Pre-execution evidence — vendor layer only",
        "goal": "federal_lane",
    },
    "S7-hardening": {
        "refs": ("engineering-hygiene",),
        "step": 10,
        "wedge": "Verify bundle stays green — no buyer story alone",
        "goal": "engineering",
    },
    "S8-agentic": {
        "refs": ("hub-commercial",),
        "step": 0,
        "wedge": "Founder Hub sends; NF-CLOUD never dials",
        "goal": "agentic",
    },
}

GTM_PHASE_BY_TIER = {
    "S0-proof": "P1-proof-moment",
    "S6-tle-wedge": "P2-tle-wedge",
    "S2-copilot-complement": "P3-copilot-story",
    "S4-trust-ui": "P4-trust-diligence",
    "S1-positioning": "P4-trust-diligence",
    "S3-msp-channel": "P5-channel",
    "S5-federal": "P5-channel",
    "S7-hardening": "P6-hardening",
    "S8-agentic": "P7-agentic",
}

# Locked Noetfield goals — keyword weights for alignment scoring
GOAL_ALIGNMENT_KEYWORDS: dict[str, tuple[tuple[str, int], ...]] = {
    "customer_1": (
        ("board", 5), ("demo", 4), ("procurement", 4), ("pilot", 4), ("quickscan", 3),
        ("confidence", 3), ("5-min", 4), ("governance meeting", 5),
    ),
    "tle_wedge": (
        ("export", 4), ("tamper", 5), ("receipt", 4), ("rid", 3), ("immutable", 3),
        ("audit-export", 4), ("board pdf", 4),
    ),
    "copilot_story": (
        ("agent 365", 4), ("purview", 4), ("registry", 3), ("copilot", 2), ("complement", 3),
    ),
    "trust_diligence": (
        ("trust center", 4), ("framework", 3), ("diligence", 4), ("control checkpoint", 3),
    ),
    "msp_channel": (
        ("msp", 3), ("partner", 2), ("sow", 4), ("gdap", 3), ("white-label", 3), ("90-day", 3),
    ),
    "federal_lane": (
        ("aia", 3), ("adm", 2), ("nist", 3), ("federal", 2), ("omb", 2),
    ),
}

# Proof-chain clusters — wise pick grouping
PICK_CLUSTERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("proof-demo", ("demo", "playwright", "quickscan", "governance meeting", "5-min", "demo-url", "smoke suite")),
    ("proof-export", ("tamper", "export", "board pack", "board pdf", "audit-export", "receipt", "tle")),
    ("copilot-registry", ("agent 365", "purview", "registry", "copilot", "m365")),
    ("trust-diligence", ("trust center", "trust-center", "framework", "diligence", "posture")),
    ("msp-channel", ("msp", "partner", "sow", "gdap", "white-label", "90-day", "partner-verify")),
    ("federal-lane", ("aia", "adm", "nist", "federal", "omb", "fedramp")),
    ("ops-hardening", ("pytest", "coherence", "openapi", "manifest", "ssot", "load test")),
)

# Ideal proof-chain order (wise sequence for customer #1)
PROOF_CHAIN_ORDER: tuple[str, ...] = (
    "governance meeting", "playwright", "quickscan", "demo-url", "tamper", "board pack", "export",
)


def classify_success_tier(plan: str, outcome: str, lane: str, icp_lane: str) -> str:
    blob = f"{plan} {outcome}".lower()
    if lane.endswith("+H") or lane == "H":
        return "S8-agentic"
    scores: list[tuple[int, str]] = []
    for tier, kws in SUCCESS_TIER_KEYWORDS.items():
        score = sum(w for k, w in kws if k in blob)
        if score:
            scores.append((score, tier))
    if not scores:
        if icp_lane == "F":
            return "S5-federal"
        if icp_lane == "M":
            return "S3-msp-channel"
        return "S7-hardening"
    scores.sort(reverse=True)
    best_score, best_tier = scores[0]
    # ICP lane is a soft bias, not a hard override when proof keywords dominate
    if icp_lane == "F" and best_score < 4:
        return "S5-federal"
    if icp_lane == "M" and best_score < 4:
        return "S3-msp-channel"
    return best_tier


def infer_ship_status(plan: str, outcome: str) -> str:
    blob = f"{plan} {outcome}".lower()
    for path_hint, artifact in PATH_ARTIFACTS:
        if path_hint.lower() in blob or path_hint.replace("/", "").strip() in blob:
            if (ROOT / artifact).is_file():
                return "partial"
    shipped_markers = ("**shipped**", "shipped —", "already shipped")
    if any(m in blob for m in shipped_markers):
        return "shipped"
    return "open"


def pattern_meta(row: dict) -> dict:
    tier = row["success_tier"]
    meta = PATTERN_BY_TIER.get(tier, PATTERN_BY_TIER["S7-hardening"])
    return {
        "pattern_refs": list(meta["refs"]),
        "pattern_step": meta["step"],
        "copy_wedge": meta["wedge"],
        "locked_goal": meta["goal"],
    }


def goal_alignment_score(row: dict) -> int:
    if row["ship_status"] == "shipped":
        return 0
    blob = f"{row['plan']} {row['outcome']}".lower()
    tier_goal = PATTERN_BY_TIER.get(row["success_tier"], {}).get("goal", "engineering")
    kws = GOAL_ALIGNMENT_KEYWORDS.get(tier_goal, ())
    score = sum(w for k, w in kws if k in blob)
    if row["success_tier"] == "S0-proof":
        score += sum(w for k, w in GOAL_ALIGNMENT_KEYWORDS["customer_1"] if k in blob)
    if row["tier"] == "T1":
        score += 8
    if row["lane"] in ("A", "F+A", "M+A"):
        score += 6
    if row["ship_status"] == "partial":
        score = int(score * 0.4)
    return max(0, min(100, score * 4))


def infer_artifact_path(row: dict) -> str:
    blob = f"{row['plan']} {row['outcome']}"
    for m in re.findall(r"`(/[^`]+)`", blob):
        return m
    for m in re.findall(r"(/[\w\-./]+)", row["plan"]):
        if m.startswith("/") and len(m) > 2:
            return m
    lane_hints = {
        "S2-copilot-complement": "/copilot/",
        "S4-trust-ui": "/trust-center/",
        "S6-tle-wedge": "/trust-ledger/",
        "S3-msp-channel": "/partners/msp/",
        "S5-federal": "/federal/",
    }
    return lane_hints.get(row["success_tier"], "docs/ or governance-console/")


def buyer_moment(row: dict) -> str:
    tier = row["success_tier"]
    moments = {
        "S0-proof": "CIO opens demo URL → sees evaluate + confidence → exports board PDF in <5 min",
        "S6-tle-wedge": "Procurement asks for tamper evidence → export FAIL on mutation proves integrity",
        "S2-copilot-complement": "Workspace admin compares platform registry vs Noetfield receipt in briefing",
        "S4-trust-ui": "Security reviewer opens trust center → framework grid + honest posture",
        "S1-positioning": "Founder Form PICK → hero copy matches PRODUCT_TRUTH",
        "S3-msp-channel": "MSP partner attaches 90-day SOW → white-label board PDF for end client",
        "S5-federal": "Federal vendor diligence → AIA/ADM/NIST mapping without clearance claims",
        "S7-hardening": "Engineer merges PR → verify bundle green, no www regression",
        "S8-agentic": "Hub sends one named CIO outreach — NF-CLOUD updated tracker template only",
    }
    return moments.get(tier, "Buyer-visible artifact ships with verify gate")


def redesigned_prompt(row: dict) -> str:
    """Brainstorm-enriched high-grade agent instruction."""
    bm = pattern_meta(row)
    s = row.get("prompt_structured") or structured_prompt(row)
    refs = " · ".join(bm["pattern_refs"][:3])
    artifact = infer_artifact_path(row)
    moment = buyer_moment(row)
    if row["lane"].endswith("+H") or row["lane"] == "H":
        return (
            f"## {row['id']} FQ-{row['fq']:03d} [HUB ONLY]\n"
            f"**Task:** {row['plan']}\n"
            f"**Outcome:** {row['outcome']}\n"
            f"**NF-CLOUD scope:** Maintain copy/template on disk. Hub executes per R-011.\n"
            f"**Stop:** No send/call from cloud agent.\n"
        )
    return (
        f"## {row['id']} FQ-{row['fq']:03d}\n"
        f"**Tier:** {row['success_tier']} · **Phase:** {row.get('gtm_phase', '')} · "
        f"**Goal:** {bm['locked_goal']} · **GTM:** {row.get('gtm_impact', 0)} · "
        f"**Alignment:** {row.get('goal_alignment', 0)}\n"
        f"**Success pattern ({refs}):** {bm['copy_wedge']}\n"
        f"**Buyer moment:** {moment}\n"
        f"**Task:** {row['plan']}\n"
        f"**Outcome:** {row['outcome']}\n"
        f"**Primary artifact:** `{artifact}`\n"
        f"**Pre-read:** {', '.join(s['pre_read'][:4])}\n"
        f"**Success when:** {'; '.join(s['success_when'][:3])}\n"
        f"**Stop if:** {'; '.join(s['stop_if'][:3])}\n"
        f"**Anti-scope:** {'; '.join(s['anti_scope'][:2])}\n"
        f"**Verify:** `{s['verify']}` · ≤3 tasks this iter\n"
    )


def classify_pick_cluster(plan: str, outcome: str) -> str:
    blob = f"{plan} {outcome}".lower()
    best = ("general", 0)
    for cluster, kws in PICK_CLUSTERS:
        score = sum(1 for k in kws if k in blob)
        if score > best[1]:
            best = (cluster, score)
    return best[0]


def estimate_effort(row: dict) -> str:
    lane = row["lane"]
    verify = row.get("verify", "").lower()
    if lane.endswith("+D") or lane == "D":
        return "S"
    if "manual" in verify or "spec review" in verify:
        return "S"
    if row["tier"] == "T3" or "load test" in row["plan"].lower():
        return "L"
    if "playwright" in row["plan"].lower() or "openapi" in row["plan"].lower():
        return "M"
    return "M" if lane.endswith("+A") or lane == "A" else "S"


def infer_unlocks(row: dict) -> list[str]:
    blob = f"{row['plan']} {row['outcome']}".lower()
    unlocks: list[str] = []
    if any(k in blob for k in ("demo", "governance meeting", "5-min", "quickscan")):
        unlocks.append("design_partner_meeting")
    if any(k in blob for k in ("tamper", "export", "board pack", "receipt")):
        unlocks.append("procurement_close")
    if any(k in blob for k in ("playwright", "verify-ui", "smoke")):
        unlocks.append("ci_buyer_regression")
    if any(k in blob for k in ("procurement", "diligence", "trust center")):
        unlocks.append("security_questionnaire")
    if any(k in blob for k in ("msp", "partner", "sow")):
        unlocks.append("msp_pilot_contract")
    if any(k in blob for k in ("agent 365", "purview", "registry")):
        unlocks.append("copilot_design_partner")
    return unlocks[:3]


def proof_chain_rank(row: dict) -> int | None:
    blob = f"{row['plan']} {row['outcome']}".lower()
    if row["success_tier"] not in ("S0-proof", "S6-tle-wedge"):
        return None
    for i, token in enumerate(PROOF_CHAIN_ORDER):
        if token in blob:
            return i
    return None


def wisdom_score(row: dict) -> int:
    if row["ship_status"] == "shipped":
        return 0
    gtm = row.get("gtm_impact", 0)
    goal = row.get("goal_alignment", 0)
    unlock_bonus = min(20, len(row.get("unlocks", [])) * 7)
    effort_bonus = {"S": 10, "M": 5, "L": 0}.get(row.get("effort", "M"), 5)
    chain = row.get("proof_chain_rank")
    chain_bonus = max(0, 15 - chain) if chain is not None else 0
    partial_penalty = 25 if row["ship_status"] == "partial" else 0
    raw = gtm * 0.38 + goal * 0.38 + unlock_bonus + effort_bonus + chain_bonus - partial_penalty
    return max(0, min(100, int(raw)))


def why_now(row: dict) -> str:
    if row["ship_status"] == "partial":
        return "Live slice exists — extend only if founder wants depth on shipped path."
    unlocks = row.get("unlocks", [])
    if "design_partner_meeting" in unlocks:
        return "Directly enables customer #1 — buyer sees proof in <5 minutes."
    if "procurement_close" in unlocks:
        return "Closes procurement on receipt portability — TLE wedge."
    if "ci_buyer_regression" in unlocks:
        return "Locks buyer paths in CI — prevents www regression before outreach."
    if row.get("wisdom_score", 0) >= 85:
        return "Top wisdom composite — high GTM + goal alignment."
    return "Supports locked goal without scope creep."


def defer_if(row: dict) -> str:
    if row["success_tier"] == "S7-hardening":
        return "Defer until S0–S4 proof slices ship this sprint."
    if row["success_tier"] == "S8-agentic":
        return "Always defer disk implement — Hub only (R-011)."
    if row["icp_lane"] == "M" and row.get("pick_cluster") != "msp-channel":
        return "Defer unless founder declared MSP sprint."
    if row["icp_lane"] == "F" and row.get("pick_cluster") != "federal-lane":
        return "Defer unless founder declared federal intake."
    if row["ship_status"] == "partial":
        return "Defer unless extending an already-live buyer path."
    return "Do not pick if iter already has 2 S0 or 3× same cluster."


def prompt_wise(row: dict) -> str:
    ws = row.get("wisdom_score", 0)
    return (
        f"WISE PICK {row['id']} (wisdom {ws}/100) · {row.get('pick_cluster', 'general')} · "
        f"{row['success_tier']} · effort {row.get('effort', 'M')}\n"
        f"WHY NOW: {why_now(row)}\n"
        f"DEFER IF: {defer_if(row)}\n"
        f"TASK: {row['plan']} → {row['outcome']}\n"
        f"UNLOCKS: {', '.join(row.get('unlocks', [])) or 'incremental proof'}\n"
        f"VERIFY: {row.get('verify', 'plan-with-no-asf')}"
    )


def gtm_impact_score(row: dict) -> int:
    if row["ship_status"] == "shipped":
        return 0
    score = GTM_BASE.get(row["success_tier"], 40)
    if row["tier"] == "T1":
        score += 12
    elif row["tier"] == "T2":
        score += 5
    lane = row["lane"]
    if lane in ("A", "F+A", "M+A"):
        score += 10
    elif lane in ("D", "F+D", "M+D"):
        score -= 4
    elif lane.endswith("+H") or lane == "H":
        score -= 20
    blob = f"{row['plan']} {row['outcome']}".lower()
    if any(k in blob for k in ("www", "homepage", "procurement", "demo", "board", "export")):
        score += 6
    verify = row.get("verify", "").lower()
    if "plan-with-no-asf" in verify or "verify-gtm" in verify or "verify-ui" in verify:
        score += 4
    if row["ship_status"] == "partial":
        score = int(score * 0.35)
    return max(0, min(100, score))


def priority_score(row: dict) -> int:
    """Lower = higher priority. Wisdom-weighted within tier."""
    tier = TIER_PICK_ORDER.get(row["success_tier"], 9)
    shipped = 0 if row["ship_status"] == "open" else (8 if row["ship_status"] == "partial" else 80)
    wisdom = 100 - row.get("wisdom_score", wisdom_score(row))
    t1 = 0 if row["tier"] == "T1" else (2 if row["tier"] == "T2" else 4)
    lane = 0 if row["lane"].endswith("+A") or row["lane"] == "A" else 2
    return tier * 1000 + shipped + wisdom + t1 + lane


def pick_rationale(row: dict) -> str:
    parts: list[str] = []
    if row["tier"] == "T1":
        parts.append("T1 critical")
    if row["lane"].endswith("+A") or row["lane"] == "A":
        parts.append("disk-ship")
    parts.append(row["success_tier"])
    if row["ship_status"] == "partial":
        parts.append("extend shipped slice")
    elif row["ship_status"] == "open":
        parts.append("greenfield")
    impact = gtm_impact_score(row)
    if impact >= 85:
        parts.append("high GTM impact")
    elif impact >= 70:
        parts.append("buyer-visible")
    return " · ".join(parts)


def success_when(row: dict) -> list[str]:
    verify = row.get("verify", "plan-with-no-asf")
    items = [f"`{verify}` passes"]
    blob = f"{row['plan']} {row['outcome']}".lower()
    if "www" in blob or "/" in row["plan"]:
        items.append("Buyer page loads in verify-ui-e2e")
    if "export" in blob or "tle" in blob:
        items.append("TLE export tamper gate holds")
    if row["icp_lane"] == "F":
        items.append("No clearance / RPAA claims on page")
    if row["icp_lane"] == "M":
        items.append("MSP SOW attach path documented")
    items.append("cursor-reply-latest.txt updated")
    return items


def structured_prompt(row: dict) -> dict:
    tier = row["success_tier"]
    lane = row["lane"]
    icp = row["icp_lane"]
    pre_read = list(PRE_READ_BY_TIER.get(tier, PRE_READ_BY_TIER["S0-proof"]))
    if icp == "F" and "FEDERAL_AIA_ADM_NIST_v1.md" not in pre_read:
        pre_read.insert(1, "FEDERAL_AIA_ADM_NIST_v1.md")
    if icp == "M" and "NOETFIELD_FORWARD_QUEUE_100_v5_MSP.md" not in pre_read:
        pre_read.insert(1, "NOETFIELD_FORWARD_QUEUE_100_v5_MSP.md")

    role = "NF-CLOUD-AGENT"
    if lane.endswith("+H") or lane == "H":
        role = "NF-CLOUD-AGENT (copy/templates only — Hub executes R-011)"

    return {
        "role": role,
        "id": row["id"],
        "fq": row["fq"],
        "task": row["plan"],
        "outcome": row["outcome"],
        "success_tier": tier,
        "pre_read": pre_read,
        "success_when": success_when(row),
        "stop_if": list(STOP_ALWAYS),
        "anti_scope": list(ANTI_SCOPE),
        "verify": row.get("verify", "plan-with-no-asf"),
        "pick_rationale": pick_rationale(row),
    }


def enriched_prompt(row: dict) -> str:
    s = structured_prompt(row)
    pre = ", ".join(s["pre_read"][:3])
    success = "; ".join(s["success_when"][:2])
    stop = "; ".join(s["stop_if"][:2])
    icp = row["icp_lane"]
    lane_note = ""
    if icp == "F":
        lane_note = " F lane — no clearance/RPAA claims."
    elif icp == "M":
        lane_note = " M lane — channel SOW; no client billing through NF."
    elif row["lane"].endswith("+H") or row["lane"] == "H":
        return (
            f"[AGENTIC Hub only — R-011] {s['id']} FQ-{s['fq']:03d}: {s['task']}. "
            f"Outcome: {s['outcome']}. NF-CLOUD maintains templates/copy; Hub executes outreach. "
            f"Pre-read: {pre}. Stop if: {stop}."
        )
    return (
        f"As {s['role']}, implement {s['id']} FQ-{s['fq']:03d}: {s['task']}. "
        f"Outcome: {s['outcome']}. Tier {s['success_tier']}; rationale: {s['pick_rationale']}.{lane_note} "
        f"Pre-read: {pre}. Success when: {success}. Stop if: {stop}. Verify: {s['verify']}."
    )


def suggest_iter_bundles(rows: list[dict], n: int = 5) -> list[dict]:
    """Smart 3-packs: diversify tier + lane; max 1 partial; no Hub."""
    open_rows = [r for r in rows if r["ship_status"] == "open" and r["success_tier"] != "S8-agentic"]
    open_rows.sort(key=priority_score)
    bundles: list[dict] = []
    used: set[str] = set()

    tier_targets = ("S0-proof", "S6-tle-wedge", "S2-copilot-complement", "S4-trust-ui", "S3-msp-channel")
    for bundle_idx in range(n):
        picks: list[dict] = []
        for tier in tier_targets:
            if len(picks) >= 3:
                break
            for r in open_rows:
                if r["id"] in used or r["success_tier"] != tier:
                    continue
                if r["lane"].endswith("+H") or r["lane"] == "H":
                    continue
                picks.append(r)
                used.add(r["id"])
                break
        if len(picks) < 3:
            for r in open_rows:
                if r["id"] in used:
                    continue
                if r["lane"].endswith("+H") or r["lane"] == "H":
                    continue
                picks.append(r)
                used.add(r["id"])
                if len(picks) >= 3:
                    break
        if picks:
            bundles.append({
                "bundle": f"iter-{bundle_idx + 1}",
                "theme": f"Proof-first pack {bundle_idx + 1}",
                "ids": [p["id"] for p in picks],
                "tiers": [p["success_tier"] for p in picks],
                "clusters": [p.get("pick_cluster", "") for p in picks],
                "wisdom_sum": sum(p.get("wisdom_score", 0) for p in picks),
                "gtm_sum": sum(gtm_impact_score(p) for p in picks),
            })
    return bundles


def parse_queues() -> list[dict]:
    rows: list[dict] = []
    for batch, rel, icp_lane in QUEUE_FILES:
        path = ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            m = ROW_RE.match(line.strip())
            if not m:
                continue
            plan = m.group(5).strip()
            outcome = m.group(6).strip()
            verify = m.group(7).strip()
            lane = m.group(4).strip()
            row = {
                "id": m.group(1),
                "fq": int(m.group(2)),
                "tier": m.group(3),
                "lane": lane,
                "lane_exec": LANE_TO_ICP.get(lane, lane),
                "plan": plan,
                "outcome": outcome,
                "verify": verify,
                "batch": batch,
                "icp_lane": icp_lane,
            }
            row["success_tier"] = classify_success_tier(plan, outcome, lane, icp_lane)
            row["ship_status"] = infer_ship_status(plan, outcome)
            row["gtm_impact"] = gtm_impact_score(row)
            row["goal_alignment"] = goal_alignment_score(row)
            row["gtm_phase"] = GTM_PHASE_BY_TIER.get(row["success_tier"], "P6-hardening")
            row.update(pattern_meta(row))
            row["artifact_path"] = infer_artifact_path(row)
            row["buyer_moment"] = buyer_moment(row)
            row["pick_cluster"] = classify_pick_cluster(plan, outcome)
            row["effort"] = estimate_effort(row)
            row["unlocks"] = infer_unlocks(row)
            row["proof_chain_rank"] = proof_chain_rank(row)
            row["wisdom_score"] = wisdom_score(row)
            row["why_now"] = why_now(row)
            row["defer_if"] = defer_if(row)
            row["priority_rank"] = 0
            row["pick_rationale"] = pick_rationale(row)
            row["prompt_structured"] = structured_prompt(row)
            row["prompt_enriched"] = enriched_prompt(row)
            row["prompt_redesigned"] = redesigned_prompt(row)
            row["prompt_wise"] = prompt_wise(row)
            rows.append(row)
    ranked = sorted(rows, key=priority_score)
    for i, r in enumerate(ranked, 1):
        r["priority_rank"] = i
    return rows


def emit_markdown(rows: list[dict], out: Path, bundles: list[dict], next_3: list[dict]) -> None:
    by_success: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_success[r["success_tier"]].append(r)

    lines = [
        "# Unified 500 prompt pack — v4 wisdom engine",
        "",
        "**Status:** Wisdom-scored FQ-001–500 · proof-chain clusters · sprint themes",
        "**Generated by:** `scripts/generate_unified_prompt_pack_500.py`",
        f"**Rows:** {len(rows)} · **Engine:** v4 (wisdom_score · pick_cluster · why_now/defer_if)",
        "",
        "**Wise picks:** [WISDOM_PICK_RULES_v1.md](./WISDOM_PICK_RULES_v1.md)",
        "**Full 500 table:** [ALL_500_TIER_INDEX_v1.md](./ALL_500_TIER_INDEX_v1.md)",
        "",
        "## How agents should pick (wise order)",
        "",
        "1. **Filter** `ship_status: open` first; `partial` only when extending a shipped slice",
        "2. **Sort** by `priority_rank` ascending (lower = pick sooner)",
        "3. **Cap** ≤3 per iter · max 2 S0 · never 3× S7 · never mix S8 Hub disk work",
        "4. **Read** `prompt_wise` first — then `prompt_redesigned` if implementing",
        "",
        "Full intelligence: [PICK_INTELLIGENCE_v1.md](./PICK_INTELLIGENCE_v1.md)",
        "",
        "## Next 3 recommended (computed)",
        "",
        "| # | ID | FQ | Wisdom | Cluster | Tier | Status | Plan |",
        "|---|-----|-----|--------|---------|------|--------|------|",
    ]
    for i, r in enumerate(next_3, 1):
        lines.append(
            f"| {i} | **{r['id']}** | {r['fq']:03d} | **{r.get('wisdom_score', 0)}** | "
            f"{r.get('pick_cluster', '')} | `{r['success_tier']}` | "
            f"{r['ship_status']} | {r['plan'][:42]} |"
        )

    lines.extend([
        "",
        "## Success model tiers (pick order)",
        "",
        "| Tier | Pattern cluster | Pick when |",
        "|------|-----------------|-----------|",
        "| **S0-proof** | board-pdf-moment | Customer #1 — board PDF in real meeting |",
        "| **S6-tle-wedge** | receipt-export-wedge | Procurement close — receipt differentiation |",
        "| **S2-copilot-complement** | registry-vs-receipt | Copilot design partner runway |",
        "| **S4-trust-ui** | trust-center-grid | Diligence questionnaire inbound |",
        "| **S1-positioning** | buyer-hero | www copy refresh after Form PICK |",
        "| **S3-msp-channel** | msp-two-tier | MSP partner briefing |",
        "| **S5-federal** | AIA · ADM · NIST | F lane intake only |",
        "| **S7-hardening** | Engineering hygiene | After S0–S4 slices ship |",
        "| **S8-agentic** | Hub outreach | R-011 — not NF-CLOUD disk |",
        "",
        "## Suggested iter bundles (smart 3-packs)",
        "",
    ])
    for b in bundles:
        ids = ", ".join(f"`{x}`" for x in b["ids"])
        lines.append(
            f"- **{b['bundle']}** — wisdom {b.get('wisdom_sum', 0)} · GTM {b['gtm_sum']}: {ids}"
        )

    lines.extend([
        "",
        "## Top 25 picks (priority rank)",
        "",
    ])
    ranked = sorted(rows, key=priority_score)
    for i, r in enumerate(ranked[:25], 1):
        lines.append(
            f"{i}. **{r['id']}** FQ-{r['fq']:03d} · `{r['success_tier']}` · "
            f"{r.get('gtm_phase', '')} · GTM {r['gtm_impact']} · goal {r.get('goal_alignment', 0)} · "
            f"{r['ship_status']} · {r['plan']} — _{r['pick_rationale']}_ — "
            f"pattern: {', '.join(r.get('pattern_refs', [])[:2])}"
        )

    lines.extend(["", "## Enriched prompts by success tier", ""])
    tier_labels = {
        "S0-proof": "S0 — Proof (demo · TLE · procurement)",
        "S6-tle-wedge": "S6 — TLE differentiation",
        "S2-copilot-complement": "S2 — Copilot complement",
        "S4-trust-ui": "S4 — Trust / institutional UI",
        "S1-positioning": "S1 — Positioning / copy",
        "S3-msp-channel": "S3 — MSP channel",
        "S5-federal": "S5 — Federal lane",
        "S7-hardening": "S7 — Hardening",
        "S8-agentic": "S8 — Agentic (Hub)",
    }
    for st in sorted(by_success.keys(), key=lambda x: TIER_PICK_ORDER.get(x, 9)):
        items = sorted(by_success[st], key=lambda r: r["priority_rank"])
        lines.append(f"### {tier_labels.get(st, st)} ({len(items)} plans)")
        lines.append("")
        for r in items[:4]:
            lines.append(f"- **{r['id']}** FQ-{r['fq']:03d} · GTM {r['gtm_impact']} · goal {r.get('goal_alignment', 0)} · {r['ship_status']} · {r['lane']} · {r['plan']}")
            lines.append(f"  - Wedge: {r.get('copy_wedge', '')[:120]}")
        if len(items) > 4:
            lines.append(f"- _…and {len(items) - 4} more in tier_")
        lines.append("")

    lines.extend([
        "## Related",
        "",
        "- [PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md](./PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md)",
        "- [ALL_500_TIER_INDEX_v1.md](./ALL_500_TIER_INDEX_v1.md)",
        "- [PICK_INTELLIGENCE_v1.md](./PICK_INTELLIGENCE_v1.md)",
        "- [SUCCESS_MODEL_TIERS_v1.md](./SUCCESS_MODEL_TIERS_v1.md)",
        "- [ENRICHED_PICKS_NEXT_50_v1.md](./ENRICHED_PICKS_NEXT_50_v1.md)",
        "- [INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md](../../strategy/INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md)",
        "",
    ])
    out.write_text("\n".join(lines), encoding="utf-8")


def emit_enriched_picks(rows: list[dict], out: Path) -> None:
    waves = [
        ("A", "S0-proof", "S0 proof (customer #1)", 8),
        ("B", "S6-tle-wedge", "S6 TLE wedge (procurement)", 6),
        ("C", "S2-copilot-complement", "S2 Copilot complement", 6),
        ("D", "S4-trust-ui", "S4 Trust UI", 6),
        ("E", "S3-msp-channel", "S3 MSP channel", 8),
        ("F", "S5-federal", "S5 Federal (F lane)", 6),
        ("G", "S7-hardening", "S7 Hardening (after proof)", 6),
        ("H", "S1-positioning", "S1 Positioning", 4),
    ]
    lines = [
        "# Enriched prompt picks — next 50 (pattern-ranked)",
        "",
        "**Status:** Goal-aligned · pattern-mapped · auto-ranked",
        "**Full redesigned prompts:** `unified_500_index.json` → `prompt_redesigned` per ID",
        "**Regenerate:** `python3 scripts/generate_unified_prompt_pack_500.py`",
        "**Pick rule:** ≤3 per iter · open first · read `prompt_structured` in index JSON",
        "",
        "---",
        "",
    ]
    pick_num = 0
    for wave_id, tier, title, limit in waves:
        tier_rows = [r for r in rows if r["success_tier"] == tier]
        tier_rows.sort(key=priority_score)
        lines.append(f"## Wave {wave_id} — {title}")
        lines.append("")
        lines.append("| # | ID | FQ | GTM | Goal | Status | Pattern | Plan |")
        lines.append("|---|-----|-----|-----|------|--------|---------|------|")
        shown = 0
        for r in tier_rows:
            if shown >= limit:
                break
            pick_num += 1
            label = f"{wave_id}{shown + 1}"
            refs = r.get("pattern_refs", ["—"])[0]
            lines.append(
                f"| {label} | {r['id']} | {r['fq']:03d} | {r['gtm_impact']} | "
                f"{r.get('goal_alignment', 0)} | {r['ship_status']} | {refs} | {r['plan'][:35]} |"
            )
            shown += 1
        lines.append("")
    lines.extend([
        "---",
        "",
        "## Copy-paste agent prompt",
        "",
        "```",
        "PLAN WITH NO ASF — pick ≤3 from ENRICHED_PICKS waves (open rows first).",
        "",
        "For each task:",
        "1. Load prompt_redesigned from unified_500_index.json for the ID",
        "2. Read every pre_read doc; obey stop_if and anti_scope",
        "3. Branch cursor/{slug}-37f0",
        "4. Implement outcome only",
        "5. Run ./scripts/plan-with-no-asf-verify.sh",
        "6. Update cursor-reply-latest.txt + GTM_NEXT shipped table",
        "```",
        "",
        "## Related",
        "",
        "- [PICK_INTELLIGENCE_v1.md](./PICK_INTELLIGENCE_v1.md)",
        "- [UNIFIED_500_MASTER_v1.md](./UNIFIED_500_MASTER_v1.md)",
        "",
    ])
    out.write_text("\n".join(lines), encoding="utf-8")


def emit_pick_intelligence(rows: list[dict], bundles: list[dict], out: Path) -> None:
    open_count = sum(1 for r in rows if r["ship_status"] == "open")
    partial_count = sum(1 for r in rows if r["ship_status"] == "partial")
    lines = [
        "# Pick intelligence — unified 500 v3",
        "",
        "**Status:** LOCKED pick logic · pattern synthesis",
        "**Regenerate:** `python3 scripts/generate_unified_prompt_pack_500.py`",
        "",
        "## Executive rule",
        "",
        "> Pick **proof that buyers can see in 5 minutes** before **engineering hygiene**.",
        "> GTM validation is 2/10 until a board PDF is used in a real governance meeting.",
        "",
        "## v3 scoring model (GTM + goal alignment)",
        "",
        "| Signal | Weight | Why |",
        "|--------|--------|-----|",
        "| Success tier (S0–S8) | 0–100 base | Pattern-aligned buyer outcome |",
        "| Goal alignment | 0–100 | Locked goal keyword match (customer_1, tle_wedge, …) |",
        "| Pattern step | 1–10 | Maps to INSTITUTIONAL_SITE_PLAN_10_STEP |",
        "| T1 vs T2/T3 | +12 / +5 | Revenue-critical path |",
        "| Disk lane (A) | +10 | Ships buyer-visible artifact |",
        "| Hub lane (H) | −20 | R-011 — not NF-CLOUD implement |",
        "| `partial` status | ×0.35 | Extend only when slice already live |",
        "| `shipped` status | 0 | Skip — log in GTM_NEXT instead |",
        "",
        f"**Inventory:** {open_count} open · {partial_count} partial · {500 - open_count - partial_count} other",
        "",
        "## Wise pick sequence (PLAN WITH NO ASF)",
        "",
        "```mermaid",
        "flowchart TD",
        "  A[Read QUICK_PICK + GTM_NEXT] --> B{ship_status open?}",
        "  B -->|yes| C[Sort priority_rank asc]",
        "  B -->|partial| D[Extend only if founder asked]",
        "  B -->|shipped| E[Skip — already in GTM_NEXT]",
        "  C --> F[Pick ≤3 diversify tier]",
        "  F --> G[Read prompt_structured.pre_read]",
        "  G --> H[Implement + verify bundle]",
        "```",
        "",
        "## Anti-patterns (never pick together)",
        "",
        "| Bad combo | Why |",
        "|-----------|-----|",
        "| 3× S7 hardening | No buyer proof this iter |",
        "| 2× S3 MSP + 1× S5 federal | Mixed ICP — confuses GTM story |",
        "| S8 Hub + any disk task | R-011 boundary |",
        "| Tier B connector + SSO | GTM 60-day lock |",
        "",
        "## Suggested iter bundles",
        "",
    ]
    for b in bundles:
        ids = " · ".join(b["ids"])
        lines.append(f"- **{b['bundle']}** (GTM {b['gtm_sum']}): {ids}")
    lines.extend([
        "",
        "## Structured prompt fields",
        "",
        "Every plan in `unified_500_index.json` includes `prompt_structured`:",
        "",
        "| Field | Purpose |",
        "|-------|---------|",
        "| `pre_read` | Locked docs to load before code |",
        "| `success_when` | Definition of done |",
        "| `stop_if` | Hard gates (R-001, R-011, ≤3 tasks) |",
        "| `anti_scope` | Tier B/C / P9 deferrals |",
        "| `pick_rationale` | Why this rank |",
        "| `prompt_redesigned` | Full brainstorm-enriched agent brief |",
        "| `pattern_refs` | Internal pattern labels (trust-center-grid, msp-two-tier, …) |",
        "| `copy_wedge` | Buyer-facing pattern wedge |",
        "",
        "## Related",
        "",
        "- [PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md](./PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md)",
        "- [SUCCESS_MODEL_TIERS_v1.md](./SUCCESS_MODEL_TIERS_v1.md)",
        "- [UNIFIED_500_MASTER_v1.md](./UNIFIED_500_MASTER_v1.md)",
        "- [QUICK_PICK.md](../no-asf/QUICK_PICK.md)",
        "",
    ])
    out.write_text("\n".join(lines), encoding="utf-8")


def emit_executive_synthesis(rows: list[dict], next_3: list[dict], out: Path) -> None:
    open_n = sum(1 for r in rows if r["ship_status"] == "open")
    partial_n = sum(1 for r in rows if r["ship_status"] == "partial")
    tier_counts = Counter(r["success_tier"] for r in rows)
    phase_counts = Counter(r.get("gtm_phase", "") for r in rows)
    goal_counts = Counter(r.get("locked_goal", "") for r in rows)

    lines = [
        "# Prompt pack executive synthesis — unified 500 (v3)",
        "",
        "**Status:** Deep analysis · pattern-mapped · goal-prioritized",
        "**Generated:** `scripts/generate_unified_prompt_pack_500.py`",
        "",
        "---",
        "",
        "## Executive summary",
        "",
        "All **500 forward-queue prompts** (FQ-001–500) were analyzed against the",
        "**INSTITUTIONAL_SITE_PLAN_10_STEP** success model and re-tiered into",
        "**S0–S8** with **goal alignment scoring**, **internal pattern references**, and",
        "**brainstorm-enriched `prompt_redesigned`** briefs per plan.",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total plans | 500 |",
        f"| Open (pick now) | {open_n} |",
        f"| Partial (extend only) | {partial_n} |",
        f"| Bottleneck | GTM validation 2/10 — **customer #1 proof** |",
        "",
        "## Locked goal distribution",
        "",
        "| Goal | Plans | Priority |",
        "|------|-------|----------|",
    ]
    goal_order = ("customer_1", "tle_wedge", "copilot_story", "trust_diligence", "msp_channel", "federal_lane", "positioning", "engineering", "agentic")
    for g in goal_order:
        c = goal_counts.get(g, 0)
        if c:
            pri = "**P0**" if g in ("customer_1", "tle_wedge") else ("**P1**" if g in ("copilot_story", "trust_diligence") else "P2+")
            lines.append(f"| {g} | {c} | {pri} |")

    lines.extend([
        "",
        "## GTM phase organization",
        "",
        "| Phase | Theme | Count |",
        "|-------|-------|-------|",
    ])
    phase_labels = {
        "P1-proof-moment": "Customer #1 — demo · board PDF",
        "P2-tle-wedge": "Procurement — receipt differentiation",
        "P3-copilot-story": "Registry-vs-receipt complement",
        "P4-trust-diligence": "Trust center · positioning",
        "P5-channel": "MSP + federal lanes",
        "P6-hardening": "Engineering hygiene",
        "P7-agentic": "Hub outreach only",
    }
    for ph in sorted(phase_counts.keys()):
        lines.append(f"| {ph} | {phase_labels.get(ph, ph)} | {phase_counts[ph]} |")

    lines.extend([
        "",
        "## Success tier distribution (pattern-mapped)",
        "",
        "| Tier | Count | Pattern refs | Pick cap/iter |",
        "|------|-------|--------------|---------------|",
    ])
    for st in sorted(TIER_PICK_ORDER.keys(), key=lambda x: TIER_PICK_ORDER[x]):
        meta = PATTERN_BY_TIER.get(st, {})
        refs = ", ".join(meta.get("refs", ())[:3])
        cap = "2" if st == "S0-proof" else ("0 Hub" if st == "S8-agentic" else "1")
        lines.append(f"| {st} | {tier_counts.get(st, 0)} | {refs} | {cap} |")

    lines.extend([
        "",
        "## What to pick (wise — based on our goals)",
        "",
        "### Pick first (P0 — customer #1)",
        "",
        "S0-proof + S6-tle-wedge disk tasks that produce **board PDF**, **tamper export**,",
        "**demo URL**, or **QuickScan** — buyer must see value in 5 minutes.",
        "",
        "### Pick second (P1 — story + diligence)",
        "",
        "S2-copilot complement + S4-trust-ui — registry-vs-receipt narrative and framework grid.",
        "",
        "### Pick when ICP matches (P2)",
        "",
        "S3-msp (v5 batch 401–500) · S5-federal (v4 batch 301–400) — never mixed in one iter.",
        "",
        "### Defer (P3)",
        "",
        f"S7-hardening ({tier_counts.get('S7-hardening', 0)} plans) — after S0–S4 slices ship.",
        "S8-agentic — Hub only (R-011).",
        "",
        "## Next 3 recommended (computed)",
        "",
    ])
    for i, r in enumerate(next_3, 1):
        lines.append(f"{i}. **{r['id']}** · {r['success_tier']} · goal align {r.get('goal_alignment', 0)} · {r['plan']}")
        lines.append(f"   - Wedge: {r.get('copy_wedge', '')}")
        lines.append(f"   - Moment: {r.get('buyer_moment', '')[:100]}")
        lines.append("")

    lines.extend([
        "## Top 10 redesigned prompts (brainstorm sample)",
        "",
    ])
    ranked = sorted(rows, key=priority_score)
    for r in ranked[:10]:
        lines.append(r.get("prompt_redesigned", ""))
        lines.append("---")
        lines.append("")

    lines.extend([
        "## Brainstorm — pattern → Noetfield only",
        "",
        "| Pattern teaches | Noetfield keeps | Noetfield drops |",
        "|-----------------|-----------------|-----------------|",
        "| trust-center-grid | Framework grid + honest posture | SOC 2 certification claims |",
        "| msp-two-tier | 90-day SOW + white-label TLE | Client billing through NF |",
        "| registry-vs-receipt | Complement evaluate + RID | Competing with platform registry |",
        "| receipt-export-wedge | Tamper FAIL + board PDF path | Custody / PSP claims |",
        "| federal-framework-map | F lane mapping doc | Clearance / RPAA claims |",
        "",
        "## Related",
        "",
        "- [ALL_500_TIER_INDEX_v1.md](./ALL_500_TIER_INDEX_v1.md)",
        "- [UNIFIED_500_MASTER_v1.md](./UNIFIED_500_MASTER_v1.md)",
        "- [INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md](../../strategy/INSTITUTIONAL_SITE_PLAN_10_STEP_v1.md)",
        "",
    ])
    out.write_text("\n".join(lines), encoding="utf-8")


def emit_all_500_index(rows: list[dict], out: Path) -> None:
    ranked = sorted(rows, key=priority_score)
    lines = [
        "# All 500 prompts — tier index (v4 wisdom order)",
        "",
        "**Generated:** `scripts/generate_unified_prompt_pack_500.py`",
        "**Sorted by:** `priority_rank` (wisdom-weighted)",
        "",
        "| Rank | ID | FQ | Wisdom | Cluster | Tier | Status | Plan |",
        "|------|-----|-----|--------|---------|------|--------|------|",
    ]
    for r in ranked:
        plan = r["plan"].replace("|", "/")[:38]
        lines.append(
            f"| {r['priority_rank']} | {r['id']} | {r['fq']:03d} | {r.get('wisdom_score', 0)} | "
            f"{r.get('pick_cluster', '')} | {r['success_tier']} | "
            f"{r['ship_status']} | {plan} |"
        )
    lines.extend(["", "## Related", "", "- [PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md](./PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md)", ""])
    out.write_text("\n".join(lines), encoding="utf-8")


def suggest_next_3(rows: list[dict]) -> list[dict]:
    """v4: proof-chain clusters + wisdom_score — max 2 S0, diversify clusters."""
    pickable = [
        r for r in rows
        if r["ship_status"] == "open" and r["success_tier"] != "S8-agentic"
        and not (r["lane"].endswith("+H") or r["lane"] == "H")
    ]
    pickable.sort(key=lambda r: (-r.get("wisdom_score", 0), r.get("priority_rank", 999)))

    picks: list[dict] = []
    cluster_targets = ("proof-demo", "proof-export")

    for cluster in cluster_targets:
        if len(picks) >= 3:
            break
        for r in pickable:
            if r in picks:
                continue
            if cluster and r.get("pick_cluster") != cluster:
                continue
            s0 = sum(1 for p in picks if p["success_tier"] == "S0-proof")
            if r["success_tier"] == "S0-proof" and s0 >= 2:
                continue
            picks.append(r)
            break

    if len(picks) < 3:
        for r in pickable:
            if r in picks:
                continue
            if r["success_tier"] == "S6-tle-wedge" and r.get("pick_cluster") == "proof-export":
                picks.append(r)
                break

    for r in pickable:
        if len(picks) >= 3:
            break
        if r not in picks:
            s0 = sum(1 for p in picks if p["success_tier"] == "S0-proof")
            if r["success_tier"] == "S0-proof" and s0 >= 2:
                continue
            # Final slot: stay on proof chain unless nothing left
            if len(picks) == 2 and r.get("pick_cluster") not in (
                "proof-demo", "proof-export"
            ) and r["success_tier"] != "S6-tle-wedge":
                continue
            picks.append(r)
    return picks[:3]


def suggest_sprint_themes(rows: list[dict]) -> list[dict]:
    configs: tuple[tuple[str, callable], ...] = (
        ("customer-1-proof-week", lambda r: r.get("pick_cluster") in ("proof-demo", "proof-export")),
        ("copilot-story-week", lambda r: r.get("pick_cluster") == "copilot-registry"),
        ("trust-diligence-week", lambda r: r.get("pick_cluster") == "trust-diligence"),
        ("msp-enablement-week", lambda r: r.get("pick_cluster") == "msp-channel" and r["icp_lane"] == "M"),
        ("federal-intake-week", lambda r: r.get("pick_cluster") == "federal-lane" and r["icp_lane"] == "F"),
    )
    themes: list[dict] = []
    for theme_id, pred in configs:
        cand = [r for r in rows if r["ship_status"] == "open" and pred(r)]
        cand.sort(key=lambda r: -r.get("wisdom_score", 0))
        top = cand[:5]
        if top:
            themes.append({
                "theme": theme_id,
                "ids": [r["id"] for r in top],
                "wisdom_avg": sum(r.get("wisdom_score", 0) for r in top) // len(top),
            })
    return themes


def emit_wisdom_pick_rules(rows: list[dict], sprint_themes: list[dict], next_3: list[dict], out: Path) -> None:
    cluster_counts = Counter(r.get("pick_cluster", "general") for r in rows)
    lines = [
        "# Wisdom pick rules — unified 500 v4",
        "",
        "**Status:** LOCKED wise pick logic for cloud agents",
        "**Use:** Read `prompt_wise` in index JSON before every implement",
        "",
        "## The one rule",
        "",
        "> Sort by **`wisdom_score`** descending among `open` rows.",
        "> Pick ≤3 that span **proof-demo** + **proof-export** clusters when possible.",
        "> Never outrun the 5-min board PDF moment.",
        "",
        "## Wisdom score formula",
        "",
        "| Component | Weight |",
        "|-----------|--------|",
        "| GTM impact | 38% |",
        "| Goal alignment | 38% |",
        "| Unlocks (buyer outcomes) | up to +20 |",
        "| Effort S/M/L | +10 / +5 / 0 |",
        "| Proof-chain position | up to +15 |",
        "| Partial penalty | −25 |",
        "",
        "## Pick clusters",
        "",
        "| Cluster | Count | Wise use |",
        "|---------|-------|----------|",
    ]
    cluster_use = {
        "proof-demo": "Customer #1 iter — demo script, Playwright, QuickScan",
        "proof-export": "Same iter or next — tamper, board pack, TLE export",
        "copilot-registry": "Design partner briefing — registry-vs-receipt complement",
        "trust-diligence": "Security questionnaire inbound",
        "msp-channel": "MSP sprint only (M lane)",
        "federal-lane": "Federal intake only (F lane)",
        "ops-hardening": "After proof ships",
        "general": "Evaluate case-by-case",
    }
    for cl, cnt in cluster_counts.most_common():
        lines.append(f"| {cl} | {cnt} | {cluster_use.get(cl, '—')} |")

    lines.extend(["", "## Sprint themes (founder pick one/week)", ""])
    for t in sprint_themes:
        ids = " · ".join(t["ids"])
        lines.append(f"- **{t['theme']}** (avg wisdom {t['wisdom_avg']}): {ids}")

    lines.extend(["", "## Next 3 (proof-chain wise)", ""])
    for i, r in enumerate(next_3, 1):
        lines.append(f"{i}. **{r['id']}** wisdom {r.get('wisdom_score')} · {r.get('pick_cluster')}")
        lines.append(f"   - WHY NOW: {r.get('why_now', '')}")
        lines.append(f"   - DEFER IF: {r.get('defer_if', '')}")
        lines.append("")

    lines.extend([
        "## prompt_wise template",
        "",
        "Every plan has `prompt_wise` — one screen with WHY NOW + DEFER IF + UNLOCKS.",
        "",
        "## Related",
        "",
        "- [PICK_INTELLIGENCE_v1.md](./PICK_INTELLIGENCE_v1.md)",
        "- [PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md](./PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md)",
        "- [QUICK_PICK.md](../no-asf/QUICK_PICK.md)",
        "",
    ])
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = parse_queues()
    if len(rows) != 500:
        print(f"WARN expected 500 rows, got {len(rows)}")

    ranked = sorted(rows, key=priority_score)
    next_3 = suggest_next_3(rows)
    bundles = suggest_iter_bundles(rows)
    sprint_themes = suggest_sprint_themes(rows)

    out_dir = ROOT / "docs/ops/plans/PROMPT_PACK_LOCKED"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": "v4",
        "engine": "wisdom-score+proof-chain-clusters+sprint-themes",
        "count": len(rows),
        "success_tier_counts": dict(Counter(r["success_tier"] for r in rows)),
        "ship_status_counts": dict(Counter(r["ship_status"] for r in rows)),
        "pick_cluster_counts": dict(Counter(r.get("pick_cluster", "general") for r in rows)),
        "gtm_phase_counts": dict(Counter(r.get("gtm_phase", "") for r in rows)),
        "locked_goal_counts": dict(Counter(r.get("locked_goal", "") for r in rows)),
        "icp_counts": dict(Counter(r["icp_lane"] for r in rows)),
        "top_25_ids": [r["id"] for r in ranked[:25]],
        "next_3_recommended": [
            {
                "id": r["id"], "fq": r["fq"], "success_tier": r["success_tier"],
                "wisdom_score": r.get("wisdom_score", 0),
                "pick_cluster": r.get("pick_cluster", ""),
                "why_now": r.get("why_now", ""),
                "unlocks": r.get("unlocks", []),
                "ship_status": r["ship_status"],
            }
            for r in next_3
        ],
        "sprint_themes": sprint_themes,
        "iter_bundles": bundles,
        "plans": rows,
    }

    (out_dir / "unified_500_index.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    emit_markdown(rows, out_dir / "UNIFIED_500_MASTER_v1.md", bundles, next_3)
    emit_enriched_picks(rows, out_dir / "ENRICHED_PICKS_NEXT_50_v1.md")
    emit_pick_intelligence(rows, bundles, out_dir / "PICK_INTELLIGENCE_v1.md")
    emit_executive_synthesis(rows, next_3, out_dir / "PROMPT_PACK_EXECUTIVE_SYNTHESIS_v1.md")
    emit_all_500_index(rows, out_dir / "ALL_500_TIER_INDEX_v1.md")
    emit_wisdom_pick_rules(rows, sprint_themes, next_3, out_dir / "WISDOM_PICK_RULES_v1.md")

    print(f"unified_500_index.json: {len(rows)} plans (v4)")
    print(f"ship status: {payload['ship_status_counts']}")
    print(f"clusters: {payload['pick_cluster_counts']}")
    print(f"next 3: {[r['id'] for r in next_3]} (wisdom: {[r.get('wisdom_score') for r in next_3]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
