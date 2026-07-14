---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-07-14"
doc_id: nf-www-universal-policy-enforcement-candidate-v1
---

> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-07-14

# Noetfield www — universal policy enforcement candidate (v1)

**Status:** `CANDIDATE_PENDING_UNIVERSAL_POLICY_INTEGRATION`  
**Not:** institutional closure · not production promote · not merge authority

## What this candidate is

1. Durable repository copy of `.cursor/rules/000-noetfield-universal-change-preservation-law-v1.mdc`
2. Noetfield.com anti-stale / protected-surface gate under that law

## Authority chain (canonical)

```text
founder-approved source SHA
  → verified build
  → exact-SHA promotion
  → verified public fingerprint
  → immutable receipt
```

**Live HTML is not SSOT.** Live is a deploy constraint signal (detect `LIVE_AHEAD_OF_GIT` / protected regressions). Locked markers live in `config/noetfield-www-protected-surfaces.v1.json`.

## Insufficient proof (rejected)

- HTTP 200 alone
- CI green alone
- Generic marketing text
- Clean local HEAD without `NF_AUTHORIZED_PROMOTE_SHA`
- Stash → deploy HEAD isolation

## Machine artifacts

| Artifact | Path |
|----------|------|
| Change manifest | `config/change-manifests/www-universal-policy-enforcement-v1.json` |
| Protected surfaces SSOT | `config/noetfield-www-protected-surfaces.v1.json` |
| Gate | `scripts/nf_www_deploy_anti_stale_v1.py` |
| Deploy hook | `scripts/deploy-www-cloudflare.sh` (minimum promote-mode invocation) |
| CI hook | `.github/workflows/noetfield-www-ci.yml` (non-skippable self-test + offline dist mode when dist exists) |

## Promote command shape (after founder authority — not this PR)

```bash
export NF_AUTHORIZED_PROMOTE_SHA="<full founder-approved SHA>"
# tree must be clean; SHA must equal HEAD; gate must PASS
./scripts/deploy-www-cloudflare.sh
```

## Related

- Incident: `.cursor/incidents/INCIDENT-2026-07-14-001-www-stale-deploy-overwrite.md`
- Supersedes incomplete PR #106 shape (`data/`-only gate without policy package)
