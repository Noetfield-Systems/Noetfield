<!-- ADVISOR_ARCHITECT_CHECKLIST_STUB (auto-inserted) -->
Advisor / Architect Minimal Checklist (AUTO-STUB)
-----------------------------------------------

- protects: Which founder goal does this protect? (pick one)
- sina_workload: reduces / increases + short rationale
- permission_loop: yes / no + explanation
- sandbox_autonomy: yes / no + where/how (sandbox lane path)
- target_to_blocker: yes / no + mitigation
- canon_version: (string)
- sandbox_evidence: link(s) to sandbox receipt(s)

# Investor governance checklist map (v1)

**Audience:** VC associates, PE operating partners, corp dev — diligencing a **target** with Copilot/M365 or “enterprise AI governance” claims.

**Orientation only.** Not legal advice. Structure aligns with common 2026 VC governance questionnaires (see [AI Policy Desk 18-item checklist](https://www.aipolicydesk.com/blog/vc-ai-governance-due-diligence-checklist-2026) as external reference).

## Group 1 — Policy and documentation

| # | Investor asks for | Noetfield artifact | Honest gap |
|---|-----------------|------------------|------------|
| 1 | Written AI acceptable-use policy | Trust Brief → policy map orientation | Target must produce signed AUP |
| 2 | AI system inventory | Trust Brief materiality map; TLE cover metadata | Full vendor register = target-owned |
| 3 | DPAs for AI tools processing personal data | Connectors / evidence intake orientation | Target legal must hold DPAs |
| 4 | AI incident response procedure | Evaluate → record → export spine (orientation) | Target IR playbook required |
| 5 | Employee AI training records | — | **Out of scope** — HR-owned |

## Group 2 — Bias, fairness, and harm

| # | Investor asks for | Noetfield artifact | Honest gap |
|---|-----------------|------------------|------------|
| 6 | Bias testing before deployment | — | **Out of scope** — model/HR vendors |
| 7 | Demographic impact analysis | — | **Out of scope** |
| 8 | Human review for high-stakes outputs | TLE samples — confidence score, approver chain | Target must operationalize |
| 9 | User feedback mechanism | — | Product-owned |
| 10 | Third-party red-team / audit | — | Refer specialist; not Noetfield |

## Group 3 — Data and IP

| # | Investor asks for | Noetfield artifact | Honest gap |
|---|-----------------|------------------|------------|
| 11 | Training data provenance | Metadata-only fence (orientation) | Legal + tech DD |
| 12 | No unlicensed training data | — | Counsel sign-off required |
| 13 | Customer data not used to train vendor models | RPAA-safe / vendor positioning orientation | Target reviews M365/vendor terms |
| 14 | IP ownership of AI outputs | — | Legal analysis required |

## Group 4 — Regulatory exposure

| # | Investor asks for | Noetfield artifact | Honest gap |
|---|-----------------|------------------|------------|
| 15 | EU AI Act risk classification | Playbook EU AI Act + framework orientation | Not certification |
| 16 | GDPR/CCPA vendor DPA checklist | Procurement pack + privacy cross-links | Target legal owns list |
| 17 | EEOC / hiring AI review | — | **Out of scope** unless hiring AI in scope |
| 18 | Ongoing regulatory monitoring | Trust Ledger cadence orientation | Target owns monitoring program |

## Noetfield deliverables for buy-side engagements

| Artifact | Location |
|----------|----------|
| Trust Brief (6-week diagnostic) | `/trust-brief/` |
| TLE v1 samples | `/trust-ledger/sample-report/` |
| Engagement / procurement pack | `/gate/procurement/procurement-pack/` |
| IC appendix template | This folder — `IC_GOVERNANCE_APPENDIX_TEMPLATE_v1.md` |
| Intake | `/trust-brief/intake/?vector=investor-diligence` |

## Maturity score (artifact-based)

| Level | Signal |
|-------|--------|
| **Exposed** | Copilot claims without inventory or policy map |
| **Documented** | Policies exist but no exportable go/no-go record |
| **Receipt-ready** | TLE-style record with approvers + evidence index |
| **Architected** | Shadow evaluate + board PDF + procurement export path |

See [IC_GOVERNANCE_APPENDIX_TEMPLATE_v1.md](./IC_GOVERNANCE_APPENDIX_TEMPLATE_v1.md) for IC memo structure.
