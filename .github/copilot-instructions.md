# Copilot Instructions for Noetfield-Systems/Noetfield

**Last Updated:** 2026-07-03  
**Org:** Noetfield-Systems  
**Repo:** Noetfield  
**Tier:** T1 (code) + T2 (local build)  

## Critical Rules

### 1. Slug Enforcement
- **REQUIRED:** Use only `Noetfield-Systems` org slug in all configs, links, and references.
- **FORBIDDEN:** Any reference to `kazemnezhadsina144-dot`.
- **Verification:** `grep -r "kazemnezhadsina144-dot" .` must return 0 results.

### 2. Read Repo State First
- Always check `.noetfield/agent_manifest.yml` for deployment restrictions.
- Read `noetfield-org/LOOP_STATE.json` in noetfeld-OS for mission priorities.
- Do NOT treat stale June docs (MSB_DEPLOY_AND_PILOT.md, WAVE0_SHIP_CHECKLIST.md) as current truth.
- If unsure, flag as `HISTORICAL_REFERENCE` instead of editing.

### 3. LOCKED Documents (Read-Only)
Files marked LOCKED must NOT be edited without `HISTORICAL_REFERENCE` marker:
- `.cursor/agent-memory/MEMORY_LOCKED.yaml`
- `PROJECT_BOUNDARIES_LOCKED.md`
- `docs/ops/CLOUD_INVENTORY_LOCKED_v1.md`
- `docs/ops/NOETFIELD_CLOUD_ORGANIZE_MASTER_PLAN_LOCKED_v1.md`
- etc.

**Exception:** Update only if document is in active execution path (e.g., active deployment URLs).

### 4. buyer-audience-verify Gate (M4 Requirement)
- All deployments must pass `verify-www-buyer-audience.sh` gate.
- You (T1): ensure gate script syntax correct.
- Do NOT bypass gate to speed deployment.
- Report failures and hand off to T0/Vercel.

### 5. No Background Waiting
- Do NOT wait for Vercel deployments to complete.
- Report merge status in PR, hand off to deployment team.
- Do NOT wait for buyer-audience verification to finish.

### 6. Forbidden Actions
- No force push.
- No direct main mutation without PR + approval.
- No editing LOCKED files without HISTORICAL_REFERENCE marker.
- No deployment without passing buyer-audience-verify.
- No editing June status without marking as HISTORICAL.

## Workflow Integration

### Noetfield Execution Flows
1. **Web Deployment (M4 Platform Surface)**
   - You (T1): update website code, pass tests
   - T0: executes `vercel-www-deploy.yml`
   - Verification: `verify-www-buyer-audience.sh` (you write, T0 runs)
   - Receipt: `web_deployment_receipt_v1.json`

2. **Trust Ledger Export (M4 Asset)**
   - You: maintain TLE sample export script
   - Fetch TLEE samples from sina-governance-SSOT with Noetfield-Systems URLs
   - Report via `tlee_sample_export_receipt_v1.json`

3. **Buyer Audience Verification (M4 Gate)**
   - Script runs audience validation before deployment
   - You: ensure script logic correct
   - T0: orchestrates workflow
   - Receipt: `buyer_audience_verification_receipt_v1.json`

### Your T1/T2 Responsibilities
- Implement website features (T1)
- Fix buyer-audience-verify failing checks (T1)
- Local build validation (T2 via Cursor)
- Maintain TLE export script
- Report status via PR (no waiting)

## Repo State Checklist (Before Any Work)

```bash
# 1. Verify org slug
grep -r "kazemnezhadsina144-dot" . && echo "ERROR: Old slug found!" || echo "✓ No old slug"

# 2. Check mission M4 state
cat ../noetfeld-OS/noetfield-org/LOOP_STATE.json | jq '.mission_stack.M4'

# 3. Identify LOCKED files touched
git status | grep -E "LOCKED|CHECKLIST|MSB_DEPLOY"

# 4. Verify Vercel deploy config
grep -r "github.com" . | grep -v "Noetfield-Systems" && echo "WARNING: Old slug URLs!" || echo "✓ All org URLs"

# 5. Run tests
npm test 2>/dev/null || npm run build 2>/dev/null || echo "No tests configured"
```

## LOCKED Files Policy

If you need to edit a LOCKED file:
1. Mark edits with `HISTORICAL_REFERENCE` comment
2. Explain why edit was necessary (active config vs. historical prose)
3. Example:
   ```markdown
   <!-- HISTORICAL_REFERENCE: Updated GitHub URL from kazemnezhadsina144-dot to Noetfield-Systems (2026-07-03) -->
   ```
4. Open PR, explain change
5. Request approval

**Do NOT delete LOCKED files** — preserve audit trail.

## buyer-audience-verify Debugging (If Gate Fails)

1. **Check script syntax:** `bash verify-www-buyer-audience.sh --dry-run`
2. **Review error log:** See what validation failed
3. **Fix issue:** Update script or website config
4. **Open PR:** Describe fix
5. **Let T0 re-run:** Do NOT manually re-trigger workflow

## Signing Off (Before PR)

When changes are ready:
1. Run checklist above
2. Commit: `feat: [description] — Noetfield-Systems org migration`
3. Push to branch
4. Open PR with:
   - **Title:** Concise description
   - **Description:**
     ```
     **Repo:** Noetfield-Systems/Noetfield
     **Tier:** T1/T2 builder
     **Mission:** M4 platform surface
     
     **Changes:**
     - [File changes summary]
     - [LOCKED file edits with HISTORICAL_REFERENCE if any]
     
     **buyer-audience-verify:** [pass/fail]
     **Vercel Deploy Hook:** [URL check]
     **TLEE Export:** [working/needs fix]
     **SHA:** [git rev-parse HEAD]
     **Files Changed:** [git diff --stat HEAD~1 HEAD]
     ```
   - **Reviewers:** Request 2 approvals

## Escalation Path

- **Deployment gate failed:** GitHub issue `buyer-audience-verify-debug`
- **Need Vercel action:** File issue `needs-t0-vercel-deploy`
- **TLEE fetch failing:** GitHub issue `tlee-sync-error`
- **LOCKED file conflict:** GitHub issue `locked-file-update-needed` (with reason)

## Related Docs

- **Manifest:** `.noetfield/agent_manifest.yml` (your M4 builder role)
- **Tool Routing:** `../noetfeld-OS/noetfield-org/ROUTING_MATRIX.md` (L17 access)
- **Agent Registry:** `../noetfeld-OS/noetfield-org/AGENT_REGISTRY.md` (M4 assignment)
- **Loop State:** `../noetfeld-OS/noetfield-org/LOOP_STATE.json` (mission priorities)
- **Verification:** `../noetfeld-OS/noetfield-org/SYNC_RECEIPTS.md` (verified windows)

---

**Last Rule:** Before pushing: "Am I using Noetfield-Systems slug? Did I mark LOCKED edits? Will buyer-audience-verify pass? Am I on a branch? Ready for PR?" If yes to all, proceed. If no, do not commit.
