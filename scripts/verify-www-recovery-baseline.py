#!/usr/bin/env python3
"""Verify that the recoverable Pages artifact is complete and query-stable."""

from __future__ import annotations

import hashlib
import http.server
import os
import re
import threading
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "www-pages-dist"
ROUTES = {
    "/": "index.html",
    "/about/": "about/index.html",
    "/investors/": "investors/index.html",
    "/proof/": "proof/index.html",
    "/enterprise/": "enterprise/index.html",
    "/motors/": "motors/index.html",
    "/invest/": "invest/index.html",
    "/investor-workflows/": "investor-workflows/index.html",
    "/enterprise/agent-transformation/": "enterprise/agent-transformation/index.html",
    "/enterprise/application-factory/": "enterprise/application-factory/index.html",
    "/enterprise/copilot-governance/": "enterprise/copilot-governance/index.html",
    "/frontier-systems/": "frontier-systems/index.html",
    "/frontier-systems/memo/": "frontier-systems/memo/index.html",
}
FAVICON = "/noetfield-favicon-512.png"
DYNAMIC_PREFIXES = (
    "/api/",
    "/workspace/",
    "/cdn-cgi/",
)
RECOVERED_PUBLIC_FILES = {
    "about/index.html",
    "enterprise/agent-transformation/index.html",
    "enterprise/application-factory/index.html",
    "enterprise/copilot-governance/index.html",
    "frontier-systems/index.html",
    "frontier-systems/memo/index.html",
    "invest/index.html",
    "investor-workflows/index.html",
    "motors/index.html",
}
NON_PUBLIC_LINK_PREFIXES = (
    "/.agents/",
    "/.claude/",
    "/.cursor/",
    "/docs/",
    "/packages/",
    "/reports/",
    "/scripts/",
    "/tests/",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.references: list[str] = []
        self.navigation_references: list[str] = []
        self._in_title = False
        self._h1_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self._h1_depth += 1
        if tag in {"a", "link"} and values.get("href"):
            self.references.append(str(values["href"]))
            if tag == "a":
                self.navigation_references.append(str(values["href"]))
        elif tag in {"script", "img", "source"} and values.get("src"):
            self.references.append(str(values["src"]))
        elif tag == "form" and values.get("action"):
            self.references.append(str(values["action"]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "h1" and self._h1_depth:
            self._h1_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._h1_depth:
            self.h1_parts.append(data)

    @staticmethod
    def normalized(parts: list[str]) -> str:
        return re.sub(r"\s+", " ", "".join(parts)).strip()

    @property
    def title(self) -> str:
        return self.normalized(self.title_parts)

    @property
    def h1(self) -> str:
        return self.normalized(self.h1_parts)


def local_target(reference: str) -> Path | None:
    parsed = urllib.parse.urlsplit(reference)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return None
    path = urllib.parse.unquote(parsed.path)
    if path.startswith(DYNAMIC_PREFIXES):
        return None
    if path == "/":
        return DIST / "index.html"
    relative = path.lstrip("/")
    if path.endswith("/"):
        return DIST / relative / "index.html"
    direct = DIST / relative
    if direct.exists():
        return direct
    return DIST / relative / "index.html"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


def request(base: str, path: str, host: str) -> tuple[int, bytes]:
    req = urllib.request.Request(base + path, headers={"Host": host})
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.status, response.read()


def main() -> int:
    failures: list[str] = []
    rows: list[tuple[str, str, str, str]] = []

    if not DIST.is_dir():
        raise SystemExit("missing www-pages-dist; run scripts/build-www-pages-dist.sh")

    for route, relative in ROUTES.items():
        path = DIST / relative
        if not path.is_file():
            failures.append(f"missing protected artifact: {relative}")
            continue
        data = path.read_bytes()
        parser = PageParser()
        parser.feed(data.decode("utf-8"))
        if not parser.title:
            failures.append(f"missing title: {relative}")
        if not parser.h1:
            failures.append(f"missing h1: {relative}")
        rows.append((route, sha256(data), parser.title, parser.h1))

    html_count = 0
    for path in sorted(DIST.rglob("*.html")):
        relative = path.relative_to(DIST).as_posix()
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
        html_count += 1
        for reference in parser.references:
            parsed = urllib.parse.urlsplit(reference)
            local_path = urllib.parse.unquote(parsed.path)
            if local_path.startswith(NON_PUBLIC_LINK_PREFIXES):
                failures.append(f"non-public reference from {relative}: {reference}")
            target = local_target(reference)
            if target is not None and not target.is_file():
                failures.append(f"broken reference from {relative}: {reference}")
        if relative in RECOVERED_PUBLIC_FILES:
            for reference in parser.navigation_references:
                parsed = urllib.parse.urlsplit(reference)
                if parsed.path == "/workspace" or parsed.path.startswith("/workspace/"):
                    failures.append(
                        f"unapproved workspace navigation from {relative}: {reference}"
                    )

    favicon = DIST / FAVICON.lstrip("/")
    if not favicon.is_file() or favicon.stat().st_size == 0:
        failures.append("missing or empty favicon")

    previous = Path.cwd()
    os.chdir(DIST)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        for route, _relative in ROUTES.items():
            bodies: list[bytes] = []
            for host in ("noetfield.com", "www.noetfield.com"):
                for suffix in ("", "?nf_rel_002=1"):
                    try:
                        status, body = request(base, route + suffix, host)
                    except Exception as exc:  # pragma: no cover - failure reporting
                        failures.append(f"request failed {host}{route}{suffix}: {exc}")
                        continue
                    if status != 200:
                        failures.append(f"status {status} for {host}{route}{suffix}")
                    bodies.append(body)
            if bodies and any(body != bodies[0] for body in bodies[1:]):
                failures.append(f"host/query body mismatch: {route}")

        for host in ("noetfield.com", "www.noetfield.com"):
            for suffix in ("", "?nf_rel_002=1"):
                try:
                    status, body = request(base, FAVICON + suffix, host)
                except Exception as exc:  # pragma: no cover - failure reporting
                    failures.append(f"favicon request failed for {host}{suffix}: {exc}")
                    continue
                if status != 200 or not body:
                    failures.append(f"favicon invalid for {host}{suffix}: status={status}")
    finally:
        server.shutdown()
        server.server_close()
        os.chdir(previous)

    print("route\tsha256\ttitle\th1")
    for row in rows:
        print("\t".join(row))
    if favicon.is_file():
        print(f"{FAVICON}\t{sha256(favicon.read_bytes())}\tbinary\tbinary")
    print(f"artifact_html_checked\t{html_count}")

    if failures:
        for failure in sorted(set(failures)):
            print(f"FAIL {failure}")
        return 1
    print("verify-www-recovery-baseline: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
