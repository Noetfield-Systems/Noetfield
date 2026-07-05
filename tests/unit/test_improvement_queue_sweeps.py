"""Repo health + security sweep helpers."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from nf_security_sweep import scan_tracked_secrets  # noqa: E402


def test_security_scan_tracked_secrets_returns_list() -> None:
    hits = scan_tracked_secrets()
    assert isinstance(hits, list)
