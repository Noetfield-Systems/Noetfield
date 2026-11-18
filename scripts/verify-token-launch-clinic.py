#!/usr/bin/env python3
"""Noetfield Token Launch Clinic: public customer journey without duplicate intake/CRM."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / "token-launch/index.html").read_text(encoding="utf-8")

class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.forms = []
        self.links = []
        self.buttons = []
        self.details = 0
        self.scripts = []
        self.inline = False
        self.active = ""
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "form":
            self.forms.append(attrs)
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "button" and "data-clinic-track" in attrs:
            self.buttons.append(attrs)
        if tag == "details":
            self.details += 1
        if tag == "script" and not attrs.get("src") and attrs.get("type") != "application/ld+json":
            self.inline = True
    def handle_endtag(self, tag):
        if tag == "script":
            self.inline = False
    def handle_data(self, data):
        if self.inline:
            self.scripts.append(data)

scan = Scan()
scan.feed(page)
assert len(scan.forms) == 1, "Exactly one canonical service intake required"
form = scan.forms[0]
assert "data-nf-intake-form" in form
assert form.get("data-intake-vector") == "onchain-project"
assert form.get("data-intake-sku") == "general"
assert len(scan.ids) == len(set(scan.ids)), "Duplicate DOM IDs"
assert {x["data-clinic-track"] for x in scan.buttons} == {"startup", "community", "business", "rwa"}
assert all(x.get("aria-pressed") in ("true", "false") for x in scan.buttons)
assert scan.details >= 5
# Buyer packaging must remain interactive and use the same canonical intake.
assert len([x for x in scan.forms if x.get("id") == "nfTokenLaunchIntake"]) == 1
for expected in ("blueprint", "contracts", "launch", "rwa"):
    assert f'data-clinic-offer="{expected}"' in page
for expected in (
    'id="launch-plan"', 'id="clinic-generate-brief"', 'id="clinic-fit-stage"',
    'id="clinic-fit-focus"', 'id="clinic-fit-timing"', 'id="clinic-copy-brief"',
    'id="clinic-use-brief"', 'id="clinic-selected-offer"',
    'US$950', "Written quote", "No wallet, email",
    '/token-launch/clinic-growth-v2.js', '/token-launch/clinic-offers-v2.css',
):
    assert expected in page, f"Missing benchmark-driven buyer feature: {expected}"
for resource in ("token-launch/clinic-growth-v2.js", "token-launch/clinic-offers-v2.css"):
    assert (ROOT / resource).is_file(), f"Unshipped public clinic asset: {resource}"
extra_js = (ROOT / "token-launch/clinic-growth-v2.js").read_text(encoding="utf-8")
for marker in (
    "clinic-generate-brief", "clinic-use-brief", "clinic-copy-brief",
    "requested_package=", "utm_medium=", "utm_content=", "launch",
):
    assert marker in extra_js, f"Missing service attribution/first-value flow: {marker}"
subprocess.run(["node","--check",str(ROOT / "token-launch/clinic-growth-v2.js")],check=True,capture_output=True)

for marker in (
    '<html lang="en">', 'https://www.noetfield.com/token-launch/',
    'Planning a', 'token launch?', 'Request a launch scope',
    '/assets/noetfield-intake-core.js?v=42', '/assets/noetfield-forms.js?v=42',
    'id="clinic-type"', 'id="clinic-stage"', 'id="clinic-context"',
    'name="email"', 'name="notes"', 'name="org"',
    'data-nf-intake-status', 'utm_source', 'utm_campaign', 'No wallet needed',
):
    assert marker in page, f"Missing required route/UX: {marker}"
for forbidden in (
    "Guaranteed return", "Risk-free profits", "Instant exchange listing",
    "Your token is live", "We are a licensed broker", "Start token sale now",
):
    assert forbidden not in page, f"Unsupported claim: {forbidden}"
for href in scan.links:
    if not href.startswith("/") or href.startswith("//"):
        continue
    pathname = urlparse(href).path
    target = ROOT / pathname.lstrip("/")
    assert target.is_dir() or target.is_file(), f"Dead first-party link: {href}"
for asset in ["/onchain/hero-architecture-hd.webp", "/noetfield-favicon-512.png"]:
    assert (ROOT / asset.lstrip("/")).is_file(), f"Missing displayed asset: {asset}"
assert scan.scripts, "No interactive customer workbench logic"
with tempfile.TemporaryDirectory() as d:
    js = Path(d) / "clinic.js"
    js.write_text("\n".join(scan.scripts), encoding="utf-8")
    subprocess.run(["node", "--check", str(js)], check=True, capture_output=True)
print("PASS: premium token clinic HTML, four interactive tracks, genuine intake, attribution, first-party links, existing assets and JavaScript syntax")
