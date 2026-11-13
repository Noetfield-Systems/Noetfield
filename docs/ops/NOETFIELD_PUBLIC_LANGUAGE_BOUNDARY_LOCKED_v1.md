# NOETFIELD PUBLIC LANGUAGE BOUNDARY — LOCKED v1.0

**Owner:** Founder, Noetfield Systems Inc.  
**Status:** Binding brand and product rule for Noetfield's public website and its agent/release workflows.  
**Applicable production surface:** `https://www.noetfield.com/`, `https://noetfield.com/`, and the exact Cloudflare Pages `www-pages-dist` release.

## 1. The public corporate website is English-only

Every public, customer-facing Noetfield page, navigation link, onboarding form, CTA, SEO alternate, public chat interface and language selector must display **English only**. Do not add Persian or any other non-English language option, alternate-language link, translated Noetfield Connect page, query-string language switcher, or link to a translated copy of the corporate experience. The same rule applies to public pages about Noetfield Connect, WorkforceOS, product offerings and partnerships when served from the Noetfield corporate public web release. User-submitted content is not automatically equivalent to Noetfield-authored public marketing copy.

## 2. The Founder's private workspace is a different audience and boundary

The authenticated, operator-only Founder Desk is an internal tool. Its interface **may be English, Persian, bilingual, or localized in another language**. Do not extend the corporate marketing language restriction to that private workspace. Keep its authentication, tenant isolation and permission checks intact. A page available without authentication is not a private Founder Desk merely because it is labelled “internal”; sensitive content must remain behind the existing operator session boundary.

Do not reclassify a private operator interface as a public corporate marketing page, and do not delete internal translation support on the pretext of public branding.

## 3. Independent non-English outreach satellites are permitted

A **separately registered and hosted domain** for the Persian-speaking community is optional. It may serve Persian-only **or bilingual Persian/English** experiences (including Connect or community outreach) and may link **to the canonical English site** (`https://www.noetfield.com/connect/`). It is an independent audience-specific satellite, not a localized version or alternate-language entry point of the authoritative Noetfield corporate website. Its existence must not alter the primary international brand, English-only corporate release, or the site's language controls. Build and promote this satellite only when it serves a concrete Persian-speaking audience need; **no launch requirement, default promotion, extra infrastructure, or pressure to market it** is implied.

**One-way relationship:**

`Independent Persian satellite → Noetfield English public site` is allowed.

`Noetfield English public site → Independent Persian satellite` is prohibited.

The satellite must be isolated from the `www-pages-dist` corporate release and not appear in the primary site's navigation, footer, alternate/hreflang tags, sitemap language variants, public chatbot CTAs, or any other page link. Once a separate satellite hostname exists, register it in the outbound language-host deny policy and test the one-way rule. Do not invent a hostname or claim it is live before DNS and deployment verification.

## 4. Enforcement

`scripts/verify-public-output-allowlist.py` is the existing public-release gate. It must reject non-English public locale links, non-English `lang` or `hreflang` markers, visible Persian/Arabic script in first-party public HTML, and active public translation links. It must not scan or reject private Founder Desk source solely for containing Persian text.

No new scheduler, governance service or language-switching framework is needed. Extend the existing artifact verification and CI, do not create a parallel pipeline.

## 5. Cases

| Surface | Persian UI | Links to English Noetfield | Links from English Noetfield |
| --- | --- | --- | --- |
| `www.noetfield.com` public pages | **Never** | Native page | **Never** to any non-English Noetfield version |
| Private authenticated Founder Desk | **Allowed** | Allowed | Not a public language-switch target |
| Independently hosted Persian community satellite (Persian-only or bilingual) | **Allowed** | **Allowed** | **Forbidden** |
| Independent, separately owned ventures | Venture-specific | Case-by-case | No implied subsidiary or data ownership |

**Conflict rule:** The stricter English-only public rule applies to the corporate website. The private/satellite exceptions must not be deleted or overridden by a blanket company-wide English-only interpretation.
