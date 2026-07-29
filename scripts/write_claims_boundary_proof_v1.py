#!/usr/bin/env python3
"""NOETFIELD_SFF_CANONICAL_PATCH_V1 — claims-boundary proof + supersede noetfield audit."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CLAIMS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <title>Claims-boundary correction — Noetfield Systems</title>
 <meta name="description" content="Public correction of prior over-broad corporate claims under Noetfield Systems Inc. control." />
 <meta name="robots" content="index,follow" />
 <meta name="theme-color" content="#07080a" />
 <link rel="canonical" href="https://www.noetfield.com/proof/claims-boundary-correction/" />
 <link rel="icon" href="/noetfield-favicon-512.png" type="image/png" />
 <link rel="preconnect" href="https://fonts.googleapis.com" />
 <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
 <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&amp;display=swap" />
 <link rel="stylesheet" href="/assets/noetfield-gate-v1.css?v=1" />
 <link rel="stylesheet" href="/assets/noetfield-gate-pages-v1.css?v=5" />
</head>
<body class="nf-gate nf-gate--vc">
 <div class="nf-gate__bg" aria-hidden="true"></div>
 <div class="nf-gate__frame">
  <header class="nf-gate__top">
   <a class="nf-gate__mark" href="/">Noetfield Systems Inc.</a>
   <span class="nf-gate__locale">Evidence</span>
  </header>
  <main id="main" class="nf-gate__main">
   <a class="nf-vc-back" href="/proof/">← Evidence register</a>
   <header class="nf-vc-hero">
    <p class="nf-vc-kicker">Claims-boundary correction</p>
    <h1>Current public claim boundaries</h1>
    <p class="nf-vc-lead">This proof item replaces the superseded parent-company self-audit. It records what the corporate site claims today, what was retired, and what remains open.</p>
   </header>
   <div class="nf-vc-strip">
    <span class="nf-vc-pill nf-vc-pill--live">LIVE</span>
    <span class="nf-vc-pill">Scope: corporate www narrative</span>
    <span class="nf-vc-pill">Not external adoption proof</span>
   </div>
   <section class="nf-vc-section">
    <h2>What changed</h2>
    <ul>
     <li>Retired stale three-product-line and /enterprise-as-current narratives from the public index.</li>
     <li>TrustField is stated as a separate venture — not a Noetfield Systems Inc. product or subsidiary.</li>
     <li>SourceB removed from canonical corporate pages; portfolio references narrowed to stated scopes.</li>
     <li>Prior <code>/proof/noetfield/</code> self-audit marked SUPERSEDED + NOINDEX.</li>
    </ul>
   </section>
   <section class="nf-vc-section">
    <h2>What this proves</h2>
    <p>Honest status labeling, explicit evidence boundaries, and alignment between homepage, About, Investors, Applications, and TrustField separate-venture boundary copy.</p>
   </section>
   <section class="nf-vc-section">
    <h2>What this does not prove</h2>
    <p>External customer adoption, revenue, ARR, SOC 2, universal correctness, or third-party certification.</p>
   </section>
   <nav class="nf-vc-grid nf-vc-grid--2" aria-label="Artifacts">
    <a class="nf-vc-tile" href="/proof/claims-boundary-correction.json">
     <span class="nf-vc-tile__arrow" aria-hidden="true">↗</span>
     <span class="nf-vc-tile__label">Machine-readable bundle (JSON)</span>
     <span class="nf-vc-tile__desc">Illustrative receipt schema fields are labeled sample-only in the bundle.</span>
    </a>
    <a class="nf-vc-tile" href="/proof/governed-replacement/">
     <span class="nf-vc-tile__arrow" aria-hidden="true">↗</span>
     <span class="nf-vc-tile__label">Governed replacement proof</span>
     <span class="nf-vc-tile__desc">Client-zero execution demonstration — separate scope.</span>
    </a>
   </nav>
   <p class="nf-vc-note">Release: NOETFIELD_SFF_CANONICAL_PATCH_V1 · Supersedes parent-company self-audit at /proof/noetfield/.</p>
  </main>
  <footer class="nf-gate__foot"><span>© 2026 Noetfield Systems Inc.</span></footer>
 </div>
</body>
</html>
"""

NOETFIELD_SUPERSEDED_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <title>SUPERSEDED — Parent-company self-audit</title>
 <meta name="description" content="Superseded evidence item. See claims-boundary correction." />
 <meta name="robots" content="noindex,nofollow" />
 <meta name="theme-color" content="#07080a" />
 <link rel="canonical" href="https://www.noetfield.com/proof/noetfield/" />
 <link rel="icon" href="/noetfield-favicon-512.png" type="image/png" />
 <link rel="stylesheet" href="/assets/noetfield-gate-v1.css?v=1" />
 <link rel="stylesheet" href="/assets/noetfield-gate-pages-v1.css?v=5" />
</head>
<body class="nf-gate nf-gate--vc">
 <div class="nf-gate__bg" aria-hidden="true"></div>
 <div class="nf-gate__frame">
  <header class="nf-gate__top">
   <a class="nf-gate__mark" href="/">Noetfield Systems Inc.</a>
   <span class="nf-gate__locale">Superseded</span>
  </header>
  <main id="main" class="nf-gate__main">
   <p class="nf-vc-kicker">SUPERSEDED · HISTORICAL ARTIFACT · NOT CURRENT COMPANY DOCUMENTATION · NOINDEX</p>
   <h1>Parent-company self-audit (retired)</h1>
   <p class="nf-vc-lead">This case study contained stale three-product-line and /enterprise narrative. It is a historical artifact — not current company documentation.</p>
   <p class="nf-vc-kicker" style="margin-top:1rem">SUPERSEDED · HISTORICAL ARTIFACT · NOT CURRENT COMPANY DOCUMENTATION</p>
   <p><a href="/proof/claims-boundary-correction/">Open claims-boundary correction →</a></p>
  </main>
  <footer class="nf-gate__foot"><span>© 2026 Noetfield Systems Inc.</span></footer>
 </div>
</body>
</html>
"""

CLAIMS_JSON = {
    "schema": "noetfield_public_evidence_bundle_v1",
    "schema_note": "Illustrative receipt fields are labeled sample-only; not live execution receipts.",
    "entity": "Noetfield Systems Inc.",
    "entity_type": "claims_boundary_correction",
    "generated_at": "2026-07-29T13:30:00Z",
    "release": "NOETFIELD_SFF_FINAL_RECONCILIATION_V1",
    "title": "Claims-boundary correction",
    "status": "LIVE",
    "scope": "Corporate www and public narrative under Noetfield Systems Inc. control",
    "proves": [
        "Current claim boundaries on www.noetfield.com",
        "Retirement of stale enterprise and three-product-line narratives",
        "TrustField stated as a separate venture — not a Noetfield Systems Inc. product or subsidiary",
    ],
    "does_not_prove": [
        "External customer adoption",
        "Revenue or ARR",
        "Universal correctness",
        "Third-party certification",
    ],
    "supersedes": {
        "route": "/proof/noetfield/",
        "label": "Parent-company self-audit (2026 Q1 narrative)",
    },
    "artifacts": {
        "html": "/proof/claims-boundary-correction/",
        "json": "/proof/claims-boundary-correction.json",
    },
    "illustrative_receipt_schema": {
        "label": "SAMPLE ONLY — not a live receipt",
        "fields": [
            "receipt_id",
            "runway",
            "authority",
            "verification_attempts",
            "promotion_decision",
            "boundary_note",
        ],
    },
}

NOETFIELD_JSON = {
    "schema": "noetfield_public_evidence_bundle_v1",
    "status": "SUPERSEDED",
    "historical_artifact": True,
    "not_current_company_documentation": True,
    "robots": "noindex,nofollow",
    "superseded_by": "/proof/claims-boundary-correction/",
    "superseded_at": "2026-07-29T13:30:00Z",
    "release": "NOETFIELD_SFF_FINAL_RECONCILIATION_V1",
    "note": "Retired parent-company self-audit with stale three-product-line narrative.",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    write(ROOT / "proof/claims-boundary-correction/index.html", CLAIMS_HTML)
    write(
        ROOT / "proof/claims-boundary-correction.json",
        json.dumps(CLAIMS_JSON, indent=2, sort_keys=True) + "\n",
    )
    write(ROOT / "proof/noetfield/index.html", NOETFIELD_SUPERSEDED_HTML)
    write(
        ROOT / "proof/noetfield.json",
        json.dumps(NOETFIELD_JSON, indent=2, sort_keys=True) + "\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
