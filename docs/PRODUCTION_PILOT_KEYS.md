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

# Production pilot API keys

Server-side only — never commit secrets. See [.env.example](../.env.example).

## Enable pilot auth

On **platform.noetfield.com** (not www):

```bash
GOVERNANCE_PILOT_AUTH_REQUIRED=true
GOVERNANCE_PILOT_API_KEYS=<tenant_uuid>:<secret>[,<tenant_uuid2>:<secret2>]
```

Format: comma-separated `tenant_id:secret` pairs on the **server env**. The `tenant_id` must match JSON body `tenant_id` on evaluate.

Client `Authorization` header uses the **secret only** (see `_parse_pilot_keys` in `pilot_auth.py`). Do **not** send `tenant:secret` as the Bearer token.

## Issue a prospect key (example)

1. Generate secret: `openssl rand -hex 24`
2. Pick stable tenant UUID for the prospect sandbox (or use org id from engagement letter).
3. Add `tenant_uuid:secret` to `GOVERNANCE_PILOT_API_KEYS` and redeploy/restart platform.
4. Send prospect: `Authorization: Bearer <secret>` (secret only — not the tenant prefix).
5. Founder console paste: same Bearer secret only (from `CONSOLE_BEARER` in `~/.noetfield-platform-secrets/`).

Deploy scripts fail closed when `GOVERNANCE_PILOT_AUTH_REQUIRED=true` and keys are missing; they sync from `~/.noetfield-platform-secrets/{noetfield,platform}.env` when present.

## Verify

```bash
export PLATFORM=https://platform.noetfield.com
export PILOT_SECRET='your-secret-only'

curl -sS -X POST "$PLATFORM/api/v1/governance/evaluate" \
  -H "Authorization: Bearer $PILOT_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "00000000-0000-4000-8000-000000000099",
    "organization_id": "00000000-0000-4000-8000-000000000002",
    "action": "initiate_transfer_intent",
    "resource_type": "partner_msb",
    "resource_id": "pilot-smoke",
    "mode": "shadow",
    "request_id": "RID-PILOT-SMOKE-001"
  }'
```

## Optional

- `GOVERNANCE_WEBHOOK_URLS` — comma-separated URLs for `governance.decision.recorded`
- `INTAKE_OPS_WEBHOOK_URL` — Slack (or compatible) for new intakes → [INTAKE_OPS.md](./INTAKE_OPS.md)
