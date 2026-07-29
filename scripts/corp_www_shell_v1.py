"""Shared corporate www shell — canonical domain v2 (warm paper / editorial)."""
from __future__ import annotations

CORP_CSS_VER = "4"
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
    ("system", "/system/", "System"),
    ("applications", "/applications/", "Applications"),
    ("evidence", "/proof/", "Evidence"),
    ("program", "/public-interest/", "Program"),
    ("company", "/about/", "Company"),
    ("contact", "/contact/", "Contact"),
)

CLIENT_ZERO_URL = "https://app.noetfield.com/"
CLIENT_ZERO_LABEL = "Open client-zero alpha"
GITHUB_URL = "https://github.com/Noetfield-Systems/Noetfield"
TRUSTFIELD_URL = "https://trustfield.ca/"
TRUSTFIELD_BOUNDARY_LINE = (
    "TrustField is a separate venture whose synthetic regulated-workflow "
    "demonstrations provide a bounded validation context; it is not a "
    "Noetfield Systems Inc. product or subsidiary."
)
TRUSTFIELD_SHORT = "separate venture"


def corp_head(
    title: str,
    desc: str,
    canonical: str,
    *,
    theme: str = "#f3f0e9",
    extra_css: str = "",
    og_image: str = "https://www.noetfield.com/assets/social/noetfield-corporate-v2.png",
    include_intake: bool = True,
) -> str:
    intake_block = INTAKE_SCRIPTS if include_intake else ""
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
{intake_block}
</head>"""


def _nav_link(key: str, href: str, label: str, active: str | None) -> str:
    current = ' aria-current="page"' if active == key else ""
    return f'<a href="{href}"{current}>{label}</a>'


def corp_header(active: str | None = None) -> str:
    links = "".join(_nav_link(k, h, l, active) for k, h, l in NAV_ITEMS)
    return f""" <header class="nf-corp-header">
  <div class="nf-corp-wrap nf-corp-navrow">
   <a class="nf-corp-brand" href="/" aria-label="Noetfield Systems home">
    <span class="nf-corp-brand__mark" aria-hidden="true">N</span>
    <span>Noetfield Systems <small>Inc.</small></span>
   </a>
   <nav class="nf-corp-nav" aria-label="Primary navigation">
    {links}
    <a class="nf-corp-nav__cta nf-corp-nav__alpha" href="{CLIENT_ZERO_URL}" rel="noopener noreferrer">{CLIENT_ZERO_LABEL}</a>
   </nav>
  </div>
 </header>"""


def corp_footer() -> str:
    return f""" <footer class="nf-corp-footer">
  <div class="nf-corp-wrap nf-corp-footer__grid">
   <div>
    <a class="nf-corp-brand nf-corp-brand--footer" href="/"><span class="nf-corp-brand__mark" aria-hidden="true">N</span><span>Noetfield Systems <small>Inc.</small></span></a>
    <p>Governed AI execution infrastructure.<br />Vancouver, British Columbia, Canada.</p>
   </div>
   <nav aria-label="Footer"><strong>Company</strong><a href="/investors/">Investors / Ecosystem</a><a href="/trust/">Trust &amp; Security</a><a href="/privacy/">Privacy</a><a href="/contact/">Contact</a><a href="{GITHUB_URL}" rel="noopener noreferrer">GitHub ↗</a></nav>
   <nav aria-label="Separate ventures"><strong>Separate ventures</strong><a href="/applications/trustfield/">TrustField boundary</a><a href="{TRUSTFIELD_URL}" rel="noopener noreferrer">trustfield.ca ↗</a></nav>
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
    extra_css: str = "",
    include_intake: bool = True,
) -> str:
    return (
        corp_head(
            title,
            desc,
            canonical,
            og_image=og_image,
            extra_css=extra_css,
            include_intake=include_intake,
        )
        + f'\n<body class="{body_class}">\n <a class="nf-skip" href="#main">Skip to main content</a>\n'
        + corp_header(active)
        + '\n <main id="main">\n'
    )


def corp_page_close() -> str:
    return "\n </main>\n" + corp_footer()


def status_rail() -> str:
    return """<div class="nf-status-rail" role="list" aria-label="Company status vocabulary">
  <span class="nf-status nf-status--live" role="listitem">LIVE</span>
  <span class="nf-status nf-status--demonstrated" role="listitem">DEMONSTRATED</span>
  <span class="nf-status nf-status--commissioning" role="listitem">COMMISSIONING</span>
  <span class="nf-status nf-status--planned" role="listitem">NOT YET ESTABLISHED</span>
</div>"""
