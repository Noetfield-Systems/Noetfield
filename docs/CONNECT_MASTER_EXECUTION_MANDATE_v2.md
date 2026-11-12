# NOETFIELD CONNECT — UNIVERSAL RELATIONSHIP & OPPORTUNITY EXECUTION OS

Version: 2.0 — Founder-Authorized Master Implementation Mandate  
Owner: Founder, Noetfield Systems Inc.  
Canonical public entry: https://www.noetfield.com/connect/  
Code owners: Noetfield public site + Platform API; existing deployed Business OS Core; Sina Founder OS, WorkforceOS, Agent Fabric, Company Floor, and independent venture adapters as authorized.  
Execution contract: DISCOVER → INGEST → IDENTITY → QUALIFY → MATCH → ACT → VERIFY → FOLLOW UP → LEARN → MONETIZE.

**THIS IS AN IMPLEMENTATION MISSION. NOT A PRESENTATION, CONSULTING DELIVERABLE, CRM MOCKUP, OR RESEARCH-ONLY TASK.**

## 0. Founder thesis, scope, and precedence

Create a world-class relationship-to-execution network and operating platform for **all professional relationships**, starting with LinkedIn and Noetfield inbound opportunities. Every meaningful connection should receive an appropriately scoped path to an outcome: customer, collaborator, founding teammate, investor introduction, channel partner, supplier, implementation partner, human/AI contributor, conference, award, research, grant, procurement lead, press contact, or ecosystem participant.

Two-way value creation is mandatory. A person may offer funding, distribution, introductions, advice, services, or labor; the system must also discover what Noetfield or an opted-in ecosystem participant can offer that person. **One person is not one lead**: a Person can hold many identities, roles, relationships, offers, asks, and opportunities over time.

Do not convert every message into a sales opportunity, push every visitor into a paid Noetfield diagnostic, send people to an external Calendly by default, or subsume distinct ventures into one legal entity. Stop misclassifying human relationships as "AI agent" or "customer" simply because these labels already exist in the system.

Commercial priority: qualified opportunities, activated users, real collaborations, successful referrals, completed deliverables, signed engagements, and verified collected cash. Record actual commercial outcomes separately from hypotheses and internal activity. Use the fastest legal and technically sound path to paid business. Avoid unnecessary approval loops and duplicate infrastructure.

## 1. Read canonical context and inventory before edits

Read the applicable AGENTS.md, repo-policy.json, L0 graph memory, Connect v1 contract, Company OS Business Core test suite, deployment environments, and only the specific related code. Locate the already-implemented paths before designing replacements.

Verified working baseline as of 2026-11-12:
- Public /connect/ on the canonical www site, with 3-step wizard and choice of opportunity type, initiative, proposal, terms, contact and next step.
- Existing POST /api/intake through Cloudflare to Platform PostgreSQL. Unique RID/idempotency and canonical intake_id. A synthetic production E2E verified HTML, persistence, duplicate prevention and readback.
- Platform API internal authenticated PII-free Business OS intake feed for external-opportunities.
- Existing Business OS worker/agent role hierarchy, scoped tasks, persisted intake signals, specialist handoff and dashboard.
- Connect opportunity-specific routing and Company OS case records, stages, owner-review role, due date, next action, evidence URL, notes and version-conflict handling.
- WorkforceOS + Postgres service and Agent Fabric components are separately deployed.
- Core system deploys and tests are **not** proof that all external integrations, paid contracts, human contributors and scheduling pathways are end-to-end operational.

Do not re-create these assets or introduce another source of truth. Inspect live deployments and source SHAs, then implement only missing or broken sections.

## 2. Relationship OS domain model

Use a clean distinction between:
- PERSON: human identity, verified owned contact channels, LinkedIn URL only when voluntarily supplied or legitimately obtained.
- ORGANIZATION: company, fund, institution, agency, accelerator, organizer or community; organization role and actual affiliation need evidence.
- AGENT IDENTITY: technical agent/tool contributor with a responsible operator and optionally an A2A Agent Card. Public Agent Cards are discovery evidence, never execution grants.
- RELATIONSHIP: an edge between people or organizations with direction, context, source, consent/scope, last interaction, strength evidence and introduction permissions.
- INTERACTION: an actual message, form, email, meeting, introduction, call, event or activity with timestamp and provenance. Drafts do not count as sent.
- OFFER: what the counterparty can offer, concrete constraints, terms, geography, budget, availability.
- ASK: what the counterparty wants and the action required from us; distinguish from assumptions inferred by AI.
- OPPORTUNITY: explicit potential exchange/value creation, linked to multiple participants and ventures, probability based on facts, due date and accountable owner.
- MATCH: proposed connection between offer, ask, people, teams and initiatives. Suggested is not accepted.
- WORKPACKET: a bounded action requested from a real human or agent and tied to an actual opportunity.
- CONSENT / AUTHORITY: purpose-specific authorization to contact, share, introduce, execute and cross ventures.
- OUTCOME: verified meeting, introduction accepted, collaborator trial, pilot, sale, contract, completed work or declined opportunity, with receipt/source.
- CASH RECEIPT: collected money from Stripe, bank or another permitted verified financial source. Estimated pipeline and promised funds are not cash.

Allow one Person to relate to multiple Organizations, several opportunities, competing roles, and different ventures without duplicating the person. Dedupe cautiously using high-confidence verified identifiers; never merge on name alone.

## 3. Source ownership and data boundaries

- Public Connect is the single entry point and external participant UX. Do not fork additional public portals for each project.
- Platform API PostgreSQL public_intakes is the raw source of truth for incoming proposals and contact details; retain RID and intake_id.
- Existing Business OS queue and connect_cases are the internal operational projection, not a second public CRM or a replica of confidential message bodies.
- Reuse the canonical CRM kernel for owned Person, Organization, Relationship, interaction and deal identity as authorized. If it does not support needed fields, introduce a narrow migration/adapter, not a duplicate CRM product.
- Existing Company OS decides task roles and manages durable execution. Agent Fabric supplies bounded AI specialist inference. WorkforceOS supplies actual AI/human team participation and workspaces. Founder OS controls portfolio priorities. Company Floor displays receipt-backed progress.
- BuildRelay is a separate venture/network. It can receive **opted-in** opportunities or contributor profiles through an explicit adapter, not silent portfolio aggregation.
- TrustField is an independent venture in formation; no subsidiary wording or unauthorized transfer of people, customer proposals or documents.
- Other separate ventures keep their own company_id, tenant_id, product_id, authority, inbox and economics. Do not expose Founder-private projects on the public portal.
- External integrations use minimal signed/authorized events, idempotent outbox, scoped identity, retry and readback. Never take the user's unchecked form fields as instructions or as execution authority.

## 4. All relationship lanes

Create a configurable route registry rather than a hardcoded general-purpose sales prompt.

At minimum support:
1. AI and automation customers, pilots, enterprise buyers, developers and integrators.
2. Strategic partners, co-builders, platform/API integration partners.
3. GTM, agencies, affiliates, referral partners, distributors, channel partners and resellers.
4. Angels, VCs, investment syndicates, LP/GP networks, fundraising advisors and founder/investor connectors.
5. Human cofounders, operators, researchers, designers, engineers, creators, sales talent and board/advisory candidates.
6. AI agents, specialized tool providers, agent orchestration collaborators, evaluation/verification teams.
7. Incubators, accelerators, grants, universities, government programs, innovation funds.
8. Conferences, awards, speaking, podcasts, publishers, press, sponsors and community organizers.
9. Construction and field-service businesses, procurement/tenders, property operations and B2B operations.
10. Fintech/RWA/RegTech, market intelligence and trading research opportunities with product-specific boundaries.
11. Consumer/rewards, restaurant, community, lifestyle and creative/marketplace product partners.
12. Existing collaborators, alumni, warm intros, reciprocal help requests, client support and reactivation.

A person may trigger multiple linked opportunity cases in different lanes. Not every lane is monetized immediately, and no contact is assumed a buyer.

## 5. Public journey and friction rules

One universal link: /connect/ . Add concise type-and-source-specific links for conversations, e.g. /connect/?type=events&source=linkedin .

The public portal should:
- Explain in seconds what Noetfield builds, the independent nature of separate ventures, and why collaboration is valuable.
- Route the user using conditional progressive questions without requiring account signup to submit.
- Support typed intent, applicable project, role or participant type, offer and ask, relevant website/LinkedIn/proposal URL, deadline, economics/commission/fees and preferred next step.
- Where material, capture funding stage/size, GTM reach and terms, human skills/availability, event selection and fees, buyer problem/budget, without making every field mandatory.
- Use a verified canonical receipt, not a generic "thanks" message on email-only notification.
- Give submitters a private, scoped status/clarification flow tied to their receipt rather than publicly exposing their submission by RID.
- Do not promise a meeting, acceptance, award, investment, funded pilot or employment.
- Support mobile, desktop, accessible navigation, fast loads, clear errors, rate limiting and abuse control.
- Add Open Graph previews, search discoverability, credible product proof, and useful category landing sections.

No fake customer logos, testimonials, usage numbers, financing milestones or agent execution.

## 6. Opportunity intelligence and ranking

After a persisted intake:
1. Identity reconciliation: person/organization by appropriate evidence and consent.
2. Category classification: deterministic category and initiative first; AI only to improve ambiguous cases.
3. Research: verify source links, venture fit and relevant external context with citations.
4. Reciprocal offer-ask mapping: what can both parties gain?
5. Alternative lane exploration: sales, partnership, workforce and referrals may coexist without cross-venture data leakage.
6. Evidence and confidence grading: VERIFIED, DOCUMENTED, REPORTED_BY_COUNTERPARTY, INFERRED, UNKNOWN.
7. Recommendation and role routing into the existing specialist hierarchy.
8. Next best action with actual owner, proposed timing and resource cost.
9. Follow-up until outcome, decline, archive or evidence-based reactivation.

Use two separate measures:
- RELATIONSHIP POTENTIAL: trust context, relevance, network leverage, mutual fit, reciprocity.
- OPPORTUNITY PRIORITY: expected *incremental* value, probability of a concrete next milestone, time sensitivity, execution cost, verified evidence and risk-adjusted opportunity cost.

Do not score a nonprofit advisor using customer ACV assumptions, or treat a paid award sales pitch as earned recognition. Each route needs an appropriate economics function and explainable confidence.

Avoid fabricated weighted-pipeline dollars. Use a value range or "unknown" until buyer, scope and terms support a calculation.

## 7. Human and AI workforce execution

For every qualified opportunity:
- Assign an appropriate specialist reviewer from the existing Company OS registry.
- Produce a scoped workpacket with concrete deliverable, evidence, cost/time envelope and acceptance criteria.
- For AI execution, invoke real Agent Fabric/WorkforceOS tools only with current scoped authority and verify actual output.
- For human participation, implement invitations, responsible operator identity, opt-in acceptance, role, agreed scope, task status, output and receipt. A suggested collaborator is never a hired/activated contributor.
- Support hybrid teams, handoffs and independent review, without making the customer navigate internal Company OS complexity.
- Preserve unrelated work when one party fails to respond. "WAITING_EXTERNAL" and "WAITING_FOUNDER" are per-case states, not global workflow stops.
- Allow reasonably safe internal research and drafting to proceed by default; external publishing, payments, commitments and cross-venture information sharing require actual authority.

## 8. Relationship graph and introduction workflows

Build on canonical CRM instead of a second duplicate contact database:
- Person ↔ Organization / current and historical affiliation, trust evidence.
- Person ↔ Person / connected through what context and when, with a permitted introduction path.
- Person ↔ Opportunity ↔ Venture ↔ Workpacket ↔ Outcome.
- Organization ↔ Fund / Accelerator / Event / Community relationships.
- Source references, uncertainty labels and edge validity windows.

For warm introductions, produce a two-sided intro proposal; obtain the relevant person's agreement before transmitting personal details, send through an authorized connected channel, then record acceptance/decline. No invented "mutual connections".

Read/write integration with LinkedIn must use actual permitted API products and user authorizations. LinkedIn permissions are restricted and not a generic inbox/scraping API. Ship now with user-owned portal links, voluntary submitted profiles, safe copy/paste assists, user-initiated share links, and approved email/calendar integrations rather than blocking the business awaiting broad LinkedIn API access.

## 9. Operator / Founder command center

The existing Founder Control Plane should become a coherent **Connect Desk**:
- Unified case inbox, search/filter by type, initiative, stage, person/org (where authorized), source and priority.
- Compact relationship timeline and source-linked opportunity history.
- Owner, next action, due date, evidence, notes and current version. Support edit concurrency.
- A single contact with multiple distinct cases; dedupe and merges with audit trail.
- Task progress, model runs, missing answers, human acceptance and source receipts.
- One-click response drafting, introduction prep, pilot brief and assignment (only where authorized).
- Overdue follow-ups, stalled cases, inbound response gaps and high-value opportunities.
- Event/award assessment: credible organizer, selection mechanism, real pricing, benefits and alternative use of capital.
- Pipeline economics by venture with real cash only from verified payment sources.
- Clear "unverified" display for AI suggestions, alleged partner titles, self-declared revenue or role claims.

The current case ledger and authenticated update endpoint are the starting implementation, not the entire finished graph.

## 10. Event-driven follow-up and autonomous continuity

Use existing Company OS worker, queue, retry and Agent Fabric. Do not add a redundant scheduler or uncontrolled cron.

Define durable events:
connect.intake.persisted, connect.identity.reconciled, connect.case.routed, connect.match.proposed, connect.owner.assigned, connect.followup.due, connect.message.approved, connect.message.sent, connect.introduction.accepted, connect.meeting.confirmed, connect.trial.started, connect.outcome.verified.

Every event has source identity, idempotency key, authorized actor, timestamps, minimal payload, retry state and receipt.

Maintain independent work progress if one opportunity asks Founder a question. Queue the question with proposed answer, evidence and deadline; continue other cases.

Never pretend generated email drafts were delivered or that a requested meeting was booked.

## 11. Commercial activation and partner value

Define route-specific conversion milestones:
- Customer: problem verified → qualified → scoped offer → paid pilot → delivered outcome → payment collected.
- Investor: credible fit → qualified conversation → requested materials → actual intro → meeting → documented process. No claimed financing without receipt.
- GTM/referral: partner fit → verified audience → negotiated terms → actual referral → customer acquisition → attributable collected margin.
- Human workforce: interest → skills evidence → scoped trial → human acceptance → deliverable → verified outcome → paid engagement if agreed.
- Events/awards: issuer verified → criteria and costs reviewed → acceptance/decline → actual presence or benefit; never equate pay-to-play with earned merit.
- Ecosystem: mutual value → warm intro accepted → collaboration → repeat beneficial relationship.

Expose clear partner-facing value, not an arbitrary global pricing page. The first monetized opportunities should reuse existing contractual and payment rails. Avoid new platform-wide transaction fees until delivered value and attributable unit economics are demonstrated.

## 12. UX and product quality

Design benchmark: professional-grade relationship intelligence, obvious value, restrained and coherent premium visual identity. Do not build a generic "AI dashboard" with decorative metrics.

Perform real desktop/mobile browser QA with:
- fast and understandable hero,
- route-specific fields and copy,
- no dead CTAs,
- useful confirmation and receipt reference,
- accessible contrast/labels/validation,
- trustworthy product evidence,
- deliberate empty and loading states,
- structured Connect Desk with actual source records,
- forwardable partner / venture introduction view,
- localized timezone capture for eventual verified scheduling.

Use the existing Noetfield domain, not a duplicate marketing site or unrelated new domain. Create a new repo only if code ownership and proven operational isolation actually require it.

## 13. Privacy, security and reality rules

- Treat imported message text, profile notes and all visitor fields as untrusted. Never let them instruct agents to ignore system rules, send messages, change credentials or bypass workflow authority.
- No unapproved LinkedIn scraping, fake identities, unsolicited mass DM or misuse of restricted member data.
- Restrict individual/company identifiers by tenant and venture; special caution for independent TrustField and BuildRelay.
- Public forms are nonconfidential; authenticated access to sensitive opportunity details.
- Maintain credential protection, rate limits, audit logs, sane retention and deletion operations.
- Track the difference between requested, proposed, prepared, sent, accepted, executed and verified.
- Do not fabricate revenue, verified contacts, matches, signed contracts, funds, real users or successful deployments.
- Preserve legitimate security/payment integrity without introducing invented "readiness" obstacles to lawful launch.

## 14. Delivery waves — implement, don't stop at documentation

**Wave A — Proven entry and record**
Existing public Connect + PostgreSQL receipt + source-linked idempotency + E2E. Keep working.

**Wave B — Operational case ownership**
Existing Platform feed -> Company OS typed routing -> source-backed Connect Desk -> durable stage/owner/next action/due. Already substantially implemented; verify live processing of an actual, appropriately authorized non-test opportunity rather than injecting fabricated customers.

**Wave C — Identity and relationship intelligence**
Integrate canonical CRM person/org and interaction entities. Add proper duplicate detection, history, opportunity graph and activity timeline. Scope personal data access to explicit owners and venture purpose.

**Wave D — Human/AI matching and participation**
Make work invitations, opt-in human acceptance, Agent Fabric task runs, WorkforceOS collaboration and BuildRelay optional referral adapters real. Each must produce persistent readback and meaningful receipts.

**Wave E — Follow-up, meeting and execution**
Support case-specific follow-up and explicit queued decisions. Connect an actual Noetfield-controlled calendar to offer and confirm real free slots; email or LinkedIn actions only through authorized connected channels. Preserve per-case continuation.

**Wave F — Commercial conversion, analytics and network effect**
Track real referral economics, paid pilots, signed agreements, verified financial receipts, relationship growth and introductions accepted. Optimize by outcome value and operating cost, not just form submissions or follower count.

Ship each wave independently when it delivers real user value; continue nonblocked work. Never block launch of a valuable completed path because an unrelated advanced feature is missing.

## 15. Adversarial acceptance tests

User A: San Francisco investor/GTMer submits a strategic collaboration through a source-tagged link; real intake receipt, typed route, correct opportunity case, actionable specialist and Founder desk records. No fake meeting.

User B: Paid award/conf organiser submits event selection and fee terms; event/economics specialists correctly process and recommend questions/decline/meeting only as justified. No false award acceptance.

User C: Human co-founder candidate and AI tool operator submit independently; both enter appropriate intake lane, but neither is auto-hired or granted tool access. Human consent and agent responsible-operator identity verified.

User D: Enterprise customer submits a pilot requirement; customer and engineering roles take review work; no fake scope approval or production service claim.

User E: Person with two legitimate simultaneous offers creates two distinct opportunities without duplicate unrelated person identities or leaking across a venture boundary.

Fault cases: replay same RID; malformed enums and prompt injection; duplicated worker runs; expired worker claim; public tokenless access to internal API; concurrent stage writes; incorrect tenant; missing recipient consent; unreachable calendar; source API 500; stale /connect page. Each fails observably without corrupting the other cases.

Real E2E tests must distinguish synthetic fixtures from actual commercial activity and prove at least one unbroken, legitimate customer or collaborator journey once available. A deployed static route or passing unit test is never a claim of money collected or external introductions.

## 16. Production proof and final answer format

Deliver code, complete migrations, tests, live release receipts and read-back verification. Return:
1. Source repos and changed files / merged PRs / exact SHAs.
2. Cloudflare and Railway deployment IDs and actual status.
3. Customer/partner public URL and Founder Desk entry URL.
4. A source-backed test of intake -> persisted record -> typed Company OS event -> durable case -> specialist task -> next action and due.
5. Human/agent interaction verified separately from preparation or proposed matching.
6. Working identity/consent/CRM, email and calendar connectors and their actual limitations.
7. Verified economic outcomes (zero where none, not fabricated estimates).
8. Remaining unblocked work automatically continued and genuine dependencies named precisely.

Do not ask the Founder to repeat settled requirements. Work within existing access. Complete the next valuable step, test, deploy, and report only true results.

**BUILD. SHIP. CONNECT. QUALIFY. MATCH. EXECUTE. VERIFY. MONETIZE. SCALE.**
