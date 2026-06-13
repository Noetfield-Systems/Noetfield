#!/usr/bin/env python3
"""Analyze + emit unified 500 forward-queue index — v2 intelligence engine."""

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
        "INSTITUTIONAL_BENCHMARK_10_STEP_PLAN_v1.md",
        "NOETFIELD_GTM_60_DAY_LOCKED_v1.md",
    ),
    "S6-tle-wedge": (
        "MEMORY_LOCKED.yaml",
        "TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md",
        "POSITIONING_BENCHMARK_SYNTHESIS_v1.md",
    ),
    "S2-copilot-complement": (
        "MEMORY_LOCKED.yaml",
        "COPILOT_COMPLEMENT_BENCHMARK_v1.md",
        "NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md",
    ),
    "S4-trust-ui": (
        "MEMORY_LOCKED.yaml",
        "INSTITUTIONAL_BENCHMARK_10_STEP_PLAN_v1.md",
        "PAGE_AUTHORITY_MAP.md",
    ),
    "S1-positioning": (
        "MEMORY_LOCKED.yaml",
        "PRODUCT_TRUTH.md",
        "POSITIONING_BENCHMARK_SYNTHESIS_v1.md",
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
    """Lower = higher priority for picking."""
    tier = TIER_PICK_ORDER.get(row["success_tier"], 9)
    t1 = 0 if row["tier"] == "T1" else (1 if row["tier"] == "T2" else 2)
    lane = 0 if row["lane"].endswith("+A") or row["lane"] == "A" else 1
    shipped = 0 if row["ship_status"] == "open" else (5 if row["ship_status"] == "partial" else 50)
    impact = 100 - gtm_impact_score(row)
    return tier * 1000 + shipped + impact + t1 * 10 + lane


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
            row["priority_rank"] = 0  # filled after sort
            row["pick_rationale"] = pick_rationale(row)
            row["prompt_structured"] = structured_prompt(row)
            row["prompt_enriched"] = enriched_prompt(row)
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
        "# Unified 500 prompt pack — v2 intelligence engine",
        "",
        "**Status:** Smart-tiered forward queue FQ-001–500 + benchmark alignment",
        "**Generated by:** `scripts/generate_unified_prompt_pack_500.py`",
        f"**Rows:** {len(rows)} · **Engine:** v2 (weighted tiers · ship-aware · GTM impact)",
        "",
        "## How agents should pick (wise order)",
        "",
        "1. **Filter** `ship_status: open` first; `partial` only when extending a shipped slice",
        "2. **Sort** by `priority_rank` ascending (lower = pick sooner)",
        "3. **Cap** ≤3 per iter · max 2 S0 · never 3× S7 · never mix S8 Hub disk work",
        "4. **Diversify** tier + lane per bundle — use suggested iter packs below",
        "5. **Read** `prompt_structured.pre_read` before implement",
        "",
        "Full intelligence doc: [PICK_INTELLIGENCE_v1.md](./PICK_INTELLIGENCE_v1.md)",
        "",
        "## Next 3 recommended (computed)",
        "",
        "| # | ID | FQ | Tier | GTM | Status | Plan |",
        "|---|-----|-----|------|-----|--------|------|",
    ]
    for i, r in enumerate(next_3, 1):
        lines.append(
            f"| {i} | **{r['id']}** | {r['fq']:03d} | `{r['success_tier']}` | "
            f"{r['gtm_impact']} | {r['ship_status']} | {r['plan'][:50]} |"
        )

    lines.extend([
        "",
        "## Success model tiers (pick order)",
        "",
        "| Tier | Benchmark lane | Pick when |",
        "|------|----------------|-----------|",
        "| **S0-proof** | Demo / TLE / procurement | Customer #1 — board PDF in real meeting |",
        "| **S6-tle-wedge** | Veridra · ADJUDON · Audital | Procurement close — receipt differentiation |",
        "| **S2-copilot-complement** | Purview · Agent 365 · Inforcer | Copilot design partner runway |",
        "| **S4-trust-ui** | OneTrust · Vanta · Drata | Diligence questionnaire inbound |",
        "| **S1-positioning** | Credo · Holistic · Veridra | www copy refresh after Form PICK |",
        "| **S3-msp-channel** | Inforcer · AvePoint · Lighthouse | MSP partner briefing |",
        "| **S5-federal** | AIA · ADM · NIST | F lane intake only |",
        "| **S7-hardening** | Engineering hygiene | After S0–S4 slices ship |",
        "| **S8-agentic** | Hub outreach | R-011 — not NF-CLOUD disk |",
        "",
        "## Suggested iter bundles (smart 3-packs)",
        "",
    ])
    for b in bundles:
        ids = ", ".join(f"`{x}`" for x in b["ids"])
        lines.append(f"- **{b['bundle']}** — {b['theme']} (GTM sum {b['gtm_sum']}): {ids}")

    lines.extend([
        "",
        "## Top 25 picks (priority rank)",
        "",
    ])
    ranked = sorted(rows, key=priority_score)
    for i, r in enumerate(ranked[:25], 1):
        lines.append(
            f"{i}. **{r['id']}** FQ-{r['fq']:03d} · `{r['success_tier']}` · "
            f"GTM {r['gtm_impact']} · {r['ship_status']} · {r['plan']} — "
            f"_{r['pick_rationale']}_ — verify `{r['verify']}`"
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
        for r in items[:6]:
            lines.append(f"- **{r['id']}** FQ-{r['fq']:03d} · GTM {r['gtm_impact']} · {r['ship_status']} · {r['lane']} · {r['plan']}")
            lines.append(f"  - {r['prompt_enriched'][:220]}…")
        if len(items) > 6:
            lines.append(f"- _…and {len(items) - 6} more in tier_")
        lines.append("")

    lines.extend([
        "## Related",
        "",
        "- [PICK_INTELLIGENCE_v1.md](./PICK_INTELLIGENCE_v1.md)",
        "- [SUCCESS_MODEL_TIERS_v1.md](./SUCCESS_MODEL_TIERS_v1.md)",
        "- [ENRICHED_PICKS_NEXT_50_v1.md](./ENRICHED_PICKS_NEXT_50_v1.md)",
        "- [INSTITUTIONAL_BENCHMARK_10_STEP_PLAN_v1.md](../../strategy/INSTITUTIONAL_BENCHMARK_10_STEP_PLAN_v1.md)",
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
        "# Enriched prompt picks — next 50 (v2 auto-ranked)",
        "",
        "**Status:** Machine-ranked from v2 intelligence engine",
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
        lines.append("| # | ID | FQ | GTM | Status | Plan | Rationale |")
        lines.append("|---|-----|-----|-----|--------|------|-----------|")
        shown = 0
        for r in tier_rows:
            if shown >= limit:
                break
            pick_num += 1
            label = f"{wave_id}{shown + 1}"
            lines.append(
                f"| {label} | {r['id']} | {r['fq']:03d} | {r['gtm_impact']} | "
                f"{r['ship_status']} | {r['plan'][:40]} | {r['pick_rationale']} |"
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
        "1. Load prompt_structured from unified_500_index.json for the ID",
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
        "# Pick intelligence — unified 500 v2",
        "",
        "**Status:** LOCKED pick logic for cloud agents",
        "**Regenerate:** `python3 scripts/generate_unified_prompt_pack_500.py`",
        "",
        "## Executive rule",
        "",
        "> Pick **proof that buyers can see in 5 minutes** before **engineering hygiene**.",
        "> GTM validation is 2/10 until a board PDF is used in a real governance meeting.",
        "",
        "## v2 scoring model",
        "",
        "| Signal | Weight | Why |",
        "|--------|--------|-----|",
        "| Success tier (S0–S8) | 0–100 base | Benchmark-aligned buyer outcome |",
        "| T1 vs T2/T3 | +12 / +5 | Revenue-critical path |",
        "| Disk lane (A) | +10 | Ships buyer-visible artifact |",
        "| Hub lane (H) | −20 | R-011 — not NF-CLOUD implement |",
        "| Buyer keywords | +6 | www · demo · procurement · board |",
        "| Verify maturity | +4 | plan-with-no-asf / verify-gtm family |",
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
        "",
        "## Related",
        "",
        "- [SUCCESS_MODEL_TIERS_v1.md](./SUCCESS_MODEL_TIERS_v1.md)",
        "- [UNIFIED_500_MASTER_v1.md](./UNIFIED_500_MASTER_v1.md)",
        "- [QUICK_PICK.md](../no-asf/QUICK_PICK.md)",
        "",
    ])
    out.write_text("\n".join(lines), encoding="utf-8")


def suggest_next_3(rows: list[dict]) -> list[dict]:
    """Wise next 3: max 2 S0, diversify tier, open only, no Hub."""
    pickable = [
        r for r in sorted(rows, key=priority_score)
        if r["ship_status"] == "open" and r["success_tier"] != "S8-agentic"
        and not (r["lane"].endswith("+H") or r["lane"] == "H")
    ]
    picks: list[dict] = []
    s0_count = 0
    tiers_seen: set[str] = set()

    for r in pickable:
        if len(picks) >= 3:
            break
        tier = r["success_tier"]
        if tier == "S0-proof" and s0_count >= 2:
            continue
        if tier in tiers_seen and tier not in ("S0-proof",):
            continue
        picks.append(r)
        tiers_seen.add(tier)
        if tier == "S0-proof":
            s0_count += 1

    for r in pickable:
        if len(picks) >= 3:
            break
        if r in picks:
            continue
        picks.append(r)
    return picks[:3]


def main() -> int:
    rows = parse_queues()
    if len(rows) != 500:
        print(f"WARN expected 500 rows, got {len(rows)}")

    ranked = sorted(rows, key=priority_score)
    next_3 = suggest_next_3(rows)
    bundles = suggest_iter_bundles(rows)

    out_dir = ROOT / "docs/ops/plans/PROMPT_PACK_LOCKED"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": "v2",
        "engine": "weighted-tiers+ship-aware+gtm-impact",
        "count": len(rows),
        "success_tier_counts": dict(Counter(r["success_tier"] for r in rows)),
        "ship_status_counts": dict(Counter(r["ship_status"] for r in rows)),
        "icp_counts": dict(Counter(r["icp_lane"] for r in rows)),
        "top_25_ids": [r["id"] for r in ranked[:25]],
        "next_3_recommended": [
            {"id": r["id"], "fq": r["fq"], "success_tier": r["success_tier"],
             "gtm_impact": r["gtm_impact"], "ship_status": r["ship_status"],
             "pick_rationale": r["pick_rationale"]}
            for r in next_3
        ],
        "iter_bundles": bundles,
        "plans": rows,
    }

    (out_dir / "unified_500_index.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    emit_markdown(rows, out_dir / "UNIFIED_500_MASTER_v1.md", bundles, next_3)
    emit_enriched_picks(rows, out_dir / "ENRICHED_PICKS_NEXT_50_v1.md")
    emit_pick_intelligence(rows, bundles, out_dir / "PICK_INTELLIGENCE_v1.md")

    print(f"unified_500_index.json: {len(rows)} plans (v2)")
    print(f"ship status: {payload['ship_status_counts']}")
    print(f"next 3: {[r['id'] for r in next_3]}")
    print("success tiers:", payload["success_tier_counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
