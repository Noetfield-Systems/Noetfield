#!/usr/bin/env python3
"""Fail-closed pre-deploy guard for Noetfield's locked public surfaces.

The candidate is authoritative only when it is the exact authorized Git SHA and
its built public artifact satisfies the versioned protected-surface contract.
Production is fetched as a regression constraint; live HTML is never treated as
the source of truth.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "config" / "noetfield-www-protected-surfaces.v2.json"
DEFAULT_LIVE = "https://www.noetfield.com"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
USER_AGENT = "Mozilla/5.0 (compatible; NoetfieldReleaseGuard/2.0; +https://www.noetfield.com)"


class SurfaceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for name, value in attrs:
            if name.lower() == "href" and value:
                self.links.append(value.strip())

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.text.append(data)


def normalized_text(value: str) -> str:
    return " ".join(unescape(value).split())


def normalized_link(value: str) -> str:
    parsed = urllib.parse.urlsplit(value.strip())
    if parsed.scheme or parsed.netloc:
        path = parsed.path or "/"
    else:
        path = parsed.path or value.strip()
    query = f"?{parsed.query}" if parsed.query else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""
    return f"{path}{query}{fragment}"


def link_has_prefix(link: str, prefix: str) -> bool:
    path = urllib.parse.urlsplit(link).path
    normalized_prefix = prefix.rstrip("/")
    return path == normalized_prefix or path.startswith(f"{normalized_prefix}/")


def evaluate_html(html: str, contract: dict[str, Any]) -> dict[str, Any]:
    parser = SurfaceParser()
    parser.feed(html)
    text = normalized_text(" ".join(parser.text))
    links = sorted({normalized_link(link) for link in parser.links})

    required_text = [normalized_text(str(item)) for item in contract.get("required_text", [])]
    forbidden_text = [normalized_text(str(item)) for item in contract.get("forbidden_text", [])]
    required_links = [normalized_link(str(item)) for item in contract.get("required_links", [])]
    forbidden_prefixes = [
        normalized_link(str(item)) for item in contract.get("forbidden_link_prefixes", [])
    ]

    missing_text = [item for item in required_text if item not in text]
    present_forbidden_text = [item for item in forbidden_text if item in text]
    missing_links = [item for item in required_links if item not in links]
    present_forbidden_links = [
        link
        for link in links
        if any(link_has_prefix(link, prefix) for prefix in forbidden_prefixes)
    ]

    return {
        "ok": not (
            missing_text or present_forbidden_text or missing_links or present_forbidden_links
        ),
        "missing_required_text": missing_text,
        "present_forbidden_text": present_forbidden_text,
        "missing_required_links": missing_links,
        "present_forbidden_links": present_forbidden_links,
    }


def fetch_html(url: str, timeout: float = 25.0) -> str:
    request = urllib.request.Request(
        url,
        headers={"Accept": "text/html", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        return response.read().decode("utf-8", errors="replace")


def git_head(repo: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def load_contract(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema") != "noetfield-www-protected-surfaces-v2":
        raise ValueError(f"unexpected protected-surface schema in {path}")
    surfaces = document.get("surfaces")
    if not isinstance(surfaces, dict) or not surfaces:
        raise ValueError("protected-surface contract has no surfaces")
    return document


def _live_regressions(
    candidate: dict[str, Any],
    live: dict[str, Any],
) -> list[str]:
    regressions: list[str] = []
    for key in ("missing_required_text", "missing_required_links"):
        for item in candidate[key]:
            if item not in live[key]:
                regressions.append(f"candidate lost live protection: {item}")
    for key in ("present_forbidden_text", "present_forbidden_links"):
        for item in candidate[key]:
            if item not in live[key]:
                regressions.append(f"candidate introduces protected-surface leak: {item}")
    return regressions


def run_gate(
    *,
    dist: Path,
    contract: dict[str, Any],
    expected_sha: str,
    authorized_sha: str,
    live_base: str | None,
    repo: Path = ROOT,
    actual_sha: str | None = None,
    fetcher: Callable[[str], str] = fetch_html,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": "noetfield-www-anti-stale-receipt-v2",
        "generated_at": datetime.now(UTC).isoformat(),
        "ok": False,
        "verdict": "BLOCKED_UNAPPROVED_PROMOTION",
        "candidate_sha": expected_sha,
        "authorized_sha": authorized_sha,
        "live_is_constraint_not_ssot": True,
        "surfaces": {},
        "errors": [],
    }

    actual = actual_sha or git_head(repo)
    result["actual_sha"] = actual
    if not FULL_SHA.fullmatch(expected_sha):
        result["errors"].append("expected SHA must be a full lowercase Git SHA")
        return result
    if not FULL_SHA.fullmatch(authorized_sha):
        result["errors"].append("authorized SHA must be a full lowercase Git SHA")
        return result
    if actual != expected_sha or authorized_sha != expected_sha:
        result["errors"].append(
            f"exact-SHA mismatch: actual={actual} expected={expected_sha} "
            f"authorized={authorized_sha}"
        )
        return result

    live_base = live_base.rstrip("/") if live_base else None
    has_contract_failure = False
    has_live_failure = False
    for surface_id, surface_contract in contract["surfaces"].items():
        rel = str(surface_contract["dist_path"])
        candidate_path = dist / rel
        surface_result: dict[str, Any] = {"dist_path": rel}
        if not candidate_path.is_file():
            surface_result["candidate"] = {"ok": False, "missing_file": rel}
            result["surfaces"][surface_id] = surface_result
            has_contract_failure = True
            continue

        candidate_html = candidate_path.read_text(encoding="utf-8", errors="replace")
        candidate_eval = evaluate_html(candidate_html, surface_contract)
        surface_result["candidate"] = candidate_eval
        if not candidate_eval["ok"]:
            has_contract_failure = True

        if live_base:
            route = str(surface_contract.get("route") or "/")
            separator = "&" if "?" in route else "?"
            live_url = f"{live_base}{route}{separator}nf_release_guard={expected_sha[:12]}"
            surface_result["live_url"] = live_url
            try:
                live_html = fetcher(live_url)
                live_eval = evaluate_html(live_html, surface_contract)
                surface_result["live"] = live_eval
                regressions = _live_regressions(candidate_eval, live_eval)
                surface_result["live_regressions"] = regressions
                if regressions:
                    has_contract_failure = True
            except (OSError, RuntimeError, TimeoutError, urllib.error.URLError) as exc:
                surface_result["live_error"] = str(exc)
                has_live_failure = True

        result["surfaces"][surface_id] = surface_result

    if has_live_failure:
        result["verdict"] = "BLOCKED_PRODUCTION_IDENTITY_UNAVAILABLE"
        result["errors"].append("one or more protected live surfaces could not be fetched")
        return result
    if has_contract_failure:
        result["verdict"] = "BLOCKED_PROTECTED_SURFACE_REGRESSION"
        result["errors"].append("candidate violates the protected-surface contract")
        return result

    result["ok"] = True
    result["verdict"] = "PASS_SCOPED_CHANGE"
    return result


def write_receipt(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--live", default=DEFAULT_LIVE)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--authorized-sha", required=True)
    parser.add_argument("--receipt", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        contract = load_contract(Path(args.contract))
        result = run_gate(
            dist=Path(args.dist),
            contract=contract,
            expected_sha=args.expected_sha,
            authorized_sha=args.authorized_sha,
            live_base=None if args.offline else args.live,
        )
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        result = {
            "schema": "noetfield-www-anti-stale-receipt-v2",
            "generated_at": datetime.now(UTC).isoformat(),
            "ok": False,
            "verdict": "BLOCKED_PROTECTED_SURFACE_REGRESSION",
            "errors": [str(exc)],
        }

    if args.receipt:
        write_receipt(Path(args.receipt), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "nf_www_deploy_anti_stale_v2: "
            f"{'PASS' if result['ok'] else 'FAIL'} verdict={result['verdict']}"
        )
        for error in result.get("errors", []):
            print(f"  - {error}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
