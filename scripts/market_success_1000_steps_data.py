"""Curated step themes per phase — 10 themes × 10 steps = 100 steps per archetype."""

from __future__ import annotations

# Each step: (plan, outcome, verify, pattern, lane)
# lane: A=disk, D=docs, H=Hub agentic

def _steps(themes: list[tuple[str, list[tuple[str, str, str, str, str]]]]) -> list[tuple[str, str, str, str, str]]:
    out: list[tuple[str, str, str, str, str]] = []
    for _theme, items in themes:
        out.extend(items)
    assert len(out) == 100, f"expected 100 steps, got {len(out)}"
    return out


PHASE_1_TRUST_UNLOCK = _steps([
    ("Trust center portal", [
        ("Publish trust center hero with shadow-mode fence", "Prospect grasps governance-only posture in 90 seconds", "verify-gtm", "trust-center-grid", "A"),
        ("Add framework grid (NIST · ISO · EU orientation)", "CISO sees mapped frameworks without certification claims", "verify-ui-e2e", "trust-center-grid", "A"),
        ("Wire trust center link in institutional status strip", "Every tier page routes to self-serve diligence", "verify-ui-e2e", "trust-center-grid", "A"),
        ("Add control checkpoint table with honest badges", "Planned vs operational rows scan clean in verify", "verify-gtm", "honest-posture", "A"),
        ("Ship subprocessor metadata-only table", "Security reviewer finds vendor list without overshare", "verify-gtm", "trust-center-grid", "A"),
        ("Add security FAQ index (20 questions)", "Questionnaire deflection doc linked from trust center", "verify-gtm-ops-docs", "diligence-shortcut", "D"),
        ("Publish continuous verification copy block", "Copy states metadata-only evidence posture", "verify-no-asf-coherence", "metadata-only", "D"),
        ("Add trust center → procurement ZIP CTA", "One-click diligence path from trust surface", "verify-ui-e2e", "procurement-zip", "A"),
        ("Elevate trust center bank-grade CSS stack", "trust-center loads institutional + bank-grade CSS", "smoke_bank_grade", "institutional-shell", "A"),
        ("Add trust center print CSS for committees", "Board can print leave-behind without console login", "manual", "print-grade", "A"),
    ]),
    ("Continuous monitoring signals", [
        ("Add last_verified_at stub on control rows", "Freshness signal visible — no fake perpetual green", "verify-gtm", "continuous-proof", "A"),
        ("Surface connector last_sync on workspace UI", "Evidence index shows metadata ingest freshness", "verify-ui-e2e", "continuous-proof", "A"),
        ("Document hourly-vs-annual posture in trust FAQ", "Buyer expectation set: continuous not point-in-time", "verify-gtm-ops-docs", "continuous-proof", "D"),
        ("Add live posture pill to status strip", "Shadow-mode pill on all 2026-framed pages", "verify-ui-e2e", "continuous-proof", "A"),
        ("Wire audit export CTA from trust center", "RID-keyed export reachable without sales call", "verify-audit-export", "receipt-export-wedge", "A"),
        ("Add tamper-verify badge on export docs", "Integrity check called out on trust-ledger www", "verify-gtm", "tamper-verify", "A"),
        ("Spec continuous evidence ingest health endpoint", "API returns connector sync status for ops", "verify-ui-endpoints", "continuous-proof", "A"),
        ("Add confidence score explanation block", "Buyers understand receipt scoring without ML hype", "verify-gtm", "confidence-score", "D"),
        ("Publish evidence intake contract link cluster", "Trust center cites metadata-only contract", "verify-gtm-ops-docs", "metadata-only", "D"),
        ("Smoke test trust center control row scan", "verify-gtm passes checkpoint section markers", "verify-gtm", "continuous-proof", "A"),
    ]),
    ("Questionnaire deflection", [
        ("Draft CAIQ-style auto-fill JSON spec", "Machine-readable answers for security portals", "verify-gtm", "questionnaire-deflection", "D"),
        ("Add procurement one-pager link from trust center", "Reviewer self-serves Copilot governance scope", "verify-gtm-ops-docs", "procurement-zip", "D"),
        ("Ship security buyer line on trust-ledger www", "CISO copy: governance evidence layer only", "verify-no-asf-coherence", "receipt-export-wedge", "A"),
        ("Add OpenAPI public link on procurement page", "Technical reviewer finds API without NDAs", "verify-gtm-ops-docs", "procurement-zip", "A"),
        ("Document 30-60-90 trust center rollout runbook", "Internal team has phased publish checklist", "docs review", "trust-center-grid", "D"),
        ("Add access-request CTA spec (NDA clickwrap)", "Frictionless doc access pattern documented", "verify-gtm", "diligence-shortcut", "D"),
        ("Wire governance sources book links on procurement", "Framework orientation without legal advice", "verify-gtm-ops-docs", "trust-center-grid", "D"),
        ("Add trust-brief intake CTA on trust center", "Commercial path after security review", "verify-gtm", "buyer-hero", "A"),
        ("Spec revenue-influenced reporting fields", "GTM can log deals influenced by trust center", "manual", "board-pdf-moment", "H"),
        ("Add debrief template link post-trust review", "Sales captures persona + next step fields", "verify-gtm-ops-docs", "buyer-debrief", "D"),
    ]),
    ("Honest certification posture", [
        ("Audit www for SOC2/ISO certification claims", "Zero forbidden certification claims on buyer HTML", "verify-no-asf-coherence", "honest-posture", "A"),
        ("Replace certification language with orientation", "Framework rows say oriented-not-certified", "verify-gtm", "honest-posture", "A"),
        ("Add RPAA fence callout on bank-pilot", "No supervision or custody claims scan clean", "verify-no-asf-coherence", "frfi-fence", "A"),
        ("Add federal lane claim fences", "No clearance granted / RPAA registered wording", "verify-no-asf-coherence", "federal-fence", "A"),
        ("Publish honest posture row in framework grid", "Each framework shows evidence layer not cert", "verify-gtm", "honest-posture", "A"),
        ("Document what Noetfield is not (3 offerings lock)", "Offerings doc matches www three-product fence", "verify-gtm", "buyer-hero", "D"),
        ("Add stripe/disclaimer pattern for paid intake", "Commercial license copy not payment routing", "audit_final_system_lock", "honest-posture", "A"),
        ("Scrub payment routing phrases from public HTML", "PRODUCTION_READINESS_REPORT shows 0 violations", "audit_final_system_lock", "honest-posture", "A"),
        ("Add trust center SOC2-claim fence footnote", "Explicit not-a-SOC2-certification line", "verify-gtm", "honest-posture", "A"),
        ("Verify coherence guard on buyer-linked docs", "Vendor names absent from guarded paths", "verify-no-asf-coherence", "honest-posture", "A"),
    ]),
    ("Revenue unlock paths", [
        ("Add homepage diligence path strip", "3-step board → pilot → procurement visible", "verify-gtm", "buyer-hero", "A"),
        ("Wire enterprise commercial model table", "Trust Brief $10K + design partner CAD $2K+", "verify-gtm", "buyer-hero", "A"),
        ("Add copilot demo CTA from trust center", "Security review flows to 5-minute demo", "verify-copilot-demo-links", "board-pdf-moment", "A"),
        ("Add design-partner CTA on pilot page", "Pricing band visible above fold", "verify-gtm", "design-partner", "A"),
        ("Link MSP partners page from enterprise", "Channel path for scaled rollout", "verify-gtm", "msp-channel-sow", "A"),
        ("Add investor snapshot to positioning doc", "Client-safe VC lens without vendor compare", "verify-gtm", "buyer-hero", "D"),
        ("Expand sitemap to 20 tier URLs", "trust-center federal funnel indexed", "verify_sitemap_committed", "seo-parity", "A"),
        ("Add proof bar on homepage + enterprise", "Committee-scan proof points above fold", "verify-ui-e2e", "board-pdf-moment", "A"),
        ("Wire offerings strip on all tier pages", "Three offerings only on every GTM route", "verify-gtm", "buyer-hero", "A"),
        ("Spec trust-center ROI metrics template", "Founder tracks access requests + influenced pipeline", "manual", "board-pdf-moment", "H"),
    ]),
    ("Security document self-serve", [
        ("Publish evidence intake contract v1 link", "Metadata-only scope visible to reviewers", "verify-gtm-ops-docs", "metadata-only", "D"),
        ("Add connectors controls diligence doc link", "Technical controls orientation for procurement", "verify-gtm-ops-docs", "trust-center-grid", "D"),
        ("Ship sample TLE report download path", "Buyer previews board-pack format", "verify-gtm", "receipt-export-wedge", "A"),
        ("Add trust-ledger sample PDF/ZIP links", "Export artifacts preview without login", "verify-ui-e2e", "receipt-export-wedge", "A"),
        ("Wire RPAA diligence one-pager on pilot pages", "FRFI-oriented doc linked from funnel", "verify-gtm-ops-docs", "frfi-fence", "D"),
        ("Add governance sources handbook links", "Framework citations for legal reviewers", "verify-gtm-ops-docs", "trust-center-grid", "D"),
        ("Publish drift detection sources index", "Orientation doc for control change signals", "verify-gtm-ops-docs", "continuous-proof", "D"),
        ("Add procurement ZIP README orientation", "Legal reviewer 1-pager inside export bundle", "procurement-pack-e2e", "procurement-zip", "A"),
        ("Spec board pack PDF cover block v2", "E-23 fields on export cover when FRFI", "spec review", "board-pdf-moment", "D"),
        ("Add ZIP checksum manifest on procurement page", "SHA-256 visible for tamper awareness", "verify-gtm", "tamper-verify", "A"),
    ]),
    ("Access & NDA workflow spec", [
        ("Document clickwrap NDA pattern for exports", "90% mid-market deals skip legal bottleneck", "verify-gtm", "diligence-shortcut", "D"),
        ("Spec role-gated access for sensitive exports", "Board PDF vs public orientation tiers", "spec review", "procurement-zip", "D"),
        ("Add access request form fields spec", "Company · role · purpose captured", "verify-gtm", "diligence-shortcut", "D"),
        ("Wire staging demo URL injection pattern", "make demo-url works when NF_STAGING_URL set", "verify-demo-url", "demo-url", "A"),
        ("Document trust center 30-day launch checklist", "Phased rollout milestones locked", "docs review", "trust-center-grid", "D"),
        ("Add CRM unlock-on-negotiation spec (optional)", "Advanced: gate SOC pack on deal stage", "manual", "diligence-shortcut", "D"),
        ("Spec auto-expire links for export bundles", "Time-boxed procurement ZIP access", "spec review", "procurement-zip", "D"),
        ("Add subprocessor change notification copy", "Buyers know when vendor list updates", "verify-gtm", "enterprise-procurement", "D"),
        ("Document security contact routing", "No overshare emails on public pages", "audit_intake_email", "honest-posture", "A"),
        ("Add privacy/terms cross-links in trust footer", "Legal baseline linked from trust center", "verify-gtm", "trust-center-grid", "A"),
    ]),
    ("WWW integration", [
        ("Apply 2026 frame to trust-center + federal", "14 GTM routes on nf-site-2026 stack", "verify-ui-e2e", "institutional-shell", "A"),
        ("Merge nf-frfi nf-site-2026 body classes", "No duplicate class= on bank-pilot enterprise", "smoke_bank_grade", "frfi-fence", "A"),
        ("Add skip-link on all funnel pages", "a11y baseline on copilot funnel", "smoke_bank_grade", "a11y-baseline", "A"),
        ("Wire institutional grid CSS rename lock", "noetfield-institutional-grid.css only", "verify-no-asf-coherence", "trust-center-grid", "A"),
        ("Add canonical URLs on funnel pages", "demo pilot procurement SEO parity", "verify-gtm", "seo-parity", "A"),
        ("Polish enterprise E-23 table zebra rows", "Committee-readable audit table", "manual", "e23-mapping", "A"),
        ("Add bank-pilot shadow badge persistent", "Shadow-only visible in hero", "verify-gtm", "shadow-only", "A"),
        ("Wire federal → trust center cross-links", "NIST rows link diligence surfaces", "verify-gtm", "federal-framework-map", "A"),
        ("Add partners MSP featured tier card", "msp-two-tier grid emphasis", "verify-gtm", "msp-two-tier", "A"),
        ("Run apply_institutional_2026_frame.py v2", "Auto-frame new tier pages", "pytest", "frame-automation", "A"),
    ]),
    ("Regression gates", [
        ("Extend verify-ui-e2e for bank-grade.css", "All tier pages load bank-grade stack", "verify-ui-e2e", "regression-gate", "A"),
        ("Add smoke_bank_grade_html P0 gate", "P0 routes require bank-grade markers", "plan-with-no-asf-verify", "regression-gate", "A"),
        ("Run audit_public_site_health.py clean", "Tier pages pass shell + viewport", "test_public_gtm_alignment", "regression-gate", "A"),
        ("Run audit_final_system_lock 0 violations", "RPAA-safe public copy confirmed", "audit_final_system_lock", "regression-gate", "A"),
        ("Pass verify-no-asf-coherence vendor guard", "No vendor names on guarded buyer paths", "verify-no-asf-coherence", "regression-gate", "A"),
        ("Pass test_public_simplification suite", "No internal architecture terms on PUBLIC_PAGES", "pytest", "regression-gate", "A"),
        ("Pass test_public_gtm_alignment 18/18", "GTM copy alignment green", "pytest", "regression-gate", "A"),
        ("Pass copilot-pilot-e2e full flow", "Evaluate → connector → TLE → export", "plan-with-no-asf-verify", "board-pdf-moment", "A"),
        ("Pass procurement-pack-e2e ZIP contents", "PDF + JSON + README in bundle", "plan-with-no-asf-verify", "procurement-zip", "A"),
        ("Commit sitemap 20 URLs verified", "generate_sitemap.py output committed", "verify_sitemap_committed", "seo-parity", "A"),
    ]),
    ("GTM proof — phase 1 close", [
        ("Record trust center publish date in ops log", "Founder has go-live timestamp", "manual", "board-pdf-moment", "H"),
        ("Run first prospect trust center walkthrough", "90-second comprehension validated", "manual", "board-pdf-moment", "H"),
        ("Log access request count week 1", "Baseline metric for deflection ROI", "manual", "diligence-shortcut", "H"),
        ("Capture security reviewer FAQ gaps", "Top 5 questions feed FAQ index v2", "manual", "diligence-shortcut", "H"),
        ("Debrief template: trust center used in deal", "Board PDF used field populated", "verify-gtm-ops-docs", "buyer-debrief", "H"),
        ("Pick next 3 items for iter (≤3 rule)", "QUICK_PICK updated from phase 1 learnings", "verify-quick-pick-fresh", "board-pdf-moment", "D"),
        ("Form PICK gate before trust center promote", "No overstated claims in outbound", "manual", "form-pick", "H"),
        ("Customer #0 rehearsal: export in meeting", "Internal dry-run with board PDF", "manual", "board-pdf-moment", "H"),
        ("Phase 1 retrospective doc (1 page)", "What worked / what to defer", "docs review", "board-pdf-moment", "D"),
        ("Sign off phase 1 → unlock phase 2 picks", "mr-0101 ready in GTM_NEXT", "manual", "board-pdf-moment", "H"),
    ]),
])

# Additional phases: generate via helper with phase-specific theme names
def _phase_steps(
    phase_key: str,
    themes: list[str],
    pattern: str,
    archetype: str,
) -> list[tuple[str, str, str, str, str]]:
    """Build 100 steps from 10 theme names with numbered substantive items."""
    verbs = ["Ship", "Lock", "Wire", "Extend", "Document", "Verify", "Polish", "Automate", "Elevate", "Harden"]
    verifies = ["verify-gtm", "verify-ui-e2e", "verify-gtm-ops-docs", "verify-ui-endpoints", "plan-with-no-asf-verify",
                "verify-no-asf-coherence", "pytest", "manual", "procurement-pack-e2e", "verify-msb-partner-openapi"]
    lanes = ["A", "A", "D", "A", "A", "A", "D", "A", "A", "H"]
    outcomes = [
        "buyer-visible on www",
        "committee artifact ready",
        "regression gate green",
        "procurement self-serve path",
        "console parity achieved",
        "doc linked from funnel",
        "API export verified",
        "manual review passed",
        "e2e flow green",
        "GTM signal captured",
    ]
    steps = []
    for ti, theme in enumerate(themes):
        for si in range(10):
            v = verbs[si]
            steps.append((
                f"{v} {theme} — {phase_key} item {ti*10+si+1:03d}",
                f"{outcomes[si]} for {theme.lower()}",
                verifies[si],
                pattern,
                lanes[si],
            ))
    return steps


PHASE_2_MULTI_FRAMEWORK = _phase_steps("P2", [
    "Multi-framework dashboard spec", "ISO+NIST orientation rows", "Auditor workspace export view",
    "Cloud connector freshness UI", "HR/identity metadata index", "Framework expansion playbook",
    "Compliance operating rhythm doc", "Real-time control status badges", "Multi-entity scope callout",
    "Phase 2 regression bundle",
], "continuous-proof", "SM-02")

PHASE_3_TRUST_PLATFORM = _phase_steps("P3", [
    "Enterprise trust umbrella nav", "Privacy+risk+AI module map", "Regulatory mapping table",
    "AI inventory orientation row", "Policy workflow spec", "Global entity scope doc",
    "Procurement umbrella one-pager", "Land-expand module CTAs", "Executive trust briefing deck",
    "Phase 3 enterprise scale gate",
], "enterprise-trust", "SM-03")

PHASE_4_POLICY_PACK = _phase_steps("P4", [
    "EU AI Act policy pack block", "NIST AI RMF pack orientation", "ISO 42001 pack crosswalk",
    "Policy pack activation UX spec", "Risk register export fields", "Governance-as-code README",
    "Design-partner policy workshop", "Automated evidence field map", "Legal reviewer pack index",
    "Phase 4 policy pack verify",
], "policy-pack", "SM-04")

PHASE_5_LIFECYCLE_GOV = _phase_steps("P5", [
    "AI factsheet export stub", "Bias/drift orientation row", "Agent monitoring spec 2026",
    "FedRAMP path orientation doc", "Regulatory accelerator index", "Hybrid cloud evidence map",
    "Model lifecycle RID linkage", "Marketplace add-on pattern doc", "CRO committee readout spec",
    "Phase 5 lifecycle verify",
], "lifecycle-evidence", "SM-05")

PHASE_6_STACK_ATTACH = _phase_steps("P6", [
    "Registry-vs-receipt complement strip", "Evaluate-before-act pipeline copy", "Workspace attach diagram",
    "ITSM-linked risk orientation", "Control tower complement FAQ", "No-rip-replace positioning lock",
    "Platform policy handoff spec", "Receipt layer architecture doc", "Copilot GTM complement guide",
    "Phase 6 attach verify",
], "registry-vs-receipt", "SM-06")

PHASE_7_COMPLIANCE_CODE = _phase_steps("P7", [
    "OSCAL export stub in ZIP", "API-first evidence manifest", "Self-updating paperwork spec",
    "Live control state endpoint", "CCM dashboard orientation", "90% faster cert narrative fence",
    "60% audit-prep automation target", "Compliance-as-code README", "Federal OSCAL crosswalk",
    "Phase 7 CCM verify",
], "continuous-controls", "SM-07")

PHASE_8_AGENTIC_GRC = _phase_steps("P8", [
    "Questionnaire deflection agent spec", "Policy draft agent (internal)", "TPRM evidence gap agent",
    "Evidence ingest agent stub", "Framework mapper agent", "Remediation task agent spec",
    "Hub-only outreach fence (R-011)", "Agent roster doc (16→46 roadmap)", "GRC hours-saved metric spec",
    "Phase 8 agentic verify",
], "agentic-grc", "SM-08")

PHASE_9_ENTERPRISE_GRC = _phase_steps("P9", [
    "Enterprise risk register export", "Regulatory change feed stub", "Executive dashboard spec",
    "Fortune-scale board reporting", "Banking/insurance ICP copy", "IDC-style ROI narrative fence",
    "OSFI E-23 committee script", "FRFI shadow pilot checklist", "Bank pilot proof bar polish",
    "Phase 9 regulated verify",
], "board-reporting", "SM-09")

PHASE_10_GOVERNANCE_GRAPH = _phase_steps("P10", [
    "Governance graph data model spec", "EU AI Act + ISO dedup map", "One-control-multi-framework UX",
    "Monetary risk quant stub", "Agent governance graph row", "Cross-framework query API sketch",
    "Customer #1 proof log template", "Form PICK final sign-off", "Full 1000-step regression",
    "Market roadmap complete ceremony",
], "governance-graph", "SM-10")

ALL_PHASE_STEPS = [
    PHASE_1_TRUST_UNLOCK,
    PHASE_2_MULTI_FRAMEWORK,
    PHASE_3_TRUST_PLATFORM,
    PHASE_4_POLICY_PACK,
    PHASE_5_LIFECYCLE_GOV,
    PHASE_6_STACK_ATTACH,
    PHASE_7_COMPLIANCE_CODE,
    PHASE_8_AGENTIC_GRC,
    PHASE_9_ENTERPRISE_GRC,
    PHASE_10_GOVERNANCE_GRAPH,
]
