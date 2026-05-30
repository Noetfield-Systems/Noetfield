# Go forward now — Noetfield (simple path)

**Noetfield is the company that ships today.** TrustField, VIRLUX, and other entities are separate products and repos — different paths, no mixing in this codebase.

**What Noetfield is:** A **client-facing governance platform** — public www, documented API, console, SDK, and paid engagements. Fintech, PSP, MSB, exchange, and bank teams integrate **before** they execute trades or payments.

**What Noetfield is not:** A bank, MSB, PSP, or custody layer. Partners and clients execute; Noetfield decides and records evidence.

---

## Make money (in order)

| Step | Offer | Who pays | How to start |
|------|--------|----------|--------------|
| 1 | **Trust Brief** — $10,000 CAD | Any serious buyer | [/trust-brief/intake/](/trust-brief/intake/) |
| 2 | **Pilot API** — shadow evaluate | Fintech / exchange / PSP engineering | [/partners/](/partners/) → intake `partner-msb` or `partner-exchange` |
| 3 | **Shadow Pack** (30-day pilot, private quote) | Same | SOW in `ops/private/msb/` after `./scripts/seed-msb-partner-pack.sh` |
| 4 | **Annual API license** | After shadow works | Per-tenant keys on platform |

**Inbound:** operations@noetfield.com · every deal gets a **RID**.

---

## Ship this week (founder)

1. Merge open PRs → deploy **www** + **platform.noetfield.com**
2. Turn on pilot keys: `GOVERNANCE_PILOT_AUTH_REQUIRED=true`
3. Run one **Shadow Week** demo ([SHADOW_WEEK_DEMO.md](../SHADOW_WEEK_DEMO.md))
4. Send 10 outreaches ([msb-partner-playbook.md](./msb-partner-playbook.md) — works for fintech/PSP/exchange too)

---

## Client-facing surfaces (use these in sales)

| Surface | URL |
|---------|-----|
| Partners + API story | https://www.noetfield.com/partners/ |
| API docs | https://www.noetfield.com/docs/api/ (repo: `docs/api/`) |
| Live evaluate | `POST /api/v1/governance/evaluate` |
| Console demo | https://platform.noetfield.com/console |
| Status | https://www.noetfield.com/status/ |

---

## One sentence for buyers

> Noetfield is the governance API your stack calls before a trade or payment runs — allow, restrict, or block, with an audit trail your compliance team can export.

---

## Do not block yourself on

- Perfect GovernancePacket schema — ship evaluate + audit export first
- Naming NDAX on the homepage — use “licensed exchange” until co-marketing is signed
- Building routing inside Noetfield — routing stays with TrustField or the client’s execution layer

**Move:** deploy → demo → invoice Trust Brief or Shadow Pack → wire staging API.
