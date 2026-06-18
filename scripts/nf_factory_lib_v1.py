#!/usr/bin/env python3
"""Shared helpers for NF-GAOS factory spine (W3)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def events_dir(root: Path | None = None) -> Path:
    d = (root or repo_root()) / "reports/agent-auto/events"
    d.mkdir(parents=True, exist_ok=True)
    return d


def sina_dir() -> Path:
    d = Path.home() / ".sina"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_event(name: str, data: dict, root: Path | None = None) -> Path:
    path = events_dir(root) / name
    write_json(path, data)
    return path


def write_sina(name: str, data: dict) -> Path | None:
    try:
        path = sina_dir() / name
        write_json(path, data)
        return path
    except OSError:
        return None


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_event(name: str, root: Path | None = None) -> dict | None:
    return load_json(events_dir(root) / name)


def load_sina(name: str) -> dict | None:
    return load_json(sina_dir() / name)


def first_pending_task(plan: dict) -> dict | None:
    for row in plan.get("next_tasks") or []:
        if str(row.get("status", "")).lower() == "pending":
            return row
    return None


def agent_id() -> str:
    return os.environ.get("NOETFIELD_AGENT_ID", "noetfield_cloud")


def load_lock() -> dict | None:
    return load_sina("nf-executor-lock-v1.json") or load_event("nf-executor-lock-v1.json")


def write_lock(data: dict, root: Path | None = None) -> None:
    write_event("nf-executor-lock-v1.json", data, root)
    write_sina("nf-executor-lock-v1.json", data)


def portfolio_progress() -> dict | None:
    reg = Path.home() / "Desktop/1 PAGER/portfolio-300-locked/REGISTRY.json"
    if not reg.is_file():
        reg = Path("/Users/sinakazemnezhad/Desktop/1 PAGER/portfolio-300-locked/REGISTRY.json")
    if not reg.is_file():
        return None
    data = load_json(reg)
    if not data:
        return None
    plans = data.get("plans") or []
    done = sum(1 for p in plans if p.get("status") == "done")
    return {"total": len(plans), "done": done, "backlog": len(plans) - done, "registry": str(reg)}
