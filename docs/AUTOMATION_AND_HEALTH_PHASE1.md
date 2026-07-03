# Noetfield Automation & Health Schemas (PHASE 1)

Cross-repo patterns learned from noetfeld-os and intelligently adapted for Noetfield's needs.

## Schemas

### Cycle Receipt v1 (Per-Workflow)

Every Tier-1 workflow (www-ci, platform-deploy, supabase-heartbeat) emits this on completion:

```json
{
  "schema": "noetfield-cycle-receipt-v1",
  "workflow_id": "noetfield-www-ci",
  "sandbox_id": "noetfield-repo",
  "timestamp": "2026-07-02T23:15:00Z",
  "trigger_source": "push|pull_request|schedule|manual",
  "state_before": "IDLE_NO_WORK",
  "state_after": "COMPLETE|FAILED_WITH_RECEIPT",
  "slo_target": "pass_rate>99%,latency<60s,zero_critical_issues",
  "slo_result": "PASS|MISS",
  "exit_code": 0,
  "duration_seconds": 45,
  "dirty_count_before": 5,
  "dirty_count_after": 0,
  "value_class": "revenue_path|proof_asset|hygiene",
  "evidence": [
    {
      "check": "sitemap_verified",
      "passed": true,
      "detail": "sitemap.xml committed and valid"
    }
  ]
}
```

Stored in: `governance/NOETFIELD_CYCLE_RECEIPTS_v1.jsonl` (append-only log)

### Heartbeat v1 (Daily Rollup)

One entry per calendar day at 06:00 UTC:

```json
{
  "schema": "noetfield-heartbeat-v1",
  "date": "2026-07-02",
  "workflows": [
    {
      "id": "noetfield-www-ci",
      "runs": 3,
      "passed": 3,
      "failed": 0,
      "slo_pass_rate": "100%",
      "avg_duration_seconds": 45,
      "value_class": "revenue_path"
    }
  ],
  "surfaces": {
    "www_home": { "reachable": true, "status_code": 200 },
    "platform_health": { "reachable": true, "status_code": 200 },
    "gel_api_health": { "reachable": true, "status_code": 200 }
  },
  "policy": {
    "check_pass": true,
    "policy_hash": "abc123...",
    "repo_clean": true,
    "dirty_count": 0
  },
  "escalations": []
}
```

Stored in: `governance/NOETFIELD_HEARTBEAT_v1.jsonl` (one per day)

### Gate Receipt v1 (SLO Pass/Fail)

Emitted by each workflow's health reporting step:

```json
{
  "schema": "gate-receipt-v1",
  "workflow_id": "noetfield-www-ci",
  "timestamp": "2026-07-02T23:15:00Z",
  "decision": "PASS|FAIL",
  "slo_targets": ["pass_rate>99%", "latency<60s", "zero_critical_issues"],
  "actual_results": ["pass_rate:100%", "latency:45s", "critical_issues:0"],
  "evidence": [
    {
      "command": "make site-health",
      "exit_code": 0,
      "output_tail": "all checks passed"
    }
  ]
}
```

### Cleanliness Report v1 (Repo State Snapshot)

Run by `scripts/verify_repo_cleanliness_v1.py`:

```json
{
  "schema": "repo-cleanliness-v1",
  "timestamp": "2026-07-02T23:15:00Z",
  "dirty_count": 5,
  "triage_threshold": 30,
  "status": "OK|TRIAGE_REQUIRED",
  "dirty_files": {
    "untracked": ["file1.tmp"],
    "modified": ["file2.md"],
    "staged": ["file3.py"]
  }
}
```

Stored in: `governance/NOETFIELD_CLEANLINESS_v1.jsonl` (on-demand, not append)

### Health Probe v1 (Service Status)

Run by `scripts/noetfield_health_v1.py`:

```json
{
  "schema": "noetfield-health-v1",
  "timestamp": "2026-07-02T23:15:00Z",
  "service": "noetfield",
  "version": "0.1.0",
  "status": "ok|degraded|failed",
  "policy": {
    "check_pass": true,
    "policy_hash": "abc123...",
    "forbidden_markers_found": false
  },
  "surfaces": {
    "www_probes": [
      { "name": "www-home", "reachable": true, "status_code": 200 }
    ],
    "reachable_count": 5,
    "total_probes": 6
  }
}
```

---

## Governance Files (Phase 1)

- `governance/WORKFLOW_HEALTH_RECEIPTS_LOCKED.json` — SLO definitions (already created in PR #81)
- `governance/NOETFIELD_CYCLE_RECEIPTS_v1.jsonl` — Per-workflow cycle logs (NEW)
- `governance/NOETFIELD_HEARTBEAT_v1.jsonl` — Daily rollup (NEW, workflow-driven)
- `governance/NOETFIELD_CLEANLINESS_v1.jsonl` — Repo state snapshot (NEW, script-driven)

---

## Integration Points

### Tier-1 Workflows
Each of `.github/workflows/{noetfield-www-ci,platform-deploy,supabase-heartbeat}.yml` will:
1. Run existing health checks (already done in PR #81)
2. Emit cycle receipt on success/failure (NEW)
3. Write receipt to artifact (NEW, collected by heartbeat workflow)

### Daily Heartbeat Workflow
New: `.github/workflows/noetfield-daily-heartbeat.yml`
- Schedule: 06:00 UTC daily
- Collect: All cycle receipts from past 24h
- Probe: Health endpoints
- Emit: Heartbeat receipt

### Policy Integration
- `scripts/check_repo_policy.py` already runs; include results in health probes
- `scripts/verify_repo_cleanliness_v1.py` runs on-demand (PR pre-merge)
- Both feed into daily heartbeat

---

## Phase 1 Deliverables (THIS IMPLEMENTATION)

✅ `scripts/noetfield_health_v1.py` — Health probe (new)
✅ `scripts/verify_repo_cleanliness_v1.py` — Cleanliness check (new)
✅ Updated WORKFLOW_HEALTH_RECEIPTS_LOCKED.json schema doc (already in PR #81)
✅ Cross-repo learning patterns documented

## Phase 2 (Deferred)

- Extend Tier-1 workflows to emit cycle receipts  
- Add daily heartbeat workflow
- Kaizen auto-filing on SLO miss

## Phase 3+ (Future)

- ROI-based throttling
- External verify receipts
