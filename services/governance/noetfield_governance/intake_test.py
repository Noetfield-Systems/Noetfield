"""Probe/E2E test intake detection — separate from customer leads."""

from __future__ import annotations

import re
from typing import Any

TEST_FORM_IDS = frozenset({"nf_intake_e2e", "nf_probe_cron"})
TEST_TOPICS = frozenset({"e2e", "probe"})
TEST_EMAILS = frozenset({"e2e@noetfield.com", "probe@noetfield.com"})
_TEST_RID_RE = re.compile(r"^RID-(E2E|PROBE)-", re.IGNORECASE)


def is_test_intake(
    *,
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
    contact_email: str | None = None,
) -> bool:
    meta = metadata or {}
    if meta.get("intake_kind") == "test":
        return True
    if str(meta.get("form_id") or "").lower() in TEST_FORM_IDS:
        return True
    if str(meta.get("topic") or "").lower() in TEST_TOPICS:
        return True
    email = (contact_email or "").strip().lower()
    if email in TEST_EMAILS:
        return True
    rid = (request_id or "").strip().upper()
    if rid and _TEST_RID_RE.match(rid):
        return True
    return False


def pipeline_label(metadata: dict[str, Any]) -> str:
    if metadata.get("pipeline"):
        return str(metadata["pipeline"])
    form_id = str(metadata.get("form_id") or "").lower()
    if form_id == "nf_probe_cron":
        return "probe_cron:intake_e2e"
    if form_id == "nf_intake_e2e":
        return "nf_intake_e2e:deploy_verify"
    topic = str(metadata.get("topic") or "").lower()
    if topic == "probe":
        return "probe:intake"
    if topic == "e2e":
        return "e2e:intake"
    return "test:intake"


def ensure_test_metadata(
    metadata: dict[str, Any] | None,
    *,
    request_id: str | None = None,
    contact_email: str | None = None,
) -> dict[str, Any]:
    meta = dict(metadata or {})
    if not is_test_intake(metadata=meta, request_id=request_id, contact_email=contact_email):
        return meta
    meta["intake_kind"] = "test"
    if not meta.get("pipeline"):
        meta["pipeline"] = pipeline_label(meta)
    return meta
