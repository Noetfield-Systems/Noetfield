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

# SourceA mandatory sync status (cloud VM)

**Agent tag:** `NF-CLOUD-AGENT`  
**Rule:** R-009 — do not pseudo-ACK missing mandatory files  
**Updated:** 2026-06-03 (10-step ship plan — Step 2 bridge)

---

## Step 2 bridge (10-step ship plan)

After every ops go-live, founder Mac:

```bash
./scripts/sync-sourceA-desktop.sh
```

Then:

1. Bump `governance/OPS_LIVE_STATUS_LOCKED.json` `status_version`
2. Mirror ops deltas to TrustField notice (R-001 — Noetfield repo does not auto-sync)
3. Optional: `NF_REQUIRE_SOURCEA=1 ./scripts/verify-agent-scope.sh`

**Cloud agent:** Cannot run sync on VM — uses [OPS_LIVE_STATUS_LOCKED.json](../../governance/OPS_LIVE_STATUS_LOCKED.json) + [OPS_WITNESS_AUDIT_LOCKED_v1.md](./OPS_WITNESS_AUDIT_LOCKED_v1.md) until mirror exists.

---

## Mandatory handoff files (founder Mac → cloud)

| File | Expected mirror | Cloud status |
|------|-----------------|--------------|
| `MANDATORY_NOETFIELD_CHAT` | `ops/private/sourceA/...` or founder paste | **Not readable** in cloud VM |
| Operating Tracker | SourceA sync | **Not readable** |
| RESEARCH enforcer saves | SourceA | **Not run** (no SourceA on VM) |

---

## What cloud agents use instead

| Need | In-repo substitute |
|------|-------------------|
| Read order | [AGENT_READ_LINKS_LOCKED_v1.md](./AGENT_READ_LINKS_LOCKED_v1.md) |
| Ship queue | [GTM_NEXT.md](./plans/no-asf/GTM_NEXT.md) · [os/plan.json](../../os/plan.json) |
| Agentic law | [FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md](./FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md) |

---

## Founder action (Phase 9)

```bash
# On founder Mac
./scripts/sync-sourceA-desktop.sh
```

Then confirm paths in [AGENT_READ_LINKS_LOCKED_v1.md](./AGENT_READ_LINKS_LOCKED_v1.md) § Cloud ship.

**Agentic commercial P0:** `ship-design-partner-outreach-026` — execute on founder Hub per [DESIGN_PARTNER_PIPELINE_v1.md](../../copilot/DESIGN_PARTNER_PIPELINE_v1.md) (not NF-CLOUD implement).

**Stale PRs:** Founder should close #2 and #7 on GitHub (cloud token cannot close).

**Until sync:** NF-CLOUD blocks mandatory-SourceA claims; repo-locked paths suffice for GTM/verify work.

**Optional enforce:** `NF_REQUIRE_SOURCEA=1 ./scripts/verify-agent-scope.sh` — fails if `ops/private/sourceA/.../SEMI_NOTICE_noetfield_cloud_v1.md` missing.
