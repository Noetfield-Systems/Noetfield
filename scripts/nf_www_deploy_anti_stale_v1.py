#!/usr/bin/env python3
"""Fail-closed www anti-stale / anti-leak gate before Cloudflare Pages promote.

Authority: R-014 · INCIDENT-2026-07-14-001 · universal change-preservation law.
Live www is a deploy constraint. Git HEAD is not automatically newer.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SSOT_PATH = ROOT / "data" / "nf-www-deploy-anti-stale-v1.json"
DEFAULT_LIVE = "https://www.noetfield.com"
USER_AGENT = "nf-www-deploy-anti-stale-v1/1.0"


def load_ssot(path: Path = SSOT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def fetch_url(url: str, timeout: float = 30.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return resp.read().decode("utf-8", errors="replace")


def marker_hits(html: str, markers: list[str]) -> dict[str, bool]:
    return {m: (m in html) for m in markers}


def evaluate_homepage(html: str, lock: dict[str, Any]) -> dict[str, Any]:
    required = list(lock.get("required_markers") or [])
    forbidden = list(lock.get("forbidden_markers") or [])
    req_hits = marker_hits(html, required)
    forb_hits = marker_hits(html, forbidden)
    missing_required = [m for m, ok in req_hits.items() if not ok]
    present_forbidden = [m for m, ok in forb_hits.items() if ok]
    ok = not missing_required and not present_forbidden
    return {
        "ok": ok,
        "missing_required": missing_required,
        "present_forbidden": present_forbidden,
        "required_hits": req_hits,
        "forbidden_hits": forb_hits,
    }


def compare_live_ahead(dist_eval: dict[str, Any], live_eval: dict[str, Any]) -> list[str]:
    """If live already holds the lock and dist regresses it, FAIL as LIVE_AHEAD."""
    reasons: list[str] = []
    if not live_eval.get("ok"):
        return reasons
    for m in dist_eval.get("missing_required") or []:
        if live_eval.get("required_hits", {}).get(m):
            reasons.append(f"LIVE_AHEAD: dist missing required marker present on live: {m!r}")
    for m in dist_eval.get("present_forbidden") or []:
        if not live_eval.get("forbidden_hits", {}).get(m):
            reasons.append(
                f"LIVE_AHEAD_LEAK: dist reintroduces forbidden marker absent on live: {m!r}"
            )
    return reasons


def run_gate(
    *,
    dist_dir: Path,
    live_base: str | None,
    ssot: dict[str, Any],
    homepage_html: str | None = None,
    live_html: str | None = None,
) -> dict[str, Any]:
    lock = ssot["homepage_lock"]
    homepage_rel = ssot.get("homepage_path") or "index.html"
    dist_index = dist_dir / homepage_rel

    result: dict[str, Any] = {
        "schema": "nf-www-deploy-anti-stale-result-v1",
        "ok": False,
        "fail_closed": bool(ssot.get("fail_closed", True)),
        "dist_dir": str(dist_dir),
        "homepage_rel": homepage_rel,
        "live_base": live_base,
        "errors": [],
        "reasons": [],
    }

    if homepage_html is None:
        if not dist_index.is_file():
            result["errors"].append(f"DIST_HOMEPAGE_MISSING: {dist_index}")
            result["reasons"].append("DIST_HOMEPAGE_MISSING")
            return result
        homepage_html = read_text(dist_index)

    dist_eval = evaluate_homepage(homepage_html, lock)
    result["dist"] = dist_eval

    if dist_eval["missing_required"]:
        result["reasons"].append("DIST_MISSING_REQUIRED")
        result["errors"].append(
            "dist homepage missing required markers: "
            + ", ".join(dist_eval["missing_required"])
        )
    if dist_eval["present_forbidden"]:
        result["reasons"].append("DIST_FORBIDDEN_LEAK")
        result["errors"].append(
            "dist homepage contains forbidden markers: "
            + ", ".join(dist_eval["present_forbidden"])
        )

    live_policy = ssot.get("live_ahead_policy") or {}
    if live_base and live_policy.get("enabled", True):
        if live_html is None:
            live_url = live_base.rstrip("/") + "/"
            try:
                live_html = fetch_url(live_url)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                result["errors"].append(f"LIVE_FETCH_FAILED: {live_url} ({exc})")
                result["reasons"].append("LIVE_FETCH_FAILED")
                return result
        live_eval = evaluate_homepage(live_html, lock)
        result["live"] = live_eval
        ahead = compare_live_ahead(dist_eval, live_eval)
        if ahead:
            result["reasons"].append("LIVE_AHEAD_OF_DIST")
            result["errors"].extend(ahead)

    result["ok"] = len(result["errors"]) == 0
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dist", required=True, help="Path to www-pages-dist (or fixture dir)")
    ap.add_argument(
        "--live",
        default=DEFAULT_LIVE,
        help=f"Live www base URL (default {DEFAULT_LIVE})",
    )
    ap.add_argument(
        "--offline",
        action="store_true",
        help="Skip live fetch (dist-only lock check; deploy path must NOT use this)",
    )
    ap.add_argument("--ssot", default=str(SSOT_PATH), help="SSOT JSON path")
    ap.add_argument("--json", action="store_true", help="Print full JSON result")
    args = ap.parse_args(argv)

    ssot = load_ssot(Path(args.ssot))
    live = None if args.offline else str(args.live).rstrip("/")
    result = run_gate(dist_dir=Path(args.dist), live_base=live, ssot=ssot)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        status = "PASS" if result["ok"] else "FAIL"
        print(f"nf_www_deploy_anti_stale_v1: {status}")
        for err in result.get("errors") or []:
            print(f"  - {err}")
        if result.get("reasons"):
            print("reasons: " + ", ".join(result["reasons"]))

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
