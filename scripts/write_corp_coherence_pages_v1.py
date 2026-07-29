#!/usr/bin/env python3
"""Write corporate coherence pages (contact, trust, privacy) — shared nf-corp shell."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from corp_www_shell_v1 import corp_page_close, corp_page_open  # noqa: E402

LEGACY_TOPIC_OPTIONS = """
 <option value="intelligence-diagnostic" hidden>Intelligence Diagnostic Sprint</option>
 <option value="automation-build" hidden>Automation Build inquiry</option>
 <option value="ai-ops-retainer" hidden>AI Ops Partner retainer</option>
 <option value="pilot" hidden>Copilot Governance Pack pilot</option>
 <option value="trust-brief" hidden>Trust Brief</option>
 <option value="enterprise-governance" hidden>Enterprise governance</option>
 <option value="bank-pilot" hidden>Bank Pilot</option>
 <option value="partner" hidden>Partner / MSP program</option>
 <option value="investor-diligence" hidden>Investor diligence</option>
 <option value="investor-workflow" hidden>Investor workflow design</option>
 <option value="investor-audit" hidden>Investor audit</option>
 <option value="federal" hidden>Federal / public sector</option>
 <option value="feedback" hidden>Site feedback</option>
 <option value="decision-brief-pilot" hidden>Vendor Decision Brief pilot</option>
 <option value="incubator-ecosystem" hidden>Incubator / ecosystem</option>
 <option value="custom-workflow" hidden>Custom operating workflow</option>
 <option value="custom-investor-motor" hidden>Custom investor Motor</option>
 <option value="build" hidden>Automation build</option>
 <option value="retainer" hidden>AI operations retainer</option>
 <option value="bank-pilot-boundary" hidden>Bank pilot boundary</option>
 <option value="federal-governance-pack" hidden>Federal governance pack</option>
 <option value="frontier-governance-prototype" hidden>Frontier governance prototype</option>
 <option value="msp-delivery-boundaries" hidden>MSP delivery boundaries</option>
 <option value="msp-governance-pack" hidden>MSP governance pack</option>
 <option value="privacy" hidden>Privacy</option>
 <option value="procurement-diligence" hidden>Procurement diligence</option>
 <option value="pilot-client" hidden>Pilot or client workflow</option>
 <option value="governed-motor" hidden>Custom AI Motor or Runway</option>
 <option value="operating-partner" hidden>Operating partner</option>
"""


def contact_page() -> str:
    body = """
  <section class="nf-inner-hero" aria-labelledby="contact-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div>
     <p class="nf-corp-kicker">Contact · Vancouver, Canada</p>
     <h1 id="contact-title">Bring one consequential workflow.</h1>
    </div>
    <div>
     <p class="nf-corp-lead">Describe the event, current system, decision boundary, consequence of failure, and outcome that must be proven. Noetfield will determine whether it fits a Motor, a Runway or a bounded commissioning path.</p>
     <div class="nf-corp-actions">
      <a class="nf-button nf-button--primary" href="#contact-form">Start workflow intake</a>
      <a class="nf-button nf-button--secondary" href="/proof/">Review public proof</a>
     </div>
    </div>
   </div>
  </section>

  <section class="nf-corp-section" id="contact-form" aria-labelledby="contact-form-title">
   <div class="nf-corp-wrap">
    <div class="nf-section-head">
     <div><p class="nf-corp-eyebrow" id="contact-form-title">Async intake</p><h2>Message operations</h2></div>
     <p>Non-confidential only · include your Request ID from the footer · operations@noetfield.com replies within one business day.</p>
    </div>
    <form id="nfContactForm" class="nf-pilot-apply-form" data-nf-intake-form data-intake-vector="contact" data-intake-sku="general" data-submit-label="Send message" data-intake-headline="Message recorded — async ops notify" aria-label="Contact operations">
     <div class="nf-pilot-apply-grid">
      <label>Work email<input type="email" name="email" required autocomplete="email" placeholder="you@institution.com" /></label>
      <label>Organization<input type="text" name="org" required autocomplete="organization" placeholder="Organization" /></label>
      <label>Topic
       <select name="topic" required>
        <option value="">Select topic</option>
        <option value="commission-workflow">Commission a governed workflow</option>
        <option value="governed-motor">AI Motor / agent runtime</option>
        <option value="operating-partner">Operating partner</option>
        <option value="investor">Investor or ecosystem</option>
        <option value="platform-inquiry">Product/platform inquiry</option>
        <option value="other">Other</option>
""" + LEGACY_TOPIC_OPTIONS + """
       </select>
      </label>
      <label>Your name (optional)<input type="text" name="name" autocomplete="name" placeholder="Your name" /></label>
     </div>
     <label>Message<textarea name="notes" rows="5" required placeholder="Event · system · decision boundary · failure consequence · outcome to prove"></textarea></label>
     <div class="nf-corp-actions">
      <button type="submit" class="nf-button nf-button--primary">Send message</button>
     </div>
     <div id="nfContactStatus" class="nf-intake-async-status" data-nf-intake-status hidden aria-live="polite"></div>
    </form>
   </div>
  </section>
"""
    return (
        corp_page_open(
            "Contact — Noetfield Systems",
            "Bring one consequential workflow — async intake for governed agent infrastructure.",
            "https://www.noetfield.com/contact/",
            "contact",
        )
        + body
        + corp_page_close()
    )


def trust_page() -> str:
    body = """
  <section class="nf-inner-hero" aria-labelledby="trust-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Trust &amp; security</p><h1 id="trust-title">Trust begins with explicit boundaries.</h1></div>
    <div><p class="nf-corp-lead">Security scope, data handling, authority boundaries, execution containment, verification, and evidence — stated honestly from current infrastructure and code.</p></div>
   </div>
  </section>

  <section class="nf-corp-section" aria-labelledby="scope-title">
   <div class="nf-corp-wrap nf-corp-split">
    <div><p class="nf-corp-eyebrow">01</p><h2 id="scope-title">Current security scope</h2></div>
    <div class="nf-corp-prose">
     <p>Noetfield builds governed agent infrastructure: authenticated sessions, policy-gated execution APIs, durable runtime state, and exportable evidence bundles. Public surfaces run on Cloudflare Pages and Railway with environment-scoped secrets.</p>
     <p>We do not claim SOC 2 Type II, ISO 27001 certification, regulatory approval, perfect security, or immutability unless explicitly evidenced on this page.</p>
    </div>
   </div>
  </section>

  <section class="nf-corp-section nf-inner-band" aria-labelledby="data-title">
   <div class="nf-corp-wrap nf-corp-split">
    <div><p class="nf-corp-eyebrow">02</p><h2 id="data-title">Data handling</h2></div>
    <div class="nf-corp-prose">
     <p>Contact and intake forms collect work email, organization name, topic, and message text you submit. Request IDs (RID) thread async intake on the corporate site.</p>
     <p>Product runtimes store session, project, and execution metadata required to operate governed workflows. See <a href="/privacy/">Privacy</a> for collection and retention detail.</p>
    </div>
   </div>
  </section>

  <section class="nf-corp-section" aria-labelledby="identity-title">
   <div class="nf-corp-wrap nf-corp-split">
    <div><p class="nf-corp-eyebrow">03</p><h2 id="identity-title">Identity and authority</h2></div>
    <div class="nf-corp-prose">
     <p>Authenticated users bind to organization-scoped sessions. The control plane resolves whether a proposed Action Contract may execute — models and harnesses propose; they do not self-authorize.</p>
    </div>
   </div>
  </section>

  <section class="nf-corp-section" aria-labelledby="contain-title">
   <div class="nf-corp-wrap nf-corp-split">
    <div><p class="nf-corp-eyebrow">04</p><h2 id="contain-title">Execution containment</h2></div>
    <div class="nf-corp-prose">
     <p>Motors execute only authorized contracts inside bounded runtimes: idempotency keys, execution limits, recovery caps, and stop conditions. Tool access is policy-gated per capability registry.</p>
    </div>
   </div>
  </section>

  <section class="nf-corp-section nf-inner-band" aria-labelledby="verify-title">
   <div class="nf-corp-wrap nf-corp-split">
    <div><p class="nf-corp-eyebrow">05</p><h2 id="verify-title">Verification and change control</h2></div>
    <div class="nf-corp-prose">
     <p>Independent verifiers judge evidence against stated acceptance criteria. Promotion of workflow, policy, or runtime changes requires explicit human authority — no silent self-modification in production.</p>
    </div>
   </div>
  </section>

  <section class="nf-corp-section" aria-labelledby="evidence-title">
   <div class="nf-corp-wrap nf-corp-split">
    <div><p class="nf-corp-eyebrow">06</p><h2 id="evidence-title">Evidence and provenance</h2></div>
    <div class="nf-corp-prose">
     <p>Execution produces traces, receipts, and replayable artifacts scoped to a stated boundary. Public proof items live on <a href="/proof/">Proof</a> with explicit status and scope labels.</p>
    </div>
   </div>
  </section>

  <section class="nf-corp-section" aria-labelledby="certs-title">
   <div class="nf-corp-wrap">
    <div class="nf-section-head"><div><p class="nf-corp-eyebrow">07</p><h2 id="certs-title">Certifications and non-certifications</h2></div></div>
    <table class="nf-corp-table">
     <thead><tr><th scope="col">Item</th><th scope="col">Status</th><th scope="col">Evidence</th></tr></thead>
     <tbody>
      <tr><td>Export / evidence integrity checks (product)</td><td><span class="nf-status nf-status--demo">DEMONSTRATED</span></td><td><a href="/proof/">Public proof index</a> · client-zero scope</td></tr>
      <tr><td>SOC 2 Type II (Noetfield as company)</td><td><span class="nf-status nf-status--legacy">NOT CERTIFIED</span></td><td>No audit report published</td></tr>
      <tr><td>ISO 27001 (Noetfield as company)</td><td><span class="nf-status nf-status--legacy">NOT CERTIFIED</span></td><td>No certificate published</td></tr>
      <tr><td>ISO 42001 (Noetfield as company)</td><td><span class="nf-status nf-status--legacy">NOT CERTIFIED</span></td><td>No certificate published</td></tr>
      <tr><td>Noetfield as customer certifier</td><td><span class="nf-status nf-status--legacy">NOT A CERTIFICATION BODY</span></td><td>Corporate boundary — <a href="/about/">About</a></td></tr>
      <tr><td>Regulatory approval or universal correctness</td><td><span class="nf-status nf-status--legacy">NOT CLAIMED</span></td><td>Evidence scoped per <a href="/proof/">Proof</a> item</td></tr>
     </tbody>
    </table>
   </div>
  </section>

  <section class="nf-corp-section nf-contact" aria-labelledby="sec-contact-title">
   <div class="nf-corp-wrap nf-corp-prose">
    <p class="nf-corp-eyebrow">08</p>
    <h2 id="sec-contact-title">Security contact</h2>
    <p>Security or privacy questions: <a href="/contact/?topic=privacy#contact-form">Contact operations</a> · operations@noetfield.com · include your Request ID when available.</p>
   </div>
  </section>
"""
    return (
        corp_page_open(
            "Trust &amp; Security — Noetfield Systems",
            "Trust begins with explicit boundaries — security scope, data handling, authority, execution containment, and evidence.",
            "https://www.noetfield.com/trust/",
            None,
        )
        + body
        + corp_page_close()
    )


def privacy_page() -> str:
    body = """
  <section class="nf-inner-hero" aria-labelledby="privacy-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Privacy</p><h1 id="privacy-title">How we handle information.</h1></div>
    <div><p class="nf-corp-lead">This notice describes what the Noetfield corporate site and product surfaces collect, why, and how to reach us — without marketing offers or product SKUs.</p></div>
   </div>
  </section>

  <section class="nf-corp-section">
   <div class="nf-corp-wrap nf-corp-prose">
    <p><strong>Effective date:</strong> 29 July 2026</p>

    <h2>Who we are</h2>
    <p>Noetfield Systems Inc., Vancouver, British Columbia, Canada. <strong>Corporate site:</strong> www.noetfield.com (marketing, proof, intake). <strong>Product:</strong> app.noetfield.com (authenticated sessions, projects, execution).</p>
    <p><strong>Privacy contact:</strong> operations@noetfield.com · <a href="/contact/?topic=privacy#contact-form">Privacy intake form</a></p>

    <h2>What we collect</h2>
    <p><strong>Contact and intake forms (www)</strong> — work email, organization name, optional name, topic selection, and message text submitted via <a href="/contact/">Contact</a>. Submissions post to Noetfield platform intake APIs.</p>
    <p><strong>Request IDs (RID)</strong> — generated in your browser by <code>noetfield-shell.js</code> and stored in <code>localStorage</code> under key <code>nf_rid</code>. RIDs thread async intake and are echoed in form payloads. We do not use RID as a first-party HTTP cookie on canonical corporate pages.</p>
    <p><strong>Cookie consent preference (www)</strong> — if shown, stored in <code>localStorage</code> as <code>noetfield_cookie_consent_v1</code> by <code>noetfield-cookie-consent.js</code>.</p>
    <p><strong>Product accounts (app)</strong> — when you use app.noetfield.com, we process account identifiers, session tokens, project metadata, and execution records required to operate governed workflows.</p>

    <h2>Analytics and tracking</h2>
    <p>Canonical corporate pages do not load third-party advertising trackers. Infrastructure providers (Cloudflare for www delivery; Railway for platform APIs) may log standard HTTP metadata — IP address, user agent, timestamps — for security and operations.</p>

    <h2>How we use information</h2>
    <p>To respond to intake, operate authenticated product sessions, run governed execution, produce evidence artifacts, secure surfaces, and improve reliability. We do not sell personal information.</p>

    <h2>Storage and subprocessors</h2>
    <p>Intake and product data are processed on infrastructure operated by Noetfield and contracted providers used in current deployment manifests, including Cloudflare (static site and edge) and Railway (platform API and runtime). Data may be processed in Canada and the United States depending on provider region configuration.</p>

    <h2>Retention</h2>
    <p>Contact intake records are retained for operational response and engagement history while the inquiry remains active and as required for audit trails. Product execution records are retained for workflow continuity, evidence replay, and governed recovery within active deployment configuration. Deletion requests are handled case-by-case when operational or legal retention does not require continued storage.</p>

    <h2>Your requests</h2>
    <p>Access, correction, or deletion requests: <a href="/contact/?topic=privacy#contact-form">Contact operations</a> with your Request ID when available. We respond within a reasonable period.</p>

    <h2>Changes</h2>
    <p>We update this notice when collection, infrastructure, or retention practices change. Canonical URL: https://www.noetfield.com/privacy/</p>
   </div>
  </section>
"""
    return (
        corp_page_open(
            "Privacy — Noetfield Systems",
            "Privacy notice for Noetfield corporate and product surfaces.",
            "https://www.noetfield.com/privacy/",
            None,
        )
        + body
        + corp_page_close()
    )


def proof_page() -> str:
    body = """
  <section class="nf-inner-hero" aria-labelledby="proof-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div><p class="nf-corp-kicker">Proof</p><h1 id="proof-title">Public evidence and explicit boundaries.</h1></div>
    <div><p class="nf-corp-lead">What is proven, what is demonstrated internally, and what remains planned — with scope, source, and artifact links.</p></div>
   </div>
  </section>

  <section class="nf-corp-section" aria-labelledby="proof-grid-title">
   <div class="nf-corp-wrap">
    <div class="nf-section-head"><div><p class="nf-corp-eyebrow">Evidence index</p><h2 id="proof-grid-title">Current public proof items</h2></div></div>
    <div class="nf-proof-grid">
     <article class="nf-proof-card">
      <p class="nf-proof-card__status"><span class="nf-status nf-status--live">LIVE</span> · 2026</p>
      <h3>Parent-company self-audit</h3>
      <p><strong>Scope:</strong> Noetfield corporate and product surfaces under Noetfield control.</p>
      <p><strong>Proves:</strong> Governed execution posture, public evidence boundaries, and honest status labeling.</p>
      <p><strong>Does not prove:</strong> External customer deployments or revenue traction.</p>
      <p><strong>Source:</strong> Internal audit bundle · <a href="/proof/noetfield/">Case study</a> · <a href="/proof/noetfield.json">JSON</a></p>
     </article>
     <article class="nf-proof-card">
      <p class="nf-proof-card__status"><span class="nf-status nf-status--demo">CLIENT-ZERO / INTERNAL</span> · 2026</p>
      <h3>Governed replacement demonstration</h3>
      <p><strong>Scope:</strong> Internal client-zero workflow — retain/wrap/replace with verification and repair.</p>
      <p><strong>Proves:</strong> Failure capture, bounded repair, independent verification, and receipt promotion.</p>
      <p><strong>Does not prove:</strong> Fortune-500 production deployment or universal correctness.</p>
      <p><strong>Source:</strong> <a href="/proof/governed-replacement/">Case study</a> · <a href="/proof/governed-replacement.json">JSON bundle</a></p>
     </article>
     <article class="nf-proof-card">
      <p class="nf-proof-card__status"><span class="nf-status nf-status--planned">PLANNED</span></p>
      <h3>Portfolio product surface case study</h3>
      <p><strong>Scope:</strong> Formal public case study for a portfolio product surface.</p>
      <p><strong>Proves:</strong> Not yet published.</p>
      <p><strong>Does not prove:</strong> External client outcomes until published with evidence.</p>
     </article>
    </div>
   </div>
  </section>

  <section class="nf-corp-section nf-inner-band" aria-labelledby="trace-title">
   <div class="nf-corp-wrap nf-corp-prose">
    <p class="nf-corp-eyebrow">Operational trace shape</p>
    <h2 id="trace-title">What a governed episode looks like</h2>
    <p>Sensed state → Brain proposal → authority/permit → Motor effect → verifier verdict → measured result → durable next state.</p>
    <p>Receipts prove what the runtime observed and enforced within a stated scope. They are not certification or a claim of universal correctness.</p>
   </div>
  </section>
"""
    return (
        corp_page_open(
            "Proof &amp; Public Evidence — Noetfield Systems",
            "Inspect current Noetfield systems, verified states, evidence boundaries and public execution receipts.",
            "https://www.noetfield.com/proof/",
            "proof",
            og_image="https://www.noetfield.com/assets/social/noetfield-proof-v2.png",
        )
        + body
        + corp_page_close()
    )


def main() -> None:
    pages = {
        "contact/index.html": contact_page(),
        "trust/index.html": trust_page(),
        "privacy/index.html": privacy_page(),
        "proof/index.html": proof_page(),
    }
    for rel, html in pages.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        print("wrote", rel)


if __name__ == "__main__":
    main()
