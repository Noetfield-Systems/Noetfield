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

## Primary path: Console Generate

On **https://platform.noetfield.com/console**:

1. Open the **API Keys** panel.
2. Bootstrap (first key): paste `ADMIN_DASHBOARD_SECRET` into the Admin secret field → **Generate key**.
3. Later keys: use a pilot Bearer with `workspace:admin`, or the admin secret.
4. Copy the secret **once** (shown only in the create response). The server stores a hash only.
5. Click **Use this key now** to fill the Pilot Bearer field for this session.

Admin API (same auth rules):

- `POST /api/v1/admin/pilot-keys` — create (`secret` only in 201 body)
- `GET /api/v1/admin/pilot-keys` — list (never secrets)
- `POST /api/v1/admin/pilot-keys/{key_id}/revoke`

## Break-glass: env keys

`GOVERNANCE_PILOT_API_KEYS` remains a fallback when DB keys are unavailable or for emergency access. Prefer console Generate for founders and clients.

```bash
GOVERNANCE_PILOT_AUTH_REQUIRED=true
GOVERNANCE_PILOT_API_KEYS=<tenant_uuid>:<secret>[,<tenant_uuid2>:<secret2>]
```

Format: comma-separated `tenant_id:secret` pairs on the **server env**. Client `Authorization` uses the **secret only**.

Auth order: env keys first, then hashed DB keys (`pilot_api_keys`). If auth is required and neither env nor DB has keys → `503`.

## Issue a prospect / client key

1. Console → Audience **Client** (scopes: `governance:read`, `governance:write`, `workspace:read`) — or Founder for full scopes including `workspace:admin`.
2. Optional tenant UUID binding.
3. Generate → send the prospect the secret once (Bearer only).
4. Revoke from the Keys table when the engagement ends.

## Deploy notes

Deploy scripts fail closed when `GOVERNANCE_PILOT_AUTH_REQUIRED=true` unless either:

- `GOVERNANCE_PILOT_API_KEYS` is present (vault/env/remote), **or**
- `ADMIN_DASHBOARD_SECRET` is present (DB bootstrap via console / admin API).

They still sync env pilot keys from vault when present (do not wipe Railway keys).

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
