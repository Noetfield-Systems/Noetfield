#!/usr/bin/env python3
"""Generate batch 009 prompt OS, context engines, LinkedIn, TrustField registry."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-009"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "strategic-structuring-reasoning-engine-stage2-v20-generic.md",
        "document_key": "strategic-structuring-reasoning-engine-stage2-v20-generic",
        "title": "Strategic Structuring & Reasoning Engine v2.0 — Stage-2 (Generic)",
        "domain": "prompt_stage2_structuring",
        "version_label": "stage2-v2.0-generic",
        "classification": "generic_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": "noetfield-strategic-structuring-reasoning-engine-stage2-v20",
    },
    {
        "file": "noetfield-strategic-structuring-reasoning-engine-stage2-v20.md",
        "document_key": "noetfield-strategic-structuring-reasoning-engine-stage2-v20",
        "title": "Noetfield Strategic Structuring & Reasoning Engine v2.0 — Stage-2",
        "domain": "prompt_stage2_structuring",
        "version_label": "stage2-v2.0-noetfield",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["strategic-structuring-reasoning-engine-stage2-v20-generic"],
        "superseded_by": None,
    },
    {
        "file": "master-strategic-context-engine-v35-elite.md",
        "document_key": "master-strategic-context-engine-v35-elite",
        "title": "Master Strategic Context Engine v3.5 — Elite Extraction",
        "domain": "prompt_stage1_extraction",
        "version_label": "v3.5-elite",
        "classification": "active_deep_extraction_reference",
        "status": "reference",
        "supersedes": ["master-context-engine-v31-adaptive"],
        "superseded_by": None,
    },
    {
        "file": "master-strategic-context-engine-v37-efficient.md",
        "document_key": "master-strategic-context-engine-v37-efficient",
        "title": "Master Strategic Context Engine v3.7 — High-Efficiency Extraction",
        "domain": "prompt_stage1_extraction",
        "version_label": "v3.7-efficient",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "master-context-engine-v31-adaptive.md",
        "document_key": "master-context-engine-v31-adaptive",
        "title": "Master Context Engine v3.1 — Adaptive Compression Kernel",
        "domain": "prompt_stage1_extraction",
        "version_label": "v3.1-adaptive",
        "classification": "superseded_extraction_reference",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "master-strategic-context-engine-v37-efficient",
    },
    {
        "file": "noetfield-execution-output-engine-v1-prompt.md",
        "document_key": "noetfield-execution-output-engine-v1-prompt",
        "title": "Noetfield Execution Output Engine v1 — Stage-3 Prompt",
        "domain": "prompt_stage3_execution",
        "version_label": "execution-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-prompt-constitution-blueprint-directory-v10.md",
        "document_key": "noetfield-prompt-constitution-blueprint-directory-v10",
        "title": "Noetfield Prompt Constitution & Blueprint Directory v1.0",
        "domain": "noetfield_prompt_os",
        "version_label": "constitution-v1.0",
        "classification": "active_enterprise_pipeline_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-prompt-system-constitution-v02-mvp.md",
        "document_key": "noetfield-prompt-system-constitution-v02-mvp",
        "title": "Noetfield Prompt System Constitution v0.2 — MVP Optimized",
        "domain": "noetfield_prompt_os",
        "version_label": "constitution-v0.2-mvp",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "prompt-engine-comparison-matrix-v02-mvp.md",
        "document_key": "prompt-engine-comparison-matrix-v02-mvp",
        "title": "Prompt Engine Comparison Matrix — v0.2 MVP OS",
        "domain": "noetfield_prompt_os",
        "version_label": "comparison-matrix-v1",
        "classification": "active_operational_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "all-prompt-constitutions-comparison-fa.md",
        "document_key": "all-prompt-constitutions-comparison-fa",
        "title": "All Prompt Constitutions Comparison (Persian)",
        "domain": "noetfield_prompt_os",
        "version_label": "comparison-fa-v1",
        "classification": "reference_methodology",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "linkedin-profile-hyper-commercial-v4.md",
        "document_key": "linkedin-profile-hyper-commercial-v4",
        "title": "LinkedIn Profile — Hyper-Commercial v4 (Enterprise GTM)",
        "domain": "noetfield_commercial_positioning",
        "version_label": "linkedin-v4",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "trustfield-noetfield-strategic-architecture-locked-fa.md",
        "document_key": "trustfield-noetfield-strategic-architecture-locked-fa",
        "title": "TrustField / Noetfield Strategic Architecture — Locked SSOT (Persian)",
        "domain": "noetfield_trust_gtm_strategy",
        "version_label": "locked-ssot-v1-fa",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "prompt-memory-extraction-workflow-fa.md",
        "document_key": "prompt-memory-extraction-workflow-fa",
        "title": "Prompt Memory Extraction Workflow (Persian label)",
        "domain": "prompt_stage1_extraction",
        "version_label": "workflow-label-v1-fa",
        "classification": "reference_only",
        "status": "reference",
        "supersedes": [],
        "superseded_by": "master-strategic-context-engine-v37-efficient",
    },
]

BODIES = {
    "strategic-structuring-reasoning-engine-stage2-v20-generic.md": """# Strategic Structuring & Reasoning Engine v2.0 (Generic)

Document key: `strategic-structuring-reasoning-engine-stage2-v20-generic`

Stage-2 prompt: master tables, narrative sections, strategic reasoning, golden recommendation.
Input from Stage-1 v3.5 extraction. Superseded by Noetfield-specific Stage-2 variant.
""",
    "noetfield-strategic-structuring-reasoning-engine-stage2-v20.md": """# Noetfield Strategic Structuring & Reasoning Engine v2.0

Document key: `noetfield-strategic-structuring-reasoning-engine-stage2-v20`

Noetfield-aligned Stage-2: rail-level logic table, intent-to-execution mapping,
institutional tone, multi-rail compliance reasoning, golden strategic recommendation.

**Active Stage-2 SOT** for Noetfield prompt pipeline.
""",
    "master-strategic-context-engine-v35-elite.md": """# Master Strategic Context Engine v3.5 — Elite

Document key: `master-strategic-context-engine-v35-elite`

Lossless full-chat extraction: normalization, clustering, contradiction/evolution,
memory graph, intent reconstruction. Use for complex multi-chat deep mining.
""",
    "master-strategic-context-engine-v37-efficient.md": """# Master Strategic Context Engine v3.7 — Efficient

Document key: `master-strategic-context-engine-v37-efficient`

Fast single-chat extraction with light normalization, smart clustering,
conflict/evolution check, strategic memory map. **Active Stage-1 SOT** for default runs.
""",
    "master-context-engine-v31-adaptive.md": """# Master Context Engine v3.1 — Adaptive

Document key: `master-context-engine-v31-adaptive`

Adaptive output by chat size (small/medium/complex). Superseded by v3.7 for default path.
""",
    "noetfield-execution-output-engine-v1-prompt.md": """# Noetfield Execution Output Engine v1

Document key: `noetfield-execution-output-engine-v1-prompt`

Stage-3: STATE → LOCKED DECISIONS → BLOCKERS → STRATEGIES → EXECUTION VECTOR →
GOLDEN EXECUTION COMMAND. Action-first, zero ambiguity.

**Active Stage-3 SOT** for prompt pipeline.
""",
    "noetfield-prompt-constitution-blueprint-directory-v10.md": """# Noetfield Prompt Constitution v1.0 — 3-Stage Pipeline

Document key: `noetfield-prompt-constitution-blueprint-directory-v10`

Mandatory pipeline: Stage-1 Extraction (v3.7) → Stage-2 Structuring → Stage-3 Execution.
Engine roles, interaction rules, lossless transfer, execution priority.

**Active enterprise 3-stage pipeline reference.**
""",
    "noetfield-prompt-system-constitution-v02-mvp.md": """# Noetfield Prompt Constitution v0.2 — MVP

Document key: `noetfield-prompt-system-constitution-v02-mvp`

2-step OS: Intelligence Builder → Decision Engine. Minimum structure, maximum
execution clarity, GAP tagging, action-first. **Active MVP prompt OS SOT.**
""",
    "prompt-engine-comparison-matrix-v02-mvp.md": """# Prompt Engine Comparison Matrix

Document key: `prompt-engine-comparison-matrix-v02-mvp`

21-criteria comparison of v1 mining, v2 kernel, v3.x engines, Stage-2, Execution v1,
v0.2 constitution. Positions v0.2 as governing OS layer.
""",
    "all-prompt-constitutions-comparison-fa.md": """# All Constitutions Comparison (Persian)

Document key: `all-prompt-constitutions-comparison-fa`

Compares v1.0 full, v0.2 MVP, 3-stage pipeline, execution engine constitutions.
""",
    "linkedin-profile-hyper-commercial-v4.md": """# LinkedIn Profile Hyper-Commercial v4

Document key: `linkedin-profile-hyper-commercial-v4`

Headline: AI Governance & RWA Infrastructure Architect | Pre-Execution Risk & Compliance.
Products: Trust Brief, Evidence-Grade Audit Engine, Policy Replay, Pre-Execution Regulatory Pack.
No custody/payments — outside RPAA/FINTRAC perimeter narrative.

**Active commercial positioning SOT** for enterprise inbound.
""",
    "trustfield-noetfield-strategic-architecture-locked-fa.md": """# TrustField / Noetfield Strategic Architecture (Locked)

Document key: `trustfield-noetfield-strategic-architecture-locked-fa`

Phases: conceptual framing → system design → market execution. Core assets:
Governance Latency, Audit Evidence Layer, Big Four non-conflict positioning.
14-day execution plan. Compliance-as-Infrastructure thesis.

**Active trust/GTM strategy SOT** (Persian institutional summary).
""",
    "prompt-memory-extraction-workflow-fa.md": """# Prompt Memory Extraction Workflow

Document key: `prompt-memory-extraction-workflow-fa`

Placeholder label for chat memory extraction workflow; use v3.7 / v3.5 engines as normative prompts.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_prompt_os",
        "active_document_key": "noetfield-prompt-system-constitution-v02-mvp",
        "active_version": "constitution-v0.2-mvp",
        "decision": "active_source_of_truth",
        "rationale": "v0.2 MVP constitution governs fast intelligence-to-action cycles with 2-step pipeline for founders and operators.",
        "confidence": 0.9,
    },
    {
        "domain": "noetfield_prompt_os_enterprise",
        "active_document_key": "noetfield-prompt-constitution-blueprint-directory-v10",
        "active_version": "constitution-v1.0",
        "decision": "active_enterprise_pipeline_reference",
        "rationale": "v1.0 directory defines mandatory 3-stage extraction → structuring → execution for long-form multi-chat workflows.",
        "confidence": 0.88,
    },
    {
        "domain": "prompt_stage1_extraction",
        "active_document_key": "master-strategic-context-engine-v37-efficient",
        "active_version": "v3.7-efficient",
        "decision": "active_source_of_truth",
        "rationale": "v3.7 is the default high-efficiency Stage-1 extractor; v3.5 retained for elite deep extraction on complex chats.",
        "confidence": 0.91,
    },
    {
        "domain": "prompt_stage2_structuring",
        "active_document_key": "noetfield-strategic-structuring-reasoning-engine-stage2-v20",
        "active_version": "stage2-v2.0-noetfield",
        "decision": "active_source_of_truth",
        "rationale": "Noetfield-specific Stage-2 adds rail-level and intent-to-execution tables plus institutional reasoning format.",
        "confidence": 0.9,
    },
    {
        "domain": "prompt_stage3_execution",
        "active_document_key": "noetfield-execution-output-engine-v1-prompt",
        "active_version": "execution-v1",
        "decision": "active_source_of_truth",
        "rationale": "Execution Output Engine v1 is the Stage-3 decision compiler with golden execution command.",
        "confidence": 0.92,
    },
    {
        "domain": "noetfield_commercial_positioning",
        "active_document_key": "linkedin-profile-hyper-commercial-v4",
        "active_version": "linkedin-v4",
        "decision": "active_source_of_truth",
        "rationale": "v4 LinkedIn copy is search-optimized for enterprise buyers and product-oriented governance narrative.",
        "confidence": 0.87,
    },
    {
        "domain": "noetfield_trust_gtm_strategy",
        "active_document_key": "trustfield-noetfield-strategic-architecture-locked-fa",
        "active_version": "locked-ssot-v1-fa",
        "decision": "active_source_of_truth",
        "rationale": "Locked strategic architecture defines Governance Latency thesis, Audit Evidence Layer wedge, and 14-day execution plan.",
        "confidence": 0.89,
    },
]

NEW_RULES = [
    {
        "rule_key": "prompt-pipeline-strict-stage-sequencing",
        "domain": "noetfield_prompt_os",
        "source_document_key": "noetfield-prompt-constitution-blueprint-directory-v10",
        "activation_status": "active_design_rule",
        "rule_type": "prompt_governance",
        "summary": "Long-form workflows must run Stage-1 → Stage-2 → Stage-3 without cross-role leakage.",
        "implementation_target": "developer_bootstrap",
    },
    {
        "rule_key": "prompt-mvp-action-first-two-step",
        "domain": "noetfield_prompt_os",
        "source_document_key": "noetfield-prompt-system-constitution-v02-mvp",
        "activation_status": "active_design_rule",
        "rule_type": "prompt_governance",
        "summary": "MVP prompt cycles end in decision + 1-3 actions; mark unclear items as GAP not guesses.",
        "implementation_target": "developer_bootstrap",
    },
    {
        "rule_key": "prompt-stage1-no-hallucination-lossless",
        "domain": "prompt_stage1_extraction",
        "source_document_key": "master-strategic-context-engine-v37-efficient",
        "activation_status": "active_design_rule",
        "rule_type": "extraction_governance",
        "summary": "Stage-1 extraction preserves contradictions and evolutions; no external assumptions.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "prompt-stage3-golden-execution-command",
        "domain": "prompt_stage3_execution",
        "source_document_key": "noetfield-execution-output-engine-v1-prompt",
        "activation_status": "active_design_rule",
        "rule_type": "execution_governance",
        "summary": "Stage-3 must output a single golden execution command with 1-3 concrete actions.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "commercial-pre-execution-governance-narrative",
        "domain": "noetfield_commercial_positioning",
        "source_document_key": "linkedin-profile-hyper-commercial-v4",
        "activation_status": "reference_only",
        "rule_type": "gtm",
        "summary": "Commercial narrative emphasizes pre-execution governance, no custody, and governance latency reduction.",
        "implementation_target": None,
    },
    {
        "rule_key": "trust-audit-evidence-layer-wedge",
        "domain": "noetfield_trust_gtm_strategy",
        "source_document_key": "trustfield-noetfield-strategic-architecture-locked-fa",
        "activation_status": "reference_only",
        "rule_type": "gtm",
        "summary": "First sellable unit is Continuous Audit Evidence API / Evidence Pack in one real cycle.",
        "implementation_target": None,
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-009

Noetfield Prompt Operating System (v0.2 MVP + v1.0 3-stage), context engines
v3.5/v3.7, Stage-2/3 prompts, LinkedIn v4, TrustField locked strategy.

## Pipeline (enterprise)

v3.7 extraction → Noetfield Stage-2 → Execution Engine v1 (under v1.0 constitution)

## Pipeline (MVP)

Intelligence Builder → Decision Engine (v0.2 constitution)

## Active GTM

- LinkedIn: `linkedin-profile-hyper-commercial-v4`
- Trust strategy: `trustfield-noetfield-strategic-architecture-locked-fa`
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-009", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-009"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-009/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-009",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-6"

    rules["registry_version"] = "2026-05-29-rules-6"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
