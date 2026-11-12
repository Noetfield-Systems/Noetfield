# Noetfield Connect — Opportunity OS v1

Status: IN PROGRESS (2026-11-12). Implementation owner: Noetfield Systems Inc.

## Goal
Turn credible LinkedIn, email, partner, founder, investor, customer, distribution, award and event inquiries into one Noetfield-owned, attributable, source-backed pipeline: contact -> qualification -> right venture -> human / AI owner -> action -> outcome. Visitors should not be required to book an external Calendly call before submitting. Do not replace WorkforceOS, Company OS, CRM or Sina Founder OS.

## Boundaries and reuse
- Public Connect at /connect/ owns the easy guided visitor experience. Site /api/intake persists the raw source, not the browser itself.
- Existing CRM kernel owns Noetfield person / organization / relationship / opportunity records once connected; no parallel CRM.
- Company OS owns scoped internal tasks. Agent Fabric owns real model inference. WorkforceOS provides customer-facing AI and human teams. Sina Founder OS remains Founder-private.
- BuildRelay is an independent network; cross-project handoff requires explicit purpose. TrustField is an independent venture in formation, not a Noetfield subsidiary.
- Do not treat a form submission as a booked call, an accepted partnership, a qualified customer, a confirmed award, or revenue.

## First release (implemented in branch)
The public Noetfield Connect page supports:
1. Intent: partnership / growth / capital / people / events / business / other.
2. Relevant project / venture including portfolio-wide and unsure.
3. Proposal title, description, optional URL, deadline and commercial terms.
4. Contact, organization, preferred next step (async / request conversation / referral / collaboration).
5. Source-tagged metadata (source/UTM campaign), a unique per-submission idempotent RID and stored-intake-only success confirmation.
6. Reuse of the existing POST /api/intake and existing operator inbox rather than another DB.
Source links may look like /connect/?type=events&source=linkedin. Avoid LinkedIn scraping or unauthorized messaging automation.

## Canonical opportunity data contract for next wave
Source IDs: intake_id, request_id, source_ref, received_at, source_type, consent.
Identity: person_id, organization_id, relationship_id, interaction_refs (each under actual tenant authority).
Scope: company_id, product_id, tenant_id, venture_id, related_project; cross-tenant export is opt-in.
Business: opportunity_type, offer, ask, value, terms, fees, deadline, owner, priority score and evidence, stage, last-contact date, next_action and due date.
Execution: workpacket_id, actual agent run IDs, human contributor IDs, outcome refs, meeting confirmed (not merely requested), cash collected (external payment proof only).
Stages: NEW / QUALIFYING / ROUTED / ENGAGED / NEGOTIATING / PILOT / WON / LOST / ARCHIVED. Waiting-for-Founder or waiting-for-external are issue states, not global runtime blocks.

## Future authenticated routing
Persisted /api/intake -> idempotent CRM reconciliation keyed by intake_id -> bounded Company OS event + owner assignment + task -> optional Agent Fabric research and qualification -> operator review -> actual follow-up. Reuse existing Company OS source-scoped ingestion and outbox retry. Never let public visitor data grant internal agent authority. Do not send unscoped personal details to broad AI event streams.

Routing playbooks:
- events: verify organizer/selection criteria/costs, compare relevance, determine whether award is merit recognition or paid marketing; output decline/request details/review.
- capital: distinguish real investor versus paid intermediary; find stage/geography/terms fit and introduction opportunities.
- growth: inspect referral economics, partner reach and legitimate buyers.
- partnership: mutual distribution, integration scope, co-build outcome and responsible owner.
- people: skill match / availability / venture fit; invitation to WorkforceOS or BuildRelay only with consent.
- business: actual problem, fit with Noetfield delivery and real sales/pilot proposal.

Initial priority rubric: strategic fit 25; likely commercial value 20; capability/distribution relevance 20; concrete next action and deadline 15; evidence and credibility 10; network value 10. Penalize unsupported claims and undisclosed advance fees; save score rationale. Use real Agent Fabric inference or label outputs rule-derived.

## Verified calendar boundary
A request to meet is not a booking. Only offer confirmed slots after real company-controlled calendar/free-busy, selected timezone and explicit booking confirmation are connected. Do not force an inbound proposer to book a call. Book only when useful.

## Measurable results
Persisted submissions, deduplicated people and organizations, opportunities qualified, actual introduction accepted, replies, confirmed meetings, signed deals, referral partners, paid pilots, true collected revenue. Keep test fixtures separately labeled.

## Follow-on gates
P0: current frontend, site deploy, real test intake and readback.
P1: durable CRM enrichment, owner / next action, existing Company OS triage and qualified follow-up.
P2: WorkforceOS human + AI collaborator assignment, optional BuildRelay introduction path, owned calendar scheduling.
P3: relationship graph, warm-introduction routing, economics, portfolio learning.

No code merge, static test, or 200 HTML response alone proves a complete operational pipeline.