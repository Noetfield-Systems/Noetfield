#!/usr/bin/env python3
"""Sync canonical v2 header/footer onto technical subpages (motors)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from corp_www_shell_v1 import CORP_CSS_VER, corp_footer, corp_header  # noqa: E402

TARGETS = ("motors/index.html",)


def sync_file(rel: str) -> bool:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'<link rel="stylesheet" href="/assets/noetfield-corporate-v1\.css\?v=\d+" />',
        f'<link rel="stylesheet" href="/assets/noetfield-corporate-v1.css?v={CORP_CSS_VER}" />',
        text,
        count=1,
    )
    orig = text
    header_re = re.compile(r"<header class=\"nf-corp-header\">.*?</header>", re.S)
    matches = list(header_re.finditer(text))
    for match in reversed(matches[1:]):
        text = text[: match.start()] + text[match.end() :]
    text = header_re.sub(corp_header("system").strip(), text, count=1)
    text = re.sub(
        r"<footer class=\"nf-corp-footer\">.*</footer>\s*(?:</body>\s*)?</html>\s*$",
        corp_footer().strip(),
        text,
        count=1,
        flags=re.S,
    )
    if text != orig:
        path.write_text(text, encoding="utf-8")
        print(f"synced {rel}")
        return True
    return False


def main() -> int:
    for rel in TARGETS:
        if not (ROOT / rel).is_file():
            print(f"missing {rel}")
            return 1
        sync_file(rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
