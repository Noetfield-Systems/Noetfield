"""Shared corporate www shell — navy/gold institutional (PR #186 class)."""
from __future__ import annotations

CORP_CSS_VER = "3"
CORP_FONT = (
    ' <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    ' <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    ' <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500'
    '&amp;family=Inter:wght@400;500;600&amp;family=Newsreader:opsz,wght@6..72,400;6..72,500&amp;display=swap" />'
)
INTAKE_SCRIPTS = (
    ' <script src="/assets/noetfield-intake-core.js?v=42" defer></script>\n'
    ' <script src="/assets/noetfield-forms.js?v=42" defer></script>\n'
    ' <script src="/assets/noetfield-shell.js?v=42" defer></script>'
)

NAV_ITEMS = (
    ("motors", "/motors/", "AI Motors"),
    ("runways", "/runways/", "Runways"),
    ("proof", "/proof/", "Proof"),
    ("company", "/about/", "Company"),
)


def corp_head(
    title: str,
    desc: str,
    canonical: str,
    *,
    theme: str = "#f3f0e9",
    extra_css: str = "",
    og_image: str = "https://www.noetfield.com/assets/social/noetfield-corporate-v2.png",
) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <title>{title}</title>
 <meta name="description" content="{desc}" />
 <meta name="robots" content="index,follow" />
 <meta name="theme-color" content="{theme}" />
 <link rel="canonical" href="{canonical}" />
 <meta property="og:site_name" content="Noetfield" />
 <meta property="og:title" content="{title}" />
 <meta property="og:description" content="{desc}" />
 <meta property="og:url" content="{canonical}" />
 <meta property="og:type" content="website" />
 <meta property="og:image" content="{og_image}" />
 <meta property="og:image:width" content="1200" />
 <meta property="og:image:height" content="630" />
 <meta name="twitter:card" content="summary_large_image" />
 <meta name="twitter:title" content="{title}" />
 <meta name="twitter:description" content="{desc}" />
 <meta name="twitter:image" content="{og_image}" />
 <meta name="nf-chat-api-base" content="https://platform.noetfield.com" />
 <link rel="icon" href="/noetfield-favicon-512.png" type="image/png" />
{CORP_FONT}
 <link rel="stylesheet" href="/assets/noetfield-corporate-v1.css?v={CORP_CSS_VER}" />
{extra_css}
{INTAKE_SCRIPTS}
</head>"""


def _nav_link(key: str, href: str, label: str, active: str | None) -> str:
    current = ' aria-current="page"' if active == key else ""
    return f'<a href="{href}"{current}>{label}</a>'


def corp_header(active: str | None = None) -> str:
    links = "".join(_nav_link(k, h, l, active) for k, h, l in NAV_ITEMS)
    contact_current = ' aria-current="page"' if active == "contact" else ""
    return f""" <header class="nf-corp-header">
  <div class="nf-corp-wrap nf-corp-navrow">
   <a class="nf-corp-brand" href="/" aria-label="Noetfield Systems home">
    <span class="nf-corp-brand__mark" aria-hidden="true">N</span>
    <span>Noetfield Systems <small>Inc.</small></span>
   </a>
   <nav class="nf-corp-nav" aria-label="Primary navigation">
    {links}
    <a class="nf-corp-nav__deploy" href="https://app.noetfield.com/" rel="noopener noreferrer">Deploy ↗</a>
    <a class="nf-corp-nav__cta" href="/contact/?topic=commission-workflow"{contact_current}>Contact</a>
   </nav>
  </div>
 </header>"""


def corp_footer() -> str:
    return """ <footer class="nf-corp-footer">
  <div class="nf-corp-wrap nf-corp-footer__grid">
   <div>
    <a class="nf-corp-brand nf-corp-brand--footer" href="/"><span class="nf-corp-brand__mark" aria-hidden="true">N</span><span>Noetfield Systems <small>Inc.</small></span></a>
    <p>Vancouver, British Columbia, Canada</p>
   </div>
   <nav aria-label="Systems"><strong>Systems</strong><a href="/motors/">AI Motors</a><a href="/runways/">Runways</a><a href="/proof/">Proof</a></nav>
   <nav aria-label="Company"><strong>Company</strong><a href="/about/">Company</a><a href="/investors/">Investors/Ecosystem</a><a href="/contact/">Contact</a></nav>
   <nav aria-label="Legal"><strong>Legal</strong><a href="/trust/">Trust &amp; Security</a><a href="/privacy/">Privacy</a></nav>
   <nav aria-label="Separate ventures"><strong>Separate ventures</strong><a href="https://trustfield.ca/" rel="noopener noreferrer">TrustField ↗</a></nav>
  </div>
  <div class="nf-corp-wrap nf-corp-footer__base"><span>© 2026 Noetfield Systems Inc.</span><span>Evidence before claims.</span></div>
 </footer>
</body>
</html>"""


def corp_page_open(
    title: str,
    desc: str,
    canonical: str,
    active: str,
    *,
    body_class: str = "nf-corp nf-corp--inner",
    og_image: str = "https://www.noetfield.com/assets/social/noetfield-corporate-v2.png",
) -> str:
    return (
        corp_head(title, desc, canonical, og_image=og_image)
        + f'\n<body class="{body_class}">\n <a class="nf-skip" href="#main">Skip to main content</a>\n'
        + corp_header(active)
        + '\n <main id="main">\n'
    )


def corp_page_close() -> str:
    return "\n </main>\n" + corp_footer()
