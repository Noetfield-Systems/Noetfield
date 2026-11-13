#!/usr/bin/env python3
"""Fail closed unless public output exactly matches the tracked allowlist."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "www-pages-dist"
ALLOWLIST = ROOT / "governance" / "www-public-artifact-v1.json"
DENYLIST = ROOT / "governance" / "PUBLIC_OUTPUT_DENYLIST.json"

FORBIDDEN_ROOT_FILES = {
    "AGENTS.md",
    "README.md",
    "repo-policy.json",
    "Makefile",
    "PRODUCT_BRIEF.md",
    "FOUNDER_CANON.md",
    "package.json",
    "package-lock.json",
    "pyproject.toml",
    "wrangler.toml",
    "railway.toml",
}
FORBIDDEN_PREFIXES = {
    ".agents/",
    ".claude/",
    ".cursor/",
    ".git/",
    ".github/",
    ".noetfield/",
    ".sina-agent/",
    ".vscode/",
    "L0-law/",
    "L1-operational/",
    "L2-knowledge/",
    "L3-external/",
    "Noetfield-All-Documents/",
    "_archive/",
    "api/",
    "apps/",
    "data/",
    "docs/",
    "governance-console/",
    "infra/",
    "infrastructure/",
    "node_modules/",
    "ops/",
    "os/",
    "packages/",
    "receipts/",
    "reports/",
    "scripts/",
    "tests/",
    "tmp/",
    "tools/pr-conflict-resolver-report/",
    "var/",
}
FORBIDDEN_SUFFIXES = (
    ".bak",
    ".gz",
    ".orig",
    ".py",
    ".pyc",
    ".rej",
    ".sh",
    ".sql",
    ".tar",
    ".tmp",
    ".toml",
    ".tsx",
    ".ts",
    ".zip",
    "~",
    ".swp",
    ".swo",
)


def expected_files() -> set[str]:
    data = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    return set(data["static_files"])


def denylist() -> dict[str, list[str]]:
    return json.loads(DENYLIST.read_text(encoding="utf-8"))


def actual_files(output: Path) -> set[str]:
    return {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }


def forbidden_reason(rel_path: str) -> str | None:
    if rel_path in FORBIDDEN_ROOT_FILES:
        return "internal root file"
    if any(rel_path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        return "internal/source prefix"
    lower = rel_path.lower()
    if ".bak" in Path(lower).name or lower.endswith(FORBIDDEN_SUFFIXES):
        return "backup/source/editor/archive/temporary file"
    return None



# Founder brand rule: Noetfield's PUBLIC artifact is English-only. An
# authenticated Founder Desk and an independently deployed Persian satellite
# are deliberately not part of this artifact check.
NON_ENGLISH_SCRIPT = re.compile(
    "[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF"
    "\u0900-\u097F\u0E00-\u0E7F\u3040-\u30FF\u3400-\u9FFF"
    "\uAC00-\uD7AF\uFB50-\uFDFF\uFE70-\uFEFF]"
)
LOCALE_QUERY_KEYS = frozenset({"lang", "language", "locale", "hl"})
NON_ENGLISH_LOCALE = re.compile(
    r"^(?:fa|farsi|persian|fr|ar|de|es|it|pt|ru|zh|ja|ko|hi|tr|ur|nl|"
    r"sv|no|da|fi|he|th|vi|pl|uk|id|ms)(?:[-_][a-z0-9]{2,8})?$",
    re.IGNORECASE,
)
# Explicitly named, separately deployed language satellites belong here once
# provisioned. Keep this empty until a real host is authorized and verified.
NON_ENGLISH_SATELLITE_HOSTS: frozenset[str] = frozenset()
PUBLIC_LOCALE_LITERAL = re.compile(
    r"(?:[?&](?:lang|language|locale|hl)=)(?:fa|fr|ar|de|es|it|pt|ru|zh|ja|"
    r"ko|hi|tr|ur|nl|sv|no|da|fi|he|th|vi|pl|uk)(?:[-_][a-z0-9]+)?(?=[&#'\"\\s]|$)",
    re.IGNORECASE,
)


class _PublicLanguageLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.reasons: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        tag = tag.lower()
        if tag == "html":
            lang = values.get("lang", "").strip().lower()
            if lang and lang != "en" and not lang.startswith("en-"):
                self.reasons.append(f"public document language is not English: {lang}")
            if values.get("dir", "").strip().lower() == "rtl":
                self.reasons.append("public document declares RTL locale")
        if "hreflang" in values:
            lang = values["hreflang"].lower().strip()
            if lang and lang != "en" and not lang.startswith("en-"):
                self.reasons.append(f"public alternate language link: {lang}")
        if tag not in {"a", "link", "area"}:
            return
        href = values.get("href", "")
        if not href:
            return
        parsed = urlsplit(href)
        host = (parsed.hostname or "").lower().rstrip(".")
        if host in NON_ENGLISH_SATELLITE_HOSTS:
            self.reasons.append("outbound link to a registered non-English satellite")
        for key, value in parse_qsl(parsed.query, keep_blank_values=True):
            if key.lower() in LOCALE_QUERY_KEYS and value and not (
                value.lower() == "en" or value.lower().startswith("en-")
            ):
                self.reasons.append("public link to a non-English language variant")
                break
        segments = [
            unquote(item).lower() for item in parsed.path.split("/") if item
        ]
        if segments and NON_ENGLISH_LOCALE.fullmatch(segments[0]):
            self.reasons.append("public link points to a translated locale path")


def language_boundary_findings(output: Path, actual: set[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for relative in sorted(actual):
        suffix = Path(relative).suffix.lower()
        if suffix not in {".html", ".htm", ".js"}:
            continue
        try:
            source = (output / relative).read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            findings.append({"path": relative, "reason": "public text artifact is unreadable"})
            continue
        if NON_ENGLISH_SCRIPT.search(source):
            findings.append({
                "path": relative,
                "reason": "non-English script found in corporate public interface source",
            })
        if PUBLIC_LOCALE_LITERAL.search(source):
            findings.append({
                "path": relative,
                "reason": "public language-switch URL literal is forbidden",
            })
        if suffix in {".html", ".htm"}:
            parser = _PublicLanguageLinks()
            try:
                parser.feed(source)
                parser.close()
            except ValueError:
                findings.append({"path": relative, "reason": "public HTML language check failed"})
                continue
            for reason in sorted(set(parser.reasons)):
                findings.append({"path": relative, "reason": reason})
    return findings


def scan(output: Path) -> list[dict[str, str]]:
    if not output.is_dir():
        return [{"path": "<artifact>", "reason": "artifact directory is absent"}]

    expected = expected_files()
    actual = actual_files(output)
    findings: list[dict[str, str]] = []
    for path in sorted(expected - actual):
        findings.append({"path": path, "reason": "allowlisted artifact path is missing"})
    for path in sorted(actual - expected):
        findings.append({"path": path, "reason": "unexpected path is not allowlisted"})

    denied = denylist()
    exact = {path.lstrip("/") for path in denied.get("exact_paths", [])}
    prefixes = tuple(path.lstrip("/") for path in denied.get("prefix_paths", []))
    for path in sorted(actual):
        reason = forbidden_reason(path)
        if path in exact:
            reason = "PUBLIC_OUTPUT_DENYLIST exact path"
        elif path.startswith(prefixes):
            reason = "PUBLIC_OUTPUT_DENYLIST prefix path"
        if reason:
            findings.append({"path": path, "reason": reason})
    findings.extend(language_boundary_findings(output, actual))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    output = Path(args.output)
    findings = scan(output)
    unexpected = [
        finding
        for finding in findings
        if finding["reason"].startswith("unexpected")
        or "internal" in finding["reason"]
        or "DENYLIST" in finding["reason"]
        or "backup" in finding["reason"]
    ]
    payload = {
        "ok": not findings,
        "output": str(output),
        "blocked_count": len(findings),
        "unexpected_count": len(unexpected),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif findings:
        for finding in findings[:100]:
            print(
                f"FAIL public-output-allowlist: {finding['path']} "
                f"({finding['reason']})"
            )
        if len(findings) > 100:
            print(f"FAIL public-output-allowlist: {len(findings) - 100} more findings")
    else:
        print(
            "OK   public-output-allowlist: exact artifact; "
            f"{len(actual_files(output))} static files; unexpected=0"
        )
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
