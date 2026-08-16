#!/usr/bin/env python3
"""Submit public Noetfield URLs to IndexNow (Bing + IndexNow partners)."""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST = "www.noetfield.com"
KEY_FILE = ROOT / "indexnow-key.txt"
SITEMAP = ROOT / "sitemap.xml"
# IndexNow accepts at most 10,000 URLs per request; keep a hard ceiling.
MAX_URLS = 1000


def load_urls() -> list[str]:
    urls: list[str] = []
    if SITEMAP.exists():
        text = SITEMAP.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"<loc>(https://www\.noetfield\.com[^<]+)</loc>", text):
            urls.append(match.group(1).strip())
    if not urls:
        urls = [
            f"https://{HOST}/",
            f"https://{HOST}/motors/",
            f"https://{HOST}/developers/",
            f"https://{HOST}/system/",
            f"https://{HOST}/tools/",
            f"https://{HOST}/about/",
        ]
    urls.append(f"https://{HOST}/llms.txt")
    urls.append(f"https://{HOST}/sitemap.xml")
    seen: set[str] = set()
    ordered: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            ordered.append(url)
    return ordered[:MAX_URLS]


def main() -> int:
    key = (os.environ.get("INDEXNOW_KEY") or "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        print("FAIL missing IndexNow key", file=sys.stderr)
        return 2
    url_list = load_urls()
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"https://{HOST}/{key}.txt",
        "urlList": url_list,
    }
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            code = resp.status
            body = resp.read()[:300]
    except urllib.error.HTTPError as err:
        code = err.code
        body = err.read()[:300]
        if code not in (200, 202):
            print(f"FAIL indexnow http={code} body={body!r}", file=sys.stderr)
            return 2
    except Exception as err:  # noqa: BLE001
        print(f"FAIL indexnow {err}", file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, "http": code, "urls": len(url_list), "host": HOST}))
    print("INDEXNOW_SUBMIT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
