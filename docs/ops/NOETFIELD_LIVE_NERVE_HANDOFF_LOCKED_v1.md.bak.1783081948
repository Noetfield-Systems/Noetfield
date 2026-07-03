---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-29"
doc_id: noetfield-live-nerve-handoff-locked-v1
status: LOCKED
---

# Noetfield Live Nerve Handoff - LOCKED v1

## Purpose

Noetfield agents, chatbot behavior, and deploy checks must not treat stale static docs or prior chat summaries as live truth.

The current machine truth is:

```text
governance/NOETFIELD_LIVE_NERVE_RECEIPT.json
```

If this receipt is missing or `gate=FAIL`, repair the live nerve before using docs as truth.

This receipt is scoped to:

```text
website-platform-public
```

It can prove public website/platform readiness. It must not be used alone to claim the full ecosystem is green.

## Required First Read

Before implementation work in the website/platform repo:

```bash
make verify-live-nerve
```

Then read:

```text
governance/NOETFIELD_LIVE_NERVE_RECEIPT.json
```

## What The Receipt Proves

- `N1_PUBLIC_OUTPUT`: generated `.vercel/output/static` does not expose internal truth surfaces.
- `N2_CHAT_TRUTH`: public chatbot knowledge is manifest-gated, public, fresh, and hash-matched.
- `N3_DOC_FRESHNESS`: public Markdown exposure is accounted for and raw internal docs are blocked from output.
- `N4_WWW_LIVE_OUTPUT`: live `www.noetfield.com` blocks internal/static truth URLs.
- `N5_WWW_CHAT_SEMANTIC`: live `www` public chat does not return stale source/internal language.
- `N6_PLATFORM_CHAT_SEMANTIC`: direct `platform.noetfield.com` public chat does not return stale source/internal language.
- `N7_GEL_LIVE_RUNTIME`: `api.noetfield.com` health/readiness are live and ready.
- `N8_ROUTE_NAV_TRUTH`: public nav labels do not imply missing hubs or stale public company language.
- `N9_VALIDATOR_NODE_REGISTRY`: validator registry and node catalog have no orphan validators, orphan live nodes, or missing files.
- `N13_ROUTE_INVENTORY`: required public 200 routes come from `governance/ROUTE_INVENTORY.json`, not hardcoded E2E tuples.
- `N14_RECEIPT_FRESHNESS`: stored live nerve receipt has an explicit expiry and must be refreshed when expired.

## PASS / DEGRADED / FAIL

- `PASS`: all required nodes for this named scope are green.
- `DEGRADED`: required runtime is usable, but named non-blocking warnings must be acknowledged.
- `FAIL`: one or more required nodes failed; repair before using docs as truth.

Full ecosystem green requires every named scope receipt to be `PASS`, or `DEGRADED` only when warnings are explicit and accepted by that scope owner.

SourceA foundation drift is a warning for this website/platform receipt. It does not block `www.noetfield.com` deploy unless a Noetfield public/runtime node fails.

## Freshness

The receipt includes:

```text
receipt_freshness.generated_at
receipt_freshness.expires_at
receipt_freshness.valid_for_seconds
```

If `expires_at` is in the past, run:

```bash
make verify-live-nerve
```

before using the receipt for implementation truth.

## Agent Rule

Use this order:

```text
live nerve receipt -> current source files -> validators -> docs -> chat summaries
```

Do not use:

```text
old reports, stale generated output, raw docs/ops, prior chat summaries
```

as implementation truth unless the live nerve says the relevant source is current.

## Gates

The live nerve is wired through:

```bash
make verify-live-nerve
make verify-static-www
make ship-verify
```

The cross-scope production E2E is:

```bash
make verify-www-e2e
```

The public-output scanner is:

```bash
python3 scripts/verify-public-output-allowlist.py
```

The chatbot truth scanner is:

```bash
bash scripts/verify-public-chat-truth.sh
```
