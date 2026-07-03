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

# Sandbox production persistence (ship-sandbox-server-side-057)

**Redis-backed sessions** on `platform.noetfield.com` — optional but recommended for cross-device trial.

## Platform env

```bash
SANDBOX_ENABLED=true
SANDBOX_EVALUATE_LIMIT=50
SANDBOX_TRIAL_DAYS=14
SANDBOX_PROVISION_RATE_LIMIT_PER_HOUR=10
SANDBOX_BLOCK_FREE_EMAIL=true
REDIS_URL=redis://...
```

## Health

```bash
curl -sS https://platform.noetfield.com/api/sandbox/health | jq .
# expect: enabled: true, redis_backed: true
```

## www client

[assets/noetfield-sandbox.js](../assets/noetfield-sandbox.js) provisions via `POST /api/sandbox/provision` and stores `X-Sandbox-Token`.

**Verify:** `INTAKE_PERSISTENCE=memory pytest tests/unit/test_sandbox_v2.py`
