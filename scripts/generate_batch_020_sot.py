#!/usr/bin/env python3
"""Generate batch 020: Unified Cognitive Governance + SOT Master v1.0."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-020"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-unified-cognitive-governance-system-v1.md",
        "document_key": "noetfield-unified-cognitive-governance-system-v1",
        "title": "Unified Cognitive Governance System v1.0 (Sina AI OS)",
        "domain": "noetfield_cognitive_os_unified",
        "version_label": "ucgs-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-sot-master-document-v1.md",
        "document_key": "noetfield-sot-master-document-v1",
        "title": "Source of Truth Master Document v1.0 (Layer Hierarchy + OAS)",
        "domain": "noetfield_cognitive_os_sot_master",
        "version_label": "sot-master-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
]

NEW_SOT = [
    {
        "domain": "noetfield_cognitive_os_sot_master",
        "active_document_key": "noetfield-sot-master-document-v1",
        "active_version": "sot-master-v1",
        "decision": "active_source_of_truth",
        "rationale": "Canonical L0–L3 + archive hierarchy and OAS loop for internal repo cognition; subordinate to GCIP v4 for legal identity.",
        "confidence": 0.94,
    },
    {
        "domain": "noetfield_cognitive_os_unified",
        "active_document_key": "noetfield-unified-cognitive-governance-system-v1",
        "active_version": "ucgs-v1",
        "decision": "active_methodology_reference",
        "rationale": "Full OAS + Golden Edge synthesis spec; pairs with SOT master v1.",
        "confidence": 0.92,
    },
]

NEW_RULES = [
    {
        "rule_key": "cognitive-os-sot-master-internal-hierarchy",
        "domain": "noetfield_cognitive_os_sot_master",
        "source_document_key": "noetfield-sot-master-document-v1",
        "activation_status": "active_design_rule",
        "rule_type": "architecture_governance",
        "summary": "Use SOT master v1 for L0–L3 repo layout; GCIP v4 remains legal L0 for Noetfield Inc.",
        "implementation_target": "documentation_governance",
    },
    {
        "rule_key": "oas-owner-ratification-before-commit",
        "domain": "noetfield_cognitive_os_unified",
        "source_document_key": "noetfield-unified-cognitive-governance-system-v1",
        "activation_status": "active_design_rule",
        "rule_type": "epistemic_governance",
        "summary": "Multi-agent claims require OAS pipeline and owner ratification before L1/L2 writes.",
        "implementation_target": "governance_runtime",
    },
    {
        "rule_key": "l2-never-executes-without-l0-l1",
        "domain": "noetfield_cognitive_os_sot_master",
        "source_document_key": "noetfield-sot-master-document-v1",
        "activation_status": "active_design_rule",
        "rule_type": "architecture_governance",
        "summary": "L2 knowledge cannot override L1 runtime or L0 constitution; archive prohibited docs.",
        "implementation_target": "documentation_governance",
    },
    {
        "rule_key": "golden-edge-synthesis-not-majority-vote",
        "domain": "noetfield_cognitive_os_unified",
        "source_document_key": "noetfield-unified-cognitive-governance-system-v1",
        "activation_status": "active_design_rule",
        "rule_type": "epistemic_governance",
        "summary": "Golden Edge synthesis maximizes coherence; not chatbot majority vote.",
        "implementation_target": "governance_runtime",
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-020", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-020"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-020/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-020",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-17"

    rules["registry_version"] = "2026-05-29-rules-17"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
