#!/usr/bin/env python3
"""Noetfield site-audit crawler v2 — sitemap + BFS snapshots with mechanical-gate guards."""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "Noetfield-SiteAudit/2.0 (+governed-autorun)"
LINK_RE = re.compile(r'href=["\']([^"\'#]+)["\']', re.I)
NON_HTML_SUFFIXES = (
    ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico",
    ".json", ".xml", ".txt", ".woff", ".woff2", ".map", ".pdf", ".zip",
)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return None


def is_html_candidate(url: str, content_type: str = "") -> bool:
    if "*" in url:
        return False
    path = urllib.parse.urlparse(url).path.lower()
    if any(path.endswith(s) for s in NON_HTML_SUFFIXES):
        return False
    if content_type and "text/html" not in content_type.lower():
        return False
    return True


def fetch(url: str, follow: bool = False) -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    opener = urllib.request.build_opener(
        urllib.request.HTTPRedirectHandler if follow else NoRedirect()
    )
    try:
        resp = opener.open(req, timeout=25)
        body = resp.read()
        return resp.status, {k.lower(): v for k, v in resp.headers.items()}, body
    except urllib.error.HTTPError as exc:
        raw = exc.read() if exc.fp else b""
        return exc.code, {k.lower(): v for k, v in exc.headers.items()}, raw
    except Exception as exc:  # noqa: BLE001
        return 0, {"error": str(exc)}, b""


def norm(base: str, href: str) -> str:
    joined = urllib.parse.urljoin(base, href.strip())
    joined = urllib.parse.urldefrag(joined)[0]
    if joined.count("/") > 2 and not joined.endswith("/"):
        # keep trailing slash for directory-style www paths when base uses them
        parsed = urllib.parse.urlparse(joined)
        if not Path(parsed.path).suffix:
            joined = joined.rstrip("/") + "/"
    return joined


def slug_for(url: str, root: str) -> str:
    rel = url.replace(root.rstrip("/"), "").strip("/") or "home"
    return re.sub(r"[^a-z0-9]+", "_", rel.lower()).strip("_") or "home"


def load_route_seeds(repo_root: Path) -> list[str]:
    inv = repo_root / "governance" / "ROUTE_INVENTORY.json"
    if not inv.is_file():
        return []
    data = json.loads(inv.read_text(encoding="utf-8"))
    return [
        row["path"]
        for row in data.get("routes", [])
        if row.get("expected_status") == 200
    ]


def path_to_disk_file(repo_root: Path, www_path: str) -> Path | None:
    rel = www_path.strip("/")
    if not rel:
        candidate = repo_root / "index.html"
    else:
        candidate = repo_root / rel / "index.html"
        if not candidate.is_file():
            candidate = repo_root / f"{rel}.html"
    return candidate if candidate.is_file() else None


def crawl_disk(repo_root: Path, snap_dir: Path, max_pages: int = 120) -> dict:
    snap_dir.mkdir(parents=True, exist_ok=True)
    seeds = load_route_seeds(repo_root)
    index: list[dict] = []
    seen: set[str] = set()
    homepage_sha = ""

    for www_path in seeds:
        if len(index) >= max_pages:
            break
        disk_file = path_to_disk_file(repo_root, www_path)
        if disk_file is None or www_path in seen:
            continue
        seen.add(www_path)
        body = disk_file.read_bytes()
        html = body.decode("utf-8", errors="replace")
        sha = hashlib.sha256(body).hexdigest()
        if www_path in ("/", ""):
            homepage_sha = sha
        url = f"disk://{www_path}"
        links = sorted(
            {
                norm(url, h)
                for h in LINK_RE.findall(html)
                if not h.startswith(("mailto:", "tel:", "javascript:"))
            }
        )
        mailtos = sorted({h for h in LINK_RE.findall(html) if h.startswith("mailto:")})
        slug = slug_for(www_path, "")
        (snap_dir / f"{slug}.html").write_bytes(body)
        row = {
            "url": url,
            "www_path": www_path,
            "status": 200,
            "redirect": "",
            "sha256": sha,
            "bytes": len(body),
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "content_type": "text/html",
            "snapshot": f"{slug}.html",
            "source_file": str(disk_file.relative_to(repo_root)),
            "internal_links": [l for l in links if l.startswith(("/", "disk://"))],
            "external_links": [l for l in links if l.startswith("http")],
            "mailto_links": mailtos,
            "row_class": "HTML",
        }
        if homepage_sha and sha == homepage_sha and www_path not in ("/", ""):
            row["row_class"] = "SPA_FALLBACK"
        index.append(row)

    meta = {
        "root": "disk://" + str(repo_root),
        "mode": "disk",
        "pages": len(index),
        "crawled_at": index[0]["fetched_at"] if index else None,
        "homepage_sha256": homepage_sha,
        "index": index,
    }
    (snap_dir / "crawl_index.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def crawl_live(root: str, snap_dir: Path, max_pages: int = 120) -> dict:
    snap_dir.mkdir(parents=True, exist_ok=True)
    host = urllib.parse.urlparse(root).netloc
    seen: set[str] = set()
    queue: list[str] = [root.rstrip("/") + "/"]
    index: list[dict] = []
    homepage_sha = ""

    st, _, body = fetch(root.rstrip("/") + "/sitemap.xml", follow=True)
    if st == 200:
        for loc in re.findall(r"<loc>(.*?)</loc>", body.decode("utf-8", errors="replace")):
            if is_html_candidate(loc):
                queue.append(loc)

    while queue and len(index) < max_pages:
        url = queue.pop(0)
        if url in seen or urllib.parse.urlparse(url).netloc != host:
            continue
        if not is_html_candidate(url):
            continue
        seen.add(url)
        status, headers, body = fetch(url, follow=False)
        redirected_to = headers.get("location", "")
        if status in (301, 302, 307, 308) and redirected_to:
            status, headers, body = fetch(norm(url, redirected_to), follow=True)
        content_type = headers.get("content-type", "")
        if not is_html_candidate(url, content_type):
            continue
        html = body.decode("utf-8", errors="replace")
        sha = hashlib.sha256(body).hexdigest()
        if url.rstrip("/") in (root.rstrip("/"), root.rstrip("/") + "/") or not homepage_sha:
            homepage_sha = sha
        links = sorted(
            {
                norm(url, h)
                for h in LINK_RE.findall(html)
                if not h.startswith(("mailto:", "tel:", "javascript:"))
            }
        )
        mailtos = sorted({h for h in LINK_RE.findall(html) if h.startswith("mailto:")})
        slug = slug_for(url, root)
        (snap_dir / f"{slug}.html").write_text(html, encoding="utf-8")
        parsed_path = urllib.parse.urlparse(url).path or "/"
        row = {
            "url": url,
            "www_path": parsed_path,
            "status": status,
            "redirect": redirected_to,
            "sha256": sha,
            "bytes": len(body),
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "content_type": content_type,
            "snapshot": f"{slug}.html",
            "internal_links": [l for l in links if host in l or l.startswith("/")],
            "external_links": [l for l in links if host not in l and l.startswith("http")],
            "mailto_links": mailtos,
            "row_class": "HTML",
        }
        if homepage_sha and sha == homepage_sha and parsed_path not in ("/", ""):
            row["row_class"] = "SPA_FALLBACK"
        index.append(row)
        for link in row["internal_links"]:
            if link not in seen and is_html_candidate(link):
                queue.append(link)
        time.sleep(0.25)

    meta = {
        "root": root,
        "mode": "live",
        "pages": len(index),
        "crawled_at": index[0]["fetched_at"] if index else None,
        "homepage_sha256": homepage_sha,
        "index": index,
    }
    (snap_dir / "crawl_index.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta
