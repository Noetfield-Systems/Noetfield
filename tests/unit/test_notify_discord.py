"""Discord ops sink — node smoke + intake wiring stays additive."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_notify_discord_node_smoke() -> None:
    result = subprocess.run(
        ["node", str(ROOT / "scripts" / "test_notify_discord.cjs")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "notify-discord smoke ok" in result.stdout


def test_intake_reports_discord_without_gating_response() -> None:
    """Telegram stays the delivery decider; Discord only adds fields to the payload."""
    source = (ROOT / "api" / "intake.js").read_text(encoding="utf-8")

    assert "sendIntakeDiscord" in source, "intake posts to the Discord sink"
    assert "discord_delivered" in source, "intake reports Discord delivery"

    # No response branch may switch on Discord delivery.
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("if (") and "discord" in stripped.lower():
            raise AssertionError(f"Discord must not gate the intake response: {stripped}")


def test_pages_function_bundle_includes_discord_sink() -> None:
    bundled = (ROOT / "functions" / "api" / "intake.js").read_text(encoding="utf-8")
    assert "DISCORD_OPS_WEBHOOK_URL" in bundled, "bundle is stale — rerun scripts/bundle-pages-functions.mjs"
