# NF-GAOS W3 — Factory Spine LOCKED

**Version:** 1.0.0 · **Status:** LOCKED · **Saved:** 2026-06-18  
**Plane:** Noetfield product (`noetfield_cloud`)  
**Parent:** [`NF_GAOS_W1_LOCKED_v1.md`](./NF_GAOS_W1_LOCKED_v1.md) · [`ROUTING_CARD.md`](../ROUTING_CARD.md)  
**SourceA pattern:** session gate → live surfaces → receipt cascade → execution gatekeeper (read-only mirror)

## One sentence

> **Disk is SSOT.** NF-GAOS W3 adds SourceA-grade **live surfaces**, **truth bundle**, **receipt cascade**, and **execution gatekeeper** — orientation stays manual; implement requires gate PASS + founder `implement`.

## Mental model

```text
make nf-onboard
  → session_gate → live_orient → routing_card → stale_guard → voyage
  → live_surfaces (product_now_line) → receipt_cascade → gatekeeper (advisory)
  → panel export

Before first edit:
  NF_FOUNDER_IMPLEMENT=1 make nf-gatekeeper --require-implement
```

## New artifacts (W3)

| Asset | Path |
|-------|------|
| Orient SSOT | `data/nf_orient_routing_v1.json` |
| Live surfaces | `~/.sina/nf-live-surfaces-v1.json` |
| Truth bundle | `~/.sina/nf-truth-bundle-v1.json` |
| Receipt cascade | `~/.sina/nf-receipt-cascade-v1.json` |
| Gatekeeper | `~/.sina/nf-gatekeeper-receipt-v1.json` |
| Repo map | `os/NF_REPO_CAPABILITY_MAP.json` |

## Agent quote rule (mandatory)

Every substantive reply quotes **`product_now_line`** from `nf-live-surfaces-v1.json` — not chat memory.

## Laws

- **Never** auto-run `make nf-orient` on session start
- **Never** mix `sa-*` / `mx-*` in nf cloud session (RF-010)
- **Never** edit `~/Desktop/SourceA/` from this repo
- **Never** open visible Chrome — curl/headless verify only
- Gatekeeper FAIL → **EXECUTION DENIED** — no file edits

## Verify (machine proof — not prose)

```bash
make nf-prove-factory-spine    # scripts/prove-nf-factory-spine-v1.py
make verify-nf-gaos-w3         # full W3 gate + proof harness
pytest tests/unit/test_nf_factory_spine_v1.py -q
```

Proof receipt: `~/.sina/nf-factory-spine-proof-v1.json` · `reports/agent-auto/events/nf-factory-spine-proof-v1.json`

## Cross-plane note

SourceA Worker keeps `factory-now-v1.json` + `agent-live-surfaces-v1.json`. Noetfield keeps **nf-** prefixed mirrors. Mono `repo-find.sh` remains ecosystem router.
