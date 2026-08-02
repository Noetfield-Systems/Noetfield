#!/usr/bin/env python3
"""Verify YC / LinkedIn social-preview completeness for canonical public links."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "yc-social-links-v1.json"
DEFAULT_ARTIFACT = ROOT / "www-pages-dist"
META_NAME_RE = re.compile(
    r'<meta\s+name="([^"]+)"\s+content="([^"]*)"',
    re.IGNORECASE,
)
META_PROP_RE = re.compile(
    r'<meta\s+property="([^"]+)"\s+content="([^"]*)"',
    re.IGNORECASE,
)


def load_config() -> dict:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if config.get("schema") != "yc-social-links-v1":
        raise ValueError("unsupported yc-social-links config schema")
    return config


def parse_html(text: str) -> tuple[dict[str, str], dict[str, str]]:
    names = {m.group(1).lower(): m.group(2) for m in META_NAME_RE.finditer(text)}
    props = {m.group(1).lower(): m.group(2) for m in META_PROP_RE.finditer(text)}
    return names, props


def artifact_path_for_url(url: str, artifact: Path) -> Path | None:
    parsed = urlparse(url)
    if parsed.netloc != "www.noetfield.com":
        return None
    path = parsed.path
    if path.endswith("/"):
        rel = f"{path.lstrip('/')}index.html" if path != "/" else "index.html"
    else:
        rel = path.lstrip("/")
    candidate = artifact / rel
    return candidate if candidate.is_file() else None


def fetch(url: str, user_agent: str | None = None) -> str:
    headers = {"User-Agent": user_agent} if user_agent else {}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def head_status(url: str, user_agent: str | None = None) -> int:
    headers = {"User-Agent": user_agent} if user_agent else {}
    request = urllib.request.Request(url, headers=headers, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


def verify_link(
    link: dict,
    html: str,
    *,
    user_agent: str | None,
    check_image_fetch: bool,
) -> list[str]:
    errors: list[str] = []
    names, props = parse_html(html)
    link_id = str(link["id"])
    expected_type = str(link["og_type"])

    required_props = {
        "og:title": props.get("og:title"),
        "og:description": props.get("og:description"),
        "og:url": props.get("og:url"),
        "og:type": props.get("og:type"),
        "og:image": props.get("og:image"),
        "og:image:secure_url": props.get("og:image:secure_url"),
        "og:image:width": props.get("og:image:width"),
        "og:image:height": props.get("og:image:height"),
        "og:image:alt": props.get("og:image:alt"),
    }
    required_names = {
        "description": names.get("description"),
        "twitter:card": names.get("twitter:card"),
        "twitter:title": names.get("twitter:title"),
        "twitter:description": names.get("twitter:description"),
        "twitter:image": names.get("twitter:image"),
        "twitter:image:alt": names.get("twitter:image:alt"),
    }
    for label, value in {**required_props, **required_names}.items():
        if not value:
            errors.append(f"{link_id}: missing {label}")

    if props.get("og:type") != expected_type:
        errors.append(f"{link_id}: og:type={props.get('og:type')!r} expected {expected_type!r}")

    if link.get("require_json_ld") and "application/ld+json" not in html:
        errors.append(f"{link_id}: missing JSON-LD block")

    if link.get("require_author"):
        for key in ("author", "article:author", "article:published_time", "article:modified_time"):
            if key == "author":
                if not names.get("author"):
                    errors.append(f"{link_id}: missing meta name=author")
            elif not props.get(key):
                errors.append(f"{link_id}: missing meta property={key}")

    image = props.get("og:image")
    if image:
        image_host = urlparse(image).netloc
        page_host = urlparse(str(link["url"])).netloc
        if link.get("image_must_be_same_host") and image_host != page_host:
            errors.append(f"{link_id}: og:image host {image_host} != page host {page_host}")
        filename = link.get("image_filename")
        if filename and filename not in image:
            errors.append(f"{link_id}: og:image does not reference {filename}")
        if check_image_fetch:
            status = head_status(image, user_agent)
            if status != 200:
                errors.append(f"{link_id}: og:image HTTP {status} for {image}")

    return errors


def verify(
    *,
    artifact: Path | None,
    live: bool,
    user_agent: str | None,
) -> tuple[list[dict], list[str]]:
    config = load_config()
    rows: list[dict] = []
    errors: list[str] = []

    for link in config["links"]:
        link_id = str(link["id"])
        url = str(link["url"])
        html = ""
        source = "missing"
        if not live and link.get("host") == "app":
            rows.append(
                {
                    "id": link_id,
                    "url": url,
                    "source": "skipped-app-host",
                    "og_type": None,
                    "og_image": None,
                    "author": None,
                    "json_ld": None,
                    "verdict": "SKIP",
                }
            )
            continue
        try:
            if live:
                html = fetch(url, user_agent)
                source = "live"
            elif artifact is not None:
                path = artifact_path_for_url(url, artifact)
                if path is None or not path.is_file():
                    errors.append(f"{link_id}: artifact HTML missing for {url}")
                    continue
                html = path.read_text(encoding="utf-8")
                source = str(path.relative_to(ROOT))
            else:
                errors.append(f"{link_id}: no artifact or live mode")
                continue
        except Exception as exc:  # noqa: BLE001 — verifier aggregates failures
            errors.append(f"{link_id}: fetch failed: {exc}")
            continue

        link_errors = verify_link(
            link,
            html,
            user_agent=user_agent if live else None,
            check_image_fetch=live,
        )
        errors.extend(link_errors)
        names, props = parse_html(html)
        rows.append(
            {
                "id": link_id,
                "url": url,
                "source": source,
                "og_type": props.get("og:type"),
                "og_image": props.get("og:image"),
                "author": names.get("author"),
                "json_ld": "application/ld+json" in html,
                "verdict": "PASS" if not link_errors else "FAIL",
            }
        )

    return rows, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.live and not args.artifact.is_dir():
        print(f"verify_yc_social_links_v1: artifact missing: {args.artifact}", file=sys.stderr)
        print("verify_yc_social_links_v1: use --live for production check", file=sys.stderr)
        return 1

    config = load_config()
    ua = str(config.get("linkedin_user_agent") or "")
    rows, errors = verify(
        artifact=None if args.live else args.artifact,
        live=args.live,
        user_agent=ua if args.live else None,
    )

    receipt = {
        "schema": "yc-social-links-verification-v1",
        "mode": "live" if args.live else "artifact",
        "verdict": "PASS" if not errors else "FAIL",
        "link_count": len(rows),
        "pass_count": sum(row["verdict"] == "PASS" for row in rows),
        "links": rows,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(receipt, indent=2))
    elif errors:
        for error in errors:
            print(f"FAIL yc-social-links: {error}", file=sys.stderr)
        print(
            f"yc-social-links verifier: FAIL ({len(errors)} findings, "
            f"{receipt['pass_count']}/{receipt['link_count']} links ok)",
            file=sys.stderr,
        )
    else:
        print(
            f"yc-social-links verifier: PASS mode={receipt['mode']} "
            f"links={receipt['link_count']}"
        )

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
