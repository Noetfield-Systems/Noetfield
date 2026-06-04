#!/usr/bin/env python3
"""Generate docs/ops/plans registry (1000 no-ASF long-term plans). Re-run to refresh structure."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS_DIR = ROOT / "docs" / "ops" / "plans"

PHASES = {
    "P0": "Foundation — ship, dev stack, ops locks, CI",
    "P1": "Trust Ledger — TLE lifecycle, evidence, export",
    "P2": "Governance API — evaluate, audit, pilot auth, webhooks",
    "P3": "Connectors live — Purview, Entra, M365 audit sync",
    "P4": "Workspace & GTM — UI, www, procurement assets",
    "P5": "Enterprise — multi-tenant, RBAC, KMS signing",
    "P6": "Compliance — append-only proofs, retention, SOC narratives",
    "P7": "Scale — performance, caching, observability, SLOs",
    "P8": "Integrations — MSB channel, partners, API marketplace",
    "P9": "Horizon — research, ML confidence, cross-product bridges",
}

TIERS = {
    "T1": "Critical — unblocks revenue or production ship",
    "T2": "Near-term — next 1–2 sprints",
    "T3": "Medium — quarters 2–4",
    "T4": "Strategic — 12–24 month capability",
    "T5": "Horizon — experimental / optional",
}

AREAS = [
    "trust-ledger",
    "governance-api",
    "evidence",
    "connectors",
    "workspace-ui",
    "www-gtm",
    "devex",
    "ci-cd",
    "security",
    "data-migrations",
    "testing",
    "docs-diligence",
    "msb-partner",
    "observability",
    "performance",
]

# 20 work patterns × 10 phases × 5 tiers = 1000
WORK_PATTERNS = [
    ("api-endpoint", "Add or extend API endpoint for {area}"),
    ("integration-test", "Integration tests covering {area} happy path and 409 guards"),
    ("openapi-sync", "Align OpenAPI spec with implemented {area} routes"),
    ("migration-schema", "Supabase migration for {area} tables and RLS"),
    ("smoke-script", "Extend tle-smoke or ship-verify check for {area}"),
    ("console-ui", "Governance console surface for {area} read-only v0"),
    ("www-copy", "WWW / trust-ledger copy block for {area} buyer line"),
    ("runbook", "RUNBOOK section for operating {area} in production"),
    ("diligence-doc", "Diligence one-pager evidence for {area} controls"),
    ("rate-limit", "Pilot rate limits and auth scopes for {area}"),
    ("webhook-event", "Webhook emission on {area} state transitions"),
    ("audit-export", "Audit-export field bundle for {area} decisions"),
    ("replay-test", "Deterministic replay test for {area} rule version"),
    ("tenant-isolation", "Cross-tenant negative tests for {area}"),
    ("metrics", "Prometheus metrics and dashboards for {area}"),
    ("ci-job", "GitHub Actions job gating merges on {area} tests"),
    ("schema-validate", "Request validation against locked schema for {area}"),
    ("examples-pack", "YAML/JSON examples pack under docs/spec/examples"),
    ("deprecation", "Deprecation notice and version bump for legacy {area} path"),
    ("performance", "Load test baseline and p95 budget for {area}"),
]


def plan_id(n: int) -> str:
    return f"NF-PLAN-{n:04d}"


def build_plans() -> list[dict]:
    plans: list[dict] = []
    n = 1
    for phase_code, phase_desc in PHASES.items():
        for tier_code, tier_desc in TIERS.items():
            for pattern_key, pattern_tpl in WORK_PATTERNS:
                area = AREAS[(n - 1) % len(AREAS)]
                area_label = area.replace("-", " ")
                title = pattern_tpl.format(area=area_label)
                plans.append(
                    {
                        "id": plan_id(n),
                        "phase": phase_code,
                        "phase_name": phase_desc,
                        "tier": tier_code,
                        "tier_name": tier_desc,
                        "area": area,
                        "pattern": pattern_key,
                        "title": title,
                        "outcome": f"Shippable increment for {area_label} in {phase_code} at {tier_code} priority.",
                        "verify": f"pytest and/or make ship-verify; area={area}; pattern={pattern_key}",
                        "no_asf": tier_code != "T1" or pattern_key not in ("runbook",),
                        "asf_only": pattern_key == "runbook" and tier_code == "T1",
                        "status": "backlog",
                        "blocks": [],
                    }
                )
                n += 1
                if n > 1000:
                    return plans
    return plans


def write_by_phase(plans: list[dict]) -> None:
    by_phase: dict[str, list[dict]] = {p: [] for p in PHASES}
    for pl in plans:
        by_phase[pl["phase"]].append(pl)
    phase_dir = PLANS_DIR / "by-phase"
    phase_dir.mkdir(parents=True, exist_ok=True)
    for code, desc in PHASES.items():
        lines = [
            f"# Plans — {code}: {desc}",
            "",
            f"**Count:** {len(by_phase[code])} · **Lane:** `noetfield_cloud` · **Filter:** no ASF when `asf_only` is false",
            "",
        ]
        for pl in by_phase[code]:
            flag = "ASF" if pl["asf_only"] else "agent"
            lines.append(
                f"- **{pl['id']}** [{pl['tier']}] ({flag}) {pl['title']} — `{pl['status']}`"
            )
        lines.append("")
        (phase_dir / f"{code.lower()}.md").write_text("\n".join(lines), encoding="utf-8")


def write_by_tier(plans: list[dict]) -> None:
    by_tier: dict[str, list[dict]] = {t: [] for t in TIERS}
    for pl in plans:
        by_tier[pl["tier"]].append(pl)
    tier_dir = PLANS_DIR / "by-tier"
    tier_dir.mkdir(parents=True, exist_ok=True)
    for code, desc in TIERS.items():
        lines = [
            f"# Plans — {code}: {desc}",
            "",
            f"**Count:** {len(by_tier[code])}",
            "",
        ]
        for pl in by_tier[code]:
            lines.append(f"- **{pl['id']}** [{pl['phase']}] {pl['title']}")
        lines.append("")
        (tier_dir / f"{code.lower()}.md").write_text("\n".join(lines), encoding="utf-8")


def write_no_asf_quick_pick(plans: list[dict]) -> None:
    agent_plans = [p for p in plans if not p["asf_only"] and p["status"] == "backlog"]
    # Prioritize T1/T2 in active product phases
    priority = {"P1": 0, "P2": 1, "P3": 2, "P4": 3, "P0": 4, "P5": 5}
    tier_pri = {"T1": 0, "T2": 1, "T3": 2, "T4": 3, "T5": 4}
    agent_plans.sort(key=lambda p: (tier_pri.get(p["tier"], 9), priority.get(p["phase"], 9), p["id"]))
    lines = [
        "# PLAN WITH NO ASF — quick pick",
        "",
        "When the founder says **PLAN WITH NO ASF**, start here. Pick the next **agent** item (not `asf_only`).",
        "",
        "**Full registry:** [registry.json](./registry.json) (1000 plans) · **Update:** `python3 scripts/generate-plans-registry.py`",
        "",
        "## Next 25 agent-ready plans",
        "",
    ]
    for pl in agent_plans[:25]:
        lines.append(
            f"1. **{pl['id']}** · {pl['phase']}/{pl['tier']} · {pl['title']}  \n"
            f"   Verify: `{pl['verify']}`"
        )
    lines.append("")
    lines.append("## Recently completed (update via `scripts/update-plan-status.py`)")
    lines.append("")
    lines.append("- NF-PLAN-* marked `done` in registry — run update script after each ship session.")
    lines.append("")
    (PLANS_DIR / "no-asf" / "QUICK_PICK.md").write_text("\n".join(lines), encoding="utf-8")


def _load_existing_status() -> dict[str, str]:
    path = PLANS_DIR / "registry.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {p["id"]: p.get("status", "backlog") for p in data.get("plans", [])}


def main() -> None:
    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    (PLANS_DIR / "no-asf").mkdir(exist_ok=True)
    existing_status = _load_existing_status()
    plans = build_plans()
    assert len(plans) == 1000, len(plans)
    for pl in plans:
        if pl["id"] in existing_status and existing_status[pl["id"]] != "backlog":
            pl["status"] = existing_status[pl["id"]]

    registry = {
        "version": 1,
        "generated_by": "scripts/generate-plans-registry.py",
        "lane": "noetfield_cloud",
        "thread": "THREAD-PORTFOLIO",
        "total": 1000,
        "phases": PHASES,
        "tiers": TIERS,
        "update_policy": "After each ship session: mark completed IDs done via scripts/update-plan-status.py; regenerate only when adding phases/tiers.",
        "plans": plans,
    }
    (PLANS_DIR / "registry.json").write_text(
        json.dumps(registry, indent=2) + "\n", encoding="utf-8"
    )

    write_by_phase(plans)
    write_by_tier(plans)
    write_no_asf_quick_pick(plans)

    agent_count = sum(1 for p in plans if not p["asf_only"])
    index = [
        "# Plan registry index (1000 plans)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total plans | {len(plans)} |",
        f"| Agent (`no_asf`) | {agent_count} |",
        f"| ASF-only flagged | {len(plans) - agent_count} |",
        "",
        "## Organization",
        "",
        "- **By phase:** [by-phase/](./by-phase/) — P0–P9 (100 plans each)",
        "- **By tier:** [by-tier/](./by-tier/) — T1–T5 (200 plans each)",
        "- **No ASF quick pick:** [no-asf/QUICK_PICK.md](./no-asf/QUICK_PICK.md)",
        "- **Machine registry:** [registry.json](./registry.json)",
        "",
        "## Phases",
        "",
    ]
    for code, desc in PHASES.items():
        index.append(f"- **{code}:** {desc}")
    index.append("")
    index.append("## Tiers")
    index.append("")
    for code, desc in TIERS.items():
        index.append(f"- **{code}:** {desc}")
    index.append("")
    (PLANS_DIR / "INDEX.md").write_text("\n".join(index), encoding="utf-8")
    print(f"Wrote {len(plans)} plans to {PLANS_DIR}")


if __name__ == "__main__":
    main()
