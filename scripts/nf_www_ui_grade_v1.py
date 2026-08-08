#!/usr/bin/env python3
"""NF www UI/UX grade gate — compliance is not class (fail-closed)."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "data" / "www-home-golden-baseline-v1.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def main() -> int:
    if not BASELINE_PATH.is_file():
        print(f"FAIL www-ui-grade: missing {BASELINE_PATH}", file=sys.stderr)
        return 1
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    fails: list[str] = []
    index = ROOT / "index.html"
    corp = ROOT / "assets" / "noetfield-corporate-v1.css"
    home_css = ROOT / "assets" / "noetfield-home-v2.css"

    for key, spec in (baseline.get("files") or {}).items():
        path = ROOT / spec["path"]
        if not path.is_file():
            fails.append(f"missing file {spec['path']}")
            continue
        size = path.stat().st_size
        min_b = int(spec.get("min_bytes") or 0)
        if size < min_b:
            fails.append(f"{spec['path']} too small ({size} < {min_b})")
        pin = spec.get("sha256")
        if pin:
            got = sha256_file(path)
            if got != pin:
                fails.append(f"{spec['path']} sha256 drift (got {got[:12]}… want {pin[:12]}…)")

    html = index.read_text(encoding="utf-8") if index.is_file() else ""
    css_blob = ""
    if corp.is_file():
        css_blob += corp.read_text(encoding="utf-8")
    if home_css.is_file():
        css_blob += home_css.read_text(encoding="utf-8")
    corpus = html + "\n" + css_blob

    for fam in baseline.get("required_font_families") or []:
        if fam not in html and fam.replace("+", " ") not in html:
            fails.append(f"missing required font family in index.html: {fam}")
    for fam in baseline.get("forbidden_font_families") or []:
        if fam in html or fam.replace("+", " ") in html:
            fails.append(f"forbidden font family present: {fam}")

    for href in baseline.get("required_stylesheet_hrefs") or []:
        if href not in html:
            fails.append(f"missing stylesheet href {href}")

    for marker in baseline.get("required_markers") or []:
        if marker not in corpus:
            fails.append(f"missing marker: {marker}")

    min_sec = int(baseline.get("min_nf_corp_section") or 0)
    got_sec = html.count("nf-corp-section")
    if got_sec < min_sec:
        fails.append(f"nf-corp-section count {got_sec} < {min_sec}")

    min_main = int(baseline.get("min_main_sections") or 0)
    got_main = len(re.findall(r"<section\b", html, flags=re.I))
    if got_main < min_main:
        fails.append(f"main <section> count {got_main} < {min_main}")

    copy = baseline.get("copy_grade") or {}
    h1_id = copy.get("h1_id") or "hero-title"
    h1_m = re.search(
        rf'<h1[^>]*id="{re.escape(h1_id)}"[^>]*>(.*?)</h1>',
        html,
        flags=re.I | re.S,
    )
    if not h1_m:
        h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.I | re.S)
    h1 = strip_tags(h1_m.group(1)).strip() if h1_m else ""
    h1_min = int(copy.get("h1_min_chars") or 0)
    h1_max = int(copy.get("h1_max_chars") or 10_000)
    if len(h1) < h1_min or len(h1) > h1_max:
        fails.append(f"H1 length {len(h1)} outside [{h1_min},{h1_max}]")

    lead_m = re.search(
        r'class="hero__lead"[^>]*>(.*?)</p>',
        html,
        flags=re.I | re.S,
    )
    if lead_m:
        lead = strip_tags(lead_m.group(1)).strip()
        lead_max = int(copy.get("hero_lead_max_chars") or 10_000)
        if len(lead) > lead_max:
            fails.append(f"hero lead length {len(lead)} > {lead_max}")

    em_max = int(copy.get("max_em_dashes_in_index") or 10_000)
    em_count = html.count("—") + html.count("–")
    if em_count > em_max:
        fails.append(f"em/en dash count {em_count} > {em_max}")

    if copy.get("forbid_all_caps_cta"):
        for btn in re.findall(
            r'<a[^>]*class="[^"]*\bbtn\b[^"]*"[^>]*>(.*?)</a>',
            html,
            flags=re.I | re.S,
        ):
            label = strip_tags(btn).strip()
            letters = re.sub(r"[^A-Za-z]", "", label)
            if letters and letters == letters.upper() and len(letters) >= 8:
                fails.append(f"ALL-CAPS CTA forbidden: {label[:80]}")

    for bad in copy.get("forbidden_cta_substrings") or []:
        if bad in html:
            fails.append(f"forbidden CTA substring present: {bad}")

    lower = html.lower()
    for filler in copy.get("forbidden_filler_openers") or []:
        if filler.lower() in lower:
            fails.append(f"forbidden filler opener: {filler}")

    verbs = copy.get("required_institutional_verbs_any") or []
    if verbs and not any(v.lower() in lower for v in verbs):
        fails.append("missing institutional verbs (govern/commission/inspect/…)")

    visual = baseline.get("visual") or {}
    manifest_rel = visual.get("manifest")
    if manifest_rel:
        man_path = ROOT / manifest_rel
        if not man_path.is_file():
            fails.append(f"missing visual manifest {manifest_rel}")
        else:
            man = json.loads(man_path.read_text(encoding="utf-8"))
            for probe in man.get("structural_css_probes") or []:
                p = ROOT / probe["file"]
                needle = probe["contains"]
                if not p.is_file() or needle not in p.read_text(encoding="utf-8"):
                    fails.append(f"CSS probe fail: {probe['file']} needs {needle!r}")

    # Pages beyond the homepage, each with the markers that must survive an edit.
    # Optional and additive: a baseline without this block behaves as before.
    #
    # For the trader page the markers worth pinning are not typographic. They are
    # the sentences that keep a page about a trading agent honest — that it places
    # no orders, that it is not advice, that no performance is claimed — plus the
    # indexing directives. Those are exactly what a well-meaning copy edit drops,
    # and nothing else in the repo would notice.
    extra_pages = baseline.get("additional_pages") or {}
    for route, spec in extra_pages.items():
        rel = spec.get("path") or ""
        page = ROOT / rel
        if not page.is_file():
            fails.append(f"missing page for {route}: {rel}")
            continue
        text = page.read_text(encoding="utf-8")
        min_b = int(spec.get("min_bytes") or 0)
        if len(text.encode("utf-8")) < min_b:
            fails.append(f"{rel} too small ({len(text.encode('utf-8'))} < {min_b})")
        for needle in spec.get("required_markers") or []:
            if needle not in text:
                fails.append(f"{route} lost required marker: {needle!r}")
        for needle in spec.get("forbidden_markers") or []:
            if needle in text:
                fails.append(f"{route} has forbidden marker: {needle!r}")

    if fails:
        print("=== verify-www-ui-grade FAIL ===", file=sys.stderr)
        for f in fails:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1

    print("=== verify-www-ui-grade ===")
    print(f"OK   baseline {baseline.get('schema')} v{baseline.get('version')}")
    print(f"OK   fonts {baseline.get('required_font_families')}")
    print(f"OK   nf-corp-section={got_sec} sections={got_main} h1_len={len(h1)}")
    if extra_pages:
        print(f"OK   additional pages {sorted(extra_pages)}")
    print("verify-www-ui-grade PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
