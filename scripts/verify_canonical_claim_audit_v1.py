#!/usr/bin/env python3
"""P11 claim audit — fail closed on unscoped forbidden phrases."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANONICAL_HTML = (
    "index.html",
    "system/index.html",
    "applications/index.html",
    "applications/trustfield/index.html",
    "public-interest/index.html",
    "proof/index.html",
    "about/index.html",
    "investors/index.html",
    "contact/index.html",
    "trust/index.html",
    "privacy/index.html",
    "motors/index.html",
    "runways/index.html",
)

FORBIDDEN_PATTERNS = [
    (r"quality-checked", "quality-checked"),
    (r"universally verified", "universally verified"),
    (r"production-ready", "production-ready"),
    (r"\bcertified\b", "certified"),
    (r"complete attempt evidence", "complete attempt evidence"),
    (r"exact per-run cost", "exact per-run cost"),
    (r"complete retry count", "complete retry count"),
    (r"self-repair across all jobs", "self-repair across all jobs"),
    (r"all outputs verified", "all outputs verified"),
    (r"TrustField.{0,40}(?:product|subsidiary) of Noetfield Systems", "TrustField as Noetfield product/subsidiary"),
    (r"SourceB.{0,20}canonical", "SourceB canonical line"),
    (r"SourceB\.ca", "SourceB catalogue reference"),
    (r"site rebuild in progress", "stale rebuild copy"),
    (r"Copilot Governance Pack", "legacy Copilot offer"),
    (r"Trust Brief", "legacy Trust Brief offer"),
]

ALLOWLIST_FILE_SNIPPETS = (
    "does not prove",
    "does not demonstrate",
    "not established",
    "not a Noetfield Systems Inc. product",
    "separate venture",
    "commissioning",
    "NOT YET ESTABLISHED",
)


class _VisibleTextParser(HTMLParser):
    """Extract visible text while skipping script/style and hidden options."""

    def __init__(self) -> None:
        super().__init__()
        self._pieces: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if lowered in {"script", "style"}:
            self._skip_depth += 1
            return
        if lowered == "option" and any((name or "").lower() == "hidden" for name, _ in attrs):
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._skip_depth and tag.lower() in {"script", "style", "option"}:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._pieces.append(data)


def visible_text(html: str) -> str:
    parser = _VisibleTextParser()
    parser.feed(html)
    parser.close()
    return re.sub(r"\s+", " ", " ".join(parser._pieces))


def audit_file(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    text = visible_text(html)
    lower = text.lower()
    errors: list[str] = []
    for pattern, label in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.I):
            if label.startswith("TrustField") and "separate venture" in lower:
                continue
            if label == "certified" and "not claim" in lower:
                continue
            errors.append(f"{path.relative_to(ROOT)}: forbidden phrase [{label}]")
    if "sourceb" in lower and "sourcea" not in lower[:200]:
        if "sourceb" in lower and not any(x in lower for x in ("removed", "not in the")):
            if re.search(r"sourceb", lower):
                errors.append(f"{path.relative_to(ROOT)}: SourceB reference in canonical narrative")
    return errors


def main() -> int:
    errors: list[str] = []
    for rel in CANONICAL_HTML:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing canonical page: {rel}")
            continue
        errors.extend(audit_file(path))
    if errors:
        print("verify_canonical_claim_audit: FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"verify_canonical_claim_audit: PASS ({len(CANONICAL_HTML)} canonical pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
