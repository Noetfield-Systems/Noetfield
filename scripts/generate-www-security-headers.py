#!/usr/bin/env python3
"""Write Cloudflare Pages _headers for public marketing HTML."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "www-pages-dist" / "_headers"

CSP = (
    "default-src 'self'; base-uri 'self'; frame-ancestors 'none'; "
    "form-action 'self' https:; img-src 'self' data: https:; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com data:; script-src 'self'; "
    "connect-src 'self' https://www.noetfield.com https://noetfield.com "
    "https://platform.noetfield.com https://api.noetfield.com https://scan.noetfield.com; "
    "upgrade-insecure-requests"
)

CONTENT = f"""/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Content-Security-Policy: {CSP}
"""


def main() -> int:
    if not OUT.parent.is_dir():
        print(f"skip {OUT.relative_to(ROOT)} — www-pages-dist is absent")
        return 0
    if OUT.is_file() and OUT.read_text(encoding="utf-8") == CONTENT:
        print("ok unchanged www-pages-dist/_headers")
        return 0
    OUT.write_text(CONTENT, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
