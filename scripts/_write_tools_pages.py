#!/usr/bin/env python3
"""One-shot writer for /tools public pages. Run from repo root."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_CSS = "/assets/noetfield-corporate-v1.css?v=5"
TOOLS_CSS = "/assets/noetfield-tools.css?v=1"
TOOLS_JS = "/assets/noetfield-tools.js?v=1"
OG = "https://www.noetfield.com/assets/social/noetfield-corporate-v2.png"


def chrome(title: str, desc: str, url: str, tool: str, extra_ld: str = "") -> tuple[str, str]:
    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <title>{title}</title>
 <meta name="description" content="{desc}" />
 <meta name="robots" content="index,follow" />
 <link rel="canonical" href="{url}" />
 <meta property="og:site_name" content="Noetfield" />
 <meta property="og:title" content="{title}" />
 <meta property="og:description" content="{desc}" />
 <meta property="og:url" content="{url}" />
 <meta property="og:type" content="website" />
 <meta property="og:image" content="{OG}" />
 <meta property="og:image:width" content="1200" />
 <meta property="og:image:height" content="630" />
 <meta name="twitter:card" content="summary_large_image" />
 <meta name="twitter:title" content="{title}" />
 <meta name="twitter:description" content="{desc}" />
 <meta name="twitter:image" content="{OG}" />
 <meta name="theme-color" content="#f3f0e9" />
 <link rel="icon" href="/noetfield-favicon-512.png" type="image/png" />
 <link rel="preconnect" href="https://fonts.googleapis.com" />
 <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
 <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&amp;family=Inter:wght@400;500;600&amp;family=Newsreader:opsz,wght@6..72,400;6..72,500&amp;display=swap" />
 <link rel="stylesheet" href="{ASSET_CSS}" />
 <link rel="stylesheet" href="{TOOLS_CSS}" />
 <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "{title}",
  "url": "{url}",
  "applicationCategory": "BusinessApplication",
  "offers": {{ "@type": "Offer", "price": "0", "priceCurrency": "CAD" }},
  "description": "{desc}",
  "isAccessibleForFree": true,
  "provider": {{ "@type": "Organization", "name": "Noetfield Systems Inc.", "url": "https://www.noetfield.com/" }}
}}
 </script>{extra_ld}
</head>
<body class="nf-corp nf-corp--inner nf-tools" data-tool="{tool}">
 <a class="nf-skip" href="#main">Skip to main content</a>
 <header class="nf-corp-header">
  <div class="nf-corp-wrap nf-corp-navrow">
   <a class="nf-corp-brand" href="/">
    <span class="nf-corp-brand__mark" aria-hidden="true">N</span>
    <span>Noetfield Systems <small>Inc.</small></span>
   </a>
   <nav class="nf-corp-nav" aria-label="Primary navigation">
    <a href="/#product">Product</a><a href="/workflows/">Workflows</a><a href="/assurance/">Assurance</a><a href="/tools/">Tools</a><a href="/proof/">Proof</a><a href="/about/">Company</a>
    <a class="nf-corp-nav__cta nf-corp-nav__alpha" href="https://app.noetfield.com/" rel="noopener noreferrer">Open Noetfield App</a>
   </nav>
  </div>
 </header>
 <main id="main">
"""
    foot = """
 </main>
 <footer class="nf-corp-footer">
  <div class="nf-corp-wrap nf-corp-footer__grid">
   <div>
    <a class="nf-corp-brand nf-corp-brand--footer" href="/"><span class="nf-corp-brand__mark" aria-hidden="true">N</span><span>Noetfield Systems <small>Inc.</small></span></a>
    <p>AI agent governance and security.<br />Vancouver, British Columbia, Canada.</p>
   </div>
   <nav aria-label="Product"><strong>Product</strong><a href="https://app.noetfield.com/" rel="noopener noreferrer">App ↗</a><a href="/tools/">Tools</a><a href="/workflows/">Workflows</a><a href="/applications/">Applications</a></nav>
   <nav aria-label="Company"><strong>Company</strong><a href="/proof/">Proof</a><a href="/privacy/">Privacy</a><a href="/contact/">Contact</a><a href="/tools/embed/">Embed these tools</a></nav>
  </div>
  <div class="nf-corp-wrap nf-corp-footer__base"><span>© 2026 Noetfield Systems Inc.</span><span>Free. No signup. Nothing stored.</span></div>
 </footer>
 <script src="/assets/noetfield-tools.js?v=1" defer></script>
</body>
</html>
"""
    return head, foot


RELATED = """
  <section class="nf-corp-section nf-tools-related" aria-labelledby="more-tools">
   <div class="nf-corp-wrap">
    <p class="nf-corp-kicker" id="more-tools">More free checks</p>
    <div class="nf-tools-grid">
     <a href="/tools/quiet-leak/"><span>01</span><h3>Quiet leak</h3><p>Price one manual process. Honest hobby line at $3,000 a year.</p></a>
     <a href="/tools/ai-spend/"><span>02</span><h3>AI spend you cannot explain</h3><p>What share of the invoice maps to a named workflow.</p></a>
     <a href="/tools/who-accepted/"><span>03</span><h3>Who accepted this</h3><p>Chat log versus a named person and a replayable why.</p></a>
     <a href="/tools/copilot-seats/"><span>04</span><h3>Copilot seats</h3><p>Unused licenses and ungoverned use, shown as two numbers.</p></a>
     <a href="/tools/board-five/"><span>05</span><h3>Five board questions</h3><p>Yes or no. The tool will tell you not to buy.</p></a>
     <a href="/tools/embed/"><span>06</span><h3>Embed for advisors</h3><p>One iframe. No tracking of your visitors.</p></a>
    </div>
   </div>
  </section>
"""


def result_panel(kicker: str, show_amount: bool = True) -> str:
    amount = (
        '<p class="nf-tools-amount" data-result-amount>$0</p>'
        if show_amount
        else '<p class="nf-tools-amount" data-result-amount hidden></p>'
    )
    return f"""
     <aside class="nf-tools-result" id="nf-tools-result" aria-live="polite">
      <p class="nf-tools-kicker">{kicker}</p>
      {amount}
      <h2 data-result-headline>Fill the four numbers.</h2>
      <p data-result-body>The honest answer updates as you type. Under the hobby line, it will tell you to leave it alone.</p>
      <p data-result-extra hidden></p>
      <div class="nf-tools-actions">
       <a class="nf-button nf-button--primary" data-result-cta href="/tools/">See the other checks</a>
       <button type="button" class="nf-button nf-button--secondary" id="nf-tools-share">Copy share link</button>
       <button type="button" class="nf-button nf-button--secondary" id="nf-tools-copy">Copy result</button>
      </div>
     </aside>"""


def write(rel: str, html: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    print("wrote", rel)


def hub() -> None:
    head, foot = chrome(
        "Free operator tools — Noetfield",
        "One-minute checks that will tell you to leave a process alone. No signup. Nothing stored.",
        "https://www.noetfield.com/tools/",
        "hub",
    )
    body = """
  <section class="nf-inner-hero" aria-labelledby="tools-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div>
     <p class="nf-corp-kicker">Free · no signup · nothing stored</p>
     <h1 id="tools-title">Most operators can name the process that annoys them. Almost none can name what it costs.</h1>
    </div>
    <div>
     <p class="nf-corp-lead">Five one-minute checks. Conservative math. An honest leave-it-alone line. If the number is a hobby, the page says so instead of selling you a fix.</p>
     <div class="nf-corp-actions">
      <a class="nf-button nf-button--primary" href="/tools/quiet-leak/">Price one leak</a>
      <a class="nf-button nf-button--secondary" href="/tools/embed/">Embed on your site</a>
     </div>
    </div>
   </div>
  </section>
  <section class="nf-corp-section" aria-labelledby="tool-list">
   <div class="nf-corp-wrap">
    <h2 id="tool-list" class="nf-corp-kicker">The checks</h2>
    <div class="nf-tools-grid" style="margin-top:1.2rem">
     <a href="/tools/quiet-leak/"><span>Quiet leak</span><h3>What is this process costing you?</h3><p>Four inputs. Rate × 1.3 × 48 weeks. Under $3,000 a year, leave it alone.</p></a>
     <a href="/tools/ai-spend/"><span>AI invoice</span><h3>Spend you cannot explain</h3><p>The board question is not the model bill. It is which workflow created it.</p></a>
     <a href="/tools/who-accepted/"><span>Acceptance</span><h3>Who accepted the last output?</h3><p>If you cannot name them, you have a chat log, not a process.</p></a>
     <a href="/tools/copilot-seats/"><span>Copilot</span><h3>Seats versus a decision trail</h3><p>Unused licenses and ungoverned use, counted separately on purpose.</p></a>
     <a href="/tools/board-five/"><span>Board</span><h3>Five yes/no questions</h3><p>Score 0 or 1: do not buy. The tool will say that out loud.</p></a>
     <a href="/tools/embed/"><span>Advisors</span><h3>Put this on your own page</h3><p>One iframe. We do not track your visitors.</p></a>
    </div>
   </div>
  </section>
  <section class="nf-corp-section" aria-labelledby="rules-title">
   <div class="nf-corp-wrap nf-tools-notes">
    <article>
     <h3 id="rules-title">How the math stays honest</h3>
     <p>Loaded employer cost is 1.3× the hourly rate. Year is 48 working weeks. Errors, rework, and lateness are ignored on purpose. That keeps the number conservative, not theatrical.</p>
    </article>
    <article>
     <h3>What this is not</h3>
     <p>Not a quote. Not certification. Not a claim of customers or revenue. The Noetfield app is a founder-operated alpha. A receipt is not certification.</p>
    </article>
   </div>
  </section>
"""
    write("tools/index.html", head + body + foot)


def tool_page(
    slug: str,
    title: str,
    desc: str,
    kicker: str,
    h1: str,
    lead: str,
    form: str,
    presets: str,
    notes: str,
    math: str,
    show_amount: bool = True,
) -> None:
    head, foot = chrome(title, desc, f"https://www.noetfield.com/tools/{slug}/", slug)
    body = f"""
  <section class="nf-inner-hero" aria-labelledby="tool-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div>
     <p class="nf-corp-kicker">{kicker}</p>
     <h1 id="tool-title">{h1}</h1>
    </div>
    <div>
     <p class="nf-corp-lead">{lead}</p>
     <div class="nf-corp-actions">
      <a class="nf-button nf-button--secondary" href="/tools/">All tools</a>
      <a class="nf-button nf-button--secondary" href="/tools/embed/">Embed this</a>
     </div>
    </div>
   </div>
  </section>
  <section class="nf-corp-section" aria-labelledby="calc-title">
   <div class="nf-corp-wrap">
    <h2 id="calc-title" class="nf-corp-kicker">One minute</h2>
    {presets}
    <div class="nf-tools-layout" style="margin-top:1rem">
     <div class="nf-tools-card">
      <form id="nf-tools-form" class="nf-tools-form" action="#" method="get">
       {form}
      </form>
     </div>
     {result_panel("Honest answer", show_amount)}
    </div>
    <p class="nf-corp-lead nf-tools-math">{math}</p>
    <div class="nf-tools-notes">{notes}</div>
   </div>
  </section>
{RELATED}
"""
    write(f"tools/{slug}/index.html", head + body + foot)


def embed() -> None:
    head, foot = chrome(
        "Embed Noetfield tools — free for advisors",
        "Put the one-minute checks on your own page. One iframe. No signup. We do not track your visitors.",
        "https://www.noetfield.com/tools/embed/",
        "embed",
    )
    items = [
        ("Quiet leak", "https://www.noetfield.com/tools/quiet-leak/?embed=1"),
        ("AI spend", "https://www.noetfield.com/tools/ai-spend/?embed=1"),
        ("Who accepted", "https://www.noetfield.com/tools/who-accepted/?embed=1"),
        ("Copilot seats", "https://www.noetfield.com/tools/copilot-seats/?embed=1"),
        ("Five board questions", "https://www.noetfield.com/tools/board-five/?embed=1"),
    ]
    blocks = []
    for name, src in items:
        blocks.append(
            f"""
    <div class="nf-tools-embed-block" data-embed-src="{src}">
     <h3>{name}</h3>
     <pre><code></code></pre>
     <button type="button" class="nf-button nf-button--secondary" data-copy-embed>Copy embed</button>
    </div>"""
        )
    body = f"""
  <section class="nf-inner-hero" aria-labelledby="embed-title">
   <div class="nf-corp-wrap nf-inner-hero__grid">
    <div>
     <p class="nf-corp-kicker">Advisors · free</p>
     <h1 id="embed-title">Put the check on your own page.</h1>
    </div>
    <div>
     <p class="nf-corp-lead">One iframe. No signup. We do not set cookies on your visitors and we do not store their numbers. Keep the Noetfield link under the frame so people can open the full page.</p>
    </div>
   </div>
  </section>
  <section class="nf-corp-section">
   <div class="nf-corp-wrap">
    {''.join(blocks)}
    <p class="nf-corp-lead">If you advise operators, send them a check that is willing to say leave it alone. That is the whole point.</p>
   </div>
  </section>
{RELATED}
"""
    write("tools/embed/index.html", head + body + foot)


def main() -> None:
    hub()
    tool_page(
        "quiet-leak",
        "Quiet leak calculator — Noetfield",
        "Four numbers. What one manual process costs a year, and whether it is worth fixing.",
        "Same math as the operator post",
        "What is this process costing you?",
        "Pick the quiet one. Double entry. Status copied into a tracker. A draft rewritten after the model said it was done. Four inputs, 48 working weeks, 1.3 loaded rate.",
        """
       <label>Times a week someone touches it
        <input type="number" name="touches" min="0" step="0.5" value="8" inputmode="decimal" required />
       </label>
       <label>Minutes per touch
        <span class="hint">Include the context switch.</span>
        <input type="number" name="minutes" min="0" step="0.5" value="12" inputmode="decimal" required />
       </label>
       <label>Hourly rate before overhead (CAD)
        <input type="number" name="rate" min="0" step="1" value="45" inputmode="decimal" required />
       </label>
       <label>How many people do this
        <input type="number" name="people" min="0" step="1" value="3" inputmode="decimal" required />
       </label>
        """,
        """
    <div class="nf-tools-presets" aria-label="Example leaks">
     <button type="button" data-preset='{"touches":10,"minutes":8,"rate":45,"people":3}'>Double data entry</button>
     <button type="button" data-preset='{"touches":6,"minutes":15,"rate":40,"people":2}'>Invoice chase</button>
     <button type="button" data-preset='{"touches":12,"minutes":5,"rate":38,"people":4}'>CRM copy-paste</button>
    </div>
        """,
        """
    <article><h3>People undercount touches by about half</h3><p>Count one real day before you estimate. The number you type from memory is usually the complaint, not the work.</p></article>
    <article><h3>The expensive leaks are the quiet ones</h3><p>Nobody files a ticket for the copy between two systems. Everyone accepted it years ago. That is why it survives.</p></article>
        """,
        "Annual cost = touches × (minutes ÷ 60) × rate × 1.3 × people × 48. Under $3,000, leave it alone.",
    )
    tool_page(
        "ai-spend",
        "AI spend you cannot explain — Noetfield",
        "See how much of the AI invoice has no named workflow behind it.",
        "Invoice versus workflow",
        "Most teams can name the AI invoice. Almost none can name which workflow created it.",
        "If spend is small and one team owns it, a spreadsheet is enough. If several teams are in it and you cannot attribute 20% of the bill, the leak is explanation, not tokens.",
        """
       <label>Monthly AI / Copilot spend (CAD)
        <input type="number" name="monthly" min="0" step="50" value="4000" inputmode="decimal" required />
       </label>
       <label>Share you can attribute to a named workflow (%)
        <input type="number" name="attributed" min="0" max="100" step="1" value="15" inputmode="decimal" required />
       </label>
       <label>Teams using it
        <input type="number" name="teams" min="1" step="1" value="3" inputmode="decimal" required />
       </label>
       <label>Does a named person accept the output before it leaves?
        <select name="named" required>
         <option value="no" selected>No</option>
         <option value="yes">Yes</option>
        </select>
       </label>
        """,
        """
    <div class="nf-tools-presets">
     <button type="button" data-preset='{"monthly":800,"attributed":80,"teams":1,"named":"yes"}'>One team, small bill</button>
     <button type="button" data-preset='{"monthly":12000,"attributed":10,"teams":6,"named":"no"}'>Several teams, unexplained</button>
    </div>
        """,
        """
    <article><h3>Licensed Copilot is not the whole bill</h3><p>People count seats and forget personal ChatGPT. That unofficial line is often larger, and it never shows up in the invoice meeting.</p></article>
    <article><h3>The draft that shipped with no name on it</h3><p>Nobody files a ticket for that. So it survives. That is the expensive leak.</p></article>
        """,
        "Unattributed annual = monthly × (1 − attributed share) × 12. Leave it alone under $1,500 a month with one team.",
    )
    tool_page(
        "who-accepted",
        "Who accepted this output — Noetfield",
        "Price the unsigned AI drafts your team still rewrites by hand.",
        "Chat log versus process",
        "If you cannot name who accepted the last AI output, you do not have a process.",
        "A process has a named person, a pass/fail check, and a reason you can open later. Four inputs. The page will tell you to stop shopping if you already have that.",
        """
       <label>AI-assisted deliverables per week
        <input type="number" name="deliverables" min="0" step="1" value="20" inputmode="decimal" required />
       </label>
       <label>Share a named person signs (%)
        <input type="number" name="signed" min="0" max="100" step="1" value="25" inputmode="decimal" required />
       </label>
       <label>Minutes of redo on an unsigned item
        <input type="number" name="minutes" min="0" step="1" value="18" inputmode="decimal" required />
       </label>
       <label>Hourly rate before overhead (CAD)
        <input type="number" name="rate" min="0" step="1" value="55" inputmode="decimal" required />
       </label>
       <label>Can you replay why the last one passed?
        <select name="replay" required>
         <option value="no" selected>No</option>
         <option value="yes">Yes</option>
        </select>
       </label>
        """,
        """
    <div class="nf-tools-presets">
     <button type="button" data-preset='{"deliverables":8,"signed":95,"minutes":5,"rate":55,"replay":"yes"}'>Already signed</button>
     <button type="button" data-preset='{"deliverables":30,"signed":10,"minutes":25,"rate":65,"replay":"no"}'>Chat drafts, heavy rewrite</button>
    </div>
        """,
        """
    <article><h3>The builder must not grade itself</h3><p>If the same person or model that produced the draft also marks it done, you do not have a check. You have a hope.</p></article>
    <article><h3>Redo is the bill you already pay</h3><p>Minutes spent rewriting “finished” drafts is the real cost. The tool prices that, not a fantasy saving.</p></article>
        """,
        "Unsigned volume × redo minutes × loaded rate × 48 weeks. Leave it alone at 90% signed with a replayable why.",
    )
    tool_page(
        "copilot-seats",
        "Copilot seats versus governed use — Noetfield",
        "Unused Copilot licenses and ungoverned use, shown as two separate yearly costs.",
        "Two numbers, not one",
        "You are paying for seats. You are not paying for a decision trail.",
        "Unused licenses are an adoption problem. Ungoverned use is an explanation problem. Showing only one of those numbers is how a page stays dishonest.",
        """
       <label>Licensed seats
        <input type="number" name="licensed" min="0" step="1" value="80" inputmode="decimal" required />
       </label>
       <label>Seats used last week
        <input type="number" name="used" min="0" step="1" value="35" inputmode="decimal" required />
       </label>
       <label>Hours per used seat per week
        <input type="number" name="hours" min="0" step="0.5" value="4" inputmode="decimal" required />
       </label>
       <label>Hourly rate before overhead (CAD)
        <input type="number" name="rate" min="0" step="1" value="55" inputmode="decimal" required />
       </label>
       <label>Annual cost per seat (CAD)
        <span class="hint">Default 360 for Copilot-class licensing. Change it if you know the real number.</span>
        <input type="number" name="seat" min="0" step="10" value="360" inputmode="decimal" required />
       </label>
        """,
        """
    <div class="nf-tools-presets">
     <button type="button" data-preset='{"licensed":12,"used":11,"hours":2,"rate":45,"seat":360}'>Small team, used</button>
     <button type="button" data-preset='{"licensed":200,"used":40,"hours":6,"rate":70,"seat":360}'>Wide rollout, thin use</button>
    </div>
        """,
        """
    <article><h3>Unused seats under about 10</h3><p>That is adoption. Do not buy a control plane to fix a habit. Ask why people are not in the tool.</p></article>
    <article><h3>Used seats with no named accepter</h3><p>That is the expensive line. Hours are being spent and nobody can replay why an output left the building.</p></article>
        """,
        "Unused waste = unused seats × annual seat cost. Ungoverned use = used seats × hours × loaded rate × 48 weeks.",
    )
    tool_page(
        "board-five",
        "Five board questions — Noetfield",
        "Five yes or no questions. Score 0 or 1 means do not buy a diagnostic.",
        "Yes or no only",
        "The board questions you either can answer or you cannot.",
        "No scores dressed up as science. Check what you can actually name today. The page will tell you not to buy.",
        """
       <div class="nf-tools-checks">
        <label><input type="checkbox" name="workflow" /> Can you name the workflow?</label>
        <label><input type="checkbox" name="owner" /> Can you name the owner?</label>
        <label><input type="checkbox" name="spend" /> Can you name last month’s spend for it?</label>
        <label><input type="checkbox" name="failed" /> Can you name the last time it failed?</label>
        <label><input type="checkbox" name="accepted" /> Can you name who accepted the last output?</label>
       </div>
        """,
        """
    <div class="nf-tools-presets">
     <button type="button" data-preset='{}'>Clear all</button>
    </div>
        """,
        """
    <article><h3>0 or 1: do not buy</h3><p>Name one workflow and who accepts its output. Then come back. A diagnostic sold into a blank page is theatre.</p></article>
    <article><h3>4 or 5: a memo can be defended</h3><p>Trust Brief is a six-week policy map, not a product tour. Use it when the board needs that memo, not before.</p></article>
        """,
        "Score is a count of yes answers. 0–1 leave it. 2–3 Copilot Readiness if procurement needs a file. 4–5 Trust Brief only if you need the memo.",
        show_amount=False,
    )
    embed()


if __name__ == "__main__":
    main()
