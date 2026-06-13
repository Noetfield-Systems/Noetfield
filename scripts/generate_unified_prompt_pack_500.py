#!/usr/bin/env python3
"""Analyze + emit unified 500 forward-queue index mapped to success-model tiers."""

from __future__ import annotations

import json
import re
import subprocess
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

# Success model tiers (benchmark-aligned) — S0 highest for GTM proof bottleneck
SUCCESS_TIER_KEYWORDS: dict[str, tuple[str, ...]] = {
    "S0-proof": (
        "demo", "confidence", "procurement", "verify-ui", "tle", "export", "board pack",
        "5-min", "5 minute", "quickscan", "pilot sow", "workspace",
    ),
    "S1-positioning": (
        "homepage", "positioning", "hero", "copy", "one-pager", "buyer deck", "meta refresh",
    ),
    "S2-copilot-complement": (
        "agent 365", "purview", "copilot", "m365", "registry", "microsoft",
    ),
    "S3-msp-channel": (
        "msp", "partner", "gdap", "white-label", "csp", "channel", "pax8", "90-day",
    ),
    "S4-trust-ui": (
        "trust center", "trust-center", "control checkpoint", "framework", "diligence",
        "procurement zip", "security faq",
    ),
    "S5-federal": (
        "federal", "aia", "adm", "fedramp", "osfi", "frfi", "e-23", "bank pilot",
    ),
    "S6-tle-wedge": (
        "trust ledger", "tle", "audit-export", "immutable", "rid", "compare",
    ),
    "S7-hardening": (
        "pytest", "coherence", "manifest", "registry", "openapi", "load test", "perf",
    ),
    "S8-agentic": (
        "outreach", "hub", "agentic", "n8n",
    ),
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


def classify_success_tier(plan: str, outcome: str, icp_lane: str) -> str:
    blob = f"{plan} {outcome}".lower()
    if icp_lane == "F":
        return "S5-federal"
    if icp_lane == "M":
        return "S3-msp-channel"
    scores: list[tuple[int, str]] = []
    for tier, kws in SUCCESS_TIER_KEYWORDS.items():
        score = sum(1 for k in kws if k in blob)
        if score:
            scores.append((score, tier))
    if not scores:
        return "S7-hardening"
    scores.sort(reverse=True)
    return scores[0][1]


def enriched_prompt(row: dict) -> str:
    sid = row["id"]
    fq = row["fq"]
    lane = row["lane"]
    plan = row["plan"]
    outcome = row["outcome"]
    verify = row.get("verify", "plan-with-no-asf")
    success = row["success_tier"]
    icp = row["icp_lane"]

    if lane.endswith("+H") or lane == "H":
        return (
            f"[AGENTIC Hub only — not NF-CLOUD disk] {sid} (FQ-{fq:03d}): {plan}. "
            f"Outcome: {outcome}. Maintain copy/templates on disk; Hub executes send/call per R-011."
        )
    if icp == "F":
        return (
            f"As NF-CLOUD-AGENT (F lane only), implement {sid} FQ-{fq:03d}: {plan}. "
            f"Outcome: {outcome}. Read FEDERAL_AIA_ADM_NIST_v1 + no RPAA/clearance claims. "
            f"Verify: {verify}. Success tier: {success}."
        )
    if icp == "M":
        return (
            f"As NF-CLOUD-AGENT (M lane / MSP only), implement {sid} FQ-{fq:03d}: {plan}. "
            f"Outcome: {outcome}. Channel SOW + receipt export; no client billing through NF. "
            f"Verify: {verify}. Success tier: {success}."
        )
    return (
        f"As NF-CLOUD-AGENT (Noetfield only), implement {sid} FQ-{fq:03d}: {plan}. "
        f"Outcome: {outcome}. Read INSTITUTIONAL_BENCHMARK_10_STEP_PLAN + MEMORY_LOCKED. "
        f"Lane {lane}; verify: {verify}. Success tier: {success}. ≤3 tasks per iter."
    )


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
            row["success_tier"] = classify_success_tier(plan, outcome, icp_lane)
            row["prompt_enriched"] = enriched_prompt(row)
            rows.append(row)
    rows.sort(key=lambda r: (r["success_tier"], r["fq"]))
    return rows


def priority_score(row: dict) -> int:
    """Lower = higher priority."""
    tier_order = {
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
    t1_bonus = 0 if row["tier"] == "T1" else (1 if row["tier"] == "T2" else 2)
    lane_penalty = 0 if row["lane"].endswith("+A") or row["lane"] == "A" else 1
    return tier_order.get(row["success_tier"], 9) * 10 + t1_bonus + lane_penalty


def emit_markdown(rows: list[dict], out: Path) -> None:
    by_success: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_success[r["success_tier"]].append(r)

    lines = [
        "# Unified 500 prompt pack — success-model tiers (v1)",
        "",
        "**Status:** Enriched forward queue FQ-001–500 + benchmark alignment",
        f"**Generated by:** `scripts/generate_unified_prompt_pack_500.py`",
        f"**Rows:** {len(rows)}",
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
        "## ICP batch map",
        "",
        "| Batch | FQ | ICP lock |",
        "|-------|-----|----------|",
        "| v1–v3 | 001–300 | Mixed SME / trust / board |",
        "| v4 | 301–400 | **F** federal only |",
        "| v5 | 401–500 | **M** MSP only |",
        "",
        "## Top 25 picks (unified priority)",
        "",
    ]

    ranked = sorted(rows, key=priority_score)
    for i, r in enumerate(ranked[:25], 1):
        lines.append(
            f"{i}. **{r['id']}** FQ-{r['fq']:03d} · `{r['success_tier']}` · {r['plan']} — verify `{r['verify']}`"
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

    for st in sorted(by_success.keys(), key=lambda x: priority_score({"success_tier": x, "tier": "T1", "lane": "A"})):
        items = sorted(by_success[st], key=lambda r: r["fq"])
        lines.append(f"### {tier_labels.get(st, st)} ({len(items)} plans)")
        lines.append("")
        for r in items[:8]:
            lines.append(f"- **{r['id']}** FQ-{r['fq']:03d} · {r['lane']} · {r['plan']}")
            lines.append(f"  - Prompt: {r['prompt_enriched'][:200]}…")
        if len(items) > 8:
            lines.append(f"- _…and {len(items) - 8} more in tier_")
        lines.append("")

    lines.extend([
        "## Related",
        "",
        "- [INSTITUTIONAL_BENCHMARK_10_STEP_PLAN_v1.md](../../strategy/INSTITUTIONAL_BENCHMARK_10_STEP_PLAN_v1.md)",
        "- [NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md](../NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md)",
        "- [GTM_NEXT.md](../plans/no-asf/GTM_NEXT.md)",
        "",
    ])
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = parse_queues()
    if len(rows) != 500:
        print(f"WARN expected 500 rows, got {len(rows)}")

    out_json = ROOT / "docs/ops/plans/PROMPT_PACK_LOCKED/unified_500_index.json"
    out_md = ROOT / "docs/ops/plans/PROMPT_PACK_LOCKED/UNIFIED_500_MASTER_v1.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    ranked = sorted(rows, key=priority_score)
    payload = {
        "version": "v1",
        "count": len(rows),
        "success_tier_counts": dict(Counter(r["success_tier"] for r in rows)),
        "icp_counts": dict(Counter(r["icp_lane"] for r in rows)),
        "top_25_ids": [r["id"] for r in ranked[:25]],
        "plans": rows,
    }
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    emit_markdown(rows, out_md)

    print(f"unified_500_index.json: {len(rows)} plans")
    print(f"UNIFIED_500_MASTER_v1.md written")
    print("success tiers:", payload["success_tier_counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
