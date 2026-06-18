#!/usr/bin/env python3
"""NF live surfaces — one-line factory truth for panels + orient (L0.5)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from nf_factory_lib_v1 import (
    agent_id,
    first_pending_task,
    iso_now,
    load_event,
    load_sina,
    portfolio_progress,
    repo_root,
    write_event,
    write_sina,
)


def _git_short(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def build_live_surfaces(root: Path | None = None) -> dict:
    root = root or repo_root()
    plan_path = root / "os/plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else {}
    pending = first_pending_task(plan)

    gate = load_event("nf-session-gate-v1.json", root) or load_sina("nf_session_gate_receipt_v1.json") or {}
    stale = load_event("nf-stale-guard-v1.json", root) or {}
    voyage = load_event("nf-voyage-integrity-v1.json", root) or {}
    routing = load_event("nf-live-routing-v1.json", root) or {}

    pid = (pending or {}).get("id", "")
    title = (pending or {}).get("title", "")
    product_now_line = f"{pid} — {title}" if pid else "no pending next_tasks"

    portfolio = portfolio_progress()
    portfolio_line = None
    if portfolio:
        portfolio_line = f"portfolio {portfolio['done']}/{portfolio['total']} done"

    gate_ok = bool(gate.get("ok"))
    context_stale = bool(stale.get("context_stale"))
    voyage_ok = bool(voyage.get("ok", True))

    surfaces = {
        "schema_version": "nf-live-surfaces-v1",
        "generated_at": iso_now(),
        "agent_id": agent_id(),
        "plane": "noetfield_cloud",
        "product_now_line": product_now_line,
        "portfolio_now_line": portfolio_line,
        "gate_ok": gate_ok,
        "context_stale": context_stale,
        "voyage_ok": voyage_ok,
        "pending_task": pending,
        "git_sha": _git_short(root),
        "routing_pending": routing.get("pending_task"),
        "quote_rule": "Agents must quote product_now_line from this file — not chat memory",
        "heal": "make nf-onboard" if context_stale or not gate_ok else None,
    }
    return surfaces


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    surfaces = build_live_surfaces()
    write_event("nf-live-surfaces-v1.json", surfaces)
    write_sina("nf-live-surfaces-v1.json", surfaces)

    if args.json:
        print(json.dumps(surfaces, indent=2))
    else:
        print(f"product_now_line: {surfaces['product_now_line']}")
        if surfaces.get("portfolio_now_line"):
            print(f"portfolio_now_line: {surfaces['portfolio_now_line']}")
        print(f"gate_ok={surfaces['gate_ok']} stale={surfaces['context_stale']} voyage_ok={surfaces['voyage_ok']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
