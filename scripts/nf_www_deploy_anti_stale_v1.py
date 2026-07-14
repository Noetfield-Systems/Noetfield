#!/usr/bin/env python3
"""Noetfield www anti-stale / protected-surface gate (universal change-preservation law).

Canonical promotion chain (NOT live-HTML SSOT):
  founder-approved source SHA
  → verified build
  → exact-SHA promotion
  → verified public fingerprint
  → immutable receipt

Fail closed. Insufficient proof: HTTP 200 alone, CI green alone, marketing text alone.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROTECTED_SSOT = ROOT / "config" / "noetfield-www-protected-surfaces.v1.json"
DEFAULT_LIVE = "https://www.noetfield.com"
USER_AGENT = "nf-www-deploy-anti-stale-v1/1.0"

# Terminal verdicts (law + this candidate package)
PASS_SCOPED = "PASS_SCOPED_CHANGE"
BLOCKED_BASELINE = "BLOCKED_BASELINE_CONFLICT"
LIVE_AHEAD = "LIVE_AHEAD_OF_GIT"
BLOCKED_SCOPE = "BLOCKED_SCOPE_BREACH"
BLOCKED_PROTECTED = "BLOCKED_PROTECTED_SURFACE_REGRESSION"
BLOCKED_NON_DESCENDANT = "BLOCKED_NON_DESCENDANT_CANDIDATE"
BLOCKED_STALE = "BLOCKED_STALE_RELEASE"
BLOCKED_UNAPPROVED = "BLOCKED_UNAPPROVED_PROMOTION"
CANDIDATE_FOUNDER = "CANDIDATE_PENDING_FOUNDER_PROMOTION"
CANDIDATE_UNIVERSAL = "CANDIDATE_PENDING_UNIVERSAL_POLICY_INTEGRATION"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_git(args: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


def fetch_url(url: str, timeout: float = 30.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return resp.read().decode("utf-8", errors="replace")


def marker_hits(text: str, markers: list[str]) -> dict[str, bool]:
    return {m: (m in text) for m in markers}


def evaluate_surface(html: str, surface: dict[str, Any]) -> dict[str, Any]:
    required = list(surface.get("required_markers") or [])
    forbidden = list(surface.get("forbidden_markers") or [])
    routes = list(surface.get("required_routes") or [])
    req_hits = marker_hits(html, required)
    forb_hits = marker_hits(html, forbidden)
    route_hits = marker_hits(html, routes)
    missing_required = [m for m, ok in req_hits.items() if not ok]
    present_forbidden = [m for m, ok in forb_hits.items() if ok]
    missing_routes = [m for m, ok in route_hits.items() if not ok]
    ok = not missing_required and not present_forbidden and not missing_routes
    return {
        "ok": ok,
        "missing_required": missing_required,
        "present_forbidden": present_forbidden,
        "missing_routes": missing_routes,
        "required_hits": req_hits,
        "forbidden_hits": forb_hits,
        "route_hits": route_hits,
    }


def compare_live_ahead_regression(dist_eval: dict[str, Any], live_eval: dict[str, Any]) -> list[str]:
    """Live is a constraint signal: fail if candidate regresses a lock live already satisfies."""
    reasons: list[str] = []
    if not live_eval.get("ok"):
        return reasons
    for m in dist_eval.get("missing_required") or []:
        if live_eval.get("required_hits", {}).get(m):
            reasons.append(f"LIVE_AHEAD: candidate missing required marker present on live: {m!r}")
    for m in dist_eval.get("missing_routes") or []:
        if live_eval.get("route_hits", {}).get(m):
            reasons.append(f"LIVE_AHEAD: candidate missing required route present on live: {m!r}")
    for m in dist_eval.get("present_forbidden") or []:
        if not live_eval.get("forbidden_hits", {}).get(m):
            reasons.append(
                f"LIVE_AHEAD_LEAK: candidate reintroduces forbidden marker absent on live: {m!r}"
            )
    return reasons


def git_head(cwd: Path = ROOT) -> str:
    code, out = run_git(["rev-parse", "HEAD"], cwd=cwd)
    if code != 0 or not out:
        raise RuntimeError(f"cannot resolve HEAD: {out}")
    return out.splitlines()[0].strip()


def git_is_descendant(candidate: str, baseline: str, cwd: Path = ROOT) -> bool:
    code, _ = run_git(["merge-base", "--is-ancestor", baseline, candidate], cwd=cwd)
    return code == 0


def git_changed_files(baseline: str, candidate: str = "HEAD", cwd: Path = ROOT) -> list[str]:
    code, out = run_git(["diff", "--name-only", f"{baseline}...{candidate}"], cwd=cwd)
    if code != 0:
        return []
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def git_worktree_dirty(cwd: Path = ROOT) -> bool:
    code, out = run_git(["status", "--porcelain"], cwd=cwd)
    return code != 0 or bool(out.strip())


def path_allowed(path: str, allowed: list[str]) -> bool:
    norm = path.replace("\\", "/").lstrip("./")
    for rule in allowed:
        rule = rule.replace("\\", "/").lstrip("./")
        if rule.endswith("/"):
            if norm == rule.rstrip("/") or norm.startswith(rule):
                return True
        elif norm == rule:
            return True
    return False


def check_allowlist(changed: list[str], allowed: list[str]) -> list[str]:
    return [p for p in changed if not path_allowed(p, allowed)]


def fingerprint_surface(eval_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": bool(eval_result.get("ok")),
        "missing_required": list(eval_result.get("missing_required") or []),
        "present_forbidden": list(eval_result.get("present_forbidden") or []),
        "missing_routes": list(eval_result.get("missing_routes") or []),
    }


def run_gate(
    *,
    mode: str,
    dist_dir: Path | None,
    live_base: str | None,
    protected: dict[str, Any],
    manifest: dict[str, Any] | None,
    authorized_sha: str | None,
    baseline_sha: str | None,
    candidate_sha: str | None,
    allow_dirty: bool,
    homepage_html: str | None = None,
    live_html: str | None = None,
    changed_files: list[str] | None = None,
    cwd: Path = ROOT,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": "nf-www-deploy-anti-stale-result-v1",
        "ok": False,
        "mode": mode,
        "verdict": BLOCKED_UNAPPROVED,
        "errors": [],
        "reasons": [],
        "promotion_chain": list(protected.get("promotion_chain") or []),
        "insufficient_proof_rejected": list(protected.get("insufficient_proof") or []),
        "live_is_not_ssot": True,
    }

    constraints = protected.get("deploy_constraints") or {}
    surfaces = protected.get("surfaces") or {}
    homepage = surfaces.get("homepage") or {}

    # --- identity / ancestry / dirty ---
    try:
        head = candidate_sha or git_head(cwd)
    except RuntimeError as exc:
        result["errors"].append(str(exc))
        result["reasons"].append("PRODUCTION_IDENTITY_UNRESOLVED")
        result["verdict"] = BLOCKED_UNAPPROVED
        return result
    result["candidate_sha"] = head

    if baseline_sha is None and manifest:
        baseline_sha = str(manifest.get("verified_baseline_sha") or "") or None
    if baseline_sha:
        result["baseline_sha"] = baseline_sha
        if constraints.get("reject_non_descendant_of_baseline_when_baseline_set", True):
            if not git_is_descendant(head, baseline_sha, cwd=cwd):
                result["errors"].append(
                    f"candidate {head[:12]} is not a descendant of baseline {baseline_sha[:12]}"
                )
                result["reasons"].append(BLOCKED_NON_DESCENDANT)
                result["verdict"] = BLOCKED_NON_DESCENDANT
                return result

    dirty = git_worktree_dirty(cwd)
    result["worktree_dirty"] = dirty
    if mode == "promote" and constraints.get("require_clean_worktree", True) and dirty and not allow_dirty:
        result["errors"].append(
            "deploy originates from dirty/unverified local worktree; "
            "refuse stash/dirty/implicit HEAD promote"
        )
        result["reasons"].append("DIRTY_OR_IMPLICIT_HEAD")
        result["verdict"] = BLOCKED_UNAPPROVED
        return result

    if mode == "promote" and constraints.get("require_authorized_promote_sha", True):
        auth = (authorized_sha or os.environ.get("NF_AUTHORIZED_PROMOTE_SHA") or "").strip()
        result["authorized_sha"] = auth or None
        if not auth:
            result["errors"].append(
                "NF_AUTHORIZED_PROMOTE_SHA / --authorized-sha required for promote "
                "(exact-SHA promotion; implicit HEAD forbidden)"
            )
            result["reasons"].append(BLOCKED_UNAPPROVED)
            result["verdict"] = BLOCKED_UNAPPROVED
            return result
        if auth != head:
            result["errors"].append(
                f"promoted SHA mismatch: authorized={auth} head={head}"
            )
            result["reasons"].append("AUTHORIZED_SHA_MISMATCH")
            result["verdict"] = BLOCKED_UNAPPROVED
            return result

    # --- allowlist (manifest scope) ---
    if manifest and mode in {"preflight", "promote", "scope"}:
        allowed = list(manifest.get("allowed_paths") or [])
        baseline = str(manifest.get("verified_baseline_sha") or baseline_sha or "")
        files = changed_files
        if files is None and baseline:
            files = git_changed_files(baseline, head, cwd=cwd)
        files = files or []
        result["changed_files"] = files
        breaches = check_allowlist(files, allowed)
        if breaches:
            result["errors"].append("changed files exceed task allowlist: " + ", ".join(breaches))
            result["reasons"].append(BLOCKED_SCOPE)
            result["verdict"] = BLOCKED_SCOPE
            return result

    # --- candidate dist / protected surface lock (founder-approved markers) ---
    if mode in {"dist", "promote", "fingerprint"}:
        if dist_dir is None:
            result["errors"].append("dist dir required for protected-surface check")
            result["reasons"].append(BLOCKED_PROTECTED)
            result["verdict"] = BLOCKED_PROTECTED
            return result
        rel = homepage.get("path") or "index.html"
        dist_index = dist_dir / rel
        if homepage_html is None:
            if not dist_index.is_file():
                result["errors"].append(f"DIST_HOMEPAGE_MISSING: {dist_index}")
                result["reasons"].append(BLOCKED_PROTECTED)
                result["verdict"] = BLOCKED_PROTECTED
                return result
            homepage_html = dist_index.read_text(encoding="utf-8", errors="replace")
        dist_eval = evaluate_surface(homepage_html, homepage)
        result["candidate_fingerprint"] = fingerprint_surface(dist_eval)
        result["dist"] = dist_eval
        if not dist_eval["ok"]:
            if dist_eval["present_forbidden"]:
                result["errors"].append(
                    "forbidden markers present: " + ", ".join(dist_eval["present_forbidden"])
                )
            if dist_eval["missing_required"]:
                result["errors"].append(
                    "required markers missing: " + ", ".join(dist_eval["missing_required"])
                )
            if dist_eval["missing_routes"]:
                result["errors"].append(
                    "required routes missing: " + ", ".join(dist_eval["missing_routes"])
                )
            result["reasons"].append(BLOCKED_PROTECTED)
            result["verdict"] = BLOCKED_PROTECTED
            # continue to also collect live-ahead reasons

        # production identity + live-ahead constraint (not SSOT)
        if live_base:
            live_url = live_base.rstrip("/") + "/"
            try:
                if live_html is None:
                    live_html = fetch_url(live_url)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                result["errors"].append(f"PRODUCTION_IDENTITY_UNESTABLISHED: {live_url} ({exc})")
                result["reasons"].append("PRODUCTION_IDENTITY_UNESTABLISHED")
                result["verdict"] = BLOCKED_UNAPPROVED
                return result
            if not live_html or len(live_html) < 64:
                result["errors"].append("PRODUCTION_IDENTITY_UNESTABLISHED: empty/short live body")
                result["reasons"].append("PRODUCTION_IDENTITY_UNESTABLISHED")
                result["verdict"] = BLOCKED_UNAPPROVED
                return result
            # Reject "HTTP 200 alone" — require lock evaluation, not status code theater
            live_eval = evaluate_surface(live_html, homepage)
            result["live"] = live_eval
            result["live_fingerprint"] = fingerprint_surface(live_eval)
            ahead = compare_live_ahead_regression(dist_eval, live_eval)
            if ahead:
                result["errors"].extend(ahead)
                result["reasons"].append(LIVE_AHEAD)
                result["verdict"] = LIVE_AHEAD
                return result
            if not dist_eval["ok"]:
                return result

    if result["errors"]:
        return result

    result["ok"] = True
    if mode == "promote":
        result["verdict"] = PASS_SCOPED
    else:
        result["verdict"] = PASS_SCOPED
    return result


def self_test() -> int:
    protected = {
        "promotion_chain": ["founder-approved source SHA"],
        "insufficient_proof": ["HTTP 200 alone"],
        "deploy_constraints": {
            "require_authorized_promote_sha": False,
            "require_clean_worktree": False,
            "reject_non_descendant_of_baseline_when_baseline_set": False,
        },
        "surfaces": {
            "homepage": {
                "path": "index.html",
                "required_markers": ["nf-gate", "Enterprise", "Motor", "/enterprise/", "/motors/", "/proof/"],
                "forbidden_markers": ["/investors/", "/invest/", "Investor", "Invest in Noetfield"],
                "required_routes": ["/enterprise/", "/motors/", "/proof/"],
            }
        },
    }
    good = (
        '<!doctype html><html><body class="nf-gate">'
        '<a href="/enterprise/">Enterprise</a>'
        '<a href="/motors/">Motor</a>'
        '<a href="/proof/">Proof</a></body></html>'
    )
    leak = good + '<a href="/investors/">Investor</a><span>Invest in Noetfield</span>'
    stale = "<html><body>About only</body></html>"

    failures = 0
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        (p / "index.html").write_text(good, encoding="utf-8")
        r = run_gate(
            mode="dist",
            dist_dir=p,
            live_base=None,
            protected=protected,
            manifest=None,
            authorized_sha=None,
            baseline_sha=None,
            candidate_sha="deadbeef",
            allow_dirty=True,
            homepage_html=None,
            live_html=None,
        )
        if not r["ok"]:
            print("FAIL self-test good offline", r)
            failures += 1

        (p / "index.html").write_text(leak, encoding="utf-8")
        r = run_gate(
            mode="dist",
            dist_dir=p,
            live_base="https://www.noetfield.com",
            protected=protected,
            manifest=None,
            authorized_sha=None,
            baseline_sha=None,
            candidate_sha="deadbeef",
            allow_dirty=True,
            live_html=good,
        )
        if r["ok"] or LIVE_AHEAD not in r["reasons"] and BLOCKED_PROTECTED not in r["reasons"]:
            print("FAIL self-test leak", r)
            failures += 1

        (p / "index.html").write_text(stale, encoding="utf-8")
        r = run_gate(
            mode="dist",
            dist_dir=p,
            live_base="https://www.noetfield.com",
            protected=protected,
            manifest=None,
            authorized_sha=None,
            baseline_sha=None,
            candidate_sha="deadbeef",
            allow_dirty=True,
            live_html=good,
        )
        if r["ok"] or LIVE_AHEAD not in r["reasons"]:
            print("FAIL self-test live-ahead", r)
            failures += 1

    # allowlist breach
    manifest = {
        "verified_baseline_sha": "0" * 40,
        "allowed_paths": ["config/"],
    }
    r = run_gate(
        mode="scope",
        dist_dir=None,
        live_base=None,
        protected=protected,
        manifest=manifest,
        authorized_sha=None,
        baseline_sha=None,
        candidate_sha="1" * 40,
        allow_dirty=True,
        changed_files=["index.html", "config/foo.json"],
    )
    if r["ok"] or BLOCKED_SCOPE not in r["reasons"]:
        print("FAIL self-test scope", r)
        failures += 1

    # unauthorized promote
    protected2 = json.loads(json.dumps(protected))
    protected2["deploy_constraints"]["require_authorized_promote_sha"] = True
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        (p / "index.html").write_text(good, encoding="utf-8")
        r = run_gate(
            mode="promote",
            dist_dir=p,
            live_base=None,
            protected=protected2,
            manifest=None,
            authorized_sha="",
            baseline_sha=None,
            candidate_sha="abc",
            allow_dirty=True,
        )
        if r["ok"] or BLOCKED_UNAPPROVED not in r["reasons"]:
            print("FAIL self-test unauthorized", r)
            failures += 1

    if failures:
        print(f"nf_www_deploy_anti_stale_v1 self-test: FAIL ({failures})")
        return 1
    print("nf_www_deploy_anti_stale_v1 self-test: PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--mode",
        choices=["preflight", "scope", "dist", "promote", "fingerprint"],
        default="dist",
        help="Gate mode (promote is fail-closed for production)",
    )
    ap.add_argument("--dist", default=None, help="www-pages-dist directory")
    ap.add_argument("--live", default=DEFAULT_LIVE, help="Canonical www base URL")
    ap.add_argument("--offline", action="store_true", help="Skip live fetch (CI dist-only)")
    ap.add_argument("--ssot", default=str(PROTECTED_SSOT), help="Protected surfaces JSON")
    ap.add_argument("--manifest", default=None, help="Optional change-manifest JSON")
    ap.add_argument("--authorized-sha", default=None, help="Exact SHA authorized to promote")
    ap.add_argument("--baseline-sha", default=None, help="Verified baseline SHA")
    ap.add_argument("--candidate-sha", default=None, help="Override candidate SHA (tests)")
    ap.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Dangerous: allow dirty worktree (default refuse on promote)",
    )
    ap.add_argument("--self-test", action="store_true", help="Run embedded unit checks")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    protected = load_json(Path(args.ssot))
    manifest = load_json(Path(args.manifest)) if args.manifest else None
    live = None if args.offline else str(args.live).rstrip("/")
    dist = Path(args.dist) if args.dist else None

    result = run_gate(
        mode=args.mode,
        dist_dir=dist,
        live_base=live,
        protected=protected,
        manifest=manifest,
        authorized_sha=args.authorized_sha,
        baseline_sha=args.baseline_sha,
        candidate_sha=args.candidate_sha,
        allow_dirty=bool(args.allow_dirty),
    )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        status = "PASS" if result["ok"] else "FAIL"
        print(f"nf_www_deploy_anti_stale_v1: {status} verdict={result.get('verdict')}")
        for err in result.get("errors") or []:
            print(f"  - {err}")
        if result.get("reasons"):
            print("reasons: " + ", ".join(result["reasons"]))

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
