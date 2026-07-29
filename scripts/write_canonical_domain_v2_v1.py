#!/usr/bin/env python3
"""NOETFIELD_DOMAIN_CANONICAL_V2 — generate canonical corporate pages."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from corp_www_shell_v1 import (  # noqa: E402
    CLIENT_ZERO_URL,
    CORP_CSS_VER,
    TRUSTFIELD_URL,
    corp_footer,
    corp_head,
    corp_header,
    corp_page_close,
    corp_page_open,
    status_rail,
)

from write_corp_coherence_pages_v1 import LEGACY_TOPIC_OPTIONS  # noqa: E402

HOME_CSS = f' <link rel="stylesheet" href="/assets/noetfield-home-v2.css?v={CORP_CSS_VER}" />\n'


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def homepage() -> str:
    body = f"""
  <section class="hero nf-corp-hero" id="top" aria-labelledby="hero-title">
   <div class="nf-corp-wrap hero__grid">
    <div>
     <p class="hero__eyebrow nf-corp-eyebrow"><span class="dot" aria-hidden="true"></span>GOVERNED AI EXECUTION · CLIENT-ZERO</p>
     <h1 id="hero-title">AI systems should not decide when their own work is safe to ship.</h1>
     <p class="hero__lead">Noetfield is building the operating layer around capable AI models: explicit authority before action, bounded execution, separate acceptance, and evidence that can be reopened. The current system is live in client-zero commissioning.</p>
     <div class="actions nf-corp-actions">
      <a class="nf-button nf-button--primary" href="#what-exists">See what is live</a>
      <a class="nf-button nf-button--secondary" href="/proof/">Inspect the evidence</a>
     </div>
     {status_rail()}
    </div>
   </div>
  </section>

  <section class="nf-corp-section" aria-labelledby="problem-title">
   <div class="nf-corp-wrap nf-corp-split">
    <div><p class="nf-corp-eyebrow">Problem</p><h2 id="problem-title">Capable AI is not the same as accountable execution.</h2></div>
    <div class="nf-corp-prose"><p>Models can propose, tools can act, and agents can chain work. Institutions still need explicit authority, bounded effects, separate acceptance, and evidence that survives replay.</p></div>
   </div>
  </section>

  <section class="nf-corp-section nf-inner-band" id="what-exists" aria-labelledby="exists-title">
   <div class="nf-corp-wrap">
    <div class="nf-section-head"><div><p class="nf-corp-eyebrow">What exists today</p><h2 id="exists-title">Current surfaces and boundaries</h2></div></div>
    <div class="nf-principle-grid">
     <article><span class="nf-status nf-status--live">LIVE</span><h3>Noetfield runtime</h3><p>Client-zero execution application with bounded worker and project flow, build checks, revisioned artifacts, and authority modes.</p><p><a href="{CLIENT_ZERO_URL}" rel="noopener noreferrer">Open client-zero alpha ↗</a></p></article>
     <article><span class="nf-status nf-status--demonstrated">DEMONSTRATED</span><h3>SourceA / Runway</h3><p>Professional internal execution and evidence paths for governed software change and workflow commissioning.</p><p><a href="/applications/#sourcea">Applications overview</a></p></article>
     <article><span class="nf-status nf-status--separate">SEPARATE VENTURE</span><h3>TrustField</h3><p>Synthetic validation workflows in a separate regulated venture — not a Noetfield Systems Inc. product.</p><p><a href="/applications/trustfield/">Boundary page</a> · <a href="{TRUSTFIELD_URL}" rel="noopener noreferrer">TrustField ↗</a></p></article>
    </div>
   </div>
  </section>

  <section class="nf-corp-section" aria-labelledby="loop-title">
   <div class="nf-corp-wrap">
    <div class="nf-section-head"><div><p class="nf-corp-eyebrow">Operating loop</p><h2 id="loop-title">From authorized goal to evidence</h2></div></div>
    <ol class="nf-loop-chain">
     <li>Authorized goal</li><li>Policy + authority</li><li>Bounded execution</li><li>Checks</li>
     <li>Acceptance</li><li>Evidence</li><li>Continue / repair / escalate / stop</li>
    </ol>
    <p class="nf-corp-prose"><a href="/system/">System architecture overview</a> · <a href="/motors/">AI Motors</a> · <a href="/runways/">Runways</a></p>
   </div>
  </section>

  <section class="nf-corp-section nf-inner-band" aria-labelledby="why-title">
   <div class="nf-corp-wrap nf-principle-grid">
    <div class="nf-section-head nf-section-head--full"><div><p class="nf-corp-eyebrow">Why this matters</p><h2 id="why-title">Authority, independence, access, limits</h2></div></div>
    <article><h3>Human authority</h3><p>Promotion and acceptance stay outside probabilistic workers.</p></article>
    <article><h3>Provider independence</h3><p>Models and tools are replaceable inside a durable control plane.</p></article>
    <article><h3>Wider access</h3><p>Bounded execution can widen who may initiate work without widening who may ship it.</p></article>
    <article><h3>Inspectable limits</h3><p>Evidence states scope — not universal correctness.</p></article>
   </div>
  </section>

  <section class="nf-corp-section" aria-labelledby="evidence-title">
   <div class="nf-corp-wrap">
    <div class="nf-section-head"><div><p class="nf-corp-eyebrow">Current evidence</p><h2 id="evidence-title">Named proof within stated scope</h2></div><p><a href="/proof/">Full evidence register →</a></p></div>
    <div class="nf-proof-grid">
     <article class="nf-proof-card"><p class="nf-proof-card__status"><span class="nf-status nf-status--demonstrated">DEMONSTRATED</span></p><h3>Governed replacement</h3><p>Internal client-zero workflow with failure capture, bounded repair, and verifier judgment.</p><p><a href="/proof/governed-replacement/">Case study</a></p></article>
     <article class="nf-proof-card"><p class="nf-proof-card__status"><span class="nf-status nf-status--live">LIVE</span></p><h3>Claims-boundary correction</h3><p>Public correction of prior over-broad corporate claims; current boundaries on this site.</p><p><a href="/proof/">Evidence register</a></p></article>
    </div>
   </div>
  </section>

  <section class="nf-corp-section nf-inner-band" aria-labelledby="program-title">
   <div class="nf-corp-wrap nf-corp-split">
    <div><p class="nf-corp-eyebrow">Twelve-month public-interest program</p><h2 id="program-title">Attempt evidence, acceptance safety, explicit authority</h2></div>
    <div class="nf-corp-prose"><p>Provider-attempt ledger (commissioning) · acceptance safety · explicit authority · TrustField validation · independent review · selected public goods.</p><p>No grant-award implication. <a href="/public-interest/">Program page →</a></p></div>
   </div>
  </section>

  <section class="nf-corp-section nf-boundaries" aria-labelledby="boundary-title">
   <div class="nf-corp-wrap nf-corp-prose">
    <p class="nf-corp-eyebrow">Explicit evidence boundary</p>
    <h2 id="boundary-title">What this site does not claim</h2>
    <p>Existing evidence proves bounded infrastructure and execution properties within named scopes. It does not prove external adoption, revenue, universal correctness, certification, or complete semantic acceptance.</p>
    <p>TrustField is a separate venture in the ecosystem — not a Noetfield Systems Inc. product or subsidiary.</p>
   </div>
  </section>
"""
    return (
        corp_head(
            "Noetfield Systems | Governed AI Execution",
            "Noetfield Systems builds governed AI execution infrastructure. Client-zero commissioning is live; evidence is scoped and inspectable.",
            "https://www.noetfield.com/",
            extra_css=HOME_CSS,
        )
        + '\n<body class="nf-corp nf-home">\n <a class="nf-skip" href="#main">Skip to main content</a>\n'
        + corp_header(None)
        + "\n <main id=\"main\">\n"
        + body
        + corp_page_close()
    )


def system_page() -> str:
    body = """
  <section class="nf-inner-hero" aria-labelledby="system-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">System</p><h1 id="system-title">Governed AI execution infrastructure</h1></div>
    <div><p class="nf-corp-lead">An understandable architecture overview: harness and control plane around capable models, deterministic Motors for permitted effects, Runways for qualification, and evidence that can be reopened.</p></div>
   </div>
  </section>
  <section class="nf-corp-section" aria-labelledby="layers-title">
   <div class="nf-corp-wrap nf-corp-prose">
    <h2 id="layers-title">Layers</h2>
    <ul>
     <li><strong>Brain / harness</strong> — proposes bounded work; no execution authority.</li>
     <li><strong>Kernel / control plane</strong> — policy, identity, budget, authority resolution.</li>
     <li><strong>Motor</strong> — executes authorized Action Contracts; records effects. <a href="/motors/">Technical detail →</a></li>
     <li><strong>Verifier</strong> — judges evidence; promotion stays outside Motor.</li>
     <li><strong>Runway</strong> — versioned qualification path from goal to accepted output. <a href="/runways/">Public runways →</a></li>
    </ul>
   </div>
  </section>
"""
    return corp_page_open(
        "System — Noetfield Systems",
        "Architecture overview for governed AI execution: harness, control plane, Motors, Runways, and evidence.",
        "https://www.noetfield.com/system/",
        "system",
    ) + body + corp_page_close()


def applications_page() -> str:
    body = f"""
  <section class="nf-inner-hero" aria-labelledby="apps-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Applications</p><h1 id="apps-title">Where the infrastructure meets work</h1></div>
    <div><p class="nf-corp-lead">Client-zero commissioning, internal execution surfaces, separate ventures, and developer preview lanes — each with explicit status and boundary.</p></div>
   </div>
  </section>
  <section class="nf-corp-section" aria-labelledby="apps-grid-title">
   <div class="nf-corp-wrap nf-principle-grid">
    <article id="client-zero"><span class="nf-status nf-status--live">LIVE</span><h3>Noetfield client-zero application</h3><p>Bounded worker and project flow, build/integrity checks, revisioned artifacts, authority modes.</p><p><a href="{CLIENT_ZERO_URL}" rel="noopener noreferrer">Open client-zero alpha ↗</a></p></article>
    <article id="sourcea"><span class="nf-status nf-status--demonstrated">DEMONSTRATED</span><h3>SourceA / Runway execution surface</h3><p>Professional internal execution and evidence paths for governed software change.</p><p><a href="/runways/">Runways</a></p></article>
    <article><span class="nf-status nf-status--separate">SEPARATE VENTURE</span><h3>TrustField</h3><p>Separate regulated venture — not a Noetfield Systems Inc. product.</p><p><a href="/applications/trustfield/">Boundary page →</a></p></article>
    <article><span class="nf-status nf-status--commissioning">COMMISSIONING</span><h3>Developer API</h3><p>Developer preview / commissioning lane — not a production corporate product surface.</p><p><a href="/deterministic-api/">Developer preview</a></p></article>
   </div>
  </section>
"""
    return corp_page_open(
        "Applications — Noetfield Systems",
        "Client-zero application, SourceA execution, TrustField boundary, and developer preview lanes.",
        "https://www.noetfield.com/applications/",
        "applications",
    ) + body + corp_page_close()


def trustfield_app_page() -> str:
    body = f"""
  <section class="nf-inner-hero" aria-labelledby="tf-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Separate venture</p><h1 id="tf-title">TrustField — corporate boundary</h1></div>
    <div><p class="nf-corp-lead">TrustField is a separate venture in the Noetfield ecosystem. It is not a Noetfield Systems Inc. product, subsidiary, or regulated offering of the parent company.</p></div>
   </div>
  </section>
  <section class="nf-corp-section nf-corp-prose nf-corp-wrap">
   <h2>What it is</h2>
   <p>Synthetic validation workflows for regulated operations contexts — demonstrated as a separate venture with its own site and boundary.</p>
   <h2>What it demonstrates</h2>
   <p>Workflow setup, operational checks, and evidence boundaries within TrustField's own scope.</p>
   <h2>What it does not demonstrate</h2>
   <p>Noetfield Systems Inc. certification, MSB licensing, external customer adoption, or parent-company revenue.</p>
   <p><a href="{TRUSTFIELD_URL}" rel="noopener noreferrer">Open TrustField interactive workflow ↗</a></p>
  </section>
"""
    return corp_page_open(
        "TrustField — separate venture boundary",
        "TrustField corporate boundary: separate venture, not a Noetfield Systems Inc. product.",
        "https://www.noetfield.com/applications/trustfield/",
        "applications",
    ) + body + corp_page_close()


def public_interest_page() -> str:
    body = """
  <section class="nf-inner-hero" aria-labelledby="pi-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Public-interest program</p><h1 id="pi-title">Twelve-month program for accountable AI execution</h1></div>
    <div><p class="nf-corp-lead">Long-term problem: capable AI without inspectable authority harms freedom and fairness. This program publishes attempt evidence, acceptance safety, and explicit limits — without implying a grant award.</p></div>
   </div>
  </section>
  <section class="nf-corp-section nf-corp-wrap nf-corp-prose">
   <h2>Freedom and fairness rationale</h2>
   <p>People and institutions need to see what ran, under what authority, and what was accepted — not only what a model proposed.</p>
   <h2>Current company state</h2>
   <p>Client-zero commissioning is live. SourceA / Runway paths are demonstrated internally. External customers, revenue, and certification are not established.</p>
   <h2>Twelve-month milestones</h2>
   <ul>
    <li>Complete provider-attempt ledger (commissioning)</li>
    <li>Acceptance safety and semantic acceptance improvements</li>
    <li>TrustField validation within its separate venture scope</li>
    <li>Independent review and selected public goods outputs</li>
   </ul>
   <h2>Evidence boundaries</h2>
   <p>Milestones are published with scope and artifacts on the <a href="/proof/">evidence register</a>. No universal correctness or social-impact validation is claimed.</p>
  </section>
"""
    return corp_page_open(
        "Public-interest program — Noetfield Systems",
        "Twelve-month program for attempt evidence, acceptance safety, and explicit authority.",
        "https://www.noetfield.com/public-interest/",
        "program",
    ) + body + corp_page_close()


def proof_page() -> str:
    body = """
  <section class="nf-inner-hero" aria-labelledby="proof-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Evidence</p><h1 id="proof-title">Evidence register</h1></div>
    <div><p class="nf-corp-lead">Current proof items only — each with scope, source, what it proves, what it does not prove, and artifacts.</p></div>
   </div>
  </section>
  <section class="nf-corp-section">
   <div class="nf-corp-wrap">
    <article class="nf-evidence-register">
     <header><h2>Governed replacement demonstration</h2><p><span class="nf-status nf-status--demonstrated">DEMONSTRATED</span> · 2026-03</p></header>
     <dl class="nf-evidence-dl">
      <dt>Scope</dt><dd>Internal client-zero workflow — retain/wrap/replace with verification and bounded repair.</dd>
      <dt>Source</dt><dd>Client-zero commissioning bundle</dd>
      <dt>Proves</dt><dd>Failure capture, bounded repair, independent verification within infrastructure scope, receipt promotion.</dd>
      <dt>Does not prove</dt><dd>External customer deployment, revenue, universal correctness, or certification.</dd>
      <dt>Artifacts</dt><dd><a href="/proof/governed-replacement/">Case study</a> · <a href="/proof/governed-replacement.json">JSON</a></dd>
      <dt>Supersedes</dt><dd>—</dd>
      <dt>Superseded by</dt><dd>—</dd>
     </dl>
    </article>
    <article class="nf-evidence-register">
     <header><h2>Claims-boundary correction</h2><p><span class="nf-status nf-status--live">LIVE</span> · 2026-07</p></header>
     <dl class="nf-evidence-dl">
      <dt>Scope</dt><dd>Corporate www and public narrative under Noetfield Systems Inc. control.</dd>
      <dt>Source</dt><dd>Domain canonicalization release NOETFIELD_DOMAIN_CANONICAL_V2</dd>
      <dt>Proves</dt><dd>Current claim boundaries, retirement of stale enterprise and pricing narratives, and honest status labeling.</dd>
      <dt>Does not prove</dt><dd>External adoption, ARR, SOC 2, or production deployments at third parties.</dd>
      <dt>Artifacts</dt><dd><a href="/proof/noetfield/">Summary</a> · <a href="/proof/noetfield.json">JSON</a></dd>
      <dt>Supersedes</dt><dd>Parent-company self-audit (2026 Q1 narrative)</dd>
      <dt>Superseded by</dt><dd>—</dd>
     </dl>
    </article>
   </div>
  </section>
"""
    return corp_page_open(
        "Evidence register — Noetfield Systems",
        "Current public evidence with scope, artifacts, and explicit boundaries.",
        "https://www.noetfield.com/proof/",
        "evidence",
        og_image="https://www.noetfield.com/assets/social/noetfield-proof-v2.png",
    ) + body + corp_page_close()


def about_page() -> str:
    body = """
  <section class="nf-inner-hero" aria-labelledby="about-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Company</p><h1 id="about-title">Noetfield Systems Inc.</h1></div>
    <div><p class="nf-corp-lead">Vancouver-based company building governed AI execution infrastructure. Client-zero commissioning is live; broader external adoption is not yet established.</p></div>
   </div>
  </section>
  <section class="nf-corp-section nf-corp-wrap nf-corp-prose">
   <h2>Founder</h2><p>Founder-led company built from the operating problem outward — product strategy, systems engineering, governance design, and applied AI in one team.</p>
   <h2>Current team</h2><p>Small founder-led team in Vancouver, British Columbia. Not a generic agency or certifier.</p>
   <h2>Corporate boundaries</h2>
   <ul>
    <li><strong>Noetfield Systems Inc.</strong> owns Noetfield infrastructure and this corporate site.</li>
    <li><strong>SourceA</strong> is a Noetfield professional/internal execution surface (demonstrated).</li>
    <li><strong>TrustField</strong> is a separate venture — not a Noetfield Systems Inc. product or subsidiary.</li>
   </ul>
   <p><a href="/applications/trustfield/">TrustField boundary</a> · <a href="/investors/">Investors / ecosystem</a> (footer route)</p>
  </section>
"""
    return corp_page_open(
        "About — Noetfield Systems Inc.",
        "Company, founder, team, and corporate boundaries for Noetfield Systems Inc.",
        "https://www.noetfield.com/about/",
        "company",
    ) + body + corp_page_close()


def investors_page() -> str:
    body = """
  <section class="nf-inner-hero" aria-labelledby="inv-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Investors / ecosystem</p><h1 id="inv-title">Company thesis and current state</h1></div>
    <div><p class="nf-corp-lead">Governed AI execution infrastructure with client-zero commissioning live. Evidence is scoped; external customers and revenue are not established.</p></div>
   </div>
  </section>
  <section class="nf-corp-section nf-corp-wrap">
   <div class="nf-principle-grid">
    <article><h3>Thesis</h3><p>Explicit authority, bounded execution, separate acceptance, and reopenable evidence for consequential AI work.</p></article>
    <article><h3>Current state</h3><p>Live client-zero application · demonstrated SourceA/Runway paths · commissioning provider-attempt ledger and semantic acceptance.</p></article>
    <article><h3>Funding and support</h3><p><a href="/contact/?topic=program-funding">Program / funding</a> · <a href="/contact/?topic=technical-collaboration">Technical collaboration</a></p></article>
   </div>
   <p class="nf-corp-prose">No stale product inventory. TrustField is a separate venture — not a Noetfield Systems Inc. product or subsidiary. <a href="/proof/">Evidence register</a> · <a href="/proof/noetfield/">Claims boundary summary</a></p>
  </section>
"""
    return corp_page_open(
        "Investors / Ecosystem — Noetfield Systems",
        "Company thesis, current state, and funding routes — evidence-first.",
        "https://www.noetfield.com/investors/",
        "company",
        og_image="https://www.noetfield.com/assets/social/noetfield-investors-v2.png",
        include_intake=False,
    ) + body + corp_page_close()

HOME_CSS = f' <link rel="stylesheet" href="/assets/noetfield-home-v2.css?v={CORP_CSS_VER}" />\n'

def contact_page() -> str:
    body = f"""
  <section class="nf-inner-hero" aria-labelledby="contact-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Contact</p><h1 id="contact-title">Reach operations</h1></div>
    <div>
     <p class="nf-corp-lead">Program funding, technical collaboration, or general security and privacy inquiries.</p>
     <div class="nf-corp-actions">
      <a class="nf-button nf-button--primary" href="#contact-form">Start workflow intake</a>
      <a class="nf-button nf-button--secondary" href="/proof/">Review public proof</a>
     </div>
    </div>
   </div>
  </section>
  <section class="nf-corp-section" id="contact-form" aria-labelledby="contact-form-title">
   <div class="nf-corp-wrap">
    <h2 id="contact-form-title">Message operations</h2>
    <form id="nfContactForm" class="nf-pilot-apply-form" data-nf-intake-form data-intake-vector="contact" data-intake-sku="general" data-submit-label="Send message" data-intake-headline="Message recorded — async ops notify" aria-label="Contact operations">
     <div class="nf-pilot-apply-grid">
      <label>Work email<input type="email" name="email" required autocomplete="email" /></label>
      <label>Organization<input type="text" name="org" required autocomplete="organization" /></label>
      <label>Topic<select name="topic" required>
        <option value="">Select topic</option>
        <option value="program-funding">Program / funding</option>
        <option value="technical-collaboration">Technical or operating collaboration</option>
        <option value="general-security-privacy">General / security / privacy</option>
{LEGACY_TOPIC_OPTIONS}
      </select></label>
     </div>
     <label>Message<textarea name="notes" rows="5" required></textarea></label>
     <button type="submit" class="nf-button nf-button--primary">Send message</button>
     <div id="nfContactStatus" class="nf-intake-async-status" data-nf-intake-status hidden aria-live="polite"></div>
    </form>
   </div>
  </section>
"""
    return corp_page_open(
        "Contact — Noetfield Systems",
        "Program funding, technical collaboration, and security/privacy contact.",
        "https://www.noetfield.com/contact/",
        "company",
    ) + body + corp_page_close()


def runways_page() -> str:
    body = """
  <section class="nf-inner-hero" aria-labelledby="rw-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Runways</p><h1 id="rw-title">Governed qualification paths</h1></div>
    <div><p class="nf-corp-lead">Three public runways carry a human goal to an accepted output — or a documented safe stop — with evidence you can reopen.</p></div>
   </div>
  </section>
  <section class="nf-corp-section" aria-labelledby="featured-title">
   <div class="nf-corp-wrap nf-principle-grid">
    <div class="nf-section-head nf-section-head--full"><h2 id="featured-title">Public runways</h2></div>
    <article><h3>Governed Software Change</h3><p>Versioned path for software change with authority, checks, and evidence.</p><p><a href="/runways/">Overview</a></p></article>
    <article><h3>Decision Brief</h3><p>Structured decision workflow with stated acceptance criteria.</p><p><a href="/runways/decision-brief/">Decision Brief runway</a></p></article>
    <article><h3>Institutional Workflow Commissioning</h3><p>Bounded commissioning for consequential institutional workflows.</p><p><a href="/contact/?topic=technical-collaboration">Contact operations</a></p></article>
   </div>
   <p class="nf-corp-prose"><a href="/system/">System overview</a> · <a href="/motors/">AI Motors technical page</a></p>
  </section>
"""
    return corp_page_open(
        "Runways — Noetfield Systems",
        "Three public governed qualification paths: software change, decision brief, institutional commissioning.",
        "https://www.noetfield.com/runways/",
        "system",
        extra_css=f' <link rel="stylesheet" href="/assets/noetfield-runways-v1.css?v={CORP_CSS_VER}" />\n',
    ) + body + corp_page_close()


def main() -> int:
    pages = {
        "index.html": homepage(),
        "system/index.html": system_page(),
        "applications/index.html": applications_page(),
        "applications/trustfield/index.html": trustfield_app_page(),
        "public-interest/index.html": public_interest_page(),
        "proof/index.html": proof_page(),
        "about/index.html": about_page(),
        "investors/index.html": investors_page(),
        "contact/index.html": contact_page(),
        "runways/index.html": runways_page(),
    }
    for rel, html in pages.items():
        write(ROOT / rel, html)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
