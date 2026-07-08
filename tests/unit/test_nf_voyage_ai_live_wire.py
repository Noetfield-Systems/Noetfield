"""Tests for Noetfield Voyage AI embedding provider + live wire guards."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import nf_embedding_provider_v1 as emb  # noqa: E402
import nf_voyage_ai_live_wire_v1 as wire  # noqa: E402


def test_voyage_key_detection(monkeypatch, tmp_path: Path) -> None:
    vault = tmp_path / "secrets.env"
    vault.write_text('VOYAGE_API_KEY=pa-test-key\n', encoding="utf-8")
    monkeypatch.setattr(emb, "_vault_paths", lambda: [vault])
    monkeypatch.delenv("VOYAGE_API_KEY", raising=False)
    assert emb.voyage_key_on_disk() is True


def test_fake_green_provider_status(monkeypatch) -> None:
    monkeypatch.setattr(
        wire,
        "provider_payload",
        lambda: {
            "mode": "hash_local",
            "model": "hash_local",
            "semantic": False,
            "hybrid": True,
            "producer": "nf-embedding-provider-v1",
            "voyage_key_on_disk": True,
        },
    )
    monkeypatch.setattr(wire, "voyage_key_on_disk", lambda: True)
    status = wire._provider_status()
    assert status["voyage_key_on_disk"] is True
    assert status["mode"] == "hash_local"
    assert status["ok"] is False


def test_rate_limited_search_is_degraded_ok(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    knowledge = root / "data" / "chatbot" / "knowledge"
    knowledge.mkdir(parents=True)
    for name in ("faq.md", "site.md", "offerings.md"):
        (knowledge / name).write_text(f"# {name}\nNoetfield governance pilot.\n", encoding="utf-8")

    monkeypatch.setattr(wire, "provider_payload", lambda: {"mode": "voyage", "model": "voyage-4-lite", "semantic": True, "hybrid": True, "producer": "x", "voyage_key_on_disk": True})
    monkeypatch.setattr(wire, "voyage_key_on_disk", lambda: True)

    def _boom(text: str, is_query: bool = False) -> list[float]:
        raise RuntimeError('Embedding API error 429: {"detail":"rate limits"}')

    monkeypatch.setattr(wire, "embed_text", _boom)
    receipt = wire.run_voyage_ai_live_wire(root=root, query="pilot")
    assert receipt["ok"] is True
    assert receipt["degraded"] is True
    assert receipt["search"]["mode"] == "rate_limited"


def test_live_wire_advisory_without_key(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    knowledge = root / "data" / "chatbot" / "knowledge"
    knowledge.mkdir(parents=True)
    for name in ("faq.md", "site.md", "offerings.md"):
        (knowledge / name).write_text(f"# {name}\nNoetfield governance pilot.\n", encoding="utf-8")

    monkeypatch.setattr(emb, "_vault_paths", lambda: [])
    monkeypatch.delenv("VOYAGE_API_KEY", raising=False)
    monkeypatch.setattr(wire, "embed_text", lambda text, is_query=False: [0.1, 0.2, 0.3])
    receipt = wire.run_voyage_ai_live_wire(root=root, query="pilot")
    assert receipt["ok"] is True
    assert receipt["required_when_key_present"] is False
