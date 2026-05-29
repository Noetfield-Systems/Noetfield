"""Load source-of-truth inventory registries into PostgreSQL."""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

import asyncpg


DEFAULT_INVENTORY = Path("docs/SOURCE_OF_TRUTH/registry/source_document_inventory.json")
DEFAULT_SOT = Path("docs/SOURCE_OF_TRUTH/registry/source_of_truth_registry.json")
DEFAULT_RULES = Path("docs/SOURCE_OF_TRUTH/registry/active_rule_candidates.json")


def normalize_database_url(database_url: str) -> str:
    return database_url.replace("postgresql+asyncpg://", "postgresql://")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class IngestionPayload:
    inventory: dict[str, Any]
    sot_registry: dict[str, Any]
    rule_registry: dict[str, Any]


def build_payload(
    inventory_path: Path = DEFAULT_INVENTORY,
    sot_path: Path = DEFAULT_SOT,
    rules_path: Path = DEFAULT_RULES,
) -> IngestionPayload:
    inventory = load_json(inventory_path)
    for document in inventory["documents"]:
        source_path = Path(document["source_path"])
        document["content_sha256"] = file_sha256(source_path)
    return IngestionPayload(
        inventory=inventory,
        sot_registry=load_json(sot_path),
        rule_registry=load_json(rules_path),
    )


async def ingest_payload(database_url: str, payload: IngestionPayload) -> None:
    connection = await asyncpg.connect(normalize_database_url(database_url))
    try:
        async with connection.transaction():
            batch_id = await connection.fetchval(
                """
                insert into noetfield.source_document_batches (
                  batch_key,
                  source_folder,
                  metadata
                )
                values ($1, $2, $3::jsonb)
                on conflict (batch_key) do update
                  set source_folder = excluded.source_folder,
                      metadata = excluded.metadata
                returning id
                """,
                payload.inventory["batch_id"],
                payload.inventory["source_folder"],
                json.dumps({"created_at": payload.inventory.get("created_at")}),
            )

            for document in payload.inventory["documents"]:
                await connection.execute(
                    """
                    insert into noetfield.source_documents (
                      batch_id,
                      document_key,
                      title,
                      domain,
                      work_package,
                      version_label,
                      source_path,
                      content_sha256,
                      classification,
                      status,
                      supersedes,
                      superseded_by,
                      metadata
                    )
                    values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13::jsonb)
                    on conflict (document_key) do update
                      set batch_id = excluded.batch_id,
                          title = excluded.title,
                          domain = excluded.domain,
                          work_package = excluded.work_package,
                          version_label = excluded.version_label,
                          source_path = excluded.source_path,
                          content_sha256 = excluded.content_sha256,
                          classification = excluded.classification,
                          status = excluded.status,
                          supersedes = excluded.supersedes,
                          superseded_by = excluded.superseded_by,
                          metadata = excluded.metadata
                    """,
                    batch_id,
                    document["document_key"],
                    document["title"],
                    document["domain"],
                    document.get("work_package"),
                    document.get("version_label"),
                    document["source_path"],
                    document["content_sha256"],
                    document["classification"],
                    document["status"],
                    document.get("supersedes", []),
                    document.get("superseded_by"),
                    json.dumps(document, default=str),
                )

            for decision in payload.sot_registry["decisions"]:
                await connection.execute(
                    """
                    insert into noetfield.source_of_truth_registry (
                      registry_version,
                      domain,
                      active_document_key,
                      active_version,
                      decision,
                      rationale,
                      confidence
                    )
                    values ($1, $2, $3, $4, $5, $6, $7)
                    on conflict (registry_version, domain) do update
                      set active_document_key = excluded.active_document_key,
                          active_version = excluded.active_version,
                          decision = excluded.decision,
                          rationale = excluded.rationale,
                          confidence = excluded.confidence
                    """,
                    payload.sot_registry["registry_version"],
                    decision["domain"],
                    decision["active_document_key"],
                    decision.get("active_version"),
                    decision["decision"],
                    decision["rationale"],
                    decision["confidence"],
                )

            for rule in payload.rule_registry["active_rule_candidates"]:
                await connection.execute(
                    """
                    insert into noetfield.active_rule_candidates (
                      registry_version,
                      rule_key,
                      domain,
                      source_document_key,
                      activation_status,
                      rule_type,
                      summary,
                      implementation_target,
                      metadata
                    )
                    values ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
                    on conflict (registry_version, rule_key) do update
                      set domain = excluded.domain,
                          source_document_key = excluded.source_document_key,
                          activation_status = excluded.activation_status,
                          rule_type = excluded.rule_type,
                          summary = excluded.summary,
                          implementation_target = excluded.implementation_target,
                          metadata = excluded.metadata
                    """,
                    payload.rule_registry["registry_version"],
                    rule["rule_key"],
                    rule["domain"],
                    rule["source_document_key"],
                    rule["activation_status"],
                    rule["rule_type"],
                    rule["summary"],
                    rule.get("implementation_target"),
                    json.dumps(rule, default=str),
                )
    finally:
        await connection.close()


def summarize_payload(payload: IngestionPayload) -> dict[str, Any]:
    return {
        "batch_id": payload.inventory["batch_id"],
        "document_count": len(payload.inventory["documents"]),
        "sot_decision_count": len(payload.sot_registry["decisions"]),
        "active_rule_candidate_count": len(payload.rule_registry["active_rule_candidates"]),
        "active_documents": [
            decision["active_document_key"] for decision in payload.sot_registry["decisions"]
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--sot", default=str(DEFAULT_SOT))
    parser.add_argument("--rules", default=str(DEFAULT_RULES))
    args = parser.parse_args()

    payload = build_payload(Path(args.inventory), Path(args.sot), Path(args.rules))
    print(json.dumps(summarize_payload(payload), indent=2, sort_keys=True))
    if args.dry_run:
        return
    if not args.database_url:
        raise SystemExit("DATABASE_URL is required unless --dry-run is used")
    asyncio.run(ingest_payload(args.database_url, payload))


if __name__ == "__main__":
    main()
