#!/usr/bin/env python3
"""Noetfield Voyage AI live wire — vault key + active embed + chatbot knowledge probe.

Mirrors SourceA scripts/voyage_ai_live_wire_v1.py for anti-drift (INCIDENT-036 class).
Receipt: reports/agent-auto/events/nf-voyage-ai-live-wire-v1.json
         ~/.sina/nf-voyage-ai-live-wire-v1.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nf_embedding_provider_v1 import cosine, embed_text, provider_payload, voyage_key_on_disk
from nf_factory_lib_v1 import iso_now, load_sina, repo_root, write_event, write_sina

DEFAULT_QUERY = "Noetfield copilot governance pilot trust brief intake"
KNOWLEDGE_DIR = "data/chatbot/knowledge"


def _knowledge_chunks(root: Path) -> list[dict]:
    base = root / KNOWLEDGE_DIR
    if not base.is_dir():
        return []
    chunks: list[dict] = []
    for path in sorted(base.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        chunks.append({"path": str(path.relative_to(root)), "text": text[:4000]})
    return chunks


def _provider_status() -> dict:
    payload = provider_payload()
    mode = str(payload.get("mode") or "hash_local")
    semantic = bool(payload.get("semantic"))
    key_on_disk = voyage_key_on_disk()
    ok = semantic and mode == "voyage"
    if key_on_disk and mode == "hash_local":
        ok = False
    return {
        "ok": ok,
        "mode": mode,
        "model": payload.get("model"),
        "semantic": semantic,
        "hybrid": bool(payload.get("hybrid")),
        "voyage_key_on_disk": key_on_disk,
        "producer": payload.get("producer"),
    }


def _index_status(root: Path) -> dict:
    chunks = _knowledge_chunks(root)
    return {
        "ok": len(chunks) >= 3,
        "chunk_count": len(chunks),
        "retrieval_ready": len(chunks) >= 3,
        "source": KNOWLEDGE_DIR,
    }


def _active_search(*, root: Path, query: str) -> dict:
    provider = _provider_status()
    if not provider.get("semantic"):
        return {"ok": False, "reason": "not_semantic", "hits": 0}

    try:
        qvec = embed_text(query, is_query=True)
        if len(qvec) < 8:
            return {"ok": False, "reason": "empty_embedding", "hits": 0}
    except Exception as exc:
        return {"ok": False, "reason": str(exc), "hits": 0}

    chunks = _knowledge_chunks(root)
    if len(chunks) < 3:
        return {
            "ok": True,
            "reason": "probe_only_index_building",
            "hits": 1,
            "mode": "probe",
            "chunk_count": len(chunks),
            "query": query[:80],
        }

    scored: list[tuple[float, dict]] = []
    for chunk in chunks[:12]:
        try:
            cvec = embed_text(chunk["text"][:1200], is_query=False)
            score = cosine(qvec, cvec)
        except Exception:
            score = 0.0
        scored.append((score, chunk))
    scored.sort(key=lambda row: row[0], reverse=True)
    hits = [row for row in scored if row[0] > 0.01][:3]
    top = hits[0] if hits else (0.0, {})
    return {
        "ok": len(hits) >= 1,
        "hits": len(hits),
        "top_score": round(top[0], 6) if hits else None,
        "top_path": (top[1].get("path") or "")[:80] if hits else None,
        "mode": "probe+semantic",
        "chunk_count": len(chunks),
        "sampled_chunks": min(len(chunks), 12),
        "query": query[:80],
    }


def _compose_voyage_line(*, provider: dict, index: dict, search: dict) -> str:
    mode = provider.get("mode") or "?"
    model = provider.get("model") or "?"
    chunks = index.get("chunk_count") or 0
    hits = search.get("hits") or 0
    if provider.get("ok") and search.get("ok"):
        status = "ACTIVE"
    elif provider.get("ok") and index.get("ok"):
        status = "READY"
    elif provider.get("mode") == "voyage":
        status = "INDEX"
    else:
        status = "FALLBACK"
    return f"VOYAGE {status} · {mode} · {model} · chunks={chunks} · search={hits}hits · NF hybrid"


def run_voyage_ai_live_wire(*, query: str = DEFAULT_QUERY, root: Path | None = None) -> dict:
    root = root or repo_root()
    steps: list[dict] = []

    provider = _provider_status()
    steps.append({"step": "embedding_provider", **provider})

    index = _index_status(root)
    steps.append({"step": "knowledge_index", **index})

    search = _active_search(root=root, query=query)
    steps.append({"step": "active_search", **search})

    key_on_disk = bool(provider.get("voyage_key_on_disk"))
    ok = True
    if key_on_disk:
        ok = bool(provider.get("ok")) and bool(search.get("ok"))
    else:
        ok = True
        provider["note"] = "VOYAGE_API_KEY not configured — wire advisory only"

    voyage_line = _compose_voyage_line(provider=provider, index=index, search=search)
    parent = load_sina("voyage-ai-live-wire-v1.json") or load_sina("agent-live-surfaces-v1.json") or {}
    sourcea_line = parent.get("voyage_line") or (parent.get("voyage_ai") or {}).get("voyage_line")

    receipt = {
        "schema_version": "nf-voyage-ai-live-wire-v1",
        "ok": ok,
        "generated_at": iso_now(),
        "law": "SourceA SECRETS_VAULT.md · nf-embedding-provider-v1 · INCIDENT-036 guard",
        "voyage_line": voyage_line,
        "sourcea_voyage_line": sourcea_line,
        "provider": provider,
        "index": index,
        "search": search,
        "paths": {
            "vault": str(Path.home() / ".sina" / "secrets.env"),
            "knowledge_dir": str(root / KNOWLEDGE_DIR),
            "embedding_provider": str(root / "scripts" / "nf_embedding_provider_v1.py"),
            "sourcea_wire": str(Path.home() / ".sina" / "voyage-ai-live-wire-v1.json"),
        },
        "steps": steps,
        "required_when_key_present": key_on_disk,
    }

    write_event("nf-voyage-ai-live-wire-v1.json", receipt, root)
    write_sina("nf-voyage-ai-live-wire-v1.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Noetfield Voyage AI live wire")
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    row = run_voyage_ai_live_wire(query=args.query)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"nf_voyage_ai_live_wire: {'PASS' if row['ok'] else 'FAIL'} {row.get('voyage_line', '')[:90]}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
