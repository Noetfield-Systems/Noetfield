#!/usr/bin/env python3
"""Noetfield live nerve receipt: one machine truth for public output and chatbot knowledge."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "governance" / "NOETFIELD_LIVE_NERVE_RECEIPT.json"
PUBLIC_OUTPUT_SCRIPT = ROOT / "scripts" / "verify-public-output-allowlist.py"


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    except Exception:
        return None
    return result.stdout.strip()


def load_public_output_module() -> Any:
    spec = importlib.util.spec_from_file_location("verify_public_output_allowlist", PUBLIC_OUTPUT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load verify-public-output-allowlist.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def public_output_status() -> dict[str, Any]:
    module = load_public_output_module()
    output = ROOT / ".vercel" / "output" / "static"
    findings = module.scan(output)
    return {
        "ok": not findings,
        "output": str(output),
        "blocked_count": len(findings),
        "findings": findings[:50],
    }


def chatbot_status() -> dict[str, Any]:
    for rel in (
        ".",
        "packages/types",
        "packages/config",
        "packages/sdk",
        "services/events",
        "services/ledger",
        "services/graph",
        "services/governance",
        "services/signals",
        "services/workflow",
        "services/ai-runtime",
        "services/inspectors",
        "services/identity",
        "services/copilot-governance",
        "services/factories",
        "services/trust-brief",
        "services/legal-review",
        "services/aml-trace",
    ):
        sys.path.insert(0, str(ROOT / rel))
    from noetfield_governance.chatbot_knowledge import (  # type: ignore
        knowledge_bundle_version,
        knowledge_context_stats,
        knowledge_manifest_violations,
    )

    violations = knowledge_manifest_violations()
    return {
        "ok": not violations,
        "bundle_version": knowledge_bundle_version(),
        "manifest_hash": sha256_file(ROOT / "data" / "chatbot" / "MANIFEST.json"),
        "stats": knowledge_context_stats() if not violations else {},
        "violations": violations,
    }


def public_doc_freshness() -> dict[str, Any]:
    # First cut: public markdown must stay in explicitly allowed public folders.
    allowed_prefixes = (
        "docs/api/",
        "docs/copilot/",
        "docs/diligence/",
        "docs/federal/",
        "docs/msp/",
        "docs/runtime/",
        "docs/templates/",
        "docs/trust-brief/",
    )
    public_md = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob("docs/**/*.md")
        if any(path.relative_to(ROOT).as_posix().startswith(prefix) for prefix in allowed_prefixes)
    ]
    return {
        "ok": True,
        "public_markdown_count": len(public_md),
        "contract": "public markdown requires generated metadata in phase 2; raw internal docs are blocked from output now",
    }


def build_receipt() -> dict[str, Any]:
    public_output = public_output_status()
    chatbot = chatbot_status()
    docs = public_doc_freshness()
    ok = bool(public_output["ok"] and chatbot["ok"] and docs["ok"])
    return {
        "schema": "noetfield-live-nerve-receipt-v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repo": str(ROOT),
        "git_sha": git_sha(),
        "ok": ok,
        "gate": "PASS" if ok else "FAIL",
        "next_safe_action": (
            "use this receipt as current truth before docs or chat summaries"
            if ok
            else "repair failed live nerve surfaces before using docs as truth"
        ),
        "nodes": {
            "N1_PUBLIC_OUTPUT": public_output,
            "N2_CHAT_TRUTH": chatbot,
            "N3_DOC_FRESHNESS": docs,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt()
    if args.write:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"NOETFIELD_LIVE_NERVE {receipt['gate']} receipt={RECEIPT}")
        for node, status in receipt["nodes"].items():
            print(f"{node} ok={status['ok']}")
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
