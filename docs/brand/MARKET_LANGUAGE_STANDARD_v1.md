# Noetfield Market Language Standard — v1
**Date:** 2026-11-16
**Status:** Founder-approved P0 customer-facing language standard; technical identifiers stay stable
**Scope:** Noetfield corporate web, public product pages, sales, onboarding, community, investor materials.
**Authority:** Preserve the Founder-locked Noetfield App V4 product scope and all technical contracts; this document standardizes *communication*, not ownership or product architecture.

## Rule
**Familiar category first. Clear benefit second. Brand identity third.**

A first-time visitor must understand (1) what the product is, (2) who it serves, and (3) what they can do next in five seconds. Prioritize the vocabulary buyers already use, not bespoke architecture nouns. A term can remain in source code, SDKs, contracts, API routes and advanced technical docs even if it disappears from top-level marketing.

## Corporate and product hierarchy
- **Noetfield Systems:** Canadian technology company; AI software creation, business automation and real-world asset infrastructure. No implied enterprise customer count or licensing.
- **Noetfield App:** **AI Software Builder** / **AI App Development Platform** — the Founder-locked core customer product for creating, editing, testing and publishing software; accurately distinguish shipping capabilities from roadmap.
- **Company OS:** **AI Business Operations Platform** — a commercial service/product layer for workflows, AI agents, existing systems and managed operations. Product name may remain secondary.
- **Real-World Capital:** **Tokenization Technology & Asset Operations** / **Digital Asset Infrastructure Services**, not a generic exchange or licensed marketplace.
- **RWA Clinic:** **Tokenization Feasibility Assessment** / **Asset Readiness Assessment**, with private-credit-specific depth where applicable.
- **Community / founding:** **Early Access**, **Founding Members**, **Join the Community**, **Get Product Updates** — describe the actual rights and benefits; no implied token allocation.

## Technical-to-market mapping (context matters)
| Legacy / internal expression | Customer-facing expression | Notes |
| --- | --- | --- |
| Motor | AI execution service, workflow engine, or automation | Do not blindly rename classes or interfaces; choose by capability |
| Runway | AI workflow, task automation, or supported use case | Existing `/runways/` URL remains intact |
| Runtime | Execution infrastructure (developer documentation); usually omit in sales copy | Technical term is valid |
| AgentOS | AI agent platform / agent management | Keep proprietary identity in implementation docs |
| WorkforceOS | AI workforce management | Distinguish people and AI agents |
| WorkPacket | Task / Job / Workflow | Preserve IDs and receipts |
| Company Floor | Operations Dashboard | If the capability is actually an operations dashboard |
| Verifier / receipt | Results verification / execution record / audit trail | Never imply independent external certification |
| Fieldwork | CRM / Sales Pipeline / Relationship Management | Fieldwork is an internal product name |
| Clinical gates / verdict | Assessment criteria / readiness results | Keep technical labels in expert views |
| Asset passport | Asset record / asset information | Define legal rights precisely |
| Onchain | Blockchain integration / digital asset services | Use 'onchain' for a crypto-native audience where helpful |
| Genesis / Season 0 | Early Access / Founding Members | Venture-specific token or loyalty mechanics must remain accurately described |
| Venture Cell | Venture Studio / Startup Development | Do not imply funding or incorporation before it happens |

## Three layers of language
1. **Public:** Plain-English category, outcome, user type and working CTA.
2. **Product:** Familiar UI: Projects, Apps, Agents, Workflows, Tasks, Integrations, Activity, Results, Billing, Settings, Community.
3. **Developer / internal:** Runtime, model routing, schedulers, job IDs, verification receipts, WorkPackets, contract names, existing legacy symbols.

## Reference copy (suggested, not proof of shipped feature)
Corporate: **AI Software and Business Infrastructure.**
Supporting: **Build software, automate business operations, and explore digital infrastructure for real-world assets.**
Noetfield App: **Build and launch software with AI.**
Company OS: **Bring AI agents and business workflows into daily operations.**
Real-World Capital: **Explore tokenization feasibility and digital asset infrastructure for real-world businesses.**
Community: **Join the early community. See what's available, contribute feedback, and follow product releases.**

## Required migration approach
1. Inventory exact live pages and current repository sources; distinguish production from staging.
2. Replace high-friction terms in SEO titles, descriptions, H1, navigation, CTAs, onboarding and sales copy first.
3. Do **not** bulk-rename API routes, repositories, package names, event types, database fields, signed receipts or pinned contracts.
4. Maintain current URLs and add redirects only when explicitly changing public route strategy.
5. Preserve honest capability statuses: live, internal demo, preview, planned; and separate real outcomes from synthetic evidence.
6. Align corporate, App, Company OS and RWA landing pages, plus `llms.txt`, structured data, social previews and community invitations.
7. Run HTML/link regression checks, mobile/desktop inspection and actual production readback before claiming deployment.
8. Review wording through customer comprehension tests: 'what is it?', 'what can I do?', 'why should I trust it?', 'what next?'

## Community-first GTM
Promote useful, publicly accessible product examples and clear low-friction entry points before proprietary architecture. Start with **Try**, **Explore a Demo**, **Join Early Access**, **Talk to Us** or **Request an Assessment** only where each linked experience actually works. No compulsory wallet connection for ordinary early-access interest, no implied rewards or token issuance, and no vanity metrics.

## Acceptance
- All main public navigation and hero labels use recognized market categories.
- No new invented term becomes the first explanation of a product.
- Existing technical identifiers remain backwards compatible.
- Core AI Software Builder scope is not demoted by the corporate/RWA narrative.
- Every visible CTA resolves to a working experience and uses truthful statuses.
- Company website, App, RWA and community copy tell a consistent but non-conflated story.
